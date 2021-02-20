import requests
import novadax
import json
import time
from util import Util

class Novadax:

    def __init__(self, ativo_parte,ativo_contraparte='brl'):
        self.ativo_parte = ativo_parte
        self.ativo_contraparte = ativo_contraparte
        self.urlNovadax = 'https://api.novadax.com/'
        self.nome_corretora = 'Novadax'
    
    def obterBooks(self):
        nova_client = novadax.RequestClient()
        return nova_client.get_depth('{}_{}'.format(self.ativo_parte.upper(),self.ativo_contraparte.upper()))

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
            return nova_client.create_order('{}_{}'.format(self.ativo_parte.upper(),self.ativo_contraparte.upper()), tipoOrdem.upper(), 'BUY', value=round((quantity*precoCompra),2))
        elif tipoOrdem.upper() == 'LIMIT':
            return nova_client.create_order('{}_{}'.format(self.ativo_parte.upper(),self.ativo_contraparte.upper()), tipoOrdem.upper(), 'BUY', precoCompra, quantity)

    def enviarOrdemVenda(self, quantity, tipoOrdem, precoVenda):
       # objeto que será postado para o endpoint
        config = Util.obterCredenciais()
        nova_client = novadax.RequestClient(config[self.nome_corretora]["Authentication"], config[self.nome_corretora]["Secret"])
        if tipoOrdem.upper() == 'MARKET':
            return nova_client.create_order('{}_{}'.format(self.ativo_parte.upper(),self.ativo_contraparte.upper()), tipoOrdem.upper(), 'SELL', amount=quantity)
        elif tipoOrdem.upper() == 'LIMIT':
            return nova_client.create_order('{}_{}'.format(self.ativo_parte.upper(),self.ativo_contraparte.upper()), tipoOrdem.upper(), 'SELL', precoVenda, quantity)

    def TransferirCrypto(self, quantity, destino, crypto_tag=''):
        config = Util.obterCredenciais()
        nova_client = novadax.RequestClient(config[self.nome_corretora]["Authentication"], config[self.nome_corretora]["Secret"])
        return nova_client.withdraw_coin(self.ativo_parte.upper(),quantity, destino, crypto_tag)

    def cancelarOrdem(self, idOrdem):
        config = Util.obterCredenciais()
        nova_client = novadax.RequestClient(config[self.nome_corretora]["Authentication"], config[self.nome_corretora]["Secret"])
        return nova_client.cancle_order(idOrdem)

    def obterOrdensAbertas(self):
        config = Util.obterCredenciais()
        nova_client = novadax.RequestClient(config[self.nome_corretora]["Authentication"], config[self.nome_corretora]["Secret"])
        return nova_client.list_orders('{}_{}'.format(self.ativo_parte.upper(),self.ativo_contraparte.upper()), 'UNFINISHED')
  