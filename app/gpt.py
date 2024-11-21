import time

from datetime import datetime
from app.db import MessageDatabase
from app.assistant_ai import AssistantAI


def make_response(question: str, from_number: str) -> str:
    """Função que responde o cliente dados sua pergunta"""

    db_message = MessageDatabase(table="messages")
    resuts_db = db_message.search_messages(user_id=from_number)

    previus_messages = None
    # Obter a data atual
    current_date = datetime.now().strftime("%d de %B de %Y")

    if len(resuts_db) > 0:
        conversations = resuts_db[0]["messages"][-10:]

        previus_messages = "\n".join(
            [
                f"User: {msgs['user']} \n Assistant: {msgs['bot']}"
                for msgs in conversations
            ]
        )

        firt_instructions = (
            f""""
            - O Cliente já falou conosco segue as ultimas conversas: [{previus_messages}].
            Você deve usar este historico para melhorar a conversa com o cliente e caso o mesmo peguntar coisas que já foi falado,
            você deve responder com base no historico.
            - Hoje é {current_date} Você deve conhecer as futuras datas dado a data de hoje
            """
            if previus_messages
            else f"Hoje é {current_date} Você deve conhecer as futuras datas dado a data de hoje"
        )
    else:
        firt_instructions = f"""
        - Este é um cliente novo, trate ele muito bem para cativa-lo.
        - Hoje é {current_date} Você deve conhecer as futuras datas dado a data de hoje
        """

    assistant_id = "asst_PhStNrXzL4eOngFNXLmH91vI"

    db_threads = MessageDatabase(table="threads")
    return_db = db_threads.search_thread(user_id=from_number)

    thread_id = None
    if len(return_db) > 0:
        thread_id = return_db[0].get("thread_id")

    client = AssistantAI(assistant=assistant_id, thread_id=thread_id)
    instructions = (
        f"Hoje é {current_date} Você deve conhecer as futuras datas dado a data de hoje"
    )

    if not client.thread_id:
        client.create_thread()
        db_threads.insert(
            value={
                "user_id": from_number,
                "thread_id": client.thread_id,
                "expiron_time": time.time() + 3 * 60 * 60,
            }
        )
        instructions = firt_instructions

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
