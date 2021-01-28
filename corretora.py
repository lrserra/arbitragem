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
from bitcoinTrade import BitcoinTrade
from ordem import Ordem

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
        self.book = []
        self.ordem = self.obter_ordem_book_por_indice(0)

        self.carregarBooks(ativo)

    def obter_ordem_book_por_indice(self, indice = 0):
        ordem = Ordem()

        self.carregar_ordem_books()

        if self.nome == 'MercadoBitcoin':
            ordem.preco_compra = self.book['asks'][indice][0]
            ordem.quantidade_compra = self.book['asks'][indice][1]
            ordem.preco_venda = self.book['bids'][indice][0]
            ordem.quantidade_venda = self.book['bids'][indice][1]
            self.corretagem = 0.007

        elif self.nome == 'BrasilBitcoin':
            ordem.preco_compra = self.book['sell'][indice]['preco']
            ordem.quantidade_compra = self.book['sell'][indice]['quantidade']
            ordem.preco_venda = self.book['buy'][indice]['preco']
            ordem.quantidade_venda = self.book['buy'][indice]['quantidade']
            self.corretagem = 0.005

        elif self.nome == 'BitcoinTrade':
            ordem.preco_compra = self.book['asks'][indice]['unit_price']
            ordem.quantidade_compra = self.book['asks'][indice]['amount']
            ordem.preco_venda = self.book['bids'][indice]['unit_price']
            ordem.quantidade_venda = self.book['bids'][indice]['amount']
            self.corretagem = 0.005
        
        self.amountCompra = ordem.preco_compra * ordem.quantidade_compra
        self.amountVenda = ordem.preco_venda * ordem.quantidade_venda

        return ordem

    def carregar_ordem_books(self):

        if self.nome == 'MercadoBitcoin':
            self.book = MercadoBitcoin(self.ativo).obterBooks()

        elif self.nome == 'BrasilBitcoin':
            self.book = BrasilBitcoin(self.ativo).obterBooks()

        elif self.nome == 'BitcoinTrade':
            self.book = BitcoinTrade(self.ativo).obterBooks()

    def carregarBooks(self, ativo, ordem = 0):

        book = []

        if self.nome == 'MercadoBitcoin':
            book = MercadoBitcoin(ativo).obterBooks()
            self.precoCompra = book['asks'][ordem][0]
            self.qtdCompra = book['asks'][ordem][1]
            self.precoVenda = book['bids'][ordem][0]
            self.qtdVenda = book['bids'][ordem][1]
            self.corretagem = 0.007

        elif self.nome == 'BrasilBitcoin':
            book = BrasilBitcoin(ativo).obterBooks()
            self.precoCompra = book['sell'][ordem]['preco']
            self.qtdCompra = book['sell'][ordem]['quantidade']
            self.precoVenda = book['buy'][ordem]['preco']
            self.qtdVenda = book['buy'][ordem]['quantidade']
            self.corretagem = 0.005

        elif self.nome == 'BitcoinTrade':
            book = BitcoinTrade(self.ativo).obterBooks()
            self.precoCompra = book['asks'][ordem]['unit_price']
            self.qtdCompra = book['asks'][ordem]['amount']
            self.precoVenda = book['bids'][ordem]['unit_price']
            self.qtdVenda = book['bids'][ordem]['amount']
            self.corretagem = 0.005
        
        self.amountCompra = self.precoCompra * self.qtdCompra
        self.amountVenda = self.precoVenda * self.qtdVenda

        return book

    def obter_financeiro_corretagem_compra_por_corretora(self, quantidade_compra = 0):
        if quantidade_compra == 0:
            return self.ordem.preco_compra * self.ordem.quantidade_compra * self.corretagem
        return self.ordem.preco_compra * quantidade_compra * self.corretagem

    def obterFinanceiroCorretagemCompraPorCorretora(self, qtdCompra = 0):
        if qtdCompra == 0:
            return self.precoCompra * self.qtdCompra * self.corretagem
        return self.precoCompra * qtdCompra * self.corretagem

    def obter_financeiro_corretagem_venda_por_corretora(self, quantidade_venda = 0):
        if quantidade_venda == 0:
            return self.ordem.preco_venda * self.ordem.quantidade_venda * self.corretagem
        return self.ordem.preco_venda * quantidade_venda * self.corretagem

    def obterFinanceiroCorretagemVendaPorCorretora(self, qtdVenda = 0):
        if qtdVenda == 0:
            return self.precoVenda * self.qtdVenda * self.corretagem
        return self.precoVenda * qtdVenda * self.corretagem

    def obter_amount_compra(self, quantidade_compra = 0):
        if quantidade_compra == 0:
            return self.ordem.preco_compra * self.ordem.quantidade_compra
        return self.ordem.preco_compra * quantidade_compra

    def obterAmountCompra(self, qtdCompra = 0):
        if qtdCompra == 0:
            return self.precoCompra * self.qtdCompra
        return self.precoCompra * qtdCompra

    def obter_amount_venda(self, quantidade_venda = 0):
        if quantidade_venda == 0:
            return self.ordem.preco_venda * self.ordem.quantidade_venda
        return self.ordem.preco_venda * quantidade_venda

    def obterAmountVenda(self, qtdVenda = 0):
        if qtdVenda == 0:
            return self.precoVenda * self.qtdVenda
        return self.precoVenda * qtdVenda

    def obter_ordem_por_id(self, id_ordem):
        if self.nome == 'MercadoBitcoin':
            pass
        elif self.nome == 'BrasilBitcoin':
            return BrasilBitcoin(self.ativo).obterOrdemPorId(id_ordem)

    def obterOrdemPorId(self, idOrdem):
        if self.nome == 'MercadoBitcoin':
            pass
        elif self.nome == 'BrasilBitcoin':
            return BrasilBitcoin(self.ativo).obterOrdemPorId(idOrdem)

    def atualizar_saldo(self):
        if self.nome == 'MercadoBitcoin':
            response_json = MercadoBitcoin(self.ativo).obterSaldo()
            self.saldoBRL = float(response_json['response_data']['balance']['brl']['available'])
            self.saldoCrypto = float(response_json['response_data']['balance'][self.ativo]['available'])
        elif self.nome == 'BrasilBitcoin':
            response_json = BrasilBitcoin(self.ativo).obterSaldo()
            self.saldoBRL = float(response_json['brl'])
            self.saldoCrypto = float(response_json[self.ativo])

    def atualizarSaldo(self):
        if self.nome == 'MercadoBitcoin':
            response_json = MercadoBitcoin(self.ativo).obterSaldo()
            self.saldoBRL = float(response_json['response_data']['balance']['brl']['total'])
            self.saldoCrypto = float(response_json['response_data']['balance'][self.ativo]['total'])
        elif self.nome == 'BrasilBitcoin':
            response_json = BrasilBitcoin(self.ativo).obterSaldo()
            self.saldoBRL = float(response_json['brl'])
            self.saldoCrypto = float(response_json[self.ativo])

    def enviar_ordem_compra(self, ordem:Ordem):
        if self.nome == 'MercadoBitcoin':
            return MercadoBitcoin(self.ativo).enviarOrdemCompra(ordem.quantidade_negociada, ordem.tipo_ordem, ordem.preco_compra)
        elif self.nome == 'BrasilBitcoin':
            return BrasilBitcoin(self.ativo).enviarOrdemCompra(ordem.quantidade_negociada, ordem.tipo_ordem, ordem.preco_compra)

    def enviarOrdemCompra(self, quantity, typeOrder):
        if self.nome == 'MercadoBitcoin':
            return MercadoBitcoin(self.ativo).enviarOrdemCompra(quantity, typeOrder, self.precoCompra)
        elif self.nome == 'BrasilBitcoin':
            return BrasilBitcoin(self.ativo).enviarOrdemCompra(quantity, typeOrder, self.precoCompra)

    def enviar_ordem_venda(self, ordem:Ordem):
        if self.nome == 'MercadoBitcoin':
            return MercadoBitcoin(self.ativo).enviarOrdemVenda(ordem.quantidade_negociada, ordem.tipo_ordem, ordem.preco_venda)
        elif self.nome == 'BrasilBitcoin':
            return BrasilBitcoin(self.ativo).enviarOrdemVenda(ordem.quantidade_negociada, ordem.tipo_ordem, ordem.preco_venda)

    def enviarOrdemVenda(self, quantity, typeOrder):
        if self.nome == 'MercadoBitcoin':
            return MercadoBitcoin(self.ativo).enviarOrdemVenda(quantity, typeOrder, self.precoVenda)
        elif self.nome == 'BrasilBitcoin':
            return BrasilBitcoin(self.ativo).enviarOrdemVenda(quantity, typeOrder, self.precoVenda)

    def cancelar_ordem(self, idOrdem):
        if self.nome == 'MercadoBitcoin':
            pass
        elif self.nome == 'BrasilBitcoin':
            return BrasilBitcoin(self.ativo).cancelarOrdem(idOrdem)

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

    def transferir_crypto(self, ordem:Ordem):      
        if self.nome == 'MercadoBitcoin':
            return MercadoBitcoin(self.ativo).TransferirCrypto(ordem.quantidade_transferencia)
        elif self.nome == 'BrasilBitcoin':
            return BrasilBitcoin(self.ativo).TransferirCrypto(ordem.quantidade_transferencia)

    def TransferirCrypto(self, quantity):      
        if self.nome == 'MercadoBitcoin':
            return MercadoBitcoin(self.ativo).TransferirCrypto(quantity)
        elif self.nome == 'BrasilBitcoin':
            return BrasilBitcoin(self.ativo).TransferirCrypto(quantity)


