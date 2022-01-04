import logging
import time
from binance.spot import Spot
from uteis.logger import Logger
from uteis.settings import Settings
from construtores.ordem import Ordem

class Binance:

    def __init__(self):
        self.urlBinance = 'https://api.binance.com/'
        self.authentication = Settings().retorna_campo_de_json('broker','Binance','Authentication')
        self.secret = Settings().retorna_campo_de_json('broker','Binance','Secret')
        self.client = Spot(self.authentication,self.secret)
        self.recvWindow = 60*1000
        self.time_to_sleep = 5
        self.max_retries = 20
        
#---------------- MÉTODOS PRIVADOS ----------------#
    
    def obterBooks(self,ativo_parte,ativo_contraparte='brl'):
        '''
        carrega os books da corretora Binance
        '''
        try:
            res = self.client.depth('{}{}'.format(ativo_parte.upper(), ativo_contraparte.upper()))
            retries = 1
            while len(res['asks'])<2 and retries<self.max_retries:
                Logger.loga_warning('{}: será feito retry automatico #{} do metodo {} após {} segundos porque o book nao retornou nada'.format('Binance',retries,'obterBooks',self.time_to_sleep))
                time.sleep(self.time_to_sleep)
                res = self.client.depth('{}{}'.format(ativo_parte.upper(), ativo_contraparte.upper()))
                retries+=1
        
        except Exception as err:
            Logger.loga_erro('obterBooks','Binance',err,'Binance')
        
        return res

    def __obterSaldo(self):
        res = self.client.account(recvWindow=self.recvWindow)
        return res

    def __obterOrdemPorId(self, idOrdem):
        res = self.client.get_order('{}{}'.format(self.ativo_parte.upper(), self.ativo_contraparte.upper()), orderId=idOrdem,recvWindow=self.recvWindow)
        return res

    def __enviarOrdemCompra(self, moeda,quantity, tipoOrdem, precoCompra):
        # objeto que será postado para o endpoint

        symbol = '{}{}'.format(moeda.upper(),'brl'.upper())
        type = tipoOrdem.upper()
        side = 'BUY'

        # "timeInForce": "GTC" - só é obrigatório na ordem limitada
        # Ordem a mercado não precisa informar o preço
        if type == 'LIMIT':
            payload = {
                'symbol': symbol,
                'side': side,
                'type': type,
                "timeInForce": "GTC",
                'quantity': quantity,
                'price': precoCompra
            }
        else:
            payload = {
                'symbol': symbol,
                'side': side,
                'type': type,
                'quantity': quantity
            }

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        #res = self.client.new_order(symbol, side, type, payload)
        res = self.client.new_order(**payload,recvWindow=self.recvWindow)
        return res

    def __enviarOrdemVenda(self, moeda, quantity, tipoOrdem, precoVenda):
        # objeto que será postado para o endpoint

        symbol = '{}{}'.format(moeda.upper(),'brl'.upper())
        type = tipoOrdem.upper()
        side = 'SELL'

        if type == 'LIMIT':
            payload = {
                'symbol': symbol,
                'side': side,
                'type': type,
                "timeInForce": "GTC",
                'quantity': quantity,
                'price': precoVenda
            }
        else:
            payload = {
                'symbol': symbol,
                'side': side,
                'type': type,
                'quantity': quantity
            }

        # sem serializar o payload (json.dumps), irá retornar erro de moeda não encontrada
        #res = self.client.new_order(symbol, side, type, payload)
        res = self.client.new_order(**payload,recvWindow=self.recvWindow)
        return res

    def __cancelarOrdem(self, idOrdem):
        res = self.client.cancel_order('{}{}'.format(self.ativo_parte.upper(), self.ativo_contraparte.upper()), orderId=idOrdem)
        return res

    def __obterOrdensAbertas(self):
        res = self.client.get_open_orders('{}{}'.format(self.ativo_parte.upper(), self.ativo_contraparte.upper()))
        return res
    
