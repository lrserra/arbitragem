import requests
import novadax
import json
import time
from util import Util

class Novadax:

    def __init__(self, ativo):
        self.ativo = ativo
        self.urlNovadax = 'https://api.novadax.com/'
    
    def obterBooks(self):
        nova_client = novadax.RequestClient()
        return nova_client.get_depth('{}_BRL'.format(self.ativo.upper()))

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

    def TransferirCrypto(self, quantity, destino):      
        config = Util.obterCredenciais()
        
        # objeto que será postado para o endpoint
        payload = {
            'coin': self.ativo,
            'amount': quantity,
            'address': config[destino]["Address"][self.ativo],
            'priority': 'high'
        }
        
        if self.ativo=='xrp':
            payload['tag'] = config[destino]["Address"]["xrp_tag"]         

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        return self.executarRequestBrasilBTC('POST', json.dumps(payload), '/api/send')

    def cancelarOrdem(self, idOrdem):
        return self.executarRequestBrasilBTC('GET', '', 'api/remove_order/{}'.format(idOrdem))

    def obterOrdensAbertas(self):
        return self.executarRequestBrasilBTC('GET', '','/api/my_orders')

    def executarRequestBrasilBTC(self, requestMethod, payload, endpoint):
        config = Util.obterCredenciais()
        
        headers ={
            'Authentication': config["BrasilBitcoin"]["Authentication"],
            'Content-type': 'application/json'
        }
        # requisição básica com módulo requests
        res = requests.request(requestMethod, self.urlBrasilBitcoin+endpoint, headers=headers, data=payload)
        return json.loads(res.text.encode('utf8'))