import os

from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")


def send_simple_text(from_: str, body: str, to: str):
    """Envia uma mensagem de texto simples usando Twilio.

    Args:
        from_ (str): Número de origem
        body (str): Conteúdo da mensagem
        to (str): Número de destino
    """
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    message = client.messages.create(from_=from_, body=body, to=to)

    print(message)


def response():
    """Cria e retorna uma resposta de mensagem Twilio vazia.

    Returns:
        str: Resposta de mensagem Twilio em formato string
    """
    response = MessagingResponse()
    response_message = str(response)

    return response_message