#---------------- MÉTODOS PÚBLICOS ----------------#    

    def obter_moedas_negociaveis(self):
        
        moedas_negociaveis = []
        exchange_info = self.client.exchange_info()
        
        for symbol in exchange_info['symbols']:
            if symbol['isSpotTradingAllowed'] and symbol['quoteAsset'].lower() =='brl':
                moedas_negociaveis.append(symbol['baseAsset'].lower())
        return moedas_negociaveis
    
    def obter_saldo(self):
        '''
        Método público para obter saldo de todas as moedas conforme as regras das corretoras.
        '''
        saldo = {}
        response_json = self.__obterSaldo()

        for item in response_json['balances']:
            moeda = item['asset'].lower()
            saldo_disponivel = float(item['free'])
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

        if retorno_cancel['status'] != 'CANCELED':
            logging.info('Erro no cancelamento da Brasil: {}'.format(retorno_cancel))

        # Retorna a descrição CANCELED
        return retorno_cancel['status']

    def cancelar_todas_ordens(self, ordens_abertas):
        '''
        Cancelar todas as ordens abertas por ativo
        '''
        for ordem in ordens_abertas:
            self.cancelar_ordem(ordem['id'])

    def obter_ordem_por_id(self, ordem:Ordem):
        
        response = self.__obterOrdemPorId(ordem.id)
        ordem.status = response['status']
        ordem.quantidade_executada = float(response['executedQty'])
        ordem.quantidade_enviada = float(response['origQty'])
        ordem.preco_executado = float(response['price'])
        ordem.preco_enviado = ordem.preco_executado
        ordem.direcao = response['side']
        return ordem

    def enviar_ordem_compra(self, ordem:Ordem):
        '''
        envia ordem de compra para a Binance
        '''
        response = self.__enviarOrdemCompra(ordem.ativo_parte,ordem.quantidade_enviada, ordem.tipo_ordem.upper(), ordem.preco_enviado)
                
        if response['orderId'] > 0 and response['status'].lower() in ('filled', 'new','partially_filled'):
            ordem.id = response['orderId']
            ordem.status = response['status']
            ordem.foi_executada_completamente = ordem.status.lower() == 'filled'
            ordem.quantidade_executada = 0
            ordem.preco_executado = 0
            i = 0
            qtd = len(response['fills']) #quantidade de execuções parciais
            while i < qtd:
                quantidade_parcial = float(response['fills'][i]['qty'])
                ordem.quantidade_executada += quantidade_parcial

                preco_executado_parcial = float(response['fills'][i]['price'])

                ordem.preco_executado += preco_executado_parcial*quantidade_parcial
                i += 1
            if ordem.quantidade_executada==0: #para evitar divisão por zero
                ordem.preco_executado = ordem.preco_enviado 
            else:    
                ordem.preco_executado = ordem.preco_executado/ordem.quantidade_executada #preço medio ponderado
        else:
            Logger.loga_erro('enviar_ordem_compra','Binance',response['message'],'Binance')
        return ordem

    def enviar_ordem_venda(self, ordem:Ordem):
        '''
        envia ordem de venda para a Binance
        '''
        response = self.__enviarOrdemVenda(ordem.ativo_parte,ordem.quantidade_enviada, ordem.tipo_ordem.upper(), ordem.preco_enviado)

        if response['orderId'] > 0 and response['status'].lower() in ('filled', 'new','partially_filled'):
            ordem.id = response['orderId']
            ordem.status = response['status']
            ordem.foi_executada_completamente = ordem.status.lower() == 'filled'
            ordem.quantidade_executada = 0
            ordem.preco_executado = 0
            i = 0
            qtd = len(response['fills']) #quantidade de execuções parciais
            while i < qtd:
                quantidade_parcial = float(response['fills'][i]['qty'])
                ordem.quantidade_executada += quantidade_parcial

                preco_executado_parcial = float(response['fills'][i]['price'])

                ordem.preco_executado += preco_executado_parcial*quantidade_parcial
                i += 1
            if ordem.quantidade_executada==0: #para evitar divisão por zero
                ordem.preco_executado = ordem.preco_enviado 
            else:    
                ordem.preco_executado = ordem.preco_executado/ordem.quantidade_executada #preço medio ponderado
        else:
            Logger.loga_erro('enviar_ordem_venda','Binance',response['message'],'Binance')
        return ordem

