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
        saldo_inicial = {}
        google_config = Util.retorna_config_google_api()
        
        # Obtem nossa tabela de configs
        tabela = self.ler(google_config['sheet_name'], google_config['auxiliar'], 'tabela_config')
        
        saldo_index = tabela[0].index('Saldo Inicial')
        for entrada in tabela[1:]:
            saldo_inicial[entrada[0].lower()]=entrada[saldo_index]

        return saldo_inicial

    def ler_minimo_negociacao(self):
        minimo_compra = {}
        minimo_venda = {}
        google_config = Util.retorna_config_google_api()
        
        # Obtem nossa tabela de configs
        tabela = self.ler(google_config['sheet_name'], google_config['auxiliar'], 'tabela_config')
        
        minimo_compra_index = tabela[0].index('Minimo Compra')
        minimo_venda_index = tabela[0].index('Minimo Venda')

        for entrada in tabela[1:]:
            minimo_compra[entrada[0].lower()]=entrada[minimo_compra_index]
            minimo_venda[entrada[0].lower()]=entrada[minimo_venda_index]

        return minimo_compra, minimo_venda

    def ler(self, planilha, aba, descricao_range):
        client = self.retorna_google_sheets_client()
        sheet = client.open(planilha).worksheet(aba)
        data = sheet.get(descricao_range)
        return data




