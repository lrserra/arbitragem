import requests
import hashlib
import hmac
import json
import time
import mimetypes
from http import client
from urllib.parse import urlencode
from uteis.util import Util

class BitRecife:

    def __init__(self):

        self.urlBitRecife = 'https://exchange.bitrecife.com.br/api/v3/'
    
#---------------- MÉTODOS PRIVADOS ----------------#

    def obterBooks(self,ativo,ativo_contraparte='brl'):
        market = ativo.upper()+'_'+ativo_contraparte.upper()
        tipo = 'ALL'
        depth = '20'
        request_url =self.urlBitRecife+'public/getorderbook?market='+market+'&type='+tipo+'&depth='+depth
        return requests.get(url = request_url).json()

    def __obterSaldo(self):
        return self.executarRequestBitRecife('POST','getbalances')

    def __cancelarOrdem(self, idOrdem):
        payload = {}
        payload['orderid'] = idOrdem
        return self.executarRequestBitRecife('POST','ordercancel',payload)

    def obterOrdensAbertas(self,ativo,ativo_contraparte='brl'):
        payload = {}
        payload['market']=ativo.upper()+'_'+ativo_contraparte.upper()
        return self.executarRequestBitRecife('POST','getopenorders', payload)

    def enviarOrdemCompra(self,quantity,preco,ativo,ativo_contraparte='brl'):

        payload = {}
        payload['market']=ativo.upper()+'_'+ativo_contraparte.upper()
        payload['rate']=float(preco)
        payload['quantity']=float(quantity)

        retorno = self.executarRequestBitRecife('POST','buylimit',payload)
        return retorno

    def enviarOrdemVenda(self,quantity,preco,ativo,ativo_contraparte='brl'):
        
        payload = {}
        payload['market']=ativo.upper()+'_'+ativo_contraparte.upper()
        payload['rate']=float(preco)
        payload['quantity']=float(quantity)

        retorno = self.executarRequestBitRecife('POST','selllimit',payload)
        return retorno

    def obterOrdemPorId(self, idOrdem,ativo,ativo_contraparte='brl'):
        
        payload = {}
        payload['orderid']=int(idOrdem)
        payload['market']=ativo.upper()+'_'+ativo_contraparte.upper()
        return self.executarRequestBitRecife('POST','getorder',payload)

    def executarRequestBitRecife(self, requestMethod, endpoint, payload={}):
        # Constantes
        config = Util.obterCredenciais()
        apikey = config["BitRecife"]["Authentication"]
        apisecret = config["BitRecife"]["Secret"]
        nonce = int(time.time())

        url = self.urlBitRecife +'private/'+endpoint
        apisign = hmac.new(bytes(apisecret,'utf-8'), bytes(url,'utf-8'), hashlib.sha512).hexdigest()

        # Gerar cabeçalho da requisição
        headers = {'apisign': apisign}

        payload['nonce']=nonce
        payload['apikey']=apikey
        
        # requisição básica com módulo requests
        res = requests.request(requestMethod,url, headers=headers, data=payload)
        return json.loads(res.text.encode('utf8'))


#---------------- MÉTODOS PÚBLICOS ----------------#

    def obter_saldo(self):
        '''
        Método público para obter saldo de todas as moedas conforme as regras das corretoras.
        '''
        saldo = {}

        response_json = self.__obterSaldo()

        # Inicializa todas as moedas
        for moeda in Util.obter_lista_de_moedas():
            saldo[moeda] = 0
        
        for item in response_json['result']:
            saldo[item['Asset'].lower()] = float(item['Available'])
    
        return saldo

    def cancelar_ordem(self, idOrdem):
        '''
        Cancelar unitariamente uma ordem
        '''
        retorno_cancel = self.__cancelarOrdem(idOrdem)
        return retorno_cancel['success']