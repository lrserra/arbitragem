import json
import requests
from uteis.util import Util
from uteis.corretora import Corretora
from uteis.ordem import Ordem
from datetime import datetime
import time

ativo= 'btc'
corretoraMercadoBTC = Corretora('BitcoinTrade')
corretoraMercadoBTC.book.obter_ordem_book_por_indice(ativo,'brl',0,True,True)

#print(corretoraMercadoBTC.book.obter_preco_medio_de_compra(10))
print(corretoraMercadoBTC.book.obter_quantidade_abaixo_de_preco_compra(1000000))

ativo= 'btc'
corretoraMercadoBTC = Corretora('Novadax')
corretoraMercadoBTC.book.obter_ordem_book_por_indice(ativo,'brl',0,True,True)

#print(corretoraMercadoBTC.book.obter_preco_medio_de_compra(10))
print(corretoraMercadoBTC.book.obter_quantidade_abaixo_de_preco_compra(1000000))

ativo= 'btc'
corretoraMercadoBTC = Corretora('BrasilBitcoin')
corretoraMercadoBTC.book.obter_ordem_book_por_indice(ativo,'brl',0,True,True)

#print(corretoraMercadoBTC.book.obter_preco_medio_de_compra(10))
print(corretoraMercadoBTC.book.obter_quantidade_abaixo_de_preco_compra(1000000))

ativo= 'btc'
corretoraMercadoBTC = Corretora('MercadoBitcoin')
corretoraMercadoBTC.book.obter_ordem_book_por_indice(ativo,'brl',0,True,True)

#print(corretoraMercadoBTC.book.obter_preco_medio_de_compra(10))
print(corretoraMercadoBTC.book.obter_quantidade_abaixo_de_preco_compra(1000000))

