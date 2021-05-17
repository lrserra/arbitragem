import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
from uteis.util import Util

class GoogleSheets:

    def __init__(self):
        pass

    def retorna_google_sheets_client(self):
        scope = ["https://spreadsheets.google.com/feeds", 
                "https://www.googleapis.com/auth/spreadsheets", 
                "https://www.googleapis.com/auth/drive.file", 
                "https://www.googleapis.com/auth/drive"]

        creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
        client = gspread.authorize(creds)

        return client

    def escrever_operacao(self, operacao):
        google_config = Util.retorna_config_google_api()
        self.escrever(google_config['sheet_name'], google_config['operacoes'], operacao)

    def escrever_saldo(self, saldo):
        google_config = Util.retorna_config_google_api()
        self.escrever(google_config['sheet_name'], google_config['saldo'], saldo)

    def escrever(self, planilha, aba, linha):
        client = self.retorna_google_sheets_client()
        sheet = client.open(planilha).worksheet(aba)
        data = sheet.get_all_records()
        row_count = len(data)

        sheet.insert_row(linha, row_count + 2)






