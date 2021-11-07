from flask import Flask, request as Request, jsonify as Jsonify, Response
from flask_cors import CORS
from twilio.twiml.messaging_response import MessagingResponse
from modules.sheets import Sheets
from modules.dialogflow import DialogFlow
from modules.utils import UseSend

# Instanciando a class Flask responsavel por comecar a api
APP_WEBHOOK = Flask("API-Tibuff")
CORS(APP_WEBHOOK)


@APP_WEBHOOK.route('/webhook', methods=['GET', 'POST'])
def webhook():
    req = Request.get_json(silent=True, force=True)
    response = ""
    # Invocando a class Sheets que e responsavel pelos metodos de contato com as planilhas
    sheet = Sheets()

    # caso nao tenha um body request, respondera um erro
    if not req:
        return Jsonify(UseSend("Faltando Argumentos")), 400

    # Match ou Switch e um metodo que esta com a responsabilidade de localizar e extrair os valores de cada webwook pre determinado aqui.
    match req["queryResult"]["intent"]["displayName"]:
        case "Servicos - Acompanhar":
            params = req["queryResult"]["parameters"]
            response = sheet.servicoStatus(ordem=params["ordem"])
        case "Suporte":
            params = req["queryResult"]["parameters"]
            response = sheet.newSuporte(
                nome=params["nome"], celular=params["telefone"], problema=params["duvida"])
        case "Parceria":
            params = req["queryResult"]["parameters"]
            response = sheet.newParceria(
                nome=params["nome"], celular=params["telefone"], info=params["motivo"])
        case "Fornecedor":
            params = req["queryResult"]["parameters"]
            response = sheet.newFornecedor(
                nome=params["nome"], celular=params["telefone"], info=params["proposta"])
        case _:
            # Nao foi localizado o nome da intent webhook, informara um erro 404, not found, mais uma mensagem
            return Jsonify(UseSend("Houve algum erro e não foram localizadas as mensagens")), 404

    # Retornando aqui a mensagem para o dialogflow service
    return Jsonify(UseSend(response)), 200


# Rota especifica para receber valores da twilio service
@APP_WEBHOOK.route('/twilio', methods=['POST'])
def twilio():
    # Extraindo mensagem de texto do whatsApp
    message = Request.form.get('Body')
    # Extraindo numero da mensagem
    phone_number = Request.form.get('From')
    # instanciando a class dialogFlow para gerar as configuracoes necessarias
    dialog = DialogFlow()
    # Buscando a resposta da mensagem com a class dialogFlow
    response = dialog.FetchReply(message, phone_number)
    # instanciando a class MessagingResponse da twilio lib responsavel por responder :D
    _response = MessagingResponse()

    for fragment in response:
        _response.message(str(fragment))

    return Response(str(_response), status=200)


@APP_WEBHOOK.route('/telegram/check/<id>', methods=['POST'])
def telegramCheck(id):

    if not id:
        return Jsonify({"message": "Missing arguments"}), 400

    response = Sheets().checkTelegram(id)

    return Jsonify({"message": response}), 200


@APP_WEBHOOK.route('/telegram/on/<id>', methods=['POST'])
def telegramNew(id):

    if not id:
        return Jsonify({"message": "Missing arguments"}), 400

    sheet = Sheets()
    response = sheet.onTelegram(id)
    if "not found" in response:
        return Jsonify({"message": response}), 404

    return Jsonify({"message": response}), 200


@APP_WEBHOOK.route('/telegram/off/<id>', methods=['POST'])
def telegramDelete(id):

    if not id:
        return Jsonify({"message": "Missing arguments"}), 400

    sheet = Sheets()
    response = sheet.offTelegram(id)

    if "not found" in response:
        return Jsonify({"message": response}), 404
    elif "actived" in response:
        return Jsonify({"message": response}), 400

    return Jsonify({"message": response}), 200


@APP_WEBHOOK.route('/telegram/promocao', methods=['POST'])
def telegramPromocao():
    sheet = Sheets()
    search = Request.args.get("search")

    if search:
        response = sheet.findPromocao(search)
        return Jsonify({"message": response}), 200

    response = sheet.findPromocao()
    return Jsonify({"message": response}), 200


if __name__ == "__main__":
    APP_WEBHOOK.run(port=8000, debug=True)
