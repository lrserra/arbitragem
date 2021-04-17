import requests
import hashlib
import hmac
import json
import time
import mimetypes
from http import client
from urllib.parse import urlencode
from uteis.util import Util
from datetime import datetime

class MercadoBitcoin:

    def __init__(self, ativo_parte = Util.CCYBTC(), ativo_contraparte = Util.CCYBRL()):
        self.ativo_parte = ativo_parte
        self.ativo_contraparte = ativo_contraparte
        self.urlMercadoBitcoin = 'https://www.mercadobitcoin.net/api/{}/orderbook/'
        self.tapi = str(int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000))

#---------------- MÉTODOS PRIVADOS ----------------#

    def obterBooks(self):
        return requests.get(url = self.urlMercadoBitcoin.format(self.ativo_parte)).json()

    def __obterSaldo(self):
        tapi_nonce = self.tapi
        params = {
            'tapi_method': 'get_account_info',
            'tapi_nonce': tapi_nonce,
        }
        params = urlencode(params)
        return self.executarRequestMercadoBTC(params)

    def enviarOrdemCompra(self, quantity, tipoOrdem, precoCompra):
        tapi_nonce = self.tapi

        if tipoOrdem == 'market':
            method = 'place_market_buy_order'
        else:
            method = 'place_buy_order'

        params = {
            'tapi_method': method,
            'tapi_nonce': tapi_nonce,
            'coin_pair': '{}{}'.format(self.ativo_contraparte.upper(),self.ativo_parte.upper()),
            'quantity': quantity,
            'limit_price': precoCompra
        }

        params = urlencode(params)
        retorno = self.executarRequestMercadoBTC(params)
        return retorno

    def enviarOrdemVenda(self, quantity, tipoOrdem, precoVenda):
        tapi_nonce = self.tapi

        if tipoOrdem == 'market':
            method = 'place_market_sell_order'
        else:
            method = 'place_sell_order'

        params = {
            'tapi_method': method,
            'tapi_nonce': tapi_nonce,
            'coin_pair': '{}{}'.format(self.ativo_contraparte.upper(), self.ativo_parte.upper()),
            'quantity': quantity,
            'limit_price': precoVenda
        }
        params = urlencode(params)
        retorno = self.executarRequestMercadoBTC(params)
        return retorno

    def TransferirCrypto(self, quantity, destino):
        config = Util.obterCredenciais()
        tx_fee = {'xrp':0.01,'btc':0.0004,'ltc':0.001,'bch':0.001}

        tapi_nonce = self.tapi
        params = {
            'tapi_method': 'withdraw_coin',
            'tapi_nonce': tapi_nonce,
            'coin': str.upper(self.ativo_parte),
            'address': config[destino]["Address"][self.ativo_parte],
            'quantity': quantity,
            'tx_fee': tx_fee[self.ativo_parte]
        }

        if self.ativo_parte=='xrp':
            params['destination_tag']= config[destino]["Address"]["xrp_tag"] 

        params = urlencode(params)
        return self.executarRequestMercadoBTC(params)

    def __cancelarOrdem(self, idOrdem):
        tapi_nonce = self.tapi

        params = {
            'tapi_method': 'cancel_order',
            'tapi_nonce': tapi_nonce,
            'coin_pair': '{}{}'.format(self.ativo_contraparte.upper(), self.ativo_parte.upper()),
            'order_id': idOrdem,
            'async': 'true'
        }

        params = urlencode(params)
        retorno = self.executarRequestMercadoBTC(params)
        return retorno

    def __obterOrdensAbertas(self):
        tapi_nonce = self.tapi

        params = {
            'tapi_method': 'list_orders',
            'tapi_nonce': tapi_nonce,
            'coin_pair': '{}{}'.format(self.ativo_contraparte.upper(), self.ativo_parte.upper()),
            'status_list': '[2]'
        }

        params = urlencode(params)
        retorno = self.executarRequestMercadoBTC(params)
        return retorno

    def executarRequestMercadoBTC(self, params):
        # Constantes
        config = Util.obterCredenciais()
        MB_TAPI_ID = config["MercadoBitcoin"]["Authentication"]
        MB_TAPI_SECRET = config["MercadoBitcoin"]["Secret"]
        REQUEST_HOST = 'www.mercadobitcoin.net'
        REQUEST_PATH = '/tapi/v3/'

        # Gerar MAC
        params_string = REQUEST_PATH + '?' + params
        H = hmac.new(bytes(MB_TAPI_SECRET, encoding='utf8'), digestmod=hashlib.sha512)
        H.update(params_string.encode('utf-8'))
        tapi_mac = H.hexdigest()

        # Gerar cabeçalho da requisição
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'TAPI-ID': MB_TAPI_ID,
            'TAPI-MAC': tapi_mac
        }

        # Realizar requisição POST
        try:
            conn = client.HTTPSConnection(REQUEST_HOST)
            conn.request("POST", REQUEST_PATH, params, headers)

            # Print response data to console
            response = conn.getresponse()
            response = response.read()

            response_json = json.loads(response)
        finally:
            if conn:
                conn.close()

        return response_json


#---------------- MÉTODOS PÚBLICOS ----------------#

    def obter_saldo(self):
        '''
        Método público para obter saldo de todas as moedas conforme as regras das corretoras.
        '''
        saldo = {}
        
        response_json = self.__obterSaldo()
        
        # Retentativa em caso de erro
        while 'error_message' in response_json.keys():
            logging.info('erro ao obters saldo na mercado: {}'.format(response_json['error_message']))
            time.sleep(3)
            response_json = self.__obterSaldo()
        
        # Inicializa todas as moedas
        for moeda in Util.obter_lista_de_moedas():
            saldo[moeda] = 0

        # Obtém o saldo em todas as moedas
        for ativo in response_json['response_data']['balance'].keys():
            if float(response_json['response_data']['balance'][ativo]['total']) > 0:
                saldo[ativo.lower()] = float(response_json['response_data']['balance'][ativo]['total'])
        
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
        return len(retorno_cancel['response_data']['order']) > 0


    def cancelar_todas_ordens(self, ordens_abertas):
        '''
        Cancelar todas as ordens abertas por ativo
        '''
        pass