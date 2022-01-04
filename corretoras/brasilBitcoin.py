import logging
import requests
import json
import time
from urllib.parse import urlencode
from uteis.logger import Logger
from uteis.settings import Settings
from construtores.ordem import Ordem

class BrasilBitcoin:

    def __init__(self):
        self.urlBrasilBitcoin = 'https://brasilbitcoin.com.br/'
        self.credenciais = Settings().retorna_campo_de_json('broker','BrasilBitcoin','Authentication')
        self.timeout = 30
        self.time_to_sleep = 5
        self.max_retries = 20

#---------------- MÉTODOS PRIVADOS ----------------#
    
    def obterBooks(self,ativo_parte,ativo_contraparte='brl'):
        '''
        carrega os books da corretora BrasilBitcoin
        '''
        try:
            res = requests.get(url = self.urlBrasilBitcoin + 'API/orderbook/{}'.format(ativo_parte), timeout =self.timeout)
            retries = 1
            while res.status_code != 200 and retries<self.max_retries:
                Logger.loga_warning('{}: será feito retry automatico #{} do metodo {} após {} segundos porque res.status_code {} é diferente de 200. Mensagem de Erro: {}'.format('BrasilBitcoin',retries,'obterBooks',self.time_to_sleep,res.status_code,res.text))
                time.sleep(self.time_to_sleep)
                res = requests.get(url = self.urlBrasilBitcoin + 'API/orderbook/{}'.format(ativo_parte), timeout =self.timeout)
                retries+=1

        except Exception as err:
            Logger.loga_erro('obterBooks','BrasilBitcoin',err,'BrasilBitcoin')

        return res.json()

    def __obterSaldo(self):
        retorno = self.__executarRequestBrasilBTC('GET', '','/api/get_balance')
        return retorno

    def __obterOrdemPorId(self, idOrdem):
        return self.__executarRequestBrasilBTC('GET', '', 'api/check_order/{}'.format(idOrdem))

    def __enviarOrdemCompra(self,moeda,quantity, tipoOrdem, precoCompra):
        # objeto que será postado para o endpoint
        payload = {
            'coin_pair': '{}{}'.format('BRL',moeda.upper()),
            'order_type': tipoOrdem,
            'type': 'buy',
            'amount': quantity,
            'price': precoCompra
        }

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        retorno = self.__executarRequestBrasilBTC('POST', json.dumps(payload), 'api/create_order')
        return retorno

    def __enviarOrdemVenda(self,moeda,quantity,tipoOrdem,precoVenda):
        # objeto que será postado para o endpoint
        payload = {
            'coin_pair': '{}{}'.format('BRL',moeda.upper()),
            'order_type': tipoOrdem,
            'type': 'sell',
            'amount': quantity,
            'price': precoVenda
        }

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        retorno = self.__executarRequestBrasilBTC('POST', json.dumps(payload), 'api/create_order')
        return retorno

    def TransferirCrypto(self, quantity, destino):      
        config = ''
        
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
        return self.__executarRequestBrasilBTC('POST', json.dumps(payload), '/api/send')

    def __cancelarOrdem(self, idOrdem):
        retorno = self.__executarRequestBrasilBTC('GET', '', 'api/remove_order/{}'.format(idOrdem))
        return retorno

    def __obterOrdensAbertas(self):
        retorno = self.__executarRequestBrasilBTC('GET', '','/api/my_orders')
        return retorno

    def __executarRequestBrasilBTC(self, requestMethod, payload, endpoint):
        
        headers ={
            'Authentication': self.credenciais,
            'Content-type': 'application/json'
        }
        # requisição básica com módulo requests
        try:
            res = requests.request(requestMethod, self.urlBrasilBitcoin+endpoint, headers=headers, data=payload, timeout =self.timeout)
            retries = 1
            while res.status_code not in (200,418) and retries<self.max_retries:
                Logger.loga_warning('{}: {}, vai aguardar 61 segundos'.format('BrasilBitcoin',res.text))
                if 'Too Many Attempts' in res.text:
                    time.sleep(61)
                else:
                    Logger.loga_warning('{}: será feito retry automatico #{} do metodo {} após {} segundos porque res.status_code {} é diferente de 200. Mensagem de Erro: {}'.format('BrasilBitcoin',retries,'__executarRequestBrasilBTC',5,res.status_code,res.text))
                    time.sleep(self.time_to_sleep)
                res = requests.request(requestMethod, self.urlBrasilBitcoin+endpoint, headers=headers, data=payload, timeout =self.timeout)
                retries+=1
            
        except Exception as err:
            Logger.loga_erro('__executarRequestBrasilBTC','BrasilBitcoin',err,'BrasilBitcoin')

        return json.loads(res.text.encode('utf8'))
    
