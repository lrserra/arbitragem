import json
import requests
from uteis.util import Util
from uteis.corretora import Corretora
from uteis.ordem import Ordem
from datetime import datetime
import time

print(str(int(time.time())))

print(str(int(time.time()*1000)))

is_midnight = datetime.now().hour == 0
# ---- Testar book de ordens ---- #
# nova_dax = Corretora(nome_corretora, ativo)
# nova_dax.carregar_ordem_books()

# print(nova_dax.book)

# ---- Testar obter Saldo ---- #
# nova_dax = Corretora(nome_corretora, ativo)
# nova_dax.atualizar_saldo()

# print(nova_dax.saldoBRL)
# print(nova_dax.saldoCrypto)

# ---- Testar todas as ordens e cancela ---- #
# nova_dax = Corretora(nome_corretora, ativo)
# nova_dax.cancelar_todas_ordens()


nome_corretora = 'BitcoinTrade'
ativo = 'xrp'
paridade = 'brl'

corretora_obj = Corretora(nome_corretora)

'''
corretora_obj.book.obter_ordem_book_por_indice(ativo,'brl')
preco_compra = corretora_obj.book.preco_compra 
'''
corretora_obj.cancelar_todas_ordens(ativo)


'''


corretora_obj.atualizar_saldo()
#saldo = corretora_obj.saldo
#print('preco compra {} eh {}'.format(ativo,preco_compra))

ordem_compra = corretora_obj.ordem
ordem_compra.quantidade_enviada = 0.0006
ordem_compra.preco_enviado = 200000

ordem_compra = corretora_obj.enviar_ordem_compra(ordem_compra,ativo)
'''


ordem_venda = corretora_obj.ordem
ordem_venda.quantidade_enviada = 1
ordem_venda.preco_enviado = 10
ordem_venda.tipo_ordem = 'limited'

ordem_venda = corretora_obj.enviar_ordem_venda(ordem_venda,ativo)
ordem = corretora_obj.obter_ordem_por_id(ativo,ordem_venda)
cancelou = corretora_obj.cancelar_ordem(ativo,ordem_venda.id)

print(cancelou)