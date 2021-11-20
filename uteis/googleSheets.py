import logging
import time
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

    def atualiza_margem(self, operacoes=[],margem=[]):
        try:
            google_config = Util.retorna_config_google_api()
            self.sobrescrever(google_config['sheet_name'], google_config['futuros'],'update_futuros', operacoes)
            self.sobrescrever(google_config['sheet_name'], google_config['futuros'],'margem', margem)
        except Exception as err:
            logging.error('GoogleSheets - escrever_margem: {}'.format(err))

    def limpa_saldo(self):
        try:
            google_config = Util.retorna_config_google_api()
            client = self.retorna_google_sheets_client()
            sheet = client.open(google_config['sheet_name']).worksheet(google_config['saldo'])
            data = sheet.col_values(27)
            linhas_a_deletar = []
            today_date = datetime.now()
            for row in data:
                current_index = data.index(row)
                if row.find('/')!=-1 and current_index<len(data)-1:
                    
                    current_date = datetime.strptime(row, '%m/%d/%Y %H:%M:%S')
                    previous_date = datetime.strptime(data[current_index-1], '%m/%d/%Y %H:%M:%S') if data[current_index-1].find('/')!=-1 else 0
                    next_date = datetime.strptime(data[current_index+1], '%m/%d/%Y %H:%M:%S') if data[current_index+1].find('/')!=-1 else 0
                    
                    if previous_date !=0 and next_date !=0:
                        if current_date.day==today_date.day and current_date.month == today_date.month:
                            pass #hj nao apaga
                        if current_date.day!=today_date.day and current_date.month == today_date.month:
                            #desse mes mas nao é hoje
                            if previous_date.day == current_date.day and next_date.day == current_date.day:
                                linhas_a_deletar.append([current_index+1,current_date]) #vamos deixar só primeiro e ultimo de cada dia
                        if current_date.day!=today_date.day and current_date.month != today_date.month:
                            #meses diferentes
                            if previous_date.month == current_date.month and next_date.month == current_date.month:
                                linhas_a_deletar.append([current_index+1,current_date]) #vamos deixar só primeiro e ultimo de cada mes

            for linha_a_deletar in reversed(linhas_a_deletar):
                print('deletando a linha {}'.format(linha_a_deletar[1]))
                time.sleep(1)
                sheet.delete_row(linha_a_deletar[0])
       
        except Exception as err:
            logging.error('GoogleSheets - limpa_saldo: {}'.format(err))


    def append_futuros(self, linha=[[]]):
        try:
            google_config = Util.retorna_config_google_api()
            client = self.retorna_google_sheets_client()
            sheet = client.open(google_config['sheet_name']).worksheet(google_config['futuros'])
            data = sheet.col_values(2)
            row_count = 1
            today_date = datetime.now()
            for row in data:
                if row.find('/')!=-1:
                    data_format = datetime.strptime(row, '%m/%d/%Y %H:%M:%S')
                    if not(data_format.day == today_date.day and data_format.month == today_date.month and data_format.year == today_date.year):
                        row_count +=1 
                else:
                    row_count +=1
            sheet.update('B{}:G{}'.format(row_count,row_count),linha)
            
        except Exception as err:
            logging.error('GoogleSheets - append_futuros: {}'.format(err))

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
    
    def sobrescrever(self, planilha, aba,range, linhas=[]):
        client = self.retorna_google_sheets_client()
        sheet = client.open(planilha).worksheet(aba)
        sheet.update(range, linhas)
        
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

    def ler_status_leilao(self):
        leilao_ligado = {}
        google_config = Util.retorna_config_google_api()
        
        # Obtem nossa tabela de configs
        tabela = self.ler(google_config['sheet_name'], google_config['auxiliar'], 'tabela_config')
        
        leilao_ligado_index = tabela[0].index('LEILAO')
        for entrada in tabela[1:]:
            leilao_ligado[entrada[0].lower()]=entrada[leilao_ligado_index]

        return leilao_ligado

    def ler_status_arbitragem(self):
        arbitragem_ligado = {}
        google_config = Util.retorna_config_google_api()
        
        # Obtem nossa tabela de configs
        tabela = self.ler(google_config['sheet_name'], google_config['auxiliar'], 'tabela_config')
        
        arbitragem_ligado_index = tabela[0].index('ARBITRAGEM')
        for entrada in tabela[1:]:
            arbitragem_ligado[entrada[0].lower()]=entrada[arbitragem_ligado_index]

        return arbitragem_ligado

    def ler_status_zeragem(self):
        zeragem_ligado = {}
        google_config = Util.retorna_config_google_api()
        
        # Obtem nossa tabela de configs
        tabela = self.ler(google_config['sheet_name'], google_config['auxiliar'], 'tabela_config')
        
        zeragem_ligado_index = tabela[0].index('ZERAGEM')
        for entrada in tabela[1:]:
            zeragem_ligado[entrada[0].lower()]=entrada[zeragem_ligado_index]

        return zeragem_ligado

    def ler(self, planilha, aba, descricao_range):
        client = self.retorna_google_sheets_client()
        sheet = client.open(planilha).worksheet(aba)
        data = sheet.get(descricao_range)
        return data




