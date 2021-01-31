import requests
import hashlib
import hmac
import json
import time
import mimetypes
from http import client
from urllib.parse import urlencode
from util import Util

class BitcoinTrade:

    def __init__(self, ativo):
        self.ativo = ativo
        self.urlBitcoinTrade = 'https://api.bitcointrade.com.br/'
    
    def obterBooks(self):
        return requests.get(url = self.urlBrasilBitcoin + '/v3/public/BRL{}}/orders?limit=50'.format(self.ativo)).json()

    def obterSaldo(self):
        return self.executarRequestBTCTrade('GET', '','v3/wallets/balance')

    def obterOrdemPorId(self, idOrdem):
        # objeto que será postado para o endpoint
        payload = {
            'pair': 'BRL{}'.format(self.ativo),
            'id': tipoOrdem
        }
        return self.executarRequestBTCTrade('GET', payload, 'market/user_orders/list')

    def enviarOrdemCompra(self, quantity, tipoOrdem, precoCompra):
        # objeto que será postado para o endpoint
        payload = {
            'pair': 'BRL{}'.format(self.ativo),
            'subtype': tipoOrdem,
            'type': 'buy',
            'amount': quantity,
            'unit_price': precoCompra
        }

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        retorno = self.executarRequestBTCTrade('POST', json.dumps(payload), 'v3/market/create_order')
        return retorno

    def enviarOrdemVenda(self, quantity, tipoOrdem, precoVenda):
        # objeto que será postado para o endpoint
        payload = {
            'pair': 'BRL{}'.format(self.ativo),
            'subtype': tipoOrdem,
            'type': 'sell',
            'amount': quantity,
            'unitprice': precoVenda
        }

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        retorno = self.executarRequestBTCTrade('POST', json.dumps(payload), 'v3/market/create_order')
        return retorno

    def TransferirCrypto(self, quantity):      
        config = Util.obterCredenciais()
        api = ''
        if self.ativo == 'btc':
            api = 'v3/{}/withdraw'.format('bitcoin')
        elif self.ativo == 'eth':
            api = 'v3/{}/withdraw'.format('ethereum')
        elif self.ativo == 'xrp':
            api = 'v3/{}/withdraw'.format('ripple')
        elif self.ativo == 'ltc':
            api = 'v3/{}/withdraw'.format('litecoin')

        # objeto que será postado para o endpoint
        payload = {
            'amount': quantity,
            'destination': config["MercadoBitcoin"]["Address"],
            "fee_type": "regular"
        }

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        return self.executarRequestBTCTrade('POST', json.dumps(payload), api)

    def cancelarOrdem(self, idOrdem):
        payload = {
            'id': idOrdem
        }
        return self.executarRequestBTCTrade('DELETE', payload, 'v3/market/user_orders/')

    def obterOrdensAbertas(self):
        # objeto que será postado para o endpoint
        payload = {
            'pair': 'BRL{}'.format(self.ativo),
            'status': 'waiting'
        }
        return self.executarRequestBTCTrade('GET', payload, 'market/user_orders/list')

    def executarRequestBTCTrade(self, requestMethod, payload, endpoint):
        config = Util.obterCredenciais()
        
        headers ={
            'x-api-key': config["BitcoinTrade"]["Authentication"],
            'Content-type': 'application/json'
        }
        # requisição básica com módulo requests
        res = requests.request(requestMethod, self.urlBitcoinTrade+endpoint, headers=headers, data=payload)
        return json.loads(res.text.encode('utf8'))