import logging
import requests
import json
import time
from urllib.parse import urlencode
from uteis.util import Util
from construtores.ordem import Ordem

class BrasilBitcoin:

    def __init__(self, ativo_parte = Util.CCYBTC(),ativo_contraparte = Util.CCYBRL()):
        self.ativo_parte = ativo_parte
        self.ativo_contraparte = ativo_contraparte
        self.urlBrasilBitcoin = 'https://brasilbitcoin.com.br/'

#---------------- MÉTODOS PRIVADOS ----------------#
    
    def obterBooks(self):
        try:
            res = requests.get(url = self.urlBrasilBitcoin + 'API/orderbook/{}'.format(self.ativo_parte), timeout =30)
        except Exception as err:
            logging.error('a chamada da BrasilBitcoin falhou com o erro')
            logging.error(err)
            logging.error('vai aguardar 30 segundos e tentar novamente')
            time.sleep(30)
            res = requests.get(url = self.urlBrasilBitcoin + 'API/orderbook/{}'.format(self.ativo_parte), timeout =30)


        max_retries = 20
        retries = 1
        while res.status_code != 200 and retries<max_retries:
            logging.info('{}: será feito retry automatico #{} do metodo {} após {} segundos porque res.status_code {} é diferente de 200. Mensagem de Erro: {}'.format('BrasilBitcoin',retries,'obterBooks',Util.frequencia(),res.status_code,res.text))
            time.sleep(Util.frequencia())
            res = requests.get(url = self.urlBrasilBitcoin + 'API/orderbook/{}'.format(self.ativo_parte), timeout =30)
            retries+=1


        return res.json()

    def __obterSaldo(self):
        retorno = self.__executarRequestBrasilBTC('GET', '','/api/get_balance')
        return retorno

    def __obterOrdemPorId(self, idOrdem):
        return self.__executarRequestBrasilBTC('GET', '', 'api/check_order/{}'.format(idOrdem))

    def __enviarOrdemCompra(self, quantity, tipoOrdem, precoCompra):
        # objeto que será postado para o endpoint
        payload = {
            'coin_pair': '{}{}'.format(self.ativo_contraparte.upper(),self.ativo_parte.upper()),
            'order_type': tipoOrdem,
            'type': 'buy',
            'amount': quantity,
            'price': precoCompra
        }

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        retorno = self.__executarRequestBrasilBTC('POST', json.dumps(payload), 'api/create_order')
        return retorno

    def __enviarOrdemVenda(self, quantity, tipoOrdem, precoVenda):
        # objeto que será postado para o endpoint
        payload = {
            'coin_pair': '{}{}'.format(self.ativo_contraparte.upper(),self.ativo_parte.upper()),
            'order_type': tipoOrdem,
            'type': 'sell',
            'amount': quantity,
            'price': precoVenda
        }

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        retorno = self.__executarRequestBrasilBTC('POST', json.dumps(payload), 'api/create_order')
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
        return self.__executarRequestBrasilBTC('POST', json.dumps(payload), '/api/send')

    def __cancelarOrdem(self, idOrdem):
        retorno = self.__executarRequestBrasilBTC('GET', '', 'api/remove_order/{}'.format(idOrdem))
        return retorno

    def __obterOrdensAbertas(self):
        retorno = self.__executarRequestBrasilBTC('GET', '','/api/my_orders')
        return retorno

    def __executarRequestBrasilBTC(self, requestMethod, payload, endpoint):
        config = Util.obterCredenciais()
        
        headers ={
            'Authentication': config["BrasilBitcoin"]["Authentication"],
            'Content-type': 'application/json'
        }
        # requisição básica com módulo requests
        try:
            res = requests.request(requestMethod, self.urlBrasilBitcoin+endpoint, headers=headers, data=payload, timeout =30)
        except Exception as err:
            logging.error('a chamada da BrasilBitcoin falhou com o erro')
            logging.error(err)
            logging.error('vai aguardar 30 segundos e tentar novamente')
            time.sleep(30)
            res = requests.request(requestMethod, self.urlBrasilBitcoin+endpoint, headers=headers, data=payload, timeout =30)
        
        max_retries = 20
        retries = 1
        while res.status_code not in (200,418) and retries<max_retries:
            logging.info('{}: será feito retry automatico #{} do metodo {} após {} segundos porque res.status_code {} é diferente de 200. Mensagem de Erro: {}'.format('BrasilBitcoin',retries,'__executarRequestBrasilBTC',Util.frequencia(),res.status_code,res.text))
            time.sleep(Util.frequencia())
            res = requests.request(requestMethod, self.urlBrasilBitcoin+endpoint, headers=headers, data=payload, timeout =30)
            retries+=1
   
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
        retorno = self.__obterOrdensAbertas()
        if len(retorno)==0 or retorno is None:
            retorno=[]
        return retorno

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

    def cancelar_todas_ordens(self, ordens_abertas,white_list):
        '''
        Cancelar todas as ordens abertas por ativo
        '''
        for ordem in ordens_abertas:
            if ordem['coin'].lower() in white_list:
                self.cancelar_ordem(ordem['id'])

    def obter_ordem_por_id(self, ordem:Ordem):
        
        response = self.__obterOrdemPorId(ordem.id)
        ordem.status = response['data']['status']
        ordem.quantidade_executada = float(response['data']['executed'])
        ordem.quantidade_enviada = float(response['data']['total'])
        ordem.preco_executado = float(response['data']['price'])
        ordem.preco_enviado = ordem.preco_executado
        ordem.direcao = response['data']['type']
        return ordem

    def enviar_ordem_compra(self, ordemCompra):
        ordem = ordemCompra
        response = self.__enviarOrdemCompra(ordemCompra.quantidade_enviada, ordemCompra.tipo_ordem, ordemCompra.preco_enviado)
                
        if response['success'] == True:
            ordem.id = response['data']['id']
            ordem.status = response['data']['status']
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
            mensagem = '{}: enviar_ordem_compra - {}'.format('BrasilBitcoin', response['message'])
            print(mensagem)
        return ordem,response

    def enviar_ordem_venda(self, ordemVenda):
        ordem = ordemVenda
        response = self.__enviarOrdemVenda(ordemVenda.quantidade_enviada, ordemVenda.tipo_ordem, ordemVenda.preco_enviado)
        if response['success'] == True:
            ordem.id = response['data']['id']
            ordem.status = response['data']['status']
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
            mensagem = '{}: enviar_ordem_venda - {}'.format('BrasilBitcoin', response['message'])
            print(mensagem)
        return ordem,response

