import requests
import hashlib
import hmac
import json
import time
import mimetypes
from http import client
from urllib.parse import urlencode
from uteis.util import Util
from datetime import date, datetime, timedelta
from uteis.ordem import Ordem

class BitcoinTrade:

    def __init__(self, ativo_parte = Util.CCYBTC(),ativo_contraparte = Util.CCYBRL()):
        self.ativo_parte = ativo_parte
        self.ativo_contraparte = ativo_contraparte
        self.urlBitcoinTrade = 'https://api.bitcointrade.com.br/'
    
#---------------- MÉTODOS PRIVADOS ----------------#

    def obterBooks(self):
        return requests.get(url = self.urlBitcoinTrade + 'v3/public/{}{}/orders?limit=50'.format(self.ativo_contraparte.upper(),self.ativo_parte.upper())).json()

    def __obterSaldo(self):
        return self.__executarRequestBTCTrade('GET', '','v3/wallets/balance')

    def obterOrdemPorIdStatusExecuted(self, idOrdem):
        # objeto que será postado para o endpoint
        return self.__executarRequestBTCTrade('GET', '', 'v3/market/user_orders/list?status=executed_completely&start_date={}&end_date={}&pair={}{}'.format(date.today()-timedelta(days=1), date.today(),self.ativo_contraparte.upper(),self.ativo_parte.upper()))

    def __obterOrdemPorId(self, idOrdem):
        # objeto que será postado para o endpoint
        return self.__executarRequestBTCTrade('GET', '', 'v3/market/user_orders/list?start_date={}&end_date={}&pair={}{}'.format(date.today()-timedelta(days=1), date.today(),self.ativo_contraparte.upper(),self.ativo_parte.upper()))

    def __enviarOrdemCompra(self, quantity, tipoOrdem, precoCompra):
        # objeto que será postado para o endpoint
        payload = {
            'pair': '{}{}'.format(self.ativo_contraparte.upper(),self.ativo_parte.upper()),
            'subtype': tipoOrdem,
            'type': 'buy',
            'amount': quantity,
            'unit_price': precoCompra
        }

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        retorno = self.__executarRequestBTCTrade('POST', json.dumps(payload), 'v3/market/create_order')
        return retorno

    def __enviarOrdemVenda(self, quantity, tipoOrdem, precoVenda):
        # objeto que será postado para o endpoint
        payload = {
            'pair': '{}{}'.format(self.ativo_contraparte.upper(),self.ativo_parte.upper()),
            'subtype': tipoOrdem,
            'type': 'sell',
            'amount': quantity,
            'unit_price': precoVenda
        }

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        retorno = self.__executarRequestBTCTrade('POST', json.dumps(payload), 'v3/market/create_order')
        return retorno

    def TransferirCrypto(self, quantity,destino):      
        config = Util.obterCredenciais()
        api = ''
        if self.ativo_parte == 'btc':
            api = 'v3/{}/withdraw'.format('bitcoin')
        elif self.ativo_parte == 'eth':
            api = 'v3/{}/withdraw'.format('ethereum')
        elif self.ativo_parte == 'xrp':
            api = 'v3/{}/withdraw'.format('ripple')
        elif self.ativo_parte == 'ltc':
            api = 'v3/{}/withdraw'.format('litecoin')

        # objeto que será postado para o endpoint
        payload = {
            'amount': quantity,
            'destination': config[destino]["Address"][self.ativo_parte],
            "fee_type": "fast"
        }
        
        if self.ativo_parte=='xrp':
            payload['tag'] = config[destino]["Address"]["xrp_tag"] 

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        return self.__executarRequestBTCTrade('POST', json.dumps(payload), api)

    def __cancelarOrdem(self, idOrdem):
        
        payload = {
            "id": idOrdem
        }
        
        return self.__executarRequestBTCTrade('DELETE', json.dumps(payload), 'v3/market/user_orders/')

    def __obterOrdensAbertas(self):
        # objeto que será postado para o endpoint
        return self.executarRequestBTCTrade('GET', '', 'v3/market/user_orders/list?start_date={}&end_date={}&pair={}{}'.format(date.today()-timedelta(days=1), date.today(), self.ativo_contraparte.upper(), self.ativo_parte.upper()))

    def __executarRequestBTCTrade(self, requestMethod, payload, endpoint):
        config = Util.obterCredenciais()
        
        headers ={
            'Content-type': 'application/json',
            'x-api-key': config["BitcoinTrade"]["Authentication"]
        }
        
        res = requests.request(requestMethod, self.urlBitcoinTrade+endpoint, headers=headers, data=payload)
        
        return json.loads(res.text.encode('utf8'))


