import requests
import hashlib
import hmac
import json
import time
import mimetypes
import logging
from http import client
from urllib.parse import urlencode
from corretoras.mercadoBitcoin import MercadoBitcoin
from corretoras.brasilBitcoin import BrasilBitcoin
from corretoras.bitcoinTrade import BitcoinTrade
from corretoras.novadaxCorretora import Novadax
from uteis.ordem import Ordem
from uteis.book import Book

class Corretora:
    
    def __init__(self, nome):
        
        #propriedades qu precisam ser fornecidas
        self.nome = nome 

        #propriedades especificas de cada corretora
        self.corretagem_limitada, self.corretagem_mercado = self.__obter_corretagem(nome)
        self.descricao_status_executado = self.__obter_status_executado(nome)
        
        #propriedades dinamicas
        self.saldo = 0.0
        self.book = Book(nome)
        self.ordem = Ordem()

    #metodos exclusivos por ativo

    def atualizar_saldo(self,ativo):
        try:
            if self.nome == 'MercadoBitcoin':
                response_json = MercadoBitcoin(ativo).obterSaldo()
                self.saldo = float(response_json['response_data']['balance'][ativo]['total'])
            elif self.nome == 'BrasilBitcoin':
                response_json = BrasilBitcoin(ativo).obterSaldo()
                self.saldo = float(response_json[ativo])
            elif self.nome == 'BitcoinTrade':
                response_json = BitcoinTrade(ativo).obterSaldo()
                while response_json['message'] == 'Too Many Requests':
                    time.sleep(1)
                    response_json = BitcoinTrade(ativo).obterSaldo()
                for chave in response_json['data']:
                    if chave['currency_code'] == ativo.upper():
                        self.saldo = float(chave['available_amount']) + float(chave['locked_amount'])
            elif self.nome == 'Novadax':
                response_json = Novadax(ativo).obterSaldo()
                for chave in response_json['data']:
                    if chave['currency'] == ativo.upper():
                        self.saldo = float(chave['balance'])
        except Exception as erro:
            raise Exception(erro)

    def cancelar_todas_ordens(self,ativo):

        if self.nome == 'MercadoBitcoin':
            pass
        elif self.nome == 'BrasilBitcoin':
            ordens_abertas = BrasilBitcoin(ativo).obterOrdensAbertas()
            for ordem in ordens_abertas:
                if str(ativo).upper() == str(ordem['coin']).upper():
                    self.cancelar_ordem(ordem['id'])
        elif self.nome == 'BitcoinTrade':
            ordens_abertas = BitcoinTrade(ativo).obterOrdensAbertas()
            if ordens_abertas['message'] == 'Too Many Requests':
                time.sleep(1)
                ordens_abertas = BitcoinTrade(ativo).obterOrdensAbertas()
            elif 'data' not in ordens_abertas.keys():
                logging.info(str(ordens_abertas))
            for ordem in ordens_abertas['data']['orders']:
                if 'pair_code' in ordem.keys() and str(ativo).upper() == str(ordem['pair_code'][3:]).upper():
                    self.cancelar_ordem(ordem['id'])
        elif self.nome == 'Novadax':            
            ordens_abertas = Novadax(ativo).obterOrdensAbertas()
            if 'data' in ordens_abertas.keys():
                for ordem in ordens_abertas['data']:
                    self.cancelar_ordem(ordem['id'])

    #metodos eclusivos por ordem

    def obter_ordem_por_id(self,ativo,ordem:Ordem):
        ordem = Ordem()
        try:
            if self.nome == 'MercadoBitcoin':
                pass
            elif self.nome == 'BrasilBitcoin':
                response = BrasilBitcoin(ativo).obterOrdemPorId(obterOrdem.id)
                ordem.status = response['data']['status']
                ordem.quantidade_executada = response['data']['executed']
                ordem.preco_executado = response['data']['price']
            elif self.nome == 'BitcoinTrade':
                response = BitcoinTrade(ativo).obterOrdemPorId(obterOrdem.code)
                if 'data' in response.keys():
                    if 'orders' in response['data']:
                        for ativo in response['data']['orders']:
                            if ativo['code'] == obterOrdem.code:
                                ordem.status = ativo['status']
                                ordem.code = ativo['code']
                                ordem.id = ativo['id']
                                ordem.quantidade_executada = ativo['executed_amount']
                                ordem.preco_executado = ativo['unit_price']
                    if ordem.id == 0:
                        response = BitcoinTrade().obterOrdemPorIdStatusExecuted(obterOrdem.code)
                        for ativo in response['data']['orders']: 
                            if ativo['code'] == obterOrdem.code:
                                ordem.status = ativo['status']
                                ordem.code = ativo['code']
                                ordem.id = ativo['id']
                                ordem.quantidade_executada = ativo['executed_amount']
                                ordem.preco_executado = ativo['unit_price']
            elif self.nome == 'Novadax':
                response = Novadax(ativo).obterOrdemPorId(obterOrdem.id)
                if response['message'] == 'Success':
                    ordem.status = response['data']['status'].lower()
                    ordem.quantidade_executada = response['data']['filledAmount']
                    ordem.preco_executado = response['data']['averagePrice']
        except Exception as erro:
            print('erro na classe corretora metodo obter_ordem_por_id. corretora {} - ativo {}'.format(self.nome,ativo))
            raise Exception(erro)
        return ordem

    def enviar_ordem_compra(self,ordem:Ordem,ativo_parte,ativo_contraparte='brl'):
        
        try:
            if self.nome == 'MercadoBitcoin':
                response = MercadoBitcoin(ativo_parte,ativo_contraparte).enviarOrdemCompra(ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado)
                if response['status_code'] == 100: 
                    ordem.id = response['response_data']['order']['order_id']
                    if response['response_data']['order']['status'] == 4:
                        ordem.status = 'filled'
                    ordem.quantidade_executada = float(response['response_data']['order']['executed_quantity'])
                    ordem.preco_executado = float(response['response_data']['order']['executed_price_avg'])
                else:
                    mensagem = '{}: enviar_ordem_compra - {}'.format(self.nome, response['error_message'])
                    print(mensagem)
                    #raise Exception(mensagem)
            elif self.nome == 'BrasilBitcoin':
                response = BrasilBitcoin(ativo_parte,ativo_contraparte).enviarOrdemCompra(ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado)
                if response['success'] == True:
                    ordem.id = response['data']['id']
                    ordem.status = response['data']['status']
                    ordem.quantidade_executada = float(response['data']['amount'])
                    ordem.preco_executado = float(response['data']['price'])
                    i = 0
                    qtd = len(response['data']['fills'])
                    while i < qtd:
                        ordem.quantidade_executada += float(response['data']['fills'][i]['amount'])
                        valor = response['data']['fills'][i]['price'].replace('.','')
                        ordem.preco_executado = float(valor.replace(',','.'))
                        i += 1
                else:
                    mensagem = '{}: enviar_ordem_compra - {}'.format(self.nome, response['message'])
                    print(mensagem)
                    #raise Exception(mensagem)
            elif self.nome == 'BitcoinTrade':
                response = BitcoinTrade(ativo_parte,ativo_contraparte).enviarOrdemCompra(ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado)
                if response['message'] == 'Too Many Requests':
                    time.sleep(1)
                    response = BitcoinTrade(ativo_parte).enviarOrdemCompra(ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado)
                elif 'data' not in response.keys():
                    logging.info(str(response))
                if response['code'] == None or response['code'] == 200:
                    if response['message'] is None:
                        ordem.status = "filled"
                    ordem.code = response['data']['code']
                    ordem.id = response['data']['id']
                    ordem.quantidade_executada = float(response['data']['amount'])
                    ordem.preco_executado = float(response['data']['unit_price'])
                else:
                    mensagem = '{}: enviar_ordem_compra - {}'.format(self.nome, response['message'])
                    print(mensagem)
                    #raise Exception(mensagem)
            elif self.nome == 'Novadax':
                response = Novadax(ativo_parte,ativo_contraparte).enviarOrdemCompra(ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado)
                if response['message'] == "Success":
                    ordem_response = Novadax(ativo_parte).obterOrdemPorId(response['data']['id'])
                    
                    ordem.id = response['data']['id']
                    ordem.status = ordem_response['data']['status'].lower()
                    ordem.quantidade_executada = float(ordem_response['data']['value'])
                    
                    if ordem.status == 'filled':
                        ordem.preco_executado = float(ordem_response['data']['averagePrice'])
                    else:
                        ordem.preco_executado = float(ordem_response['data']['price'])
                    
                    ordem.quantidade_executada = 0 if ordem_response['data']['filledAmount'] is None else float(ordem_response['data']['filledAmount'])                                        
                    ordem.preco_executado = 0 if ordem_response['data']['averagePrice'] is None else float(ordem_response['data']['averagePrice'])
                else:
                    mensagem = '{}: enviar_ordem_compra - {}'.format(self.nome, response['message'])
                    print(mensagem)
        except Exception as erro:
            raise Exception(erro)

        return ordem

    def enviar_ordem_venda(self,ordem:Ordem,ativo_parte,ativo_contraparte='brl'):
        
        mensagem = ''

        try:
            if self.nome == 'MercadoBitcoin':
                response = MercadoBitcoin(ativo_parte,ativo_contraparte).enviarOrdemVenda(ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado)
                if response['status_code'] == 100:            
                    ordem.id = response['response_data']['order']['order_id']
                    if response['response_data']['order']['status'] == 4:
                        ordem.status = 'filled'
                    ordem.quantidade_executada = float(response['response_data']['order']['executed_quantity'])
                    ordem.preco_executado = float(response['response_data']['order']['executed_price_avg'])
                else:
                    mensagem = '{}: enviar_ordem_venda - {}'.format(self.nome, response['error_message'])
                    print(mensagem)
                    #raise Exception(mensagem)

            elif self.nome == 'BrasilBitcoin':
                response = BrasilBitcoin(ativo_parte,ativo_contraparte).enviarOrdemVenda(ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado)
                if response['success'] == True:
                    ordem.id = response['data']['id']
                    ordem.status = response['data']['status']
                    ordem.quantidade_venda = float(response['data']['amount'])
                    ordem.preco_venda = float(response['data']['price'])
                    i = 0
                    qtd = len(response['data']['fills'])
                    while i < qtd:
                        ordem.quantidade_executada += float(response['data']['fills'][i]['amount'])
                        valor = response['data']['fills'][i]['price'].replace('.','')
                        ordem.preco_executado = float(valor.replace(',','.'))
                        i += 1
                else:
                    mensagem = '{}: enviar_ordem_venda - {}'.format(self.nome, response['message'])
                    print(mensagem)
                    #raise Exception(mensagem)
            elif self.nome == 'BitcoinTrade':
                response = BitcoinTrade(ativo_parte,ativo_contraparte).enviarOrdemVenda(ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado)
                if response['message'] == 'Too Many Requests':
                    time.sleep(1)
                    response = BitcoinTrade(ativo_parte,ativo_contraparte).enviarOrdemVenda(ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado)
                elif 'data' not in response.keys():
                    logging.info(str(response))
                if response['code'] == None or response['code'] == 200:
                    if response['message'] is None:
                        ordem.status = "filled"
                    ordem.code = response['data']['code']
                    ordem.id = response['data']['id']
                    ordem.quantidade_executada = float(response['data']['amount'])
                    ordem.preco_executado = float(response['data']['unit_price'])
                else:
                    mensagem = '{}: enviar_ordem_venda - {}'.format(self.nome, response['message'])
                    print(mensagem)
                    #raise Exception(mensagem)
            elif self.nome == 'Novadax':
                if ativo_parte =='xrp':
                    ordem.quantidade_enviada = round(ordem.quantidade_enviada,2)
                response = Novadax(ativo_parte,ativo_contraparte).enviarOrdemVenda(ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado)
                if response['message'] == "Success":
                    ordem_response = Novadax(ativo).obterOrdemPorId(response['data']['id'])
                    
                    ordem.id = response['data']['id']
                    ordem.status = ordem_response['data']['status'].lower()
                    ordem.quantidade_executada = float(ordem_response['data']['amount'])
                    
                    if ordem.status == 'filled':
                        ordem.preco_executado = float(ordem_response['data']['averagePrice'])
                    else:
                        ordem.preco_executado = float(ordem_response['data']['price'])
                    
                    ordem.quantidade_executada = 0 if ordem_response['data']['filledAmount'] is None else float(ordem_response['data']['filledAmount'])                                        
                    ordem.preco_executado = 0 if ordem_response['data']['averagePrice'] is None else float(ordem_response['data']['averagePrice'])
                else:
                    mensagem = '{}: enviar_ordem_venda - {}'.format(self.nome, response['message'])
                    print(mensagem)
        except Exception as erro:
                raise Exception(erro)

        return ordem

    def cancelar_ordem(self,ativo_parte,idOrdem):
        if self.nome == 'MercadoBitcoin':
            pass
        elif self.nome == 'BrasilBitcoin':
            return BrasilBitcoin(ativo_parte).cancelarOrdem(idOrdem)
        elif self.nome == 'BitcoinTrade':
            return BitcoinTrade(ativo_parte).cancelarOrdem(idOrdem)
        elif self.nome == 'Novadax':
            return Novadax(ativo_parte).cancelarOrdem(idOrdem)

    def transferir_crypto(self,ativo,quantidade, destino):      
        '''
        metodo que transfere cripto entre duas corretoras
        argumentos:
        1 - ordem.quantidade_transferencia : quantidade de cripto a transferir
        2 - destino: nome da corretora que vai receber os recursos
        '''        
        if self.nome == 'MercadoBitcoin':
            retorno = MercadoBitcoin(ativo).TransferirCrypto(quantidade,destino)
            return retorno
        elif self.nome == 'BrasilBitcoin':
            retorno = BrasilBitcoin(ativo).TransferirCrypto(quantidade,destino)
            return retorno
        elif self.nome == 'BitcoinTrade':
            retorno = BitcoinTrade(ativo).TransferirCrypto(quantidade,destino)
            return retorno

    #metodo privado
    def __obter_corretagem(self,nome):

        if self.nome == 'MercadoBitcoin':
            corretagem_limitada = 0.003
            corretagem_mercado = 0.007
            
        elif self.nome == 'BrasilBitcoin':
            corretagem_limitada = 0.002
            corretagem_mercado = 0.005
            
        elif self.nome == 'BitcoinTrade':
            corretagem_limitada = 0.0025
            corretagem_mercado = 0.005
            
        elif self.nome == 'Novadax':
            corretagem_limitada = 0.001
            corretagem_mercado = 0.003
            
        return corretagem_limitada, corretagem_mercado

    #metodo privado
    def __obter_status_executado(self,nome):

        if self.nome == 'MercadoBitcoin':
            status_executado = 'filled'
            
        elif self.nome == 'BrasilBitcoin':
            status_executado = 'filled'
            
        elif self.nome == 'BitcoinTrade':
            status_executado = 'executed_completely'
            
        elif self.nome == 'Novadax':
            status_executado = 'FILLED'
            
        return status_executado

