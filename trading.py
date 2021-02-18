import json
import requests
from util import Util
from corretora import Corretora
from ordem import Ordem

ativo = 'xrp'
nome_corretora = 'BitcoinTrade'

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

btctrade = Corretora(nome_corretora,ativo)
ordem = Ordem()
ordem.tipo_ordem = 'limited'
ordem.quantidade_negociada = 10
ordem.preco_compra = 1
btctrade.enviar_ordem_compra(ordem)