import logging
import requests
import json
import time
from binance.spot import Spot
from urllib.parse import urlencode
from uteis.util import Util
from uteis.ordem import Ordem

class Binance:

    def __init__(self, ativo_parte = Util.CCYBTC(),ativo_contraparte = Util.CCYBRL()):
        self.ativo_parte = ativo_parte if ativo_parte !='usdc' else 'usdt'
        self.ativo_contraparte = ativo_contraparte
        self.urlBinance = 'https://api.binance.com/'
        self.nome_corretora = 'Binance'
        self.recvWindow = 60*1000
        
        config = Util.obterCredenciais()
        self.client = Spot(config[self.nome_corretora]["Authentication"], config[self.nome_corretora]["Secret"])

#---------------- MÉTODOS PRIVADOS ----------------#
    
    def obterBooks(self):
        if self.ativo_parte in ['bch','usdc']:
            res = {'asks':[[1000,1000],[1000,1000]],'bids':[[1000,1000],[1000,1000]]}
        else:
            try:
                res = self.client.depth('{}{}'.format(self.ativo_parte.upper(), self.ativo_contraparte.upper()))
                if len(res['asks'])<2:
                    logging.error('a chamada de book da Binance nao retornou nada')
                    logging.error('vai aguardar 30 segundos e tentar novamente')
                    time.sleep(30)
                    res = self.client.depth('{}{}'.format(self.ativo_parte.upper(), self.ativo_contraparte.upper()))
            
            except Exception as err:
                logging.error('a chamada de book da Binance falhou com o erro:')
                logging.error(err)
                logging.error('vai aguardar 30 segundos e tentar novamente')
                time.sleep(30)
                res = self.client.depth('{}{}'.format(self.ativo_parte.upper(), self.ativo_contraparte.upper()))
          

        return res

    def __obterSaldo(self):
        res = self.client.account(recvWindow=self.recvWindow)
        return res

    def __obterOrdemPorId(self, idOrdem):
        res = self.client.get_order('{}{}'.format(self.ativo_parte.upper(), self.ativo_contraparte.upper()), orderId=idOrdem,recvWindow=self.recvWindow)
        return res

    def __enviarOrdemCompra(self, quantity, tipoOrdem, precoCompra):
        # objeto que será postado para o endpoint

        symbol = '{}{}'.format(self.ativo_parte.upper(),self.ativo_contraparte.upper())
        type = tipoOrdem.upper()
        side = 'BUY'

        # "timeInForce": "GTC" - só é obrigatório na ordem limitada
        # Ordem a mercado não precisa informar o preço
        if type == 'LIMIT':
            payload = {
                'symbol': symbol,
                'side': side,
                'type': type,
                "timeInForce": "GTC",
                'quantity': quantity,
                'price': precoCompra
            }
        else:
            payload = {
                'symbol': symbol,
                'side': side,
                'type': type,
                'quantity': quantity
            }

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        #res = self.client.new_order(symbol, side, type, payload)
        res = self.client.new_order(**payload,recvWindow=self.recvWindow)
        return res

    def __enviarOrdemVenda(self, quantity, tipoOrdem, precoVenda):
        # objeto que será postado para o endpoint

        symbol = '{}{}'.format(self.ativo_parte.upper(),self.ativo_contraparte.upper())
        type = tipoOrdem.upper()
        side = 'SELL'

        if type == 'LIMIT':
            payload = {
                'symbol': symbol,
                'side': side,
                'type': type,
                "timeInForce": "GTC",
                'quantity': quantity,
                'price': precoVenda
            }
        else:
            payload = {
                'symbol': symbol,
                'side': side,
                'type': type,
                'quantity': quantity
            }

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        #res = self.client.new_order(symbol, side, type, payload)
        res = self.client.new_order(**payload,recvWindow=self.recvWindow)
        return res

    def __cancelarOrdem(self, idOrdem):
        res = self.client.cancel_order('{}{}'.format(self.ativo_parte.upper(), self.ativo_contraparte.upper()), orderId=idOrdem)
        return res

    def __obterOrdensAbertas(self):
        res = self.client.get_open_orders('{}{}'.format(self.ativo_parte.upper(), self.ativo_contraparte.upper()))
        return res

