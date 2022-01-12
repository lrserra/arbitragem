import requests
import json
from uteis.util import Util
from datetime import date, datetime, timedelta

class Coinext:

    def __init__(self, ativo):
        self.ativo = ativo
        self.urlCoinext = 'https://api.coinext.com.br:8443/AP/'       

    def service_url(self, service_name):
        return 'https://api.coinext.com.br:8443/AP/%s' % service_name

    def call_get(self, service_name):
        res = requests.get(self.service_url(service_name))
        return json.loads(res.content)        

    def call_post(self, service_name, payload):
        res = requests.post(self.service_url(service_name), data=json.dumps(payload))
        return json.loads(res.content)

    def obterBooks(self):
        payload = {
            'OMSId': 1,
            'AccountId': 1,
            'InstrumentId': 1
        }

        return self.call_post('GetL2Snapshot', payload)

        #return self.executarRequestCoinext('GET', payload, 'GetL2Snapshot')

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

    def obterOrdensAbertas(self):
        return self.executarRequestBrasilBTC('GET', '','/api/my_orders')

    def obterDadosUsuario(self):
        return self.executarRequestCoinext('POST', '', 'GetUserInfo')

    def obterToken(self):
        config = Util.obterCredenciais()
        res = requests.get(self.urlCoinext+'authenticate', auth=(config['Coinext']['Login'], config['Coinext']['Password']))
        auth = json.loads(res.text.encode('utf8'))

        if auth['Authenticated']:
            return auth['Token']        

    def executarRequestCoinext(self, requestMethod, payload, endpoint):
        headers ={
            'aptoken': self.obterToken(),
            'Content-type': 'application/json'
        }
        # requisição básica com módulo requests
        res = requests.request(requestMethod, self.urlCoinext+endpoint, headers=headers, data=payload)
        return json.loads(res.text.encode('utf8'))