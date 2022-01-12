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

    try:
        mtime = os.path.getmtime('Arbitragem.log')
        arb_modified_date =Converters.datetime_para_excel_date(datetime.fromtimestamp(mtime)) 
    except OSError:
        mtime = 0
        arb_modified_date = 0

    try:
        mtime = os.path.getmtime('Leilao.log')
        leilao_modified_date = Converters.datetime_para_excel_date(datetime.fromtimestamp(mtime))
    except OSError:
        mtime = 0
        leilao_modified_date = 0
    
    agora = Converters.datetime_para_excel_date(datetime.now())

    google_client.update(planilha,'Painel','D'+str(7+int(instance)),agora)
    google_client.update(planilha,'Painel','E'+str(7+int(instance)),arb_modified_date)
    google_client.update(planilha,'Painel','F'+str(7+int(instance)),leilao_modified_date)
    
    time.sleep(180)
