import requests
import time
import logging

from datetime import datetime, timedelta
from corretora import Corretora
from util import Util
from caixa import Caixa
from arbitragem import Arbitragem
from leilao import Leilao

#from coreTelegram import Telegram

#inicializa arquivo de logs, no arquivo vai a porra toda, mas no console só os warning ou acima
logging.basicConfig(filename='main.log', level=logging.INFO,
                    format='[%(asctime)s][%(levelname)s][%(message)s]')
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
logging.getLogger().addHandler(console)

#essa parte executa apenas uma vez
lista_de_moedas = Util.obter_lista_de_moedas()
corretora_mais_liquida = Util.obter_corretora_de_maior_liquidez()
corretora_menos_liquida = Util.obter_corretora_de_menor_liquidez()

idOrdem = {}#inicializa o dic
for moeda in lista_de_moedas:
    idOrdem[moeda]={}
    idOrdem[moeda]['compra'] = 0
    idOrdem[moeda]['venda'] = 0

#atualiza saldo inicial nesse dicionario
saldo_inicial = Caixa.atualiza_saldo_inicial(lista_de_moedas,corretora_mais_liquida,corretora_menos_liquida)

hour = 1
while hour <= 720:
    #essa parte executa uma vez por hora
    agora = datetime.now() 
    proxima_hora = agora + timedelta(hours=1)
    logging.warning('proxima atualizacao: {}'.format(proxima_hora))
    
    while agora < proxima_hora:
        #essa parte executa diversas vezes

        for moeda in lista_de_moedas:
            try:
                # Instancia das corretoras por ativo
                CorretoraMaisLiquida = Corretora(corretora_mais_liquida, moeda)
                CorretoraMenosLiquida = Corretora(corretora_menos_liquida, moeda)

                CorretoraMaisLiquida.atualizarSaldo()
                CorretoraMenosLiquida.atualizarSaldo()

                retornoCompra = Arbitragem.run(CorretoraMaisLiquida, CorretoraMenosLiquida, moeda, True)
                retornoVenda = Arbitragem.run(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True)   

                if retornoCompra['sucesso']:
                    logging.warning('operou arb de {}! + {}brl de pnl'.format(moeda,round(retornoCompra['Pnl'],2)))
                    CorretoraMaisLiquida.atualizarSaldo()
                    CorretoraMenosLiquida.atualizarSaldo()
                elif retornoVenda['sucesso']:
                    logging.warning('operou arb de {}! + {}brl de pnl'.format(moeda,round(retornoVenda['Pnl'],2)))
                    CorretoraMaisLiquida.atualizarSaldo()
                    CorretoraMenosLiquida.atualizarSaldo()
                    
            except Exception as erro:
                logging.error('deu algum ruim na arb')
                logging.error(erro)

            try:
                me_executaram_na_compra = Leilao.cancela_ordens_e_compra_na_mercado(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True, idOrdem[moeda]['compra'])
                me_executaram_na_venda = Leilao.cancela_ordens_e_vende_na_mercado(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True, idOrdem[moeda]['venda'])

                if me_executaram_na_compra['sucesso']:
                    logging.warning('operou leilao de compra de {}! + {}brl de pnl'.format(moeda,round(me_executaram_na_compra['Pnl'],2)))
                    CorretoraMaisLiquida.atualizarSaldo()
                    CorretoraMenosLiquida.atualizarSaldo()

                if me_executaram_na_venda['sucesso']:  
                    logging.warning('operou leilao de venda de {}! + {}brl de pnl'.format(moeda,round(me_executaram_na_venda['Pnl'],2)))
                    CorretoraMaisLiquida.atualizarSaldo()
                    CorretoraMenosLiquida.atualizarSaldo()              

                if me_executaram_na_compra['idOrdem'] ==0:
                    
                    CorretoraMaisLiquida = Corretora(corretora_mais_liquida, moeda) #atualizar os books aqui pra mandar a proxima ordem pro leilao
                    CorretoraMenosLiquida = Corretora(corretora_menos_liquida, moeda) #atualizar os books aqui pra mandar a proxima ordem pro leilao

                    retorno_leilao_compra = Leilao.compra(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True)
                    idOrdem[moeda]['compra'] = retorno_leilao_compra['idOrdem'] #para cancelar depois
                else:
                    idOrdem[moeda]['compra'] = me_executaram_na_compra['idOrdem']
                
                if me_executaram_na_venda['idOrdem'] ==0:
                    
                    CorretoraMaisLiquida = Corretora(corretora_mais_liquida, moeda) #atualizar os books aqui pra mandar a proxima ordem pro leilao
                    CorretoraMenosLiquida = Corretora(corretora_menos_liquida, moeda) #atualizar os books aqui pra mandar a proxima ordem pro leilao

                    retorno_leilao_venda = Leilao.venda(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True)
                    idOrdem[moeda]['venda'] = retorno_leilao_venda['idOrdem'] #para cancelar depois
                else:
                    idOrdem[moeda]['venda'] = me_executaram_na_venda['idOrdem']

            except Exception as erro:
                logging.error('deu algum ruim no leilao')
                logging.error(erro) 

            
            
            time.sleep(Util.frequencia())

        agora = datetime.now() 
    
    #zerar o pnl e reiniciar a bagaça
    Caixa.zera_o_pnl_em_cripto(lista_de_moedas,saldo_inicial,corretora_mais_liquida,corretora_menos_liquida)
    for moeda in lista_de_moedas:
        idOrdem[moeda]={}
        idOrdem[moeda]['compra'] = 0
        idOrdem[moeda]['venda'] = 0

    hour = hour+1
    
    Caixa.atualiza_saldo_inicial(lista_de_moedas,corretora_mais_liquida,corretora_menos_liquida)

    