#---------------- MÉTODOS PÚBLICOS ----------------#    

    def obter_saldo(self):
        '''
        Método público para obter saldo de todas as moedas conforme as regras das corretoras.
        '''
        saldo = {}

        lista_de_moedas = Util.obter_lista_de_moedas()+['brl']
        for moeda in lista_de_moedas:
            saldo[moeda] = 0
        
        response_json = self.__obterSaldo()

        for item in response_json['balances']:
            if float(item['free'])>0:
                for ccy in saldo:
                    if ccy.lower() == item['asset'].lower():
                        saldo[ccy] = float(item['free'])
        
        return saldo

    def obter_ordens_abertas(self):
        '''
        Obtém todas as ordens abertas
        '''
        retorno = self.__obterOrdensAbertas()
        if len(retorno)==0 or retorno is None:
            retorno=[]
        return retorno

    def cancelar_ordem(self, idOrdem):
        '''
        Cancelar unitariamente uma ordem
        '''
        retorno_cancel = self.__cancelarOrdem(idOrdem)

        if retorno_cancel['status'] != 'CANCELED':
            logging.info('Erro no cancelamento da Brasil: {}'.format(retorno_cancel))

        # Retorna a descrição CANCELED
        return retorno_cancel['status']

    def cancelar_todas_ordens(self, ordens_abertas):
        '''
        Cancelar todas as ordens abertas por ativo
        '''
        for ordem in ordens_abertas:
            self.cancelar_ordem(ordem['id'])

    def obter_ordem_por_id(self, ordem:Ordem):
        
        response = self.__obterOrdemPorId(ordem.id)
        ordem.status = response['status']
        ordem.quantidade_executada = float(response['executedQty'])
        ordem.quantidade_enviada = float(response['origQty'])
        ordem.preco_executado = float(response['price'])
        ordem.preco_enviado = ordem.preco_executado
        ordem.direcao = response['side']
        return ordem

    def enviar_ordem_compra(self, ordemCompra):
        ordem = ordemCompra
        response = self.__enviarOrdemCompra(ordemCompra.quantidade_enviada, ordemCompra.tipo_ordem.upper(), ordemCompra.preco_enviado)
                
        if response['orderId'] > 0:
            ordem.id = response['orderId']
            ordem.status = response['status']
            ordem.quantidade_executada = 0
            ordem.preco_executado = 0
            i = 0
            qtd = len(response['fills']) #quantidade de execuções parciais
            while i < qtd:
                quantidade_parcial = float(response['fills'][i]['qty'])
                ordem.quantidade_executada += quantidade_parcial

                preco_executado_parcial = float(response['fills'][i]['price'])

                ordem.preco_executado += preco_executado_parcial*quantidade_parcial
                i += 1
            if ordem.quantidade_executada==0: #para evitar divisão por zero
                ordem.preco_executado = ordem.preco_enviado 
            else:    
                ordem.preco_executado = ordem.preco_executado/ordem.quantidade_executada #preço medio ponderado
        else:
            mensagem = '{}: enviar_ordem_compra - {}'.format('Binance', response['message'])
            print(mensagem)
        return ordem,response

    def enviar_ordem_venda(self, ordemVenda):
        ordem = ordemVenda
        response = self.__enviarOrdemVenda(ordemVenda.quantidade_enviada, ordemVenda.tipo_ordem.upper(), ordemVenda.preco_enviado)

        if response['orderId'] > 0:
            ordem.id = response['orderId']
            ordem.status = response['status']
            ordem.quantidade_executada = 0
            ordem.preco_executado = 0
            i = 0
            qtd = len(response['fills']) #quantidade de execuções parciais
            while i < qtd:
                quantidade_parcial = float(response['fills'][i]['qty'])
                ordem.quantidade_executada += quantidade_parcial

                preco_executado_parcial = float(response['fills'][i]['price'])

                ordem.preco_executado += preco_executado_parcial*quantidade_parcial
                i += 1
            if ordem.quantidade_executada==0: #para evitar divisão por zero
                ordem.preco_executado = ordem.preco_enviado 
            else:    
                ordem.preco_executado = ordem.preco_executado/ordem.quantidade_executada #preço medio ponderado
        else:
            mensagem = '{}: enviar_ordem_venda - {}'.format('Binance', response['message'])
            print(mensagem)
        return ordem,response

