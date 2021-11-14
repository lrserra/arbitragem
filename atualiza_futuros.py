import sys, os, time, datetime

sys.path.append(os.getcwd())

from uteis.util import Util
from uteis.googleSheets import GoogleSheets
from corretoras.ftx import FtxClient

config = Util.obterCredenciais()
corretora_obj = FtxClient(config["FTX"]["Authentication"],config["FTX"]["Secret"])

while True:

    retorno_account = corretora_obj.get_account_info()

    lista_posicao = []
    for posicao in retorno_account['positions']:
        lista_posicao.append([posicao['future'],posicao['size'],posicao['side'],posicao['realizedPnl']])

    lista_margem = [[Util.excel_date(datetime.datetime.now())],[retorno_account['collateral']],[retorno_account['freeCollateral']],[retorno_account['totalAccountValue']],[retorno_account['totalPositionSize']]]

    GoogleSheets().escrever_futuros(lista_posicao)
    GoogleSheets().escrever_margem(lista_margem)
    time.sleep(30)

   




