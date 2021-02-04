import requests
import time
from datetime import datetime
from corretora import Corretora
from ordem import Ordem
from util import Util

bitcoinTrade = Corretora('BitcoinTrade', 'btc')

ordem = Ordem()
ordem.quantidade_negociada = 1
ordem.preco_compra = 1.00
ordem.tipo_ordem = 'limited'

#teste = bitcoinTrade.enviar_ordem_compra(ordem)
#print(teste.id)
#print(teste.code)
teste = bitcoinTrade.obter_ordem_por_id('oGLH5-s80')
print(teste.id)
teste2 = bitcoinTrade.cancelar_ordem(teste.id)






