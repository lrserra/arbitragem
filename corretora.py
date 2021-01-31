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
        self.amountCompra = 0.0
        self.amountVenda = 0.0
        self.corretagem = 0.0
        self.saldoBRL = 0.0
        self.saldoCrypto = 0.0
        self.book = []
        self.ordem = self.obter_ordem_book_por_indice(0)

    def obter_ordem_book_por_indice(self, indice = 0):
        ordem = Ordem()

        try:
            self.carregar_ordem_books()

            if self.nome == 'MercadoBitcoin':
                ordem.preco_compra = float(self.book['asks'][indice][0])
                ordem.quantidade_compra = float(self.book['asks'][indice][1])
                ordem.preco_venda = float(self.book['bids'][indice][0])
                ordem.quantidade_venda = float(self.book['bids'][indice][1])
                self.corretagem = 0.007

            elif self.nome == 'BrasilBitcoin':
                ordem.preco_compra = float(self.book['sell'][indice]['preco'])
                ordem.quantidade_compra = float(self.book['sell'][indice]['quantidade'])
                ordem.preco_venda = float(self.book['buy'][indice]['preco'])
                ordem.quantidade_venda = float(self.book['buy'][indice]['quantidade'])
                self.corretagem = 0.005

            elif self.nome == 'BitcoinTrade':
                ordem.preco_compra = float(self.book['asks'][indice]['unit_price'])
                ordem.quantidade_compra = float(self.book['asks'][indice]['amount'])
                ordem.preco_venda = float(self.book['bids'][indice]['unit_price'])
                ordem.quantidade_venda = float(self.book['bids'][indice]['amount'])
                self.corretagem = 0.005
            
            self.amountCompra = ordem.preco_compra * ordem.quantidade_compra
            self.amountVenda = ordem.preco_venda * ordem.quantidade_venda
        except Exception as erro:
            raise Exception(erro)
        
        return ordem

    def carregar_ordem_books(self):
        try:
            if self.nome == 'MercadoBitcoin':
                self.book = MercadoBitcoin(self.ativo).obterBooks()

            elif self.nome == 'BrasilBitcoin':
                self.book = BrasilBitcoin(self.ativo).obterBooks()

            elif self.nome == 'BitcoinTrade':
                self.book = BitcoinTrade(self.ativo).obterBooks()
        except Exception as erro:
            raise Exception(erro)

    def obter_financeiro_corretagem_compra_por_corretora(self, quantidade_compra = 0):
        if quantidade_compra == 0:
            return self.ordem.preco_compra * self.ordem.quantidade_compra * self.corretagem
        return self.ordem.preco_compra * quantidade_compra * self.corretagem

    def obter_financeiro_corretagem_venda_por_corretora(self, quantidade_venda = 0):
        if quantidade_venda == 0:
            return self.ordem.preco_venda * self.ordem.quantidade_venda * self.corretagem
        return self.ordem.preco_venda * quantidade_venda * self.corretagem

    def obter_amount_compra(self, quantidade_compra = 0):
        if quantidade_compra == 0:
            return self.ordem.preco_compra * self.ordem.quantidade_compra
        return self.ordem.preco_compra * quantidade_compra

    def obter_amount_venda(self, quantidade_venda = 0):
        if quantidade_venda == 0:
            return self.ordem.preco_venda * self.ordem.quantidade_venda
        return self.ordem.preco_venda * quantidade_venda

    def obter_ordem_por_id(self, id_ordem):
        ordem = Ordem()
        try:
            if self.nome == 'MercadoBitcoin':
                pass
            elif self.nome == 'BrasilBitcoin':
                response = BrasilBitcoin(self.ativo).obterOrdemPorId(id_ordem)
                ordem.status = response['data']['status']
                ordem.quantidade_executada = response['data']['executed']
                ordem.preco_executado = response['data']['price']
        except Exception as erro:
            raise Exception(erro)
        return ordem

    def atualizar_saldo(self):
        try:
            if self.nome == 'MercadoBitcoin':
                response_json = MercadoBitcoin(self.ativo).obterSaldo()
                self.saldoBRL = float(response_json['response_data']['balance']['brl']['available'])
                self.saldoCrypto = float(response_json['response_data']['balance'][self.ativo]['available'])
            elif self.nome == 'BrasilBitcoin':
                response_json = BrasilBitcoin(self.ativo).obterSaldo()
                self.saldoBRL = float(response_json['brl'])
                self.saldoCrypto = float(response_json[self.ativo])
        except Exception as erro:
            raise Exception(erro)

    def enviar_ordem_compra(self, ordem:Ordem):
        ordemRetorno = Ordem()
        
        try:
            if self.nome == 'MercadoBitcoin':
                response = MercadoBitcoin(self.ativo).enviarOrdemCompra(ordem.quantidade_negociada, ordem.tipo_ordem, ordem.preco_compra)
                if response['status_code'] == 100: 
                    ordemRetorno.id = response['response_data']['order']['order_id']
                    if response['response_data']['order']['status'] == 4:
                        ordemRetorno.status = 'filled'
                    ordemRetorno.quantidade_compra = float(response['response_data']['order']['quantity'])
                    ordemRetorno.preco_compra = float(response['response_data']['order']['limit_price'])
                    ordemRetorno.quantidade_executada = float(response['response_data']['order']['executed_quantity'])
                    ordemRetorno.preco_executado = float(response['response_data']['order']['executed_price_avg'])
                else:
                    mensagem = '{}: enviar_ordem_compra - {}'.format(self.nome, response['erro_message'])
                    print(mensagem)
                    raise Exception(mensagem)
            elif self.nome == 'BrasilBitcoin':
                response = BrasilBitcoin(self.ativo).enviarOrdemCompra(ordem.quantidade_negociada, ordem.tipo_ordem, ordem.preco_compra)
                if response['success'] == True:
                    ordemRetorno.id = response['data']['id']
                    ordemRetorno.status = response['data']['status']
                    ordemRetorno.quantidade_venda = float(response['data']['amount'])
                    ordemRetorno.preco_venda = float(response['data']['price'])
                    i = 0
                    qtd = len(response['data']['fills'])
                    while i < qtd:
                        ordemRetorno.quantidade_executada += float(response['data']['fills'][i]['amount'])
                        ordemRetorno.preco_executado = float(response['data']['fills'][i]['price'].replace(',','.'))
                        i += 1
                else:
                    mensagem = '{}: enviar_ordem_compra - {}'.format(self.nome, response['message'])
                    print(mensagem)
                    raise Exception(mensagem)
        except Exception as erro:
            raise Exception(erro)

        return ordemRetorno

    def enviar_ordem_venda(self, ordem:Ordem):
        ordemRetorno = Ordem()
        mensagem = ''

        try:
            if self.nome == 'MercadoBitcoin':
                response = MercadoBitcoin(self.ativo).enviarOrdemVenda(ordem.quantidade_negociada, ordem.tipo_ordem, ordem.preco_venda)
                if response['status_code'] == 100:            
                    ordemRetorno.id = response['response_data']['order']['order_id']
                    if response['response_data']['order']['status'] == 4:
                        ordemRetorno.status = 'filled'
                    ordemRetorno.quantidade_venda = float(response['response_data']['order']['quantity'])
                    ordemRetorno.preco_venda = float(response['response_data']['order']['limit_price'])
                    ordemRetorno.quantidade_executada = float(response['response_data']['order']['executed_quantity'])
                    ordemRetorno.preco_executado = float(response['response_data']['order']['executed_price_avg'])
                else:
                    mensagem = '{}: enviar_ordem_venda - {}'.format(self.nome, response['error_message'])
                    print(mensagem)
                    raise Exception(mensagem)

            elif self.nome == 'BrasilBitcoin':
                response = BrasilBitcoin(self.ativo).enviarOrdemVenda(ordem.quantidade_negociada, ordem.tipo_ordem, ordem.preco_venda)
                if response['success'] == True:
                    ordemRetorno.id = response['data']['id']
                    ordemRetorno.status = response['data']['status']
                    ordemRetorno.quantidade_venda = float(response['data']['amount'])
                    ordemRetorno.preco_venda = float(response['data']['price'])
                    i = 0
                    qtd = len(response['data']['fills'])
                    while i < qtd:
                        ordemRetorno.quantidade_executada += float(response['data']['fills'][i]['amount'])
                        ordemRetorno.preco_executado = float(response['data']['fills'][i]['price'].replace(',','.'))
                        i += 1
                else:
                    mensagem = '{}: enviar_ordem_venda - {}'.format(self.nome, response['message'])
                    print(mensagem)
                    raise Exception(mensagem)
        except Exception as erro:
                raise Exception(erro)

        return ordemRetorno

    def cancelar_ordem(self, idOrdem):
        if self.nome == 'MercadoBitcoin':
            pass
        elif self.nome == 'BrasilBitcoin':
            return BrasilBitcoin(self.ativo).cancelarOrdem(idOrdem)

    def cancelar_todas_ordens(self,ativo):
        if self.nome == 'MercadoBitcoin':
            pass
        elif self.nome == 'BrasilBitcoin':
            ordens_abertas = BrasilBitcoin(self.ativo).obterOrdensAbertas()
            for ordem in ordens_abertas:
                if str(ativo).upper() == str(ordem['coin']).upper():
                    self.cancelar_ordem(ordem['id'])

    def transferir_crypto(self, ordem:Ordem):      
        if self.nome == 'MercadoBitcoin':
            return MercadoBitcoin(self.ativo).TransferirCrypto(ordem.quantidade_transferencia)
        elif self.nome == 'BrasilBitcoin':
            return BrasilBitcoin(self.ativo).TransferirCrypto(ordem.quantidade_transferencia)


