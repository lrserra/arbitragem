import requests
import time
from datetime import datetime
from corretora import Corretora
from ordem import Ordem
from util import Util

bitcoinTrade = Corretora('BitcoinTrade', 'btc')

ordem = Ordem()
ordem.quantidade_negociada = 1
ordem.preco_venda = 1
ordem.tipo_ordem = 'market'

bitcoinTrade.enviar_ordem_venda(ordem)


