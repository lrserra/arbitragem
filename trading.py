import json
import requests
from uteis.util import Util
from uteis.corretora import Corretora
from uteis.ordem import Ordem
from datetime import datetime
import time

ativo= 'xrp'
corretoraMercadoBTC = Corretora('MercadoBitcoin')
corretoraMercadoBTC.book.obter_ordem_book_por_indice(ativo,'brl',0,True,False)

print(corretoraMercadoBTC.book.preco_venda)
print(corretoraMercadoBTC.book.preco_compra)

corretoraMercadoBTC.book.obter_ordem_book_por_indice(ativo,'brl',0,True,True)

print(corretoraMercadoBTC.book.preco_venda)
print(corretoraMercadoBTC.book.preco_compra)