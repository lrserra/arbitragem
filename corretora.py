import requests
import hashlib
import hmac
import json
import time
import mimetypes
import logging
from http import client
from urllib.parse import urlencode
from mercadoBitcoin import MercadoBitcoin
from brasilBitcoin import BrasilBitcoin

class Corretora:
    
    def __init__(self, nome, ativo):
        self.nome = nome
        self.ativo = ativo
        self.precoCompra = 0.0
        self.qtdCompra = 0.0
        self.amountCompra = 0.0
        self.amountVenda = 0.0
        self.precoVenda = 0.0
        self.qtdVenda = 0.0
        self.corretagem = 0.0
        self.saldoBRL = 0.0
        self.saldoCrypto = 0.0

        if self.nome == 'MercadoBitcoin':
            self.book = MercadoBitcoin(self.ativo).obterBooks()
        elif self.nome == 'BrasilBitcoin':
            self.book = BrasilBitcoin(self.ativo).obterBooks()
        elif self.nome == 'BitcoinTrade':
            self.book = BitcoinTrade(self.ativo).obterBooks()

        self.carregarBooks(ativo)

    def carregarBooks(self, ativo, ordem = 0):

        if self.nome == 'MercadoBitcoin':
            self.precoCompra = self.book['asks'][ordem][0]
            self.qtdCompra = self.book['asks'][ordem][1]
            self.precoVenda = self.book['bids'][ordem][0]
            self.qtdVenda = self.book['bids'][ordem][1]
            self.corretagem = 0.007

        elif self.nome == 'BrasilBitcoin':
            self.precoCompra = self.book['sell'][ordem]['preco']
            self.qtdCompra = self.book['sell'][ordem]['quantidade']
            self.precoVenda = self.book['buy'][ordem]['preco']
            self.qtdVenda = self.book['buy'][ordem]['quantidade']
            self.corretagem = 0.005

        elif self.nome == 'BitcoinTrade':
            self.precoCompra = self.book['asks'][ordem]['unit_price']
            self.qtdCompra = self.book['asks'][ordem]['amount']
            self.precoVenda = self.book['bids'][ordem]['unit_price']
            self.qtdVenda = self.book['bids'][ordem]['amount']
            self.corretagem = 0.005
        
        self.amountCompra = self.precoCompra * self.qtdCompra
        self.amountVenda = self.precoVenda * self.qtdVenda

    def obterFinanceiroCorretagemCompraPorCorretora(self, qtdCompra = 0):
        if qtdCompra == 0:
            return self.precoCompra * self.qtdCompra * self.corretagem
        return self.precoCompra * qtdCompra * self.corretagem

    def obterFinanceiroCorretagemVendaPorCorretora(self, qtdVenda = 0):
        if qtdVenda == 0:
            return self.precoVenda * self.qtdVenda * self.corretagem
        return self.precoVenda * qtdVenda * self.corretagem

    def obterAmountCompra(self, qtdCompra = 0):
        if qtdCompra == 0:
            return self.precoCompra * self.qtdCompra
        return self.precoCompra * qtdCompra

    def obterAmountVenda(self, qtdVenda = 0):
        if qtdVenda == 0:
            return self.precoVenda * self.qtdVenda
        return self.precoVenda * qtdVenda

    def obterOrdemPorId(self, idOrdem):
        if self.nome == 'MercadoBitcoin':
            pass
        elif self.nome == 'BrasilBitcoin':
            return BrasilBitcoin(self.ativo).obterOrdemPorId(idOrdem)

    def atualizarSaldo(self):
        if self.nome == 'MercadoBitcoin':
            response_json = MercadoBitcoin(self.ativo).obterSaldo()
            self.saldoBRL = float(response_json['response_data']['balance']['brl']['total'])
            self.saldoCrypto = float(response_json['response_data']['balance'][self.ativo]['total'])
        elif self.nome == 'BrasilBitcoin':
            response_json = BrasilBitcoin(self.ativo).obterSaldo()
            self.saldoBRL = float(response_json['brl'])
            self.saldoCrypto = float(response_json[self.ativo])

    def enviarOrdemCompra(self, quantity, typeOrder):
        if self.nome == 'MercadoBitcoin':
            return MercadoBitcoin(self.ativo).enviarOrdemCompra(quantity, typeOrder, self.precoCompra)
        elif self.nome == 'BrasilBitcoin':
            return BrasilBitcoin(self.ativo).enviarOrdemCompra(quantity, typeOrder, self.precoCompra)

    def enviarOrdemVenda(self, quantity, typeOrder):
        if self.nome == 'MercadoBitcoin':
            return MercadoBitcoin(self.ativo).enviarOrdemVenda(quantity, typeOrder, self.precoVenda)
        elif self.nome == 'BrasilBitcoin':
            return BrasilBitcoin(self.ativo).enviarOrdemVenda(quantity, typeOrder, self.precoVenda)

    def cancelarOrdem(self, idOrdem):
        if self.nome == 'MercadoBitcoin':
            pass
        elif self.nome == 'BrasilBitcoin':
            return BrasilBitcoin(self.ativo).cancelarOrdem(idOrdem)

    def cancelarTodasOrdens(self,ativo):
        if self.nome == 'MercadoBitcoin':
            pass
        elif self.nome == 'BrasilBitcoin':
            ordens_abertas = BrasilBitcoin(self.ativo).obterOrdensAbertas()
            for ordem in ordens_abertas:
                if str(ativo).upper() == str(ordem['coin']).upper():
                    self.cancelarOrdem(ordem['id'])

    def TransferirCrypto(self, quantity):      
        if self.nome == 'MercadoBitcoin':
            return MercadoBitcoin(self.ativo).TransferirCrypto(quantity)
        elif self.nome == 'BrasilBitcoin':
            return BrasilBitcoin(self.ativo).TransferirCrypto(quantity)


