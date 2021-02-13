import json
import requests
from util import Util

# Account Id = 92759

# def retorna_instrument_id(ativo):
#     retorno = 0
#     if ativo.upper() == 'XRP':
#         retorno = 6
#     elif ativo.upper() == 'ETH':
#         retorno = 4
#     elif ativo.upper() == 'LTC':
#         retorno = 2
#     elif ativo.upper() == 'BTC':
#         retorno = 1
#     return retorno

def service_url(service_name):
    return 'https://api.coinext.com.br:8443/AP/%s' % service_name


def call_get(service_name, **kwargs):
    res = requests.get(service_url(service_name), **kwargs)
    return json.loads(res.content)


def call_post(service_name, payload={}, **kwargs):
    res = requests.post(service_url(service_name), json.dumps(payload), **kwargs)
    return json.loads(res.content)


# def main():
#     config = Util.obterCredenciais()
#     auth = call_get('authenticate', auth=(config['Coinext']['Login'], config['Coinext']['Password']))
#     if auth['Authenticated']:
#         user_info = call_post('GetUserInfo', headers={
#         'aptoken': auth['Token'],
#         'Content-type': 'application/json'
#         })
#     print(user_info)

def main():
    config = Util.obterCredenciais()
    auth = call_get('authenticate', auth=(config['Coinext']['Login'], config['Coinext']['Password']))
    if auth['Authenticated']:
        
        payload = {
            'OMSId': 1,
            'AccountId': 92759,
            'InstrumentId': 1
        }

        headers ={
            'Content-type': 'application/json',
            'aptoken': auth['Token']
        }

        user_info = call_post('GetOpenQuotes', headers, payload)
    print(user_info)


if __name__ == "__main__":
    main()