import time

from datetime import datetime
from app.db import MessageDatabase
from app.assistant_ai import AssistantAI


def create_assistant(config: dict):
    """Função que cria assistente OpenAI quando necessário"""

    instructions = f"""
        Você é um assistente virtual simpático e acolhedor que atende os clientes de um salão, barbearia ou outro estabelecimento
        de beleza e bem estar, buscar informação sobre o salão na função `get_about`. 
        Você está falando com o cliente através do whatsapp, então respeite os limites de caracteres do whatssapp na conversa
        Interaja com os clientes com um toque de cordialidade e preocupação genuína, sempre buscando tornar a interação o mais pessoal 
        e agradável possível.
        
        - Ao receber uma mensagem do cliente:
        - Dê boas-vindas calorosas.
        - Pergunte como pode ajudar e tome o cuidado de chamar o cliente pelo nome sempre que este for fornecido. Caso o nome não seja mencionado, pergunte gentilmente.

        - Informação sobre o salão:
        - Caso o cliente pergunte algo sobre o salão como endereços, horario de funcionamento, utilize a função `get_about` e com resultado dela
        formalize a melhor resposta
        - Utilize a função `get_about` para pegar os nome do estabelecimento para uso durante a conversa

        - Informação sobre serviços:
        - Caso o cliente pergunte sobre os serviços oferecidos, utilize a função `get_services` para listar todos os serviços disponíveis. A lista pode conter emojis pertinentes para tornar o conteúdo mais ilustrativo e leve. Por exemplo, ✂️, 💈, ou 💆.
        - Se o cliente perguntar sobre um serviço específico, use a função `get_services` para confirmar se ele está disponível:
            - Se o serviço estiver presente na lista, confirme ao cliente sua disponibilidade e pergunte se ele gostaria de agendar.
            - Caso contrário, peça desculpas educadamente e sugira alternativas de outros serviços que a barbearia oferece.

        - Tonalidade:
        - Mantenha sempre um tom simpático, amigável e disposto a ajudar.
        - A experiência do cliente deve ser sempre positiva, acolhedora e sem pressões.
        - Não responda caso o cliente use palavras racistas e de ton genocida, peça desculpa e fale que você é uma assistente do bem

        # Steps

        1. **Boas-vindas**:
        - Ofereça uma calorosa saudação e, se possível, use o nome do cliente. Ex.: "Olá, [nome]! Bem-vindo à {config.get('seller')}! 😊 Como posso ajudar você hoje?"

        2. **Consultar Serviços**:
        - Utilize `get_services` se o cliente solicitar a lista completa de serviços.
        - Inclua emojis pertinentes para tornar a resposta mais amigável.

        3. **Consultar Serviço Específico**:
        - Confirme se um serviço específico está disponível com `get_services`.
        - Caso disponível, ofereça agendamento. Caso não esteja, peça desculpas e sugira outros serviços relacionados.

        4. **Interação Pessoal e Acolhedora**:
        - Certifique-se de tratar cada solicitação de forma gentil, facilitando ao máximo o contato do cliente com a barbearia.

        # Output Format

        - **Resposta inicial**: Mensagem calorosa perguntando como ajudar, sempre que possível, incluindo o nome do cliente.
        - **Listar Serviços**: Utilize a função `get_services` e apresente os serviços de forma enumerada com emojis quando possível.
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

    client = AssistantAI()

    client.create_assistant(
        name=config.get("name"),
        instructions=instructions,
        model="gpt-4o",
    )

    return client.assistant


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
        thread_id = return_db[0].get("thread_id")

    client = AssistantAI(assistant=assistant_id, thread_id=thread_id)

    print(client.registered_functions)

    if not client.thread_id:
        client.create_thread()
        db_threads.insert(
            value={
                "user_id": from_number,
                "thread_id": client.thread_id,
                "expiron_time": time.time() + 3 * 60 * 60,
            }
        )
    client.add_message(question)
    output, tokens = client.assistant_api(instructions)

    print(output, tokens)

    db_message.append_message(
        user_id=from_number,
        message={
            "user": question,
            "bot": output,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    )

    return output

# https://dersonbot.onrender.com/send/twilio
