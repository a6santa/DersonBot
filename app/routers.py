from typing import List
from fastapi import APIRouter, Request
from fastapi.responses import Response
from app.broker_twilio import send_simple_text, response

webhook_router = APIRouter(prefix='/send')
helth_router = APIRouter()

@helth_router.get("/health", summary="Health", description="")
def health_check():
    return {"status": "OK"}

@webhook_router.post("/twilio")
async def receive_message(request: Request):
    form = await request.form()
    from_number = form.get('From')
    user = form.get('ProfileName')
    body = form.get('Body')

    print(f"Mensagem recebida de {from_number}: {body}")
    
    send_simple_text(
        from_=f'whatsapp:+14155238886',
        body=f'olá {user}!! Seja bem vindo ao Barber Derson, vamos fazer seu Agendamento?',
        to=from_number
    )

    return Response(content=response(), media_type="application/xml")