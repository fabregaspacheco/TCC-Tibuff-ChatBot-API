import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date
from uuid import uuid4 as GenerateID
from utils.errors import sheets as SheetsError


class Sheets:
    def __init__(self):
        self.scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                      "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
            "src/config/creds.sheets.json", self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open("Tibuff - Sistema")

    def findPromocao(self, search: str = ""):
        sheet = self.sheet.get_worksheet(0)
        extractorInformations = sheet.get_all_records(
            numericise_ignore=['all'])
        listProducts = []
        customMessage = '''Veja o(s) produto(s):'''

        if search:
            for extractorInformation in extractorInformations:
                expression_0 = search.lower(
                ) in extractorInformation["NOME DO PRODUTO"].lower()
                expression_1 = search.lower(
                ) in extractorInformation["DESCRIÇÃO"].lower()
                expression_2 = search.lower(
                ) in extractorInformation["MODELO"].lower()

                if expression_0 or expression_1 or expression_2:
                    listProducts.append(extractorInformation)
        else:
            listProducts = extractorInformations

        for key, itemProduct in enumerate(listProducts):
            produto = itemProduct["NOME DO PRODUTO"]
            preco = itemProduct["PREÇO"]
            descricao = itemProduct["DESCRIÇÃO"]
            modelo = itemProduct["MODELO"]
            promocao_ate = itemProduct["EM PROMOÇÃO ATÉ"]
            key = key + 1
            customMessage += f"\n{key}-  O produto cujo nome é {produto} do modelo {modelo}, está em oferta com o preço de {preco} e vai durar até {promocao_ate}:\nveja a descrição:\n{descricao}"

        if not listProducts:
            return SheetsError.not_found_promocao

        return customMessage

    def newSuporte(self, nome: str, celular: str, problema: str):
        sheet = self.sheet.get_worksheet(1)
        sheet.insert_rows([[str(GenerateID().hex), nome, celular, problema, "Não resolvido", str(
            date.today())]], row=2, value_input_option='USER_ENTERED')
        return "Sua mensagem foi enviada para o nosso suporte e já entraremos em contato!"

    def newFornecedor(self, nome: str, celular: str, info: str):
        sheet = self.sheet.get_worksheet(5)
        sheet.insert_rows([[str(GenerateID().hex), nome, celular, info, "Não resolvido", str(
            date.today())]], row=2, value_input_option='USER_ENTERED')
        return "Sua proposta foi enviada para o nosso time e já entraremos em contato!"

    def newParceria(self, nome: str, celular: str, info: str):
        sheet = self.sheet.get_worksheet(4)
        sheet.insert_rows([[str(GenerateID().hex), nome, celular, info, "Não resolvido", str(
            date.today())]], row=2, value_input_option='USER_ENTERED')
        return "Sua proposta foi enviada para o nosso time e já entraremos em contato!"

    def servicoStatus(self, ordem: str):
        sheet = self.sheet.get_worksheet(2)
        value = sheet.findall(ordem)

        if not value:
            return "Ordem não encontrada"

        customMessage = "Serviço status \n"

        if type(value) == list:
            for item in value:
                rowValues = sheet.row_values(item.row)

                match rowValues[5]:
                    case "CONCLUIDO":
                        customMessage += f"O item {rowValues[1]}, está concluido e pronto para retirada. \n"
                    case "EM PROCESSO":
                        customMessage += f"O item {rowValues[1]}, está em processo. \n"
                    case "INICIANDO":
                        customMessage += f"O item {rowValues[1]}, ainda não iniciou o seu processo. \n"

                if rowValues[4] != "":
                    customMessage += f"Extra: {rowValues[4]} \n"

            return customMessage

        rowValues = sheet.row_values(value.row)
        match rowValues[5]:
            case "CONCLUIDO":
                customMessage += f"O item {rowValues[1]}, está concluido e pronto para retirada. \n"
            case "EM PROCESSO":
                customMessage += f"O item {rowValues[1]}, está em processo. \n"
            case "INICIANDO":
                customMessage += f"O item {rowValues[1]}, ainda não iniciou o seu processo. \n"

        if rowValues[4] != "":
            customMessage += f"Extra: {rowValues[4]} \n"

        return customMessage

    def checkTelegram(self, id: str):
        sheet = self.sheet.get_worksheet(3)
        value = sheet.find(id)
        if not value:
            return self.newTelegram(id)

        if sheet.row_values(value.row)[1] == "TRUE":
            return "User actived"

        return "User desatived"

    def newTelegram(self, id: str):
        sheet = self.sheet.get_worksheet(3)
        value = sheet.find(id)
        if value:
            return "User already actived"

        today = str(date.today())
        sheet.insert_rows([[id, False, today, today]], row=2,
                          value_input_option='USER_ENTERED')

        return "User desatived"

    def onTelegram(self, id: str):
        sheet = self.sheet.get_worksheet(3)
        value = sheet.find(id)

        if not value:
            return "User not found"

        if sheet.row_values(value.row)[1] == "TRUE":
            return "User actived"

        row = value.row
        today = str(date.today())

        sheet.update_cell(row, 2, True)
        sheet.update_cell(row, 3, today)
        return "User actived"

    def offTelegram(self, id: str):
        sheet = self.sheet.get_worksheet(3)
        value = sheet.find(id)

        if not value:
            return "User not found"

        if sheet.row_values(value.row)[1] == "FALSE":
            return "User not actived"

        row = value.row
        today = str(date.today())

        sheet.update_cell(row, 2, False)
        sheet.update_cell(row, 3, today)

        return "User desatived"
