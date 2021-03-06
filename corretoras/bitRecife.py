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
    
    def obterBooks(self,ativo,ativo_contraparte='brl'):
        market = ativo.upper()+'_'+ativo_contraparte.upper()
        tipo = 'ALL'
        depth = '20'
        request_url =self.urlBitRecife+'public/getorderbook?market='+market+'&type='+tipo+'&depth='+depth
        return requests.get(url = request_url).json()

    def obterSaldo(self):
       
        return self.executarRequestBitRecife('POST','','getbalances')

    def executarRequestBitRecife(self, requestMethod, payload, endpoint):
        # Constantes
        config = Util.obterCredenciais()
        apikey = config["BitRecife"]["Authentication"]
        apisecret = config["BitRecife"]["Secret"]
        nonce = int(time.time())

        url = self.urlBitRecife +'private/'+endpoint
        apisign = hmac.new(bytes(apisecret,'utf-8'), bytes(url,'utf-8'), hashlib.sha512).hexdigest()

        # Gerar cabeçalho da requisição
        headers = {'apisign': apisign}

        payload={'nonce':nonce,'apikey':apikey}
        
        # requisição básica com módulo requests
        res = requests.request(requestMethod,url, headers=headers, data=payload)
        return json.loads(res.text.encode('utf8'))

