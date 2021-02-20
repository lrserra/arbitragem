import requests
import novadax
import json
import time
from util import Util

class Novadax:

    def __init__(self, ativo):
        self.ativo = ativo
        self.urlNovadax = 'https://api.novadax.com/'
        self.nome_corretora = 'Novadax'
    
    def obterBooks(self):
        nova_client = novadax.RequestClient()
        return nova_client.get_depth('{}_BRL'.format(self.ativo.upper()))

    def obterSaldo(self):
        config = Util.obterCredenciais()
        nova_client = novadax.RequestClient(config[self.nome_corretora]["Authentication"], config[self.nome_corretora]["Secret"])
        return nova_client.get_account_balance()

    def obterOrdemPorId(self, idOrdem):
        config = Util.obterCredenciais()
        nova_client = novadax.RequestClient(config[self.nome_corretora]["Authentication"], config[self.nome_corretora]["Secret"])
        return nova_client.get_order(idOrdem)

    def enviarOrdemCompra(self, quantity, tipoOrdem, precoCompra):
        # objeto que será postado para o endpoint
        config = Util.obterCredenciais()
        nova_client = novadax.RequestClient(config[self.nome_corretora]["Authentication"], config[self.nome_corretora]["Secret"])
        if tipoOrdem.upper() == 'MARKET':
            return nova_client.create_order('{}_BRL'.format(self.ativo.upper()), tipoOrdem.upper(), 'BUY', value=round((quantity*precoCompra),2))
        elif tipoOrdem.upper() == 'LIMITED':
            return nova_client.create_order('{}_BRL'.format(self.ativo.upper()), 'LIMIT', 'BUY', round(precoCompra,2), round(quantity,8))

    def enviarOrdemVenda(self, quantity, tipoOrdem, precoVenda):
       # objeto que será postado para o endpoint
        config = Util.obterCredenciais()
        nova_client = novadax.RequestClient(config[self.nome_corretora]["Authentication"], config[self.nome_corretora]["Secret"])
        if tipoOrdem.upper() == 'MARKET':
            return nova_client.create_order('{}_BRL'.format(self.ativo.upper()), tipoOrdem.upper(), 'SELL', amount=round(quantity,8))
        elif tipoOrdem.upper() == 'LIMITED':
            return nova_client.create_order('{}_BRL'.format(self.ativo.upper()), 'LIMIT', 'SELL', round(precoVenda,2), round(quantity,8))

    def TransferirCrypto(self, quantity, destino, crypto_tag=''):
        config = Util.obterCredenciais()
        nova_client = novadax.RequestClient(config[self.nome_corretora]["Authentication"], config[self.nome_corretora]["Secret"])
        return nova_client.withdraw_coin(self.ativo.upper(),quantity, destino, crypto_tag)

    def cancelarOrdem(self, idOrdem):
        config = Util.obterCredenciais()
        nova_client = novadax.RequestClient(config[self.nome_corretora]["Authentication"], config[self.nome_corretora]["Secret"])
        return nova_client.cancle_order(idOrdem)

    def obterOrdensAbertas(self):
        config = Util.obterCredenciais()
        nova_client = novadax.RequestClient(config[self.nome_corretora]["Authentication"], config[self.nome_corretora]["Secret"])
        return nova_client.list_orders('{}_BRL'.format(self.ativo.upper()), 'UNFINISHED')
  