import logging
from os import execlp
import requests
import hashlib
import hmac
import json
import time
from http import client
from urllib.parse import urlencode
from uteis.util import Util
from datetime import datetime

class MercadoBitcoin:

    def __init__(self, ativo_parte = Util.CCYBTC(), ativo_contraparte = Util.CCYBRL()):
        self.ativo_parte = ativo_parte
        self.ativo_contraparte = ativo_contraparte
        self.urlMercadoBitcoin = 'https://www.mercadobitcoin.net/api/{}/orderbook/'
        self.tapi_nonce = self._obter_tapi()
        
#---------------- MÉTODOS PRIVADOS ----------------#

    def obterBooks(self):
        
        try:
            if self.ativo_parte in ['usdt']:
                retorno_json = {'asks':[[1000,1000],[1000,1000]],'bids':[[1000,1000],[1000,1000]]}
                return retorno_json
            else:
                retorno_json = requests.get(url = self.urlMercadoBitcoin.format(self.ativo_parte), timeout =30) 
        except Exception as err:
            logging.error('a chamada de book da MercadoBitcoin falhou com o erro')
            logging.error(err)
            logging.error('vai aguardar 30 segundos e tentar novamente')
            time.sleep(30)
            retorno_json = requests.get(url = self.urlMercadoBitcoin.format(self.ativo_parte), timeout =30) 


        max_retries = 20
        retries = 1
        while retorno_json.status_code!=200 and retries<max_retries:
            logging.info('{}: será feito retry automatico #{} do metodo {} porque res.status_code {} é diferente de 200. Mensagem de Erro: {}'.format('MercadoBitcoin',retries,'obterBooks',retorno_json.status_code,retorno_json.text))
            time.sleep(Util.frequencia())
            retorno_json = requests.get(url = self.urlMercadoBitcoin.format(self.ativo_parte), timeout =30) 
            retries+=1

        return retorno_json.json()

    def _obter_tapi(self):
        tapi_nonce = str(int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000000))#microseconds!
        self.tapi_nonce = tapi_nonce
        return tapi_nonce

    def __obterSaldo(self):
        tapi_nonce = self._obter_tapi()
        params = {
            'tapi_method': 'get_account_info',
            'tapi_nonce': tapi_nonce,
        }
        params = urlencode(params)
        return self.__executarRequestMercadoBTC(params)

    def __enviarOrdemCompra(self, quantity, tipoOrdem, precoCompra):
        tapi_nonce = self._obter_tapi()

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
        retorno = self.__executarRequestMercadoBTC(params)
        return retorno

    def __enviarOrdemVenda(self, quantity, tipoOrdem, precoVenda):
        tapi_nonce = self._obter_tapi()

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
        retorno = self.__executarRequestMercadoBTC(params)
        return retorno

    def TransferirCrypto(self, quantity, destino):
        config = Util.obterCredenciais()
        tx_fee = {'xrp':0.01,'btc':0.0004,'ltc':0.001,'bch':0.001}

        tapi_nonce = self._obter_tapi()
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
        return self.__executarRequestMercadoBTC(params)

    def __cancelarOrdem(self, idOrdem):
        tapi_nonce = self._obter_tapi()

        params = {
            'tapi_method': 'cancel_order',
            'tapi_nonce': tapi_nonce,
            'coin_pair': '{}{}'.format(self.ativo_contraparte.upper(), self.ativo_parte.upper()),
            'order_id': idOrdem,
            'async': 'true'
        }

        params = urlencode(params)
        retorno = self.__executarRequestMercadoBTC(params)
        return retorno

    def __obterOrdensAbertas(self):
        tapi_nonce = self._obter_tapi()

        params = {
            'tapi_method': 'list_orders',
            'tapi_nonce': tapi_nonce,
            'coin_pair': '{}{}'.format(self.ativo_contraparte.upper(), self.ativo_parte.upper()),
            'status_list': '[2]'
        }

        params = urlencode(params)
        retorno = self.__executarRequestMercadoBTC(params)
        return retorno

    def __executarRequestMercadoBTC(self, params):
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
            try:
                response_json = json.loads(response)
            except Exception as err:
                logging.warning('{}: vai aplicar retry pois nao foi possivel carregar o json {} do metodo {}. Mensagem de Erro: {}'.format('MercadoBitcoin',response,'__executarRequestMercadoBTC',err))
                time.sleep(Util.frequencia())

                conn = client.HTTPSConnection(REQUEST_HOST)
                conn.request("POST", REQUEST_PATH, params, headers)

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
        lista_de_moedas = Util.obter_lista_de_moedas()+[Util.CCYBRL()]
        for moeda in lista_de_moedas:
            saldo[moeda] = 0
        
        time.sleep(0.1)
        response_json = self.__obterSaldo()
        
        # Retentativa em caso de erro
        max_retries = 20
        retries = 1
        while 'error_message' in response_json.keys() and retries<max_retries:
            logging.info('{}: será feito retry automatico #{} do metodo {} porque error_message foi encontrado. Mensagem de Erro: {} Tapi: {}'.format('MercadoBitcoin',retries,'__obterSaldo',response_json['error_message'],self.tapi_nonce))
            time.sleep(Util.frequencia())
            response_json = self.__obterSaldo()
            retries+=1

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
        if len(ordens_abertas['response_data']['orders']) > 0:
                for ordem in ordens_abertas['response_data']['orders']:
                    self.cancelar_ordem(ordem['order_id'])

    def enviar_ordem_compra(self, ordemCompra):
        ordem = ordemCompra
        response = self.__enviarOrdemCompra(ordemCompra.quantidade_enviada, ordemCompra.tipo_ordem, ordemCompra.preco_enviado)
        if response['status_code'] == 100: 
            ordem.id = response['response_data']['order']['order_id']
            if response['response_data']['order']['status'] == 4:
                ordem.status = 'filled'
            elif response['response_data']['order']['status'] == 2:
                ordem.status = 'open'
            else:
                ordem.status = 'error'
            ordem.quantidade_executada = float(response['response_data']['order']['executed_quantity'])
            ordem.preco_executado = float(response['response_data']['order']['executed_price_avg'])
        return ordem,response
    
    def enviar_ordem_venda(self, ordemVenda):
        ordem = ordemVenda
        response = self.__enviarOrdemVenda(ordemVenda.quantidade_enviada, ordemVenda.tipo_ordem, ordemVenda.preco_enviado)
        if response['status_code'] == 100:            
            ordem.id = response['response_data']['order']['order_id']
            if response['response_data']['order']['status'] == 4:
                ordem.status = 'filled'
            elif response['response_data']['order']['status'] == 2:
                ordem.status = 'open'
            else:
                ordem.status = 'error'
            ordem.quantidade_executada = float(response['response_data']['order']['executed_quantity'])
            ordem.preco_executado = float(response['response_data']['order']['executed_price_avg'])
        return ordem,response

