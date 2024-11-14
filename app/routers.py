import os
from fastapi import APIRouter, Request
from fastapi.responses import Response
from app.broker_twilio import send_simple_text, response
from app.gpt import make_response

webhook_router = APIRouter(prefix="/send")
helth_router = APIRouter()


@helth_router.get("/health", summary="Health", description="")
def health_check():
    """Validar a saúde do servidor"""
    return {"status": "OK"}


@webhook_router.post("/twilio")
async def receive_message(request: Request):
    """Recebe as mensagens do broker twilio"""

    form = await request.form()
    from_number = form.get("From")
    user = form.get("ProfileName")

    body = form.get("Body")

    print(f"Mensagem recebida de {from_number}: {body}")

    content_ai = make_response(
        question=f"{user}: {body}",
        from_number=from_number,
    )

    send_simple_text(
        from_=os.environ.get('BOT_NUMBER'),
        body=content_ai,
        to=from_number,
    )

    return Response(content=response(), media_type="application/xml")
