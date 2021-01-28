import requests
import hashlib
import hmac
import json
import time
import mimetypes
from http import client
from urllib.parse import urlencode
from util import Util

class BrasilBitcoin:

    def __init__(self, ativo):
        self.ativo = ativo
        self.urlBrasilBitcoin = 'https://brasilbitcoin.com.br/'
    
    def obterBooks(self):
        return requests.get(url = self.urlBrasilBitcoin + 'API/orderbook/{}'.format(self.ativo)).json()

    def obterSaldo(self):
        return self.executarRequestBrasilBTC('GET', '','/api/get_balance')

    def obterOrdemPorId(self, idOrdem):
        return self.executarRequestBrasilBTC('GET', '', 'api/check_order/{}'.format(idOrdem))

    def enviarOrdemCompra(self, quantity, tipoOrdem, precoCompra):
        # objeto que será postado para o endpoint
        payload = {
            'coin_pair': 'BRL{}'.format(self.ativo),
            'order_type': tipoOrdem,
            'type': 'buy',
            'amount': quantity,
            'price': precoCompra
        }

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        retorno = self.executarRequestBrasilBTC('POST', json.dumps(payload), 'api/create_order')
        return retorno

    def enviarOrdemVenda(self, quantity, tipoOrdem, precoVenda):
        # objeto que será postado para o endpoint
        payload = {
            'coin_pair': 'BRL{}'.format(self.ativo),
            'order_type': tipoOrdem,
            'type': 'sell',
            'amount': quantity,
            'price': precoVenda
        }

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        retorno = self.executarRequestBrasilBTC('POST', json.dumps(payload), 'api/create_order')
        return retorno

    def TransferirCrypto(self, quantity):      
        config = Util.obterCredenciais()
        
        # objeto que será postado para o endpoint
        payload = {
            'coin': self.ativo,
            'amount': quantity,
            'address': config["MercadoBitcoin"]["Address"],
            'priority': 'medium'
        }

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        return self.executarRequestBrasilBTC('POST', json.dumps(payload), '/api/send')

    def cancelarOrdem(self, idOrdem):
        return self.executarRequestBrasilBTC('GET', '', 'api/remove_order/{}'.format(idOrdem))

    def executarRequestBrasilBTC(self, requestMethod, payload, endpoint):
        config = Util.obterCredenciais()
        
        headers ={
            'Authentication': config["BrasilBitcoin"]["Authentication"],
            'Content-type': 'application/json'
        }
        # requisição básica com módulo requests
        res = requests.request(requestMethod, self.urlBrasilBitcoin+endpoint, headers=headers, data=payload)
        return json.loads(res.text.encode('utf8'))