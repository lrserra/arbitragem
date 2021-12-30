import json
import logging
import sys,os
root_path = os.getcwd()
sys.path.append(root_path)
from uteis.util import Util

class Settings:
    def atualiza_app_settings(google_client,planilha,current_path):
        '''
        atualiza o json app
        '''
        try:
            app_json = {}
            app_settings = google_client.ler(planilha,'settings','settings_app')
            header = app_settings[0]
            for campo in header[1:]
                instance = campo[0]
                app_json[instance][header.]
                



    def atualiza_broker_settings(google_client,planilha,current_path):
        '''
        atualiza o json de brokers
        '''
        try:
            broker_json = {}
            broker_settings = google_client.ler(planilha,'settings','settings_broker')
            header = broker_settings[0]
            for corretora in header[1:]:
                broker_json[corretora]={}
                for linha in broker_settings[1:]:
                    campo = linha[0]
                    broker_json[corretora][campo] = linha[header.index(corretora)]

            arquivo = open(current_path+"/broker.json", "w") # Sobrescreve o arquivo
            json.dump(broker_json, arquivo) # Salva o Json no arquivo
            arquivo.close()

        except Exception as erro:
            logging.error(Util.descricao_erro_padrao().format('atualiza_broker_settings', 'N/A', erro))











