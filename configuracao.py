
import sys,os, time
root_path = os.getcwd()
sys.path.append(root_path)

from settings.settings import Settings
from google.google import Google
from uteis.erros import Erros

Erros.cria_arquivo_log('Configuracao')
Erros.loga_info('iniciando script de configuracao...')

settings_client = Settings()
google_client = Google()

planilha = settings_client.retorna_campo_de_json('rasp','sheet_name')
instance = settings_client.retorna_campo_de_json('rasp','instance')

Erros.loga_info('atualizando settings de estrategias')
google_client.atualiza_strategy_settings(planilha,instance)

Erros.loga_info('atualizando settings do app')
google_client.atualiza_app_settings(planilha)

Erros.loga_info('atualizando settings de brokers')
google_client.atualiza_broker_settings(planilha)

Erros.loga_info('comprimindo tabela position')
google_client.comprime_position(planilha)

Erros.loga_info('comprimindo tabela spot')
google_client.comprime_spot(planilha)

i=1
freq = 5
while True:
    Erros.loga_info('atualizando settings de estrategias recorrente a cada {} minutos, iteracao {}'.format(freq,i))
    google_client.atualiza_strategy_settings(planilha,instance)
    i+=1
    time.sleep(freq*60)


