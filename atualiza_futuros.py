import sys, os, time, datetime

sys.path.append(os.getcwd())

from uteis.util import Util
from uteis.googleSheets import GoogleSheets
from corretoras.ftx import FtxClient

config = Util.obterCredenciais()
corretora_obj = FtxClient(config["FTX"]["Authentication"],config["FTX"]["Secret"])
append_historico = True

while True:

    retorno_account = corretora_obj.get_account_info()

    lista_posicao = []
    pnl_total = 0
    for posicao in retorno_account['positions']:
        lista_posicao.append([posicao['future'],posicao['size'],posicao['side'],posicao['realizedPnl']])
        pnl_total += float(posicao['realizedPnl'])

    lista_margem = [[Util.excel_date(datetime.datetime.now())],[retorno_account['collateral']],[retorno_account['freeCollateral']],[retorno_account['totalAccountValue']],[retorno_account['totalPositionSize']]]
    
    GoogleSheets().atualiza_margem(lista_posicao,lista_margem)
    
    if append_historico:
        lista_append=[[Util.excel_date(datetime.datetime.now()),retorno_account['collateral'],retorno_account['freeCollateral'],retorno_account['totalAccountValue'],retorno_account['totalPositionSize'],pnl_total]]
        GoogleSheets().append_futuros(lista_append)
        append_historico = False

    time.sleep(60)

   




