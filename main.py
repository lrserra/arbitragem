import requests
import time
import logging

from datetime import datetime, timedelta
from corretora import Corretora
from util import Util
from caixa import Caixa
from arbitragem import Arbitragem
from leilao import Leilao
from ordem import Ordem

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

retorno_ordem_leilao_compra = Ordem()
retorno_ordem_leilao_venda = Ordem()

dict_leilao_compra = {}
dict_leilao_venda = {}

for moeda in lista_de_moedas:
    dict_leilao_compra[moeda]={}
    dict_leilao_venda[moeda]={}
    dict_leilao_compra[moeda]['ordem'] = Ordem()
    dict_leilao_venda[moeda]['ordem'] = Ordem()
    dict_leilao_compra[moeda]['zeragem'] = Ordem()
    dict_leilao_venda[moeda]['zeragem'] = Ordem()
    dict_leilao_compra[moeda]['foi_cancelado'] = False
    dict_leilao_venda[moeda]['foi_cancelado'] = False

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

                # Atualiza o saldo de crypto e de BRL nas corretoras
                CorretoraMaisLiquida.atualizar_saldo()
                CorretoraMenosLiquida.atualizar_saldo()

                # Roda a arbitragem nas 2 corretoras
                retorno_mais_liquida_para_menos_liquida, pnl_abritragem_mais_liquida = Arbitragem.processar(CorretoraMaisLiquida, CorretoraMenosLiquida, moeda, True)
                retorno_menos_liquida_para_mais_liquida, pnl_abritragem_menos_liquida = Arbitragem.processar(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True)   

                if retorno_mais_liquida_para_menos_liquida.id > 0:

                    CorretoraMaisLiquida.atualizar_saldo()
                    CorretoraMenosLiquida.atualizar_saldo()
                    logging.warning('operou arb de {}! + {}brl de pnl'.format(moeda,round(pnl_abritragem_mais_liquida,2)))
                
                elif retorno_menos_liquida_para_mais_liquida.id > 0:
                    
                    CorretoraMaisLiquida.atualizar_saldo()
                    CorretoraMenosLiquida.atualizar_saldo()
                    logging.warning('operou arb de {}! + {}brl de pnl'.format(moeda,round(pnl_abritragem_menos_liquida,2)))

                # -----------------------------------------------------------------------------------------------------------------------------------#

                #verifica se fui executado e se necessario cancelar ordens abertas            
                dict_leilao_compra[moeda]['zeragem'], dict_leilao_compra[moeda]['foi_cancelado'] = Leilao.cancela_ordens_e_compra_na_mercado(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True, dict_leilao_compra[moeda]['ordem'])
                dict_leilao_venda[moeda]['zeragem'], dict_leilao_venda[moeda]['foi_cancelado'] = Leilao.cancela_ordens_e_vende_na_mercado(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True, dict_leilao_venda[moeda]['ordem'])

                # Se Id diferente de zero, significa que operou leilão (fui executado)
                if dict_leilao_compra[moeda]['zeragem'].id != 0:
                    
                    pnl = ((retorno_ordem_leilao_compra.preco_compra * 0.998) - (dict_leilao_compra[moeda]['zeragem'].preco_executado * 1.007)) * dict_leilao_compra[moeda]['zeragem'].quantidade_executada

                    logging.warning('operou leilao de compra de {}! + {}brl de pnl'.format(moeda,round(pnl,2)))
                    CorretoraMaisLiquida.atualizar_saldo()
                    CorretoraMenosLiquida.atualizar_saldo()
                    dict_leilao_compra[moeda]['ordem'] = Ordem() #reinicia as ordens

                elif dict_leilao_compra[moeda]['ordem'].id == 0 or dict_leilao_compra[moeda]['foi_cancelado']: #se não ha ordens abertas ou se ordens foram canceladas, envia uma nova
                    dict_leilao_compra[moeda]['ordem']  = Leilao.compra(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True)
            
                # Se Id diferente de zero, significa que operou leilão (fui executado)
                if  dict_leilao_venda[moeda]['zeragem'].id != 0:

                    pnl = ((retorno_ordem_leilao_venda.preco_venda * 0.998) - (dict_leilao_venda[moeda]['zeragem'].preco_executado * 1.007)) * dict_leilao_venda[moeda]['zeragem'].quantidade_executada

                    logging.warning('operou leilao de venda de {}! + {}brl de pnl'.format(moeda,round(pnl,2)))
                    CorretoraMaisLiquida.atualizar_saldo()
                    CorretoraMenosLiquida.atualizar_saldo() 
                    dict_leilao_venda[moeda]['ordem'] = Ordem() #reinicia as ordens   

                elif dict_leilao_venda[moeda]['ordem'].id == 0 or  dict_leilao_venda[moeda]['foi_cancelado']:#se não ha ordens abertas ou se ordens foram canceladas, envia uma nova
                    dict_leilao_venda[moeda]['ordem'] = Leilao.venda(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True)
                   
            except Exception as erro:        
                logging.error(erro) 
            
            time.sleep(Util.frequencia())

        agora = datetime.now() 

    #zerar o pnl e reiniciar a bagaça
    Caixa.zera_o_pnl_em_cripto(lista_de_moedas,saldo_inicial,corretora_mais_liquida,corretora_menos_liquida)
    retorno_ordem_leilao_compra = Ordem()
    retorno_ordem_leilao_venda = Ordem()

    hour = hour+1
    
    Caixa.atualiza_saldo_inicial(lista_de_moedas,corretora_mais_liquida,corretora_menos_liquida)

    

