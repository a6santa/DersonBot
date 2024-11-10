import os
from openai import OpenAI

from app.services import buscar_servicos

client = OpenAI(api_key=os.environ.get("OPENAI_TOKEN"))

def excute_model(messages: list, tools: list=None) -> str:
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

def make_response(intention: str, question: str, config: dict) -> str:
    """Função que responde o cliente dados sua pergunta"""
    result = None

    if intention == "new_msg":
        prompt = f"""
        Você é um assistente virtual muito gentil, que atende os clientes da {config.get('seller')} 
        com simpatia e cordialidade. Quando um cliente entra em contato pelo WhatsApp, dê-lhe as
        boas-vindas calorosamente e pergunte o que ele deseja. Sempre que possível, chame o cliente 
        pelo nome para tornar a conversa mais pessoal e acolhedora.

        Se o cliente perguntar sobre os serviços oferecidos pela {config.get('seller')}, 
        utilize a função "buscar_servicos_salao" para listar todos os serviços disponíveis.

        Se o cliente perguntar sobre um serviço específico, utilize também a função "buscar_servicos_salao" para verificar se o 
        serviço está na lista. Se o serviço estiver disponível, responda ao cliente confirmando e oferecendo agendamento. Caso o 
        serviço não esteja disponível, peça desculpas educadamente e sugira outros serviços que a {config.get('seller')} oferece.

        Lembre-se de sempre manter um tom amigável, paciente e disposto a ajudar. 
        A experiência do cliente deve ser sempre positiva e acolhedora.

        Se perguntarem os serviços podem lista-lo com emoji pertinente ao serviço
        """
        tools = [
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
        ]

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ]

        result = excute_model(messages=messages, tools=tools)

        available_functions = {
            "buscar_servicos": buscar_servicos,
        }

        if result.choices[0].message.tool_calls:

            for call in result.choices[0].message.tool_calls:
                print(call)
                
                function_name = call.function.name
                tool_call_id = call.id
                function_to_call = available_functions.get(function_name)
                function_response = function_to_call()
                print(tool_call_id)

                messages.append({
                    "role": "assistant",
                    "name": function_name,
                    "content": function_response,
                    "tool_call_id": tool_call_id,
                })

                result = excute_model(messages=messages)
    print(type(result.choices[0].message.content))
    return result.choices[0].message.content
