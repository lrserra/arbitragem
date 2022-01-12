import sys,os, time
root_path = os.getcwd()
sys.path.append(root_path)

from uteis.settings import Settings
from uteis.google import Google
from uteis.logger import Logger

Logger.cria_arquivo_log('Configuracao')
Logger.loga_info('iniciando script de configuracao...')

settings_client = Settings()
google_client = Google()

planilha = settings_client.retorna_campo_de_json('rasp','sheet_name')

Logger.loga_warning('atualizando settings de estrategias')
google_client.atualiza_strategy_settings(planilha)

Logger.loga_warning('atualizando settings do app')
google_client.atualiza_app_settings(planilha)

Logger.loga_warning('atualizando settings de brokers')
google_client.atualiza_broker_settings(planilha)

instance = settings_client.retorna_campo_de_json('rasp','instance')
if 'bnb' in settings_client.retorna_campo_de_json_como_lista('app',str(instance),'white_list','#'):
    Logger.loga_warning('comprimindo tabela position')
    google_client.comprime_position(planilha)

    Logger.loga_warning('comprimindo tabela spot')
    google_client.comprime_spot(planilha)

i=1
freq = 5
while True:
    Logger.loga_warning('atualizando settings de estrategias recorrente a cada {} minutos, iteracao {}'.format(freq,i))
    google_client.atualiza_strategy_settings(planilha)
    i+=1
    time.sleep(freq*60)


