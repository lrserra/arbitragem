from datetime import datetime
import os, sys, time
import urllib.request

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

def get_ip():
    try:
        my_ip = urllib.request.urlopen('https://api.ipify.org/').read().decode('utf8')
    except:
        my_ip = ''
    return my_ip

settings_client = Settings()
google_client = Google()
instance = settings_client.retorna_campo_de_json('rasp','instance')
planilha = settings_client.retorna_campo_de_json('rasp','sheet_name')
my_ip_list = settings_client.retorna_campo_de_json_como_lista('rasp','ip_list')

Logger.cria_arquivo_log('WatchDog')
Logger.loga_info('iniciando script watchdog...')

while True:

    try:    
        my_external_ip = get_ip()
        if my_external_ip in my_ip_list:
            update_range =[[get_now_time(),
                            get_update_time('Arbitragem.log'),
                            get_update_time('Leilao.log'),
                            get_temperature()]]

            google_client.update(planilha,'settings','monitor{}'.format(instance),update_range)
            Logger.loga_info('updated!')
            time.sleep(180)
        else:
            Logger.loga_warning('my ip {} not in my ip list {}'.format(my_external_ip,my_ip_list))
    except Exception as err:
        Logger.loga_erro('main','watchdog',err)
        time.sleep(60)
 