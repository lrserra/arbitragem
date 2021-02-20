import json
import requests
from util import Util
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

ativo = 'ltc'
nome_corretora = 'BrasilBitcoin'

corretora_obj = Corretora(nome_corretora)
corretora_obj.book.obter_ordem_book_por_indice(ativo,'usdt')
preco_compra = corretora_obj.book.preco_compra
#corretora_obj.atualizar_saldo(ativo)
#saldo = corretora_obj.saldo
print('preco compra {} eh {}'.format(ativo,preco_compra))
