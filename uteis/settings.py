
import os, json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class Settings:
    def __init__(self):
        self.current_path = os.getcwd()

    def salva_json(self,dicionario,nome):
        '''
        salva dicionario no formato json na pasta settings
        '''
        arquivo = open(self.current_path+"/settings/"+nome+".json", "w") # Sobrescreve o arquivo
        json.dump(dicionario, arquivo) # Salva o Json no arquivo
        arquivo.close()

    def retorna_campo_de_json(self,nome, campo, campo2=''):
        '''
        retorna qualquer campo de um json da pasta settings
        '''
        with open(self.current_path+"/settings/"+nome+".json") as f:
            if campo2 == '':
                return json.load(f)[campo]
            else:
                return json.load(f)[campo][campo2]

    def retorna_google_client(self):
        scope = ["https://spreadsheets.google.com/feeds", 
                "https://www.googleapis.com/auth/spreadsheets", 
                "https://www.googleapis.com/auth/drive.file", 
                "https://www.googleapis.com/auth/drive"]

        creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
        client = gspread.authorize(creds)

        return client