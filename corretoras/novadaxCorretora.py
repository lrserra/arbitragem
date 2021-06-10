import requests
import novadax
import json
import time
from uteis.util import Util
from uteis.ordem import Ordem
import math

class Novadax:

    def __init__(self, ativo_parte = Util.CCYBTC(),ativo_contraparte = Util.CCYBRL()):
        self.ativo_parte = ativo_parte
        self.ativo_contraparte = ativo_contraparte
        self.urlNovadax = 'https://api.novadax.com/'
        self.nome_corretora = 'Novadax'
    
#---------------- MÉTODOS PRIVADOS ----------------#

    def obterBooks(self):
        nova_client = novadax.RequestClient()
        return nova_client.get_depth('{}_{}'.format(self.ativo_parte.upper(),self.ativo_contraparte.upper()))

    def __obterSaldo(self):
        config = Util.obterCredenciais()
        nova_client = novadax.RequestClient(config[self.nome_corretora]["Authentication"], config[self.nome_corretora]["Secret"])
        return nova_client.get_account_balance()

    def __obterOrdemPorId(self, idOrdem):
        config = Util.obterCredenciais()
        nova_client = novadax.RequestClient(config[self.nome_corretora]["Authentication"], config[self.nome_corretora]["Secret"])
        return nova_client.get_order(idOrdem)

    def __enviarOrdemCompra(self, quantity, tipoOrdem, precoCompra):
        # objeto que será postado para o endpoint
        config = Util.obterCredenciais()
        nova_client = novadax.RequestClient(config[self.nome_corretora]["Authentication"], config[self.nome_corretora]["Secret"])
        if tipoOrdem.upper() == 'MARKET':
            return nova_client.create_order('{}_{}'.format(self.ativo_parte.upper(),self.ativo_contraparte.upper()), tipoOrdem.upper(), 'BUY', value=round((quantity*precoCompra),2))
        elif tipoOrdem.upper() == 'LIMIT':
            return nova_client.create_order('{}_{}'.format(self.ativo_parte.upper(),self.ativo_contraparte.upper()), tipoOrdem.upper(), 'BUY', precoCompra, quantity)

    def __enviarOrdemVenda(self, quantity, tipoOrdem, precoVenda):
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

    def __cancelarOrdem(self, idOrdem):
        config = Util.obterCredenciais()
        nova_client = novadax.RequestClient(config[self.nome_corretora]["Authentication"], config[self.nome_corretora]["Secret"])
        return nova_client.cancle_order(idOrdem)

    def __obterOrdensAbertas(self):
        config = Util.obterCredenciais()
        nova_client = novadax.RequestClient(config[self.nome_corretora]["Authentication"], config[self.nome_corretora]["Secret"])
        return nova_client.list_orders('{}_{}'.format(self.ativo_parte.upper(),self.ativo_contraparte.upper()), 'UNFINISHED')


#---------------- MÉTODOS PÚBLICOS ----------------#

    def obter_saldo(self):
        '''
        Método público para obter saldo de todas as moedas conforme as regras das corretoras.
        '''
        saldo = {}
        
        # Inicializa todas as moedas
        for moeda in Util.obter_lista_de_moedas():
            saldo[moeda] = 0

        response_json = self.__obterSaldo()
        for item in response_json['data']:
            if float(item['balance'])>0:
                saldo[item['currency'].lower()] = float(item['balance'])
    
        return saldo

    def obter_ordens_abertas(self):
        '''
        Obtém todas as ordens abertas
        '''
        return self.__obterOrdensAbertas()

    def cancelar_ordem(self, idOrdem):
        '''
        Cancelar unitariamente uma ordem
        '''
        self.__cancelarOrdem(idOrdem) 
        return True

    def cancelar_todas_ordens(self, ordens_abertas):
        '''
        Cancelar todas as ordens abertas por ativo
        '''
        if 'data' in ordens_abertas.keys():
            for ordem in ordens_abertas['data']:
                self.cancelar_ordem(ativo,ordem['id'])

    def obter_ordem_por_id(self, filterOrdem):
        response = self.__obterOrdemPorId(filterOrdem.id)
        if response['message'] == 'Success':
            ordem.status = response['data']['status'].lower()
            ordem.quantidade_executada = response['data']['filledAmount']
            ordem.preco_executado = response['data']['averagePrice']
        return ordem

    def enviar_ordem_compra(self, ordemCompra):

        ordem = ordemCompra
        if ordem.ativo =='xrp':
            ordem.quantidade_enviada = round(math.trunc(ordem.quantidade_enviada*100)/100,2) #trunca na segunda
        else:
            ordem.quantidade_enviada = round(math.trunc(ordem.quantidade_enviada*10000)/10000,2)#trunca na quarta
        
        
        response = self.__enviarOrdemCompra(ordemCompra.quantidade_enviada, ordemCompra.tipo_ordem, ordemCompra.preco_enviado)
                
        if response['message'] == "Success":
            ordem_response = self.__obterOrdemPorId(response['data']['id'])
            
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
            #print(mensagem)
        return ordem,response

    def enviar_ordem_venda(self, ordemVenda):
        ordem = ordemVenda
        if ordem.ativo =='xrp':
            ordem.quantidade_enviada = round(math.trunc(ordem.quantidade_enviada*100)/100,2)#trunca na segunda
        else:
            ordem.quantidade_enviada = round(math.trunc(ordem.quantidade_enviada*10000)/10000,2)#trunca na quarta
        
        
        
        response = self.__enviarOrdemVenda(ordemVenda.quantidade_enviada, ordemVenda.tipo_ordem, ordemVenda.preco_enviado)
        if response['message'] == "Success":
            ordem_response = self.__obterOrdemPorId(response['data']['id'])
            
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
            #print(mensagem)
        return ordem,response