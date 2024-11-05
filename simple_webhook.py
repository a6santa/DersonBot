from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

app = FastAPI()

@app.get("/helth")
async def helth():
    return {"status": "OK"}

@app.post("/webhook")
async def receive_message(request: Request):
    form = await request.form()
    print(form)
    from_number = form.get('From')
    user = form.get('ProfileName')
    body = form.get('Body')

    print(f"Mensagem recebida de {from_number}: {body}")

    
    
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_=f'whatsapp:+14155238886',
        body=f'olá {user}!! Seja bem vindo ao Barber Derson, vamos fazer seu Agendamento?',
        to=from_number
    )

    response = MessagingResponse()
    response_message = str(response)

    return Response(content=response_message, media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)