# Responsavel por gerar o texto da response
def generateTextResponse(value: str):
    return {"text": {"text": [value]}}


# Funcao que reporta o valor de response esperado no dialogFlow webhook
def UseSend(response: list | str, lastMessage: bool = True):
    response_send = []

    # Aqui estamos validando o tipo da response, para assim adicionar varias mensagens caso preciso
    match type(response).__name__:
        case "str":
            # Caso string adicionamos na resposta :D
            response_send.append(generateTextResponse(
                response))
        case "list":
            # Utilizando o metodo for in para interar sobre o array e assim extrair as mensagens
            for part in response:
                response_send.append(generateTextResponse(
                    part))
        case _:
            # Caso tenha um erro no formato, geramos uma mensagem para avisar o usuario
            response_send.append(generateTextResponse(
                "Houve algum erro no momento de gerar a resposta..."))

    # Caso seja uma last mensage informamos aqui
    if lastMessage:
        response_send.append(generateTextResponse(
            "Atendimento finalizado, caso queria recomeçar digite 'oi'"))

    return {"fulfillmentMessages": response_send}
