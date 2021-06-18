import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
from uteis.util import Util
from datetime import datetime
from gspread_formatting import *

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
        try:
            google_config = Util.retorna_config_google_api()
            self.escrever(google_config['sheet_name'], google_config['operacoes'], operacao)
        except Exception as err:
            logging.error('GoogleSheets - escrever_operacao: {}'.format(err))

    def escrever_saldo(self, saldo):
        try:
            google_config = Util.retorna_config_google_api()
            self.escrever(google_config['sheet_name'], google_config['saldo'], saldo)
        except Exception as err:
            logging.error('GoogleSheets - escrever_saldo: {}'.format(err))

    def escrever(self, planilha, aba, linha):
        client = self.retorna_google_sheets_client()
        sheet = client.open(planilha).worksheet(aba)
        data = sheet.get_all_records()
        row_count = len(data)

        sheet.insert_row(linha, row_count + 2, value_input_option='USER_ENTERED')

    def ler_quantidade_moeda(self):
        google_config = Util.retorna_config_google_api()
        
        # Obtem o número de moedas parametrizadas
        contador_moeda = self.ler(google_config['sheet_name'], google_config['auxiliar'], 'contador_moeda')
        contador = int(contador_moeda[0][0]) + 2
        
        retorno = self.ler(google_config['sheet_name'], google_config['auxiliar'], 'I3:J{}'.format(str(contador)))
        return retorno

    def ler(self, planilha, aba, descricao_range):
        client = self.retorna_google_sheets_client()
        sheet = client.open(planilha).worksheet(aba)
        data = sheet.get(descricao_range)
        return data




