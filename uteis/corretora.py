
import logging
import math
from corretoras.mercadoBitcoin import MercadoBitcoin
from corretoras.brasilBitcoin import BrasilBitcoin
from corretoras.bitcoinTrade import BitcoinTrade
from corretoras.novadaxCorretora import Novadax
from corretoras.bitRecife import BitRecife
from uteis.ordem import Ordem
from uteis.book import Book
from uteis.util import Util

class Corretora:
    
    def __init__(self, nome):
        
        #propriedades qu precisam ser fornecidas
        self.nome = nome 

        #propriedades especificas de cada corretora
        self.corretagem_limitada, self.corretagem_mercado = self.__obter_corretagem(nome)
        self.descricao_status_executado = self.__obter_status_executado(nome)
        
        #propriedades dinamicas
        self.saldo={}
        self.book = Book(nome)
        self.ordem = Ordem()

        #saldo inicia zerado
        lista_de_moedas = Util.obter_lista_de_moedas()+['brl']
        for moeda in lista_de_moedas:
            self.saldo[moeda] = 0

    #metodos exclusivos por ativo

    def atualizar_saldo(self):
        try:
            
            if self.nome == 'MercadoBitcoin':
                self.saldo = MercadoBitcoin().obter_saldo()
            elif self.nome == 'BrasilBitcoin':
                self.saldo = BrasilBitcoin().obter_saldo()
            elif self.nome == 'BitcoinTrade':
                self.saldo = BitcoinTrade().obter_saldo()
            elif self.nome == 'Novadax':
                self.saldo = Novadax().obter_saldo()
            elif self.nome == 'BitRecife':
                self.saldo = BitRecife().obter_saldo()
                
        except Exception as erro:
            logging.error(Util.descricao_erro_padrao().format('atualizar_saldo', self.nome, erro))

    def obter_todas_ordens_abertas(self, ativo='btc'):
        try:
            if self.nome == 'MercadoBitcoin':
                return MercadoBitcoin(ativo).obter_ordens_abertas()
            elif self.nome == 'BrasilBitcoin':
                return BrasilBitcoin(ativo).obter_ordens_abertas()
            elif self.nome == 'BitcoinTrade':
                todas_moedas = Util.obter_lista_de_moedas()
                return BitcoinTrade(ativo).obter_ordens_abertas(todas_moedas)
            elif self.nome == 'Novadax':            
                return Novadax(ativo).obter_ordens_abertas()
        
        except Exception as erro:
            logging.error(Util.descricao_erro_padrao().format('obter_todas_ordens_abertas', self.nome, erro))
        
    def cancelar_todas_ordens(self, ativo='btc', ativo_contraparte='brl'):
        try:
            ordens_abertas = self.obter_todas_ordens_abertas()

            if self.nome == 'MercadoBitcoin':
                MercadoBitcoin().cancelar_todas_ordens(ordens_abertas)
            elif self.nome == 'BrasilBitcoin':
                BrasilBitcoin().cancelar_todas_ordens(ordens_abertas)
            elif self.nome == 'BitcoinTrade':
                BitcoinTrade().cancelar_todas_ordens(ordens_abertas)
            elif self.nome == 'Novadax':            
                Novadax().cancelar_todas_ordens(ordens_abertas)
            elif self.nome == 'BitRecife':            
                BitRecife().cancelar_todas_ordens(ordens_abertas)
        except Exception as erro:
            logging.error(Util.descricao_erro_padrao().format('cancelar_todas_ordens', self.nome, erro))
    #metodos eclusivos por ordem

    def obter_ordem_por_id(self,ativo,obterOrdem:Ordem):
        
        try:
            if self.nome == 'MercadoBitcoin':
                pass
            elif self.nome == 'BrasilBitcoin':
                obterOrdem = BrasilBitcoin().obter_ordem_por_id(obterOrdem)
            elif self.nome == 'BitcoinTrade':
                obterOrdem = BitcoinTrade().obter_ordem_por_id(obterOrdem.code)
            elif self.nome == 'Novadax':
                obterOrdem = Novadax().obter_ordem_por_id(obterOrdem.id)
            elif self.nome == 'BitRecife':
                obterOrdem = BitRecife().obter_ordem_por_id(obterOrdem.id,ativo)
        except Exception as erro:
            logging.error(Util.descricao_erro_padrao().format('obter_ordem_por_id', self.nome, erro))

        return obterOrdem

    def enviar_ordem_compra(self,ordem:Ordem,ativo_parte,ativo_contraparte='brl'):
        
        if ativo_parte =='xrp':
            ordem.quantidade_enviada = math.trunc(ordem.quantidade_enviada*1000)/1000#trunca na terceira
        else:
            ordem.quantidade_enviada = math.trunc(ordem.quantidade_enviada*10000)/10000#trunca na quarta

        try:
            if self.nome == 'MercadoBitcoin':
                ordem,response = MercadoBitcoin(ativo_parte,ativo_contraparte).enviar_ordem_compra(ordem)

                if ordem.status != 'filled' and ordem.status != 'open':
                    if 'error_message' in response.keys():
                        logging.error('{}: enviar_ordem_compra - msg de erro: {}'.format(self.nome, response['error_message']))
                        logging.error('{}: enviar_ordem_compra - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))            
                    else:
                        logging.error('{}: enviar_ordem_compra - status: {} / {} code: {}'.format(self.nome,response['response_data']['order']['status'],ordem.status,response['status_code']))
                        logging.error('{}: enviar_ordem_compra - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))
                    #raise Exception(mensagem)
            
            elif self.nome == 'BrasilBitcoin':
                ordem.tipo_ordem = 'limited' if ordem.tipo_ordem == 'limit' else ordem.tipo_ordem
                ordem,response = BrasilBitcoin(ativo_parte,ativo_contraparte).enviar_ordem_compra(ordem)
                
                if ordem.status not in (self.descricao_status_executado, 'new','partially_filled'):
                    if 'message' in response.keys():
                        logging.error('{}: enviar_ordem_compra - msg de erro: {}'.format(self.nome, response['message']))
                        logging.error('{}: enviar_ordem_compra - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))            
                    else:
                        logging.error('{}: enviar_ordem_compra - status: {}'.format(self.nome,ordem.status))
                        logging.error('{}: enviar_ordem_compra - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))

            elif self.nome == 'BitcoinTrade':
                ordem,response = BitcoinTrade(ativo_parte,ativo_contraparte).enviar_ordem_compra(ordem)

                if ordem.status != self.__obter_status_executado(self.nome) and ordem.status != 'open':
                    if 'message' in response.keys():
                        logging.error('{}: enviar_ordem_venda - msg de erro: {}'.format(self.nome, response['message']))
                        logging.error('{}: enviar_ordem_venda - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))            
                    else:
                        ordemFiltro = Ordem()
                        ordemFiltro.code = response['data']['code']
                        ordemErro = self.obter_ordem_por_id(ativo_parte, ordemFiltro)
                        logging.error('{}: enviar_ordem_venda - status: {} / {} code: {}'.format(self.nome, ordemErro.status, ordem.status, response['message']))
                        logging.error('{}: enviar_ordem_venda - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))
                
            elif self.nome == 'Novadax':
                ordem,response = Novadax(ativo_parte,ativo_contraparte).enviar_ordem_compra(ordem)
            elif self.nome == 'BitRecife':
                ordem,response = BitRecife().enviar_ordem_compra(ordem)
        except Exception as erro:
            logging.error(Util.descricao_erro_padrao().format('enviar_ordem_compra', self.nome, erro))
        
        return ordem

    def enviar_ordem_venda(self,ordem:Ordem,ativo_parte,ativo_contraparte='brl'):
        
        mensagem = ''

        if ativo_parte =='xrp':
            ordem.quantidade_enviada = math.trunc(ordem.quantidade_enviada*1000)/1000#trunca na terceira
        else:
            ordem.quantidade_enviada = math.trunc(ordem.quantidade_enviada*10000)/10000#trunca na quarta

        try:
            if self.nome == 'MercadoBitcoin':
                ordem,response = MercadoBitcoin(ativo_parte,ativo_contraparte).enviar_ordem_venda(ordem)
                
                if ordem.status != self.__obter_status_executado(self.nome) and ordem.status != 'open':
                    if 'error_message' in response.keys():
                        logging.error('{}: enviar_ordem_venda - msg de erro: {}'.format(self.nome, response['error_message']))
                        logging.error('{}: enviar_ordem_venda - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))            
                    else:
                        logging.error('{}: enviar_ordem_venda - status: {} / {} code: {}'.format(self.nome,response['response_data']['order']['status'],ordem.status,response['status_code']))
                        logging.error('{}: enviar_ordem_venda - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))
                
            elif self.nome == 'BrasilBitcoin':
                ordem.tipo_ordem = 'limited' if ordem.tipo_ordem == 'limit' else ordem.tipo_ordem
                ordem,response = BrasilBitcoin(ativo_parte,ativo_contraparte).enviar_ordem_venda(ordem)
                
                if ordem.status not in (self.descricao_status_executado, 'new','partially_filled'):
                    if 'message' in response.keys():
                        logging.error('{}: enviar_ordem_venda - msg de erro: {}'.format(self.nome, response['message']))
                        logging.error('{}: enviar_ordem_venda - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))            
                    else:
                        logging.error('{}: enviar_ordem_venda - status: {}'.format(self.nome,ordem.status))
                        logging.error('{}: enviar_ordem_venda - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))
                

            elif self.nome == 'BitcoinTrade':
                ordem,response = BitcoinTrade(ativo_parte,ativo_contraparte).enviar_ordem_venda(ordem)

                if ordem.status != self.__obter_status_executado(self.nome) and ordem.status != 'open':
                    if 'message' in response.keys():
                        logging.error('{}: enviar_ordem_venda - msg de erro: {}'.format(self.nome, response['message']))
                        logging.error('{}: enviar_ordem_venda - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))            
                    else:
                        ordemFiltro = Ordem()
                        ordemFiltro.code = response['data']['code']
                        ordemErro = self.obter_ordem_por_id(ativo_parte, ordemFiltro)
                        logging.error('{}: enviar_ordem_venda - status: {} / {} code: {}'.format(self.nome, ordemErro.status, ordem.status, response['message']))
                        logging.error('{}: enviar_ordem_venda - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))
                    
            elif self.nome == 'Novadax':
                ordem,response = Novadax(ativo_parte,ativo_contraparte).enviar_ordem_venda(ordem)
            
            elif self.nome == 'BitRecife':
                ordem,response = BitRecife().enviar_ordem_venda(ordem)
        except Exception as erro:
                logging.error(Util.descricao_erro_padrao().format('enviar_ordem_venda', self.nome, erro))
        
        return ordem

    def cancelar_ordem(self,ativo_parte='btc',idOrdem=0):
        try:
            if self.nome == 'MercadoBitcoin':
                return MercadoBitcoin(ativo_parte).cancelar_ordem(idOrdem)
            elif self.nome == 'BrasilBitcoin':
                return BrasilBitcoin(ativo_parte).cancelar_ordem(idOrdem)
            elif self.nome == 'BitcoinTrade':
                return BitcoinTrade(ativo_parte).cancelar_ordem(idOrdem)
            elif self.nome == 'Novadax':
                return Novadax(ativo_parte).cancelar_ordem(idOrdem)
            elif self.nome == 'BitRecife':
                return BitRecife().cancelar_ordem(idOrdem)
                        
        except Exception as erro:
            logging.error(Util.descricao_erro_padrao().format('cancelar_ordem', self.nome, erro))

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
            corretagem_limitada = 0.0015
            corretagem_mercado = 0.007
            
        elif self.nome == 'BrasilBitcoin':
            corretagem_limitada = 0.0018
            corretagem_mercado = 0.0045
            
        elif self.nome == 'BitcoinTrade':
            corretagem_limitada = 0.0025
            corretagem_mercado = 0.005
            
        elif self.nome == 'Novadax':
            corretagem_limitada = 0.001
            corretagem_mercado = 0.003
            
        elif self.nome == 'BitRecife':
            corretagem_limitada = 0.002
            corretagem_mercado = 0.004

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

        elif self.nome == 'BitRecife':
            status_executado = 'ok'
            
        return status_executado

