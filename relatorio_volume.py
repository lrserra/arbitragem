import sys,os,datetime
from uteis.google import Google
from uteis.requests import Requests
from uteis.settings import Settings
root_path = os.getcwd()
sys.path.append(root_path)

from construtores.corretora import Corretora

google_client = Google()
planilha = Settings().retorna_campo_de_json('rasp','sheet_name')
    
volume_diario = []
trades_diario = []
endpoint = 'https://brasilbitcoin.com.br/api/dailySummary' #BTC/13/1/2022
corretora_br = Corretora('BrasilBitcoin')
corretora_bin = Corretora('Binance')

# The size of each step in days
day_delta = datetime.timedelta(days=1)

current_date = datetime.date(2022,3,1) 
end_date = datetime.date(2022,4,12)#----->nao esquece de mudar aqui mané!!

#header da planilha
moedas_arbitraveis = [moeda for moeda in corretora_br.moedas_negociaveis if moeda in corretora_bin.moedas_negociaveis]

google_client.escrever(planilha,'volume',['data']+sorted(moedas_arbitraveis))
google_client.escrever(planilha,'trades',['data']+sorted(moedas_arbitraveis))

while end_date >= current_date:

    for moeda in sorted(moedas_arbitraveis):
        try:
            response_json = Requests.envia_get_com_retry('{}/{}/{}/{}/{}'.format(endpoint,moeda.upper(),current_date.day,current_date.month,current_date.year),30,5).json()
            volume_diario.append(response_json['volume_fiat'])
            trades_diario.append(response_json['trades'])
        except:
            volume_diario.append(0)
            trades_diario.append(0)

    google_client.escrever(planilha,'volume',[current_date.strftime("%m/%d/%Y")]+volume_diario)
    google_client.escrever(planilha,'trades',[current_date.strftime("%m/%d/%Y")]+trades_diario)
    volume_diario=[]
    trades_diario=[]
    current_date = current_date + datetime.timedelta(days=1)
    