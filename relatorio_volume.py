import sys,os,datetime,json
from uteis.google import Google
from uteis.requests import Requests
from uteis.settings import Settings
root_path = os.getcwd()
sys.path.append(root_path)

from construtores.corretora import Corretora
from uteis.converters import Converters

google_client = Google()
planilha = Settings().retorna_campo_de_json('rasp','sheet_name')
    
volume_diario = []
endpoint = 'https://brasilbitcoin.com.br/api/dailySummary' #BTC/13/1/2022
corretora_br = Corretora('BrasilBitcoin')

# The size of each step in days
day_delta = datetime.timedelta(days=1)

current_date = datetime.date(2022,1,3)
end_date = datetime.date(2022,1,12)

google_client.escrever(planilha,'volume',['data']+sorted(corretora_br.moedas_negociaveis))

while end_date.day > current_date.day:

    for moeda in sorted(corretora_br.moedas_negociaveis):
        try:
            response_json = Requests.envia_get_com_retry('{}/{}/{}/{}/{}'.format(endpoint,moeda.upper(),current_date.day,current_date.month,current_date.year),30,5).json()
            volume_diario.append(response_json['volume_fiat'])
        except:
            volume_diario.append(0)

    google_client.escrever(planilha,'volume',[current_date.strftime("%m/%d/%Y")]+volume_diario)
    volume_diario=[]
    current_date = current_date + datetime.timedelta(days=1)
    