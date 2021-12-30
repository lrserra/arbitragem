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
instance = settings_client.retorna_campo_de_json('rasp','instance')

Logger.loga_info('atualizando settings de estrategias')
google_client.atualiza_strategy_settings(planilha,instance)

Logger.loga_info('atualizando settings do app')
google_client.atualiza_app_settings(planilha)

Logger.loga_info('atualizando settings de brokers')
google_client.atualiza_broker_settings(planilha)

Logger.loga_info('comprimindo tabela position')
google_client.comprime_position(planilha)

Logger.loga_info('comprimindo tabela spot')
google_client.comprime_spot(planilha)

i=1
freq = 5
while True:
    Logger.loga_info('atualizando settings de estrategias recorrente a cada {} minutos, iteracao {}'.format(freq,i))
    google_client.atualiza_strategy_settings(planilha,instance)
    i+=1
    time.sleep(freq*60)


