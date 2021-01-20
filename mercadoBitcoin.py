import requests
import hashlib
import hmac
import json
import time
import mimetypes
from http import client
from urllib.parse import urlencode
from util import Util

class MercadoBitcoin:

    def __init__(self, ativo):
        self.ativo = ativo
        self.urlMercadoBitcoin = 'https://www.mercadobitcoin.net/api/{}/orderbook/'

    def obterBooks(self):
        return requests.get(url = self.urlMercadoBitcoin.format(self.ativo)).json()

    def obterSaldo(self):
        tapi_nonce = str(int(time.time()))
        params = {
            'tapi_method': 'get_account_info',
            'tapi_nonce': tapi_nonce,
        }
        params = urlencode(params)
        return self.executarRequestMercadoBTC(params)

    def enviarOrdemCompra(self, quantity, tipoOrdem, precoCompra):
        tapi_nonce = str(int(time.time()))
        params = {
            'tapi_method': 'place_{}_buy_order'.format(tipoOrdem),
            'tapi_nonce': tapi_nonce,
            'coin_pair': 'BRL{}'.format(str.upper(self.ativo)),
            'quantity': quantity,
            'limit_price': precoCompra
        }

        params = urlencode(params)
        return self.executarRequestMercadoBTC(params)

    def enviarOrdemVenda(self, quantity, tipoOrdem, precoVenda):
        tapi_nonce = str(int(time.time()))
        params = {
            'tapi_method': 'place_{}_sell_order'.format(tipoOrdem),
            'tapi_nonce': tapi_nonce,
            'coin_pair': 'BRL{}'.format(str.upper(self.ativo)),
            'quantity': quantity,
            'limit_price': precoVenda
        }
        params = urlencode(params)
        return self.executarRequestMercadoBTC(params)

    def TransferirCrypto(self, quantity):
        config = Util.obterCredenciais()
        
        tapi_nonce = str(int(time.time()))
        params = {
            'tapi_method': 'withdraw_coin',
            'tapi_nonce': tapi_nonce,
            'coin': str.upper(self.ativo),
            'address': config["BrasilBitcoin"]["Address"],
            'quantity': quantity,
            'tx_fee': '0.0005'
        }
        params = urlencode(params)
        return self.executarRequestMercadoBTC(params)

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