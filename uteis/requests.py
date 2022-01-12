import requests
import time
from uteis.logger import Logger

class Requests():

    def envia_requisicao_com_retry(method,url,headers,data,timeout,time_to_sleep):
        '''
        envia requisicao com retry automatico em caso de erro
        '''
        retries = 1
        while True:
            try:
                res = requests.request(method, url, headers=headers, data=data, timeout =timeout)
                return res
            except Exception as err:
                Logger.loga_erro('envia_requisicao_com_retry','Requests','tivemos os seguinte erro no request: {}'.format(err))
                Logger.loga_warning('{}: será feito retry automatico #{} após {} segundos.'.format('Requests',retries,time_to_sleep))
                retries+=1
                time.sleep(time_to_sleep)
    
    def envia_get_com_retry(url,timeout,time_to_sleep):
        '''
        envia get com retry automatico em caso de erro
        '''
        retries = 1
        while True:
            try:
                res = requests.request('get', url= url, timeout =timeout)
                return res
            except Exception as err:
                Logger.loga_erro('envia_get_com_retry','Requests','tivemos os seguinte erro no request: {}'.format(err))
                Logger.loga_warning('{}: será feito retry automatico #{} após {} segundos.'.format('Requests',retries,time_to_sleep))
                retries+=1
                time.sleep(time_to_sleep)