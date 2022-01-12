import time, sys
from corretoras.binance import Binance
from corretoras.mercadoBitcoin import MercadoBitcoin
from corretoras.brasilBitcoin import BrasilBitcoin
from corretoras.bitcoinTrade import BitcoinTrade
from construtores.ordem import Ordem
from construtores.livro import Livro
from uteis.settings import Settings
from uteis.matematica import Matematica
from uteis.logger import Logger

class Corretora:
    
    def __init__(self, nome):
        
        #propriedades qu precisam ser fornecidas
        self.nome = nome 

        #propriedades especificas de cada corretora
        settings_client = Settings()
        self.corretagem_limitada = settings_client.retorna_campo_de_json_com_fallback('broker',self.nome,'user_corretagem_limitada','default_corretagem_limitada')
        self.corretagem_mercado = settings_client.retorna_campo_de_json_com_fallback('broker',self.nome,'user_corretagem_mercado','default_corretagem_mercado')
        self.valor_minimo_compra = settings_client.retorna_campo_de_json_como_dicionario('broker',self.nome,'valor_minimo_compra')
        self.quantidade_minima_venda = settings_client.retorna_campo_de_json_como_dicionario('broker',self.nome,'quantidade_minima_venda')
        self.moedas_negociaveis = self.__obter_moedas_negociaveis()
        
        #propriedades dinamicas
        self.saldo={}
        self.livro = Livro()
        
        #inicializa saldo inicial para white list desse rasp
        instance = settings_client.retorna_campo_de_json('rasp','instance')
        self.white_list = settings_client.retorna_campo_de_json_como_lista('app',str(instance),'white_list','#')

        #inicializa variaveis de acordo com white list
        for moeda in self.white_list:
            self.saldo[moeda] = 0
            self.valor_minimo_compra[moeda]=sys.maxsize if moeda not in self.valor_minimo_compra.keys() else self.valor_minimo_compra[moeda]
            self.quantidade_minima_venda[moeda]=sys.maxsize if moeda not in self.quantidade_minima_venda.keys() else self.quantidade_minima_venda[moeda]
        self.saldo['brl']=0
    
    #metodos comuns a todas corretoras
    def atualizar_saldo(self):
        '''
        carrega saldo disponivel nas corretoras
        '''
        try:
            if self.nome == 'MercadoBitcoin':
                retorno_saldo = MercadoBitcoin().obter_saldo()
            elif self.nome == 'BrasilBitcoin':
                retorno_saldo = BrasilBitcoin().obter_saldo()
            elif self.nome == 'Binance':
                retorno_saldo = Binance().obter_saldo()
            elif self.nome == 'BitcoinTrade':
                retorno_saldo = BitcoinTrade().obter_saldo()
            
            for moeda in retorno_saldo.keys():
                self.saldo[moeda] = retorno_saldo[moeda]    

        except Exception as erro:
            Logger.loga_erro('atualizar_saldo','Corretora', erro, self.nome)
        
    def atualizar_book(self,ativo_parte,ativo_contraparte='brl'):
        '''
        carrega preços e quantidades no livro para essa moeda
        '''
        try:
            if ativo_parte in self.moedas_negociaveis:
                
                self.livro.book = self.__carregar_ordem_books(ativo_parte,ativo_contraparte)
                
                self.livro.preco_compra = float(self.livro.book['asks'][0][0])
                self.livro.quantidade_compra = float(self.livro.book['asks'][0][1])
                self.livro.preco_venda = float(self.livro.book['bids'][0][0])
                self.livro.quantidade_venda = float(self.livro.book['bids'][0][1])
                self.livro.preco_compra_segundo_na_fila = float(self.livro.book['asks'][1][0]) if len(self.livro.book['asks'])>1 else self.preco_compra
                self.livro.preco_venda_segundo_na_fila = float(self.livro.book['bids'][1][0]) if len(self.livro.book['bids'])>1 else self.preco_venda
                    
        except Exception as erro:
            Logger.loga_erro('atualizar_book','Corretora', erro, self.nome)

    def obter_todas_ordens_abertas(self):
        '''
        obtem todas as ordens limitadas em aberto na corretora
        '''
        try:
            if self.nome == 'MercadoBitcoin':
                return MercadoBitcoin().obter_ordens_abertas()
            elif self.nome == 'BrasilBitcoin':
                return BrasilBitcoin().obter_ordens_abertas()
            elif self.nome == 'Binance':
                return Binance().obter_ordens_abertas()
            elif self.nome == 'BitcoinTrade':
                return BitcoinTrade().obter_ordens_abertas()
        
        except Exception as erro:
            Logger.loga_erro('obter_todas_ordens_abertas','Corretora', erro, self.nome)
        
    def cancelar_todas_ordens(self, white_list = []):
        '''
        cancela todas ordens em aberto na corretora
        '''
        try:
            ordens_abertas = self.obter_todas_ordens_abertas()
            #no caso de querermos restringir as ordens a cancelar
            ordens_abertas = [ordem for ordem in ordens_abertas if ordem['coin'].lower() in white_list] if len(white_list)>0 else ordens_abertas

            if len(ordens_abertas)>0:
                Logger.loga_warning('{} ordens em aberto serao canceladas na {}'.format(len(ordens_abertas),self.nome))
            else:
                Logger.loga_warning('nenhuma ordem precisa ser cancelada na {}'.format(self.nome))

            if self.nome == 'MercadoBitcoin':
                MercadoBitcoin().cancelar_todas_ordens(ordens_abertas)
            elif self.nome == 'BrasilBitcoin':
                BrasilBitcoin().cancelar_todas_ordens(ordens_abertas)
            elif self.nome == 'Binance':
                Binance().cancelar_todas_ordens(ordens_abertas)
            elif self.nome == 'BitcoinTrade':
                BitcoinTrade().cancelar_todas_ordens(ordens_abertas)

        except Exception as erro:
            Logger.loga_erro('cancelar_todas_ordens','Corretora', erro, self.nome)
    
    def obter_ordem_por_id(self,ordem:Ordem):
        '''
        atualiza status atual da ordem
        '''
        try:
            if self.nome == 'MercadoBitcoin':
                ordem = MercadoBitcoin().obter_ordem_por_id(ordem)
            elif self.nome == 'BrasilBitcoin':
                ordem = BrasilBitcoin().obter_ordem_por_id(ordem)
            elif self.nome == 'Binance':
                ordem = Binance().obter_ordem_por_id(ordem)
            elif self.nome == 'BitcoinTrade':
                ordem = BitcoinTrade().obter_ordem_por_id(ordem)

        except Exception as erro:
            Logger.loga_erro('obter_ordem_por_id','Corretora', erro, self.nome)

        return ordem

    def enviar_ordem_compra(self,ordem:Ordem):
        '''
        envia ordem de compra para a corretora (cuidado!)
        '''
        #o rasp só pode enviar ordens de moedas no white list
        if ordem.ativo_parte not in self.moedas_negociaveis:
            return ordem
        
        try:
            if self.nome == 'MercadoBitcoin':
                ordem.quantidade_enviada = ordem.quantidade_enviada*0.999
                ordem.quantidade_enviada = Matematica().trunca(ordem.quantidade_enviada,ordem.ativo_parte,self.nome)
                return MercadoBitcoin().enviar_ordem_compra(ordem)

            elif self.nome == 'BrasilBitcoin':
                if ordem.tipo_ordem == 'market':
                    ordem.quantidade_enviada = ordem.quantidade_enviada*(1+self.corretagem_mercado)
                    ordem.quantidade_enviada = Matematica().trunca(ordem.quantidade_enviada,ordem.ativo_parte,self.nome)
                elif ordem.tipo_ordem == 'limited':
                    ordem.quantidade_enviada = Matematica().adiciona_numero_magico(ordem.quantidade_enviada,ordem.ativo_parte,self.nome)
                return BrasilBitcoin().enviar_ordem_compra(ordem)
                
            elif self.nome == 'Binance':
                if ordem.tipo_ordem == 'market':
                    ordem.quantidade_enviada = ordem.quantidade_enviada*(1+self.corretagem_mercado)
                    ordem.quantidade_enviada = Matematica().trunca(ordem.quantidade_enviada,ordem.ativo_parte,self.nome)
                return Binance().enviar_ordem_compra(ordem)
                
            elif self.nome == 'BitcoinTrade':
                return BitcoinTrade().enviar_ordem_compra(ordem)

        except Exception as erro:
            Logger.loga_erro('enviar_ordem_compra','Corretora', erro, self.nome)
        
        return ordem

    def enviar_ordem_venda(self,ordem:Ordem):
        '''
        envia ordem de venda para a corretora (cuidado!)
        '''
        #o rasp só pode enviar ordens de moedas no white list
        if ordem.ativo_parte not in self.moedas_negociaveis:
            return ordem

        #todas nossas ordens sao truncadas em alguma casa
        ordem.quantidade_enviada = Matematica().trunca(ordem.quantidade_enviada,ordem.ativo_parte,self.nome)
          
        try:
            if self.nome == 'MercadoBitcoin':
               return MercadoBitcoin().enviar_ordem_venda(ordem)
                       
            elif self.nome == 'BrasilBitcoin':
                if ordem.tipo_ordem == 'limited':
                    ordem.quantidade_enviada = Matematica().adiciona_numero_magico(ordem.quantidade_enviada,ordem.ativo_parte,self.nome)
                return BrasilBitcoin().enviar_ordem_venda(ordem)
                 
            elif self.nome == 'Binance':
                return Binance().enviar_ordem_venda(ordem)
           
            elif self.nome == 'BitcoinTrade':
                return BitcoinTrade().enviar_ordem_venda(ordem)

        except Exception as erro:
                Logger.loga_erro('enviar_ordem_venda','Corretora', erro, self.nome)
        
        return ordem

    def cancelar_ordem(self,ordem:Ordem):
        '''
        cancela ordem em aberto a partir do id
        '''
        #só cancelamos se a moeda esta no white list
        if ordem.ativo_parte not in self.moedas_negociaveis:
            return False
        try:
            if self.nome == 'MercadoBitcoin':
                return MercadoBitcoin().cancelar_ordem(ordem.id)
            elif self.nome == 'BrasilBitcoin':
                return BrasilBitcoin().cancelar_ordem(ordem.id)
            elif self.nome == 'Binance':
                return Binance().cancelar_ordem(ordem.id)
            elif self.nome == 'BitcoinTrade':
                return BitcoinTrade().cancelar_ordem(ordem.id)
                        
        except Exception as erro:
            Logger.loga_erro('cancelar_ordem','Corretora', erro, self.nome)

  
    def __obter_moedas_negociaveis(self):
        '''
        obtem lista de moedas na corretora negociaveis contra brl
        '''
        moedas_negociaveis = []
        try:
            if self.nome == 'BrasilBitcoin':
                return BrasilBitcoin().obter_moedas_negociaveis()
            elif self.nome == 'Binance':
                return Binance().obter_moedas_negociaveis()
        except Exception as erro:
            Logger.loga_erro('__obter_moedas_negociaveis','Corretora', erro, self.nome)

        return moedas_negociaveis

    def __carregar_ordem_books(self,ativo_parte,ativo_contraparte):
        '''
        carrega a lista atualizada de ordens no livro da corretora
        '''
        try:
            retorno_book_com_exclusoes = {'asks':[],'bids':[]}
            retorno_book ={'asks':[],'bids':[]}
            retorno_book_sem_tratar ={'asks':[],'bids':[]}
            
            if self.nome == 'MercadoBitcoin':
                retorno_book = MercadoBitcoin(ativo_parte,ativo_contraparte).obterBooks()
                while 'bids' not in retorno_book.keys():
                    retorno_book = MercadoBitcoin(ativo_parte,ativo_contraparte).obterBooks()
                    Logger.loga_warning('{}: {} nao foi encontrado no book, vai tentar novamente'.format('MercadoBitcoin','bids'))
                    time.sleep(5) #se der pau esperamos um pouco mais
            
            elif self.nome == 'BrasilBitcoin': 
                retorno_book_sem_tratar = BrasilBitcoin().obterBooks(ativo_parte,ativo_contraparte)
                while 'sell' not in retorno_book_sem_tratar.keys():
                    retorno_book_sem_tratar = BrasilBitcoin().obterBooks(ativo_parte,ativo_contraparte)
                    Logger.loga_warning('{}: {} nao foi encontrado no book, vai tentar novamente'.format('BrasilBitcoin','sell'))
                    time.sleep(5) #se der pau esperamos um pouco mais
                for preco_no_livro in retorno_book_sem_tratar['sell']:#Brasil precisa ter retorno tratado para ficar igual a mercado, dai o restantes dos metodos vai por osmose
                    retorno_book['asks'].append([preco_no_livro['preco'],preco_no_livro['quantidade']])
                for preco_no_livro in retorno_book_sem_tratar['buy']:
                    retorno_book['bids'].append([preco_no_livro['preco'],preco_no_livro['quantidade']])
              
            elif self.nome == 'BitcoinTrade': 
                retorno_book_sem_tratar = BitcoinTrade(ativo_parte,ativo_contraparte).obterBooks()
                while 'data' not in retorno_book_sem_tratar.keys():
                    retorno_book_sem_tratar = BitcoinTrade(ativo_parte,ativo_contraparte).obterBooks()
                    Logger.loga_warning('{}: {} nao foi encontrado no book, vai tentar novamente'.format('BitcoinTrade','data'))
                    time.sleep(5) #se der pau esperamos um pouco mais
                for preco_no_livro in retorno_book_sem_tratar['data']['asks']:#BT precisa ter retorno tratado para ficar igual a mercado, dai o restantes dos metodos vai por osmose
                    retorno_book['asks'].append([preco_no_livro['unit_price'],preco_no_livro['amount']])
                for preco_no_livro in retorno_book_sem_tratar['data']['bids']:
                    retorno_book['bids'].append([preco_no_livro['unit_price'],preco_no_livro['amount']])

            elif self.nome == 'Binance':
                retorno_book_sem_tratar = Binance().obterBooks(ativo_parte,ativo_contraparte)
                for preco_no_livro in retorno_book_sem_tratar['asks']:
                    retorno_book['asks'].append([float(preco_no_livro[0]),float(preco_no_livro[1])])
                for preco_no_livro in retorno_book_sem_tratar['bids']:
                    retorno_book['bids'].append([float(preco_no_livro[0]),float(preco_no_livro[1])])

            for preco_no_livro in retorno_book['bids'][:5]:
                indice = retorno_book['bids'].index(preco_no_livro)
                if Matematica().tem_numero_magico(float(preco_no_livro[1]),self.nome): #as ordens dos outros robos vão ser transparentes pra gente
                    preco_no_livro.append('DESCONSIDERAR')
                    preco_no_livro.append('NUMERO MAGICO')

            for preco_no_livro in retorno_book['asks'][:5]:
                indice = retorno_book['asks'].index(preco_no_livro)
                if Matematica().tem_numero_magico(float(preco_no_livro[1]),self.nome): #as ordens dos outros robos vão ser transparentes pra gente
                    preco_no_livro.append('DESCONSIDERAR')
                    preco_no_livro.append('NUMERO MAGICO')

            for preco_no_livro in retorno_book['bids'][:5]:
                indice = retorno_book['bids'].index(preco_no_livro)
                if float(preco_no_livro[0]) > float(retorno_book['asks'][indice][0]): #o preco de venda tem que ser maior que o de compra
                    preco_no_livro.append('DESCONSIDERAR')
                    preco_no_livro.append('ORDEM FANTASMA')

            for preco_no_livro in retorno_book['asks'][:5]:
                indice = retorno_book['asks'].index(preco_no_livro)
                if float(preco_no_livro[0]) < float(retorno_book['bids'][indice][0]): #o preco de compra tem que ser menor que o de venda
                    preco_no_livro.append('DESCONSIDERAR')
                    preco_no_livro.append('ORDEM FANTASMA')

            for preco_no_livro in retorno_book['asks'][:5]:
                indice = retorno_book['asks'].index(preco_no_livro)
                if float(preco_no_livro[1])*float(preco_no_livro[0]) < self.valor_minimo_compra[ativo_parte]: #vamos ignorar se menor que valor minimo que posso comprar
                    preco_no_livro.append('DESCONSIDERAR')
                    preco_no_livro.append('QTD PEQUENA')

            for preco_no_livro in retorno_book['bids'][:5]:
                indice = retorno_book['bids'].index(preco_no_livro)
                if float(preco_no_livro[1]) < self.quantidade_minima_venda[ativo_parte]: #vamos ignorar se menor que valor minimo que posso vender
                    preco_no_livro.append('DESCONSIDERAR')
                    preco_no_livro.append('QTD PEQUENA')
            
            retorno_book_com_exclusoes['asks']= [preco_no_livro for preco_no_livro in retorno_book['asks'] if 'DESCONSIDERAR' not in preco_no_livro]
            retorno_book_com_exclusoes['bids']= [preco_no_livro for preco_no_livro in retorno_book['bids'] if 'DESCONSIDERAR' not in preco_no_livro]
            
            return retorno_book_com_exclusoes

        except Exception as erro:
            Logger.loga_erro('__carregar_ordem_books','Corretora', erro, self.nome)
            
