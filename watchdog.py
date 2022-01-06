from datetime import datetime
import os, sys, time

root_path = os.getcwd()
sys.path.append(root_path)

from datetime import datetime
from uteis.converters import Converters
from uteis.google import Google
from uteis.settings import Settings

settings_client = Settings()
google_client = Google()
instance = settings_client.retorna_campo_de_json('rasp','instance')
planilha = settings_client.retorna_campo_de_json('rasp','sheet_name')

while True:

    agora = Converters.datetime_para_excel_date(datetime.now())
    google_client.update(planilha,'Painel','D'+str(7+int(instance)),agora)
    time.sleep(120)
