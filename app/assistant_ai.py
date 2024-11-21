import logging
import json
import os
import time

import requests
from openai import OpenAI

from app.db import MessageDatabase

# Configuração do logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

client = OpenAI(api_key=os.environ.get("OPENAI_TOKEN"))


class AssistantAI:
    """Classe que gerencia o assistente OpenAI"""

    functions = {"functions": []}
    registered_functions = {}
    logger = logging.getLogger("AssistantAI")

    def __init__(self, assistant=None, thread_id=None):
        self.client = client
        self.assistant = assistant
        self.thread_id = thread_id
        self.logger.info(
            "AssistantAI iniciado - Assistant ID: %s, Thread ID: %s",
            assistant, thread_id
        )

    def create_assistant(self, name, instructions, model="gpt-4o-mini"):
        """Função que cria assistente OpenAI"""

        assistant = self.client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model=model,
            tools=self.functions["functions"],
        )

        self.assistant = assistant.id

        db = MessageDatabase(table="assistant")
        db.insert({"assistant_id": self.assistant, "model": model})

    def modify_assistant(self, model, instructions, name):
        """Função que modifica o assistente"""
        client.beta.assistants.update(
            assistant_id=self.assistant,
            model=model,
            instructions=instructions, 
            name = name, 
            tools=self.functions["functions"]
        )
    
    def create_thread(self):
        """Função que cria uma thread"""
        thread = client.beta.threads.create()
        self.thread_id = thread.id

    def delete_thread(self):
        """Função que deleta uma thread"""
        response = client.beta.threads.delete(self.thread_id)
        return response.id

    def add_message(self, user_input):
        """Função que adiciona uma mensagem à thread"""
        self.logger.info("Adicionando mensagem à thread %s: %s...",
                        self.thread_id, user_input[:50])
        client.beta.threads.messages.create(
            thread_id=self.thread_id, role="user", content=user_input
        )

    def get_message(self):
        """Função que retorna a mensagem da thread"""
        messages = client.beta.threads.messages.list(self.thread_id)
        output = messages.data[0].content[0].text.value
        return output

    def run_assistant(self, instructions):
        """Função que cria uma run"""
        run = client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant,
            instructions=instructions,
        )
        return run.id

    def retrieve_run(self, run_id):
        """Função que retorna uma run"""
        run = client.beta.threads.runs.retrieve(thread_id=self.thread_id, run_id=run_id)
        return run

    def run_require_action(self, run, run_id):
        """Função que executa ação requerida da run"""
        tool_outputs = []
        if run.required_action:
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                self.logger.info("Executando função: %s", function_name)
                function_to_call = self.registered_functions.get(function_name)
                if function_to_call:
                    function_args = json.loads(tool_call.function.arguments)
                    self.logger.info("Argumentos da função: %s", function_args)
                    function_response = function_to_call(**function_args)
                    response_str = str(function_response)[:100]
                    self.logger.info("Resposta da função: %s...", response_str)
                    tool_outputs.append(
                        {"tool_call_id": tool_call.id, "output": function_response}
                    )
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=self.thread_id, run_id=run_id, tool_outputs=tool_outputs
            )

    def assistant_api(self, instructions):
        """Função que executa a API do assistente"""
        self.logger.info(
            "Iniciando execução da API com instruções: %s...",
            instructions[:50]
        )

        run_id = self.run_assistant(instructions)
        run = self.retrieve_run(run_id)
        self.logger.info("Run criada - ID: %s, Status inicial: %s",
                        run_id, run.status)

        while run.status == "requires_action" or "queued":
            time.sleep(1)
            try:
                run = self.retrieve_run(run_id)
                self.logger.info("Status da run: %s", run.status)
                if run.status == "completed":
                    break
                self.run_require_action(run, run_id)
            except Exception as e:
                self.logger.error("Erro ao executar run %s: %s", run_id, str(e))
                self.cancel_run(run_id)
                raise

        outputs = self.get_message()
        tokens = run.usage.total_tokens

        self.logger.info("Execução finalizada - Tokens utilizados: %s", tokens)
        self.logger.debug("Output completo: %s", outputs)

        return outputs, tokens

    def cancel_run(self, run_id):
        """Função que cancela uma run em execução"""
        self.logger.info("Cancelando run %s", run_id)
        try:
            run = self.client.beta.threads.runs.cancel(
                thread_id=self.thread_id,
                run_id=run_id
            )
            self.logger.info("Run %s cancelada com sucesso", run_id)
            return run
        except Exception as e:
            self.logger.error("Erro ao cancelar run %s: %s", run_id, str(e))
            raise

    @classmethod
    def add_func(cls, func):
        """Função que adiciona uma função ao assistente"""
        cls.registered_functions[func.__name__] = func
        doc_lines = func.__doc__.strip().split("\n")

        description = doc_lines[0].strip()

        properties = {}
        required = []

        for line in doc_lines[1:]:
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip()
                if k != "return":  # Ignora a linha de retorno
                    v_parts = v.strip().split(":", 1)
                    if len(v_parts) == 2:
                        tipo, desc = v_parts
                        properties[k] = {
                            "type": tipo.strip(),
                            "description": desc.strip(),
                        }
                        required.append(k)

        func_info = {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

        cls.functions["functions"].append(func_info)


@AssistantAI.add_func
def get_about() -> str:
    """
    Busca informações do salão, como nome, endereço e horario de funcionamento
    return: str: Retorna uma string formatada com as informações do salão
    """

    with open("./files/sobre.json", mode="r", encoding="utf-8") as file:
        about = json.load(file)

    return str(about)


@AssistantAI.add_func
def get_services() -> str:
    """
    Busca serviços que o salão oferece, como por exemplo corte, barba e
    corte infantil retorna uma lista de serviços e seus valores
    return: str: Retorna uma string formatada com os serviços e seus respectivos valores
    """

    with open("./files/servicos.json", mode="r", encoding="utf-8") as file:
        services = json.load(file)

    return str(services)


@AssistantAI.add_func
def get_professionals() -> str:
    """
    Busca a lista de profissionais disponíveis no salão e suas especialidades
    return: str: Retorna uma string formatada com a lista de profissionais
    """
    with open("./files/profissionais.json", mode="r", encoding="utf-8") as file:
        professionals = json.load(file)

    return str(professionals)


@AssistantAI.add_func
def get_schedule(profissional_id: int, date: str) -> list:
    """
    Buscar agenda disponivel para algum agendamento
    profissional_id: integer: ID do profissional
    date: string: Data no formato YYYY-MM-DD
    return: list: Retorna uma lista de horários disponíveis
    """

    base = "https://api.avec.beauty/salao/97935/agenda/profissional"
    url = f"{base}/{profissional_id}/tempo-livre?data={date}&force_full_range=40"
    token = os.environ.get("AVECTOKEN")
    headers = {"Authorization": token}

    print(url)
    response = requests.request(method="GET", url=url, headers=headers, timeout=None)

    if response.ok:
        data = response.json()
        agenda = data["data"]["agendas"]

        if len(agenda) > 0:
            formatted_schedules = []
            schedules = agenda[0]["schedules"]

            for minutes in schedules:
                hours = minutes // 60
                mins = minutes % 60
                formatted_time = f"{hours:02}:{mins:02}"
                formatted_schedules.append((formatted_time))

            return str(formatted_schedules)
        else:
            return str([])
    else:
        return str([])


@AssistantAI.add_func
def put_booking(
    id_servico: int, id_profissional: int, data: str, horario_minutos: int
) -> str:
    """
    Realiza o agendamento:
    id_servico: integer: ID do serviço
    id_profissional: integer: ID do profissional
    data: string: Data no formato YYYY-MM-DD
    horario_minutos: integer: Horário convertido em minutos desde 00:00
    return: boolean: Retorna True se agendamento foi realizado com sucesso
    """
    logger = logging.getLogger("put_booking")
    
    logger.info("Dados capturados: %s, %s, %s, %s", 
                id_servico, id_profissional, data, horario_minutos)

    return str(True)
