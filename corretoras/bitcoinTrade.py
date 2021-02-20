import requests
import hashlib
import hmac
import json
import time
import mimetypes
from http import client
from urllib.parse import urlencode
from util import Util
from datetime import date, datetime, timedelta

class BitcoinTrade:

    def __init__(self, ativo_parte,ativo_contraparte='brl'):
        self.ativo_parte = ativo_parte
        self.ativo_contraparte = ativo_contraparte
        self.urlBitcoinTrade = 'https://api.bitcointrade.com.br/'
    
    def obterBooks(self):
        return requests.get(url = self.urlBitcoinTrade + 'v3/public/{}{}/orders?limit=50'.format(self.ativo_contraparte.upper(),self.ativo_parte.upper())).json()

    def obterSaldo(self):
        return self.executarRequestBTCTrade('GET', '','v3/wallets/balance')

    def obterOrdemPorIdStatusExecuted(self, idOrdem):
        # objeto que será postado para o endpoint
        return self.executarRequestBTCTrade('GET', '', 'v3/market/user_orders/list?status=executed_completely&start_date={}&end_date={}&pair={}{}'.format(date.today()-timedelta(days=1), date.today(),self.ativo_contraparte.upper(),self.ativo_parte.upper()))

    def obterOrdemPorId(self, idOrdem):
        # objeto que será postado para o endpoint
        return self.executarRequestBTCTrade('GET', '', 'v3/market/user_orders/list?start_date={}&end_date={}&pair={}{}'.format(date.today()-timedelta(days=1), date.today(),self.ativo_contraparte.upper(),self.ativo_parte.upper()))

    def enviarOrdemCompra(self, quantity, tipoOrdem, precoCompra):
        # objeto que será postado para o endpoint
        payload = {
            'pair': '{}{}'.format(self.ativo_contraparte.upper(),self.ativo_parte.upper()),
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
            'pair': '{}{}'.format(self.ativo_contraparte.upper(),self.ativo_parte.upper()),
            'subtype': tipoOrdem,
            'type': 'sell',
            'amount': quantity,
            'unit_price': precoVenda
        }

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        retorno = self.executarRequestBTCTrade('POST', json.dumps(payload), 'v3/market/create_order')
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
        return self.executarRequestBTCTrade('POST', json.dumps(payload), api)

    def cancelarOrdem(self, idOrdem):
        
        payload = {
            "id": idOrdem
        }
        
        return self.executarRequestBTCTrade('DELETE', json.dumps(payload), 'v3/market/user_orders/')

    def obterOrdensAbertas(self):
        # objeto que será postado para o endpoint
        return self.executarRequestBTCTrade('GET', '', 'v3/market/user_orders/list?start_date={}&end_date={}&pair={}{}'.format(date.today()-timedelta(days=1), date.today(),self.ativo_contraparte.upper(),self.ativo_parte.upper()))

    def executarRequestBTCTrade(self, requestMethod, payload, endpoint):
        config = Util.obterCredenciais()
        
        headers ={
            'Content-type': 'application/json',
            'x-api-key': config["BitcoinTrade"]["Authentication"]
        }
        
        res = requests.request(requestMethod, self.urlBitcoinTrade+endpoint, headers=headers, data=payload)
        
        return json.loads(res.text.encode('utf8'))