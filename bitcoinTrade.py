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
