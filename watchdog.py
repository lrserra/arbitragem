from datetime import datetime
import os, sys, time

from uteis.logger import Logger

root_path = os.getcwd()
sys.path.append(root_path)

from datetime import datetime
from uteis.converters import Converters
from uteis.google import Google
from uteis.settings import Settings

def get_now_time():
    return Converters.datetime_para_excel_date(datetime.now())

def get_update_time(filename):
    try:
        mtime = os.path.getmtime(filename)
        modified_date =Converters.datetime_para_excel_date(datetime.fromtimestamp(mtime)) 
    except OSError:
        modified_date = 0
    return modified_date

def get_temperature():
    try:
        cpu_temp = float(os.popen("vcgencmd measure_temp").readline().replace("temp=", "").replace("'C",""))
    except:
        cpu_temp = 0
    return cpu_temp

settings_client = Settings()
google_client = Google()
instance = settings_client.retorna_campo_de_json('rasp','instance')
planilha = settings_client.retorna_campo_de_json('rasp','sheet_name')

Logger.cria_arquivo_log('WatchDog')
Logger.loga_info('iniciando script watchdog...')

while True:

    try:    
        update_range =[[get_now_time(),
                        get_update_time('Arbitragem.log'),
                        get_update_time('Leilao.log'),
                        get_temperature()]]

        google_client.update(planilha,'settings','monitor{}'.format(instance),update_range)
        Logger.loga_info('updated!')
        time.sleep(180)
    except Exception as err:
        Logger.loga_erro('main','watchdog',err)
        time.sleep(60)
 
