# DersonBot

## 📱 Sobre o Projeto
DersonBot é um assistente virtual automatizado para WhatsApp, desenvolvido especialmente para automatizar o agendamento de serviços. Utilizando a API do WhatsApp, o bot facilita o processo de marcação de horários, gerenciamento de clientes e organização da agenda de profissionais.

## 🎯 Principais Funcionalidades
- Agendamento automático de serviços
- Confirmação de horários
- Consulta de horários disponíveis
- Histórico de atendimentos

## 🛠️ Tecnologias Utilizadas
- Python
- OpenAI (API)
- Twilio (API WhatsApp)
- FastAPI (API)
- TinyDB (Banco de dados)
- Avec (API)

## 💡 Como Funciona
1. **Primeiro Contato**: O cliente envia uma mensagem para o número do WhatsApp
2. **Menu Interativo**: O bot apresenta as opções disponíveis
3. **Agendamento**: O cliente seleciona o serviço e visualiza horários disponíveis
4. **Confirmação**: Após escolher, recebe confirmação e lembretes automáticos

## 📝 Configuração
1. Instale as dependências
```bash
pip install -r requirements.txt
```
2. Variáveis de ambiente
```bash
cp .env.example .env
```
3. Execute o comando `make run` para iniciar o bot