#---------------- MÉTODOS PÚBLICOS ----------------#    
    def obter_moedas_negociaveis(self):
        '''
        Método público para obter lista de moedas negociaveis nessa corretora
        '''
        moedas_negociaveis = []
        time.sleep(0.5)
        response_json = self.__obterSaldo()

        for item in response_json.keys():
            if item != 'user_cpf':
                moedas_negociaveis.append(item.lower())
        
        return moedas_negociaveis

    def obter_saldo(self):
        '''
        Método público para obter saldo de todas as moedas conforme as regras das corretoras.
        '''
        saldo = {}
        
        time.sleep(0.5)
        response_json = self.__obterSaldo()

        for item in response_json.keys():
            if item != 'user_cpf':
                moeda = item.lower()
                saldo_disponivel =   float(response_json[item])
                if saldo_disponivel >0:
                    saldo[moeda] = saldo_disponivel
        
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
            logging.info('Erro no cancelamento da Brasil: {}'.format(retorno_cancel))
        
        if retorno_cancel['message']=='Ordem já removida.' or retorno_cancel['message']=='Ordem completamente executada.': #se a operacao ja ta cancelada, fala que cancelou
            return True 

        return retorno_cancel['success']

    def cancelar_todas_ordens(self, ordens_abertas):
        '''
        Cancelar todas as ordens abertas por ativo
        '''
        for ordem in ordens_abertas:
            self.cancelar_ordem(ordem['id'])

    def obter_ordem_por_id(self, ordem:Ordem):
        '''
        atualiza status de ordem na BrasilBitcoin
        '''
        response = self.__obterOrdemPorId(ordem.id)
        ordem.status = response['data']['status']
        ordem.foi_executada_completamente = ordem.status == 'filled'
        ordem.quantidade_executada = float(response['data']['executed'])
        ordem.quantidade_enviada = float(response['data']['total'])
        ordem.preco_executado = float(response['data']['price'])
        ordem.preco_enviado = ordem.preco_executado
        ordem.direcao = response['data']['type']
        return ordem

    def enviar_ordem_compra(self, ordem:Ordem):
        '''
        envia ordem de compra para a Brasil Bitcoin
        '''
        response = self.__enviarOrdemCompra(ordem.ativo_parte,ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado)
                
        if response['success'] == True:
            ordem.id = response['data']['id']
            ordem.status = response['data']['status']
            ordem.foi_executada_completamente = ordem.status == 'filled'
            ordem.quantidade_executada = 0
            ordem.preco_executado = 0
            i = 0
            qtd = len(response['data']['fills']) #quantidade de execuções parciais
            while i < qtd:
                quantidade_parcial = float(response['data']['fills'][i]['amount'])
                ordem.quantidade_executada += quantidade_parcial

                preco_executado_parcial = response['data']['fills'][i]['price'].replace('.','')
                preco_executado_parcial = float(preco_executado_parcial.replace(',','.'))

                ordem.preco_executado += preco_executado_parcial*quantidade_parcial
                i += 1
            if ordem.quantidade_executada==0: #para evitar divisão por zero
                ordem.preco_executado = ordem.preco_enviado 
            else:    
                ordem.preco_executado = ordem.preco_executado/ordem.quantidade_executada #preço medio ponderado
        else:
            Logger.loga_erro('enviar_ordem_compra','BrasilBitcoin',response['message'],'BrasilBitcoin')
        return ordem

    def enviar_ordem_venda(self, ordem:Ordem):
        '''
        envia ordem de venda para a Brasil Bitcoin
        '''
        response = self.__enviarOrdemVenda(ordem.ativo_parte,ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado)
        if response['success'] == True:
            ordem.id = response['data']['id']
            ordem.status = response['data']['status']
            ordem.foi_executada_completamente = ordem.status == 'filled'
            ordem.quantidade_executada = 0
            ordem.preco_executado = 0
            i = 0
            qtd = len(response['data']['fills']) #quantidade de execuções parciais
            while i < qtd:
                quantidade_parcial = float(response['data']['fills'][i]['amount'])
                ordem.quantidade_executada += quantidade_parcial

                preco_executado_parcial = response['data']['fills'][i]['price'].replace('.','')
                preco_executado_parcial = float(preco_executado_parcial.replace(',','.'))

                ordem.preco_executado += preco_executado_parcial*quantidade_parcial
                i += 1
            if ordem.quantidade_executada==0: #para evitar divisão por zero
                ordem.preco_executado = ordem.preco_enviado 
            else:    
                ordem.preco_executado = ordem.preco_executado/ordem.quantidade_executada #preço medio ponderado
        else:
            Logger.loga_erro('enviar_ordem_venda','BrasilBitcoin',response['message'],'BrasilBitcoin')
        return ordem