#---------------- MÉTODOS PÚBLICOS ----------------#    

    def obter_saldo(self):
        '''
        Método público para obter saldo de todas as moedas conforme as regras das corretoras.
        '''
        saldo = {}
        
        response_json = self.__obterSaldo()

        while 'data' not in response_json.keys():
            time.sleep(3)
            response_json = self.__obterSaldo()

        # Inicializa todas as moedas
        lista_de_moedas = Util.obter_lista_de_moedas()+['brl']
        for moeda in lista_de_moedas:
            saldo[moeda] = 0

        for item in response_json['data']:
            saldo[item['currency_code'].lower()] = float(item['available_amount']) + float(item['locked_amount'])
        
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
        retorno_cancel = self.__cancelarOrdem(idOrdem)
        return retorno_cancel['message'] is None     

    def cancelar_todas_ordens(self, ordens_abertas):
        '''
        Cancelar todas as ordens abertas por ativo
        '''
        for moeda in self.saldo.keys():
            if ordens_abertas['message'] == 'Too Many Requests':
                    time.sleep(1)
            elif 'data' not in ordens_abertas.keys():
                    logging.info(str(ordens_abertas))
            
            for ordem in ordens_abertas['data']['orders']:
                    if 'pair_code' in ordem.keys():
                        self.cancelar_ordem(moeda,ordem['id'])
    
    def obter_ordem_por_id(self, filterOrdem):
        ordem = Ordem()
        response = self.__obterOrdemPorId(filterOrdem.code)
        if 'data' in response.keys():
            if 'orders' in response['data']:
                for ativo in response['data']['orders']:
                    if ativo['code'] == filterOrdem.code:
                        ordem.status = ativo['status']
                        ordem.code = ativo['code']
                        ordem.id = ativo['id']
                        ordem.quantidade_executada = ativo['executed_amount']
                        ordem.preco_executado = ativo['unit_price']
            if ordem.id == 0:
                response = BitcoinTrade(ativo).obterOrdemPorIdStatusExecuted(filterOrdem.code)
                for ativo in response['data']['orders']: 
                    if ativo['code'] == filterOrdem.code:
                        ordem.status = ativo['status']
                        ordem.code = ativo['code']
                        ordem.id = ativo['id']
                        ordem.quantidade_executada = ativo['executed_amount']
                        ordem.preco_executado = ativo['unit_price']
        return ordem
    
    def enviar_compra(self, ordemCompra):
        ordem = Ordem()
        response = self.__enviarOrdemCompra(ordemCompra.quantidade_enviada, ordemCompra.tipo_ordem, ordemCompra.preco_enviado)
        if response['message'] != None:
            logging.warning(response['message'])
            time.sleep(1)
            response = self.__enviarOrdemCompra.enviarOrdemCompra(ordemCompra.quantidade_enviada, ordemCompra.tipo_ordem, ordemCompra.preco_enviado)
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
        return ordem

    def enviar_ordem_venda(self, ordemVenda):
        ordem = Ordem()
        response = self.__enviarOrdemVenda(ordemVenda.quantidade_enviada, ordemVenda.tipo_ordem, ordemVenda.preco_enviado)
        if response['message'] != None:
            logging.warning(response['message'])
            time.sleep(1)
            response = self.__enviarOrdemVenda(ordemVenda.quantidade_enviada, ordemVenda.tipo_ordem, ordemVenda.preco_enviado)
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
        return ordem