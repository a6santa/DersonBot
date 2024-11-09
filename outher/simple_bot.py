def get_services(service=None):
    ## transformar isso em consultado no banco de dados ou API SV depois
    services = [
        {"id": 1, "name": "Corte de Cabelo", "desc": "Cortes tradicionais e modernos com finalizações personalizadas.", "professional": [1,2]},
        {"id": 2, "name": "Aparação e Modelagem de Barba", "desc": "Aparar e modelar a barba com técnicas de navalha e finalização com produtos específicos.", "professional": [1]},
        {"id": 3, "name": "Raspar a Barba (Barba Completa)", "desc": "Processo de barbear com lâmina para um acabamento suave, com aplicação de cremes e óleos para evitar irritações.", "professional": [1]},
        {"id": 4, "name": "Relaxamento Capilar", "desc": "Reduz o volume e ondulação dos fios, proporcionando um visual mais alinhado.", "professional": [1]},
        {"id": 5, "name": "Alisamento e Escova", "desc": "Serviço para deixar o cabelo mais liso e polido, com escova e produtos alisantes.", "professional": [1,2]},
        {"id": 6, "name": "Cortes Infantis", "desc": "Corte de cabelo para crianças, com uma abordagem que torna a experiência agradável.", "professional": [1,2]}
    ]
    if service:
        return next((s for s in services if s["id"] == service))
    else:
        return services

def get_professional(professional):
    ## transformar isso em consultado no banco de dados ou API SV depois
    professionals = [
        {"id": 1, "name": "Emanuel", "schedule": ["2024-11-05 10:00", "2024-11-05 15:00", "2024-11-06 11:00"]},
        {"id": 2, "name": "André", "schedule": ["2024-11-06 10:00", "2024-11-06 14:00", "2024-11-07 13:00"]}
    ]

    return next((p for p in professionals if p["id"] == professional))


def get_option_service(option):
    service = get_services(option)
    professionals = [get_professional(p) for p in service.get("professional")]
    if len(professionals) > 1:
        print("\nPara este serviço temos os seguintes Profissionais")
        results = "\n".join(f"{p['id']}. {p['name']}" for p in professionals)
        print(results)
        print(f"0. Sair")
    else:
        print(f"\nPara este serviço temos o seguinte Profissional {professionals[0].get("name")} deseja continuar ?")
        print(f"{professionals[0].get("id")}. Sim")
        print(f"0. Não")
    pass

def get_option_professional(option):
    professional = get_professional(option)
    print("\nQual Data e Hora você quer agendar")
    for i, sch in enumerate(professional.get("schedule"), start=1):
        print(f"{i}. {sch}")
    print(f"0. Sair")

    return professional.get("schedule")

def simple_bot():
    print("Bem-vindo Meu nome é DersonBot estou aqui para fazer seu agendamento!")
    nome_usuario = input("Qual é o seu nome? ")

    while True:
        print(f"\n{nome_usuario} Qual serviço você gostaria de agendar:")
        results = "\n".join(f"{s['id']}. {s['name']}" for s in get_services())
        print(results)
        print("0. Sair")

        option = int(input("Digite o número da opção desejada: "))

        if option != 0:
            get_option_service(option)
            option_prof = int(input("Digite o número da opção desejada: "))
            if option_prof != 0:
                schedules = get_option_professional(option_prof)
                option_schedule = int(input(f"Digite o número da opção desejada: "))
                if option_schedule != 0:
                    schedule = schedules[option_schedule-1]
                    option_final = int(input(f"\n{nome_usuario} você confirma seu agendamento nesta data {schedule} \n1. Sim \n2. Não?"))
                    if option_final == 1:
                        print("Obrigado pelo agendamento!!!")
                        break
                    elif option_final == 2:
                        print("Que pena que não conseguimos te atender, iremos entrar em contato")
                        break
                else:
                    print("Obrigado por utilizar o Bot de Agendamento. Até mais!")
                    break    
            else:
                print("Obrigado por utilizar o Bot de Agendamento. Até mais!")
                break
        else:
            print("Obrigado por utilizar o Bot de Agendamento. Até mais!")
            break

if __name__ == "__main__":
    simple_bot()
