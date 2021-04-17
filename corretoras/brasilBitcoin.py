import requests
import hashlib
import hmac
import json
import time
import mimetypes
from http import client
from urllib.parse import urlencode
from uteis.util import Util

class BrasilBitcoin:

    def __init__(self, ativo_parte = Util.CCYBTC(),ativo_contraparte = Util.CCYBRL()):
        self.ativo_parte = ativo_parte
        self.ativo_contraparte = ativo_contraparte
        self.urlBrasilBitcoin = 'https://brasilbitcoin.com.br/'

#---------------- MÉTODOS PRIVADOS ----------------#
    
    def obterBooks(self):
        return requests.get(url = self.urlBrasilBitcoin + 'API/orderbook/{}'.format(self.ativo_parte)).json()

    def __obterSaldo(self):
        retorno = self.executarRequestBrasilBTC('GET', '','/api/get_balance')
        return retorno

    def obterOrdemPorId(self, idOrdem):
        return self.executarRequestBrasilBTC('GET', '', 'api/check_order/{}'.format(idOrdem))

    def enviarOrdemCompra(self, quantity, tipoOrdem, precoCompra):
        # objeto que será postado para o endpoint
        payload = {
            'coin_pair': '{}{}'.format(self.ativo_contraparte.upper(),self.ativo_parte.upper()),
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
            'coin_pair': '{}{}'.format(self.ativo_contraparte.upper(),self.ativo_parte.upper()),
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
            'coin': self.ativo_parte,
            'amount': quantity,
            'address': config[destino]["Address"][self.ativo_parte],
            'priority': 'high'
        }
        
        if self.ativo_parte=='xrp':
            payload['tag'] = config[destino]["Address"]["xrp_tag"]         

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        return self.executarRequestBrasilBTC('POST', json.dumps(payload), '/api/send')

    def __cancelarOrdem(self, idOrdem):
        retorno = self.executarRequestBrasilBTC('GET', '', 'api/remove_order/{}'.format(idOrdem))
        return retorno

    def __obterOrdensAbertas(self):
        retorno = self.executarRequestBrasilBTC('GET', '','/api/my_orders')
        return retorno

    def executarRequestBrasilBTC(self, requestMethod, payload, endpoint):
        config = Util.obterCredenciais()
        
        headers ={
            'Authentication': config["BrasilBitcoin"]["Authentication"],
            'Content-type': 'application/json'
        }
        # requisição básica com módulo requests
        res = requests.request(requestMethod, self.urlBrasilBitcoin+endpoint, headers=headers, data=payload)
        
        if res.status_code == 429:
            return None
        else:
            return json.loads(res.text.encode('utf8'))


#---------------- MÉTODOS PÚBLICOS ----------------#    

    def obter_saldo(self):
        '''
        Método público para obter saldo de todas as moedas conforme as regras das corretoras.
        '''
        saldo = {}
        
        response_json = self.__obterSaldo()

        while response_json is None:
            time.sleep(3)
            response_json = self.__obterSaldo()

        # Inicializa todas as moedas
        for moeda in Util.obter_lista_de_moedas():
            saldo[moeda] = 0

        for ativo in response_json.keys():
            if ativo != 'user_cpf':
                saldo[ativo.lower()] = float(response_json[ativo])
        
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

        if not retorno_cancel['success']:
            logging.warning('Erro no cancelamento da Brasil: {}'.format(retorno_cancel))
        
        if retorno_cancel['message']=='Ordem já removida.' or retorno_cancel['message']=='Ordem completamente executada.': #se a operacao ja ta cancelada, fala que cancelou
            return True 

        return retorno_cancel['success']