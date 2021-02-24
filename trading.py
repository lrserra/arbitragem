import json
import requests
from uteis.util import Util
from uteis.corretora import Corretora
from uteis.ordem import Ordem


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

ativo = 'xrp'
nome_corretora = 'BitcoinTrade'

corretora_obj = Corretora(nome_corretora)
#corretora_obj.book.obter_ordem_book_por_indice(ativo,'brl')
#preco_compra = corretora_obj.book.preco_compra
#corretora_obj.atualizar_saldo(ativo)
#saldo = corretora_obj.saldo
#print('preco compra {} eh {}'.format(ativo,preco_compra))
ordem_compra = corretora_obj.ordem
ordem_compra.quantidade_enviada = 1
ordem_compra.preco_enviado = 1
ordem_compra.tipo_ordem = 'limited'
ordem_compra = corretora_obj.enviar_ordem_compra(ordem_compra,ativo)
print('Rumo aos 1000 cakes')