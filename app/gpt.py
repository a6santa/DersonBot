import os
import time

from openai import OpenAI
from datetime import datetime

from app.services import buscar_servicos
from app.db import MessageDatabase

client = OpenAI(api_key=os.environ.get("OPENAI_TOKEN"))


def excute_model_completions(messages: list, tools: list = None) -> str:
    """Função que executa o modelo do openai"""
    if tools:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=1,
            max_tokens=500,
            top_p=1,
            frequency_penalty=0.5,
            presence_penalty=0,
            tools=tools,
            parallel_tool_calls=True,
            response_format={"type": "text"},
        )
    else:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=1,
            max_tokens=500,
            top_p=1,
            frequency_penalty=0.5,
            presence_penalty=0,
            response_format={"type": "text"},
        )

    return response


def create_assistant(config: dict):
    """Função que cria assistente OpenAI"""

    db = MessageDatabase(table="assistant")

    instructions = f"""
        Você é um assistente virtual simpático e acolhedor que atende os clientes da {config.get('seller')} via WhatsApp. Interaja com os clientes com um toque de cordialidade e preocupação genuína, sempre buscando tornar a interação o mais pessoal e agradável possível.
        - Ao receber uma mensagem do cliente:
        - Dê boas-vindas calorosas.
        - Pergunte como pode ajudar e tome o cuidado de chamar o cliente pelo nome sempre que este for fornecido. Caso o nome não seja mencionado, pergunte gentilmente.

        - Informação sobre serviços:
        - Caso o cliente pergunte sobre os serviços oferecidos, utilize a função `buscar_servicos_salao` para listar todos os serviços disponíveis. A lista pode conter emojis pertinentes para tornar o conteúdo mais ilustrativo e leve. Por exemplo, ✂️, 💈, ou 💆.
        - Se o cliente perguntar sobre um serviço específico, use a função `buscar_servicos_salao` para confirmar se ele está disponível:
            - Se o serviço estiver presente na lista, confirme ao cliente sua disponibilidade e pergunte se ele gostaria de agendar.
            - Caso contrário, peça desculpas educadamente e sugira alternativas de outros serviços que a barbearia oferece.

        - Tonalidade:
        - Mantenha sempre um tom simpático, amigável e disposto a ajudar.
        - A experiência do cliente deve ser sempre positiva, acolhedora e sem pressões.

        # Steps

        1. **Boas-vindas**:
        - Ofereça uma calorosa saudação e, se possível, use o nome do cliente. Ex.: "Olá, [nome]! Bem-vindo à {config.get('seller')}! 😊 Como posso ajudar você hoje?"

        2. **Consultar Serviços**:
        - Utilize `buscar_servicos_salao` se o cliente solicitar a lista completa de serviços.
        - Inclua emojis pertinentes para tornar a resposta mais amigável.

        3. **Consultar Serviço Específico**:
        - Confirme se um serviço específico está disponível com `buscar_servicos_salao`.
        - Caso disponível, ofereça agendamento. Caso não esteja, peça desculpas e sugira outros serviços relacionados.

        4. **Interação Pessoal e Acolhedora**:
        - Certifique-se de tratar cada solicitação de forma gentil, facilitando ao máximo o contato do cliente com a barbearia.

        # Output Format

        - **Resposta inicial**: Mensagem calorosa perguntando como ajudar, sempre que possível, incluindo o nome do cliente.
        - **Listar Serviços**: Utilize a função `buscar_servicos_salao` e apresente os serviços de forma enumerada com emojis quando possível.
        - **Confirmação/Atenção ao Cliente**: Sempre seja educado, confirme se um serviço está disponível e ofereça alternativas caso não esteja.

        # Examples

        **Input**: "Oi, eu gostaria de saber os serviços que vocês oferecem."
        **Output**:
        "Olá! 😊 Esses são os serviços que oferecemos na {config.get('seller')}:
        - ✂️ Corte de cabelo
        - 💇‍♂️ Barba
        - 💆 Tratamento capilar
        Em qual desses serviços você gostaria de agendar?"

        **Input**: "Vocês fazem coloração?"
        **Output**:
        "Olá! Pelo que consultei aqui, não temos serviço de coloração disponível no momento. 😔 Mas temos outros serviços como:
        - ✂️ Corte de cabelo
        - 💇‍♂️ Barba
        Talvez algum outro interesse você? Estou aqui para ajudar!"

        # Notes

        - Sempre busque criar uma atmosfera agradável e acolhedora.
        - Se o cliente parecer indeciso, encoraje-o de maneira gentil e nunca coloque pressão para a tomada de decisões.
        Por exemplo, use frases como "Fique à vontade para me dizer o que prefere, estou aqui para ajudar!"
    """

    assistant = client.beta.assistants.create(
        name="BotDerson",
        instructions=instructions,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "buscar_servicos",
                    "description": "Busca serviços que o salão oferece, como por exemplo corte, barba e corte infantil",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                        "required": [],
                    },
                },
            }
        ],
        model="gpt-4o",
    )

    db.insert({"assistant_id": assistant.id, "model": assistant.model})


def execute_assistant(
    question: str, instructions: str, assistant_id: str, thread_id: str = None
):
    """Executa thread de conversa com assistente OpenAI"""

    messages = None
    # Cria ou usa a thread existente
    if not thread_id:
        thread = client.beta.threads.create()
        thread_id = thread.id

    # Envia a mensagem do usuário para a thread
    client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=question
    )

    # Cria e executa o assistente
    run = client.beta.threads.runs.create(
        thread_id=thread_id, assistant_id=assistant_id, instructions=instructions
    )

    available_functions = {
        "buscar_servicos": buscar_servicos,
    }

    # Aguarda a execução ser concluída
    while run.status in ["queued", "in_progress", "cancelling"]:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    # Processa a execução conforme o status
    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread_id)

    elif run.status == "requires_action":
        tool_outputs = []
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            function_name = tool.function.name
            function_to_call = available_functions.get(function_name)
            if function_to_call:
                function_response = function_to_call()
                tool_outputs.append(
                    {"tool_call_id": tool.id, "output": function_response}
                )

        if tool_outputs:
            try:
                client.beta.threads.runs.submit_tool_outputs_and_poll(
                    thread_id=thread_id, run_id=run.id, tool_outputs=tool_outputs
                )
                print("Tool outputs submitted successfully.")
                run = client.beta.threads.runs.retrieve(
                    thread_id=thread_id, run_id=run.id
                )

                messages = client.beta.threads.messages.list(thread_id=thread_id)

            except Exception as e:
                print(f"Failed to submit tool outputs: {e}")
        else:
            print("No tool outputs to submit.")
    else:
        print(f"Erro: {run.status}")

    return thread_id, messages.data[0].content[0].text.value


def make_response(question: str, from_number: str) -> str:
    """Função que responde o cliente dados sua pergunta"""

    db_message = MessageDatabase(table="messages")
    resuts_db = db_message.search_messages(user_id=from_number)

    previus_messages = None
    if len(resuts_db) > 0:
        conversations = resuts_db[0]["messages"][-10:]

        previus_messages = "\n".join(
            [
                f"User: {msgs['user']} \n Assistant: {msgs['bot']}"
                for msgs in conversations
            ]
        )

        instructions = (
            f"O Cliente já falou conosco segue as ultimas conversas: {previus_messages}"
            if previus_messages
            else None
        )
    else:
        instructions = "Este cliente não tem historico de conversa no bot, trate ele muito bem para cativa-lo"

    assistant_id = "asst_PhStNrXzL4eOngFNXLmH91vI"
    
    db_threads = MessageDatabase(table="threads")
    return_db = db_threads.search_thread(user_id=from_number)
    
    thread_id = None
    
    if len(return_db) > 0:
        thread_id = return_db[0].get('thread_id')


    new_thread_id, return_assistant = execute_assistant(
        question=question,
        instructions=instructions,
        assistant_id=assistant_id,
        thread_id=thread_id,
    )

    if not thread_id:
        db_threads.insert(
            value={
                "user_id": from_number,
                "thread_id": new_thread_id,
                "expiron_time": time.time() + 24 * 60 * 60,
            }
        )

    db_message.append_message(
        user_id=from_number,
        message={
            "user": question,
            "bot": return_assistant,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    )

    return return_assistant
