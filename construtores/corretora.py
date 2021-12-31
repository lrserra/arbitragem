import time
from corretoras.binance import Binance
from corretoras.mercadoBitcoin import MercadoBitcoin
from corretoras.brasilBitcoin import BrasilBitcoin
from corretoras.bitcoinTrade import BitcoinTrade
from construtores.ordem import Ordem
from construtores.livro import Livro
from uteis.settings import Settings
from uteis.util import Util
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
        self.ordem = Ordem()

        #inicializa saldo inicial para white list desse rasp
        instance = settings_client.retorna_campo_de_json('rasp','instance')
        white_list = settings_client.retorna_campo_de_json_como_lista('app',str(instance),'white_list','#')

        for moeda in white_list+['brl']:
            self.saldo[moeda] = 0

    #metodos comuns a todas corretoras
    def atualizar_saldo(self):
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
        
    def obter_ordem_book_por_indice(self,ativo_parte,ativo_contraparte='brl',indice = 0,ignorar_quantidades_pequenas = False, ignorar_ordens_fantasmas = False):
        
        try:
            if ativo_parte in self.moedas_negociaveis:
                
                self.livro.book = self.__carregar_ordem_books(ativo_parte,ativo_contraparte,ignorar_quantidades_pequenas,ignorar_ordens_fantasmas)
                
                self.livro.preco_compra = float(self.livro.book['asks'][indice][0])
                self.livro.quantidade_compra = float(self.livro.book['asks'][indice][1])
                self.livro.preco_venda = float(self.livro.book['bids'][indice][0])
                self.livro.quantidade_venda = float(self.livro.book['bids'][indice][1])
                self.livro.preco_compra_segundo_na_fila = float(self.livro.book['asks'][indice+1][0]) if len(self.livro.book['asks'])>1 else self.preco_compra
                self.livro.preco_venda_segundo_na_fila = float(self.livro.book['bids'][indice+1][0]) if len(self.livro.book['bids'])>1 else self.preco_venda
                    
        except Exception as erro:
            Logger.loga_erro('obter_ordem_book_por_indice','Corretora', erro, self.nome)

    def obter_todas_ordens_abertas(self, ativo='btc'):
        try:
            if self.nome == 'MercadoBitcoin':
                return MercadoBitcoin(ativo).obter_ordens_abertas()
            elif self.nome == 'BrasilBitcoin':
                return BrasilBitcoin(ativo).obter_ordens_abertas()
            elif self.nome == 'Binance':
                return Binance(ativo).obter_ordens_abertas()
            elif self.nome == 'BitcoinTrade':
                todas_moedas = Util.obter_lista_de_moedas()
                return BitcoinTrade(ativo).obter_ordens_abertas(todas_moedas)
        
        except Exception as erro:
            Logger.loga_erro('obter_todas_ordens_abertas','Corretora', erro, self.nome)
        
    def cancelar_todas_ordens(self):
        try:
            ordens_abertas = self.obter_todas_ordens_abertas()
            white_list = Util.obter_white_list()
            qtd_ordens_abertas = len([ordem for ordem in ordens_abertas if ordem['coin'].lower in white_list])
            
            if qtd_ordens_abertas>0:
                logging.warning('{} ordens em aberto serao canceladas na {}'.format(qtd_ordens_abertas,self.nome))
            else:
                logging.warning('nenhuma ordem precisa ser cancelada na {}'.format(self.nome))

            if self.nome == 'MercadoBitcoin':
                MercadoBitcoin().cancelar_todas_ordens(ordens_abertas,white_list)
            elif self.nome == 'BrasilBitcoin':
                BrasilBitcoin().cancelar_todas_ordens(ordens_abertas,white_list)
            elif self.nome == 'Binance':
                Binance().cancelar_todas_ordens(ordens_abertas,white_list)
            elif self.nome == 'BitcoinTrade':
                BitcoinTrade().cancelar_todas_ordens(ordens_abertas,white_list)

        except Exception as erro:
            Logger.loga_erro('cancelar_todas_ordens','Corretora', erro, self.nome)
    
    def obter_ordem_por_id(self,ativo,obterOrdem:Ordem):
        
        try:
            if self.nome == 'MercadoBitcoin':
                pass
            elif self.nome == 'BrasilBitcoin':
                obterOrdem = BrasilBitcoin().obter_ordem_por_id(obterOrdem)
            elif self.nome == 'Binance':
                obterOrdem = Binance().obter_ordem_por_id(obterOrdem)
            elif self.nome == 'BitcoinTrade':
                obterOrdem = BitcoinTrade(ativo).obter_ordem_por_id(obterOrdem)

        except Exception as erro:
            Logger.loga_erro('obter_ordem_por_id','Corretora', erro, self.nome)

        return obterOrdem

    def enviar_ordem_compra(self,ordem:Ordem,ativo_parte,ativo_contraparte='brl'):
        
        if ativo_parte not in self.moedas_negociaveis:
            return Ordem()

        if ordem.tipo_ordem in ['limited','limit']:
            ordem.tipo_ordem = 'limited'
            ordem.quantidade_enviada = Util.trunca_171(ativo_parte,ordem.quantidade_enviada,171)

        try:
            if self.nome == 'MercadoBitcoin':
                if ordem.tipo_ordem == 'market':
                    ordem.quantidade_enviada = ordem.quantidade_enviada*0.999
                    ordem.quantidade_enviada = Util.trunca_171(ativo_parte,ordem.quantidade_enviada,0)
            
                ordem,response = MercadoBitcoin(ativo_parte,ativo_contraparte).enviar_ordem_compra(ordem)

                if ordem.status != 'filled' and ordem.status != 'open':
                    if 'error_message' in response.keys():
                        logging.error('{}: enviar_ordem_compra - msg de erro: {}'.format(self.nome, response['error_message']))
                        logging.error('{}: enviar_ordem_compra - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))            
                    else:
                        logging.error('{}: enviar_ordem_compra - status: {} / {} code: {}'.format(self.nome,response['response_data']['order']['status'],ordem.status,response['status_code']))
                        logging.error('{}: enviar_ordem_compra - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))
                    #raise Exception(mensagem)
            
            elif self.nome == 'BrasilBitcoin':
                if ordem.tipo_ordem == 'market':
                    ordem.quantidade_enviada = ordem.quantidade_enviada*(1+self.corretagem_mercado)
                    ordem.quantidade_enviada = Util.trunca_171(ativo_parte,ordem.quantidade_enviada,0)

                ordem,response = BrasilBitcoin(ativo_parte,ativo_contraparte).enviar_ordem_compra(ordem)
                
                if ordem.status not in (self.descricao_status_executado, 'new','partially_filled'):
                    if 'message' in response.keys():
                        logging.error('{}: enviar_ordem_compra - msg de erro: {}'.format(self.nome, response['message']))
                        logging.error('{}: enviar_ordem_compra - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))            
                    else:
                        logging.error('{}: enviar_ordem_compra - status: {}'.format(self.nome,ordem.status))
                        logging.error('{}: enviar_ordem_compra - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))
            
            elif self.nome == 'Binance':
                if ordem.tipo_ordem == 'market':
                    ordem.quantidade_enviada = ordem.quantidade_enviada*(1+self.corretagem_mercado)
                    ordem.quantidade_enviada = Util.trunca_moeda(ativo_parte,ordem.quantidade_enviada)

                ordem,response = Binance(ativo_parte,ativo_contraparte).enviar_ordem_compra(ordem)
                
                if ordem.status.lower() not in (self.descricao_status_executado.lower(), 'new','partially_filled'):
                    if 'message' in response.keys():
                        logging.error('{}: enviar_ordem_compra - msg de erro: {}'.format(self.nome, response['message']))
                        logging.error('{}: enviar_ordem_compra - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))            
                    else:
                        logging.error('{}: enviar_ordem_compra - status: {}'.format(self.nome,ordem.status))
                        logging.error('{}: enviar_ordem_compra - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))

            elif self.nome == 'BitcoinTrade':
                ordem,response = BitcoinTrade(ativo_parte,ativo_contraparte).enviar_ordem_compra(ordem)

                if ordem.status not in (self.descricao_status_executado,'open','waiting','executed_partially'):
                    if 'message' in response.keys():
                        logging.error('{}: enviar_ordem_venda - msg de erro: {}'.format(self.nome, response['message']))
                        logging.error('{}: enviar_ordem_venda - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))            
                    else:
                        ordemFiltro = Ordem()
                        ordemFiltro.id = response['data']['code']
                        ordemErro = self.obter_ordem_por_id(ativo_parte, ordemFiltro)
                        logging.error('{}: enviar_ordem_venda - status: {} / {} code: {}'.format(self.nome, ordemErro.status, ordem.status, response['message']))
                        logging.error('{}: enviar_ordem_venda - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))
                

        except Exception as erro:
            Logger.loga_erro('enviar_ordem_compra','Corretora', erro, self.nome)
        
        return ordem

    def enviar_ordem_venda(self,ordem:Ordem,ativo_parte,ativo_contraparte='brl'):
        
        if ativo_parte not in self.moedas_negociaveis:
            return Ordem()

        if ordem.tipo_ordem in ['limited','limit']:
            ordem.tipo_ordem = 'limited'
            ordem.quantidade_enviada = Util.trunca_171(ativo_parte,ordem.quantidade_enviada,171)
        elif ordem.tipo_ordem == 'market':
            ordem.quantidade_enviada = Util.trunca_171(ativo_parte,ordem.quantidade_enviada,0)
          
        try:
            if self.nome == 'MercadoBitcoin':
                ordem,response = MercadoBitcoin(ativo_parte,ativo_contraparte).enviar_ordem_venda(ordem)
                
                if ordem.status != self.__obter_status_executado(self.nome) and ordem.status != 'open':
                    if 'error_message' in response.keys():
                        logging.error('{}: enviar_ordem_venda - msg de erro: {}'.format(self.nome, response['error_message']))
                        logging.error('{}: enviar_ordem_venda - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))            
                    else:
                        logging.error('{}: enviar_ordem_venda - status: {} / {} code: {}'.format(self.nome,response['response_data']['order']['status'],ordem.status,response['status_code']))
                        logging.error('{}: enviar_ordem_venda - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))
                
            elif self.nome == 'BrasilBitcoin':
                ordem,response = BrasilBitcoin(ativo_parte,ativo_contraparte).enviar_ordem_venda(ordem)
                
                if ordem.status not in (self.descricao_status_executado, 'new','partially_filled'):
                    if 'message' in response.keys():
                        logging.error('{}: enviar_ordem_venda - msg de erro: {}'.format(self.nome, response['message']))
                        logging.error('{}: enviar_ordem_venda - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))            
                    else:
                        logging.error('{}: enviar_ordem_venda - status: {}'.format(self.nome,ordem.status))
                        logging.error('{}: enviar_ordem_venda - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))
            
            elif self.nome == 'Binance':
                if ordem.tipo_ordem == 'market':
                    ordem.quantidade_enviada = Util.trunca_moeda(ativo_parte,ordem.quantidade_enviada)
                ordem,response = Binance(ativo_parte,ativo_contraparte).enviar_ordem_venda(ordem)
                
                if ordem.status.lower() not in (self.descricao_status_executado.lower(), 'new','partially_filled'):
                    if 'message' in response.keys():
                        logging.error('{}: enviar_ordem_venda - msg de erro: {}'.format(self.nome, response['message']))
                        logging.error('{}: enviar_ordem_venda - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))            
                    else:
                        logging.error('{}: enviar_ordem_venda - status: {}'.format(self.nome,ordem.status))
                        logging.error('{}: enviar_ordem_venda - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))
                

            elif self.nome == 'BitcoinTrade':
                ordem,response = BitcoinTrade(ativo_parte,ativo_contraparte).enviar_ordem_venda(ordem)

                if ordem.status not in (self.descricao_status_executado,'open','waiting','executed_partially'):
                    if 'message' in response.keys():
                        logging.error('{}: enviar_ordem_venda - msg de erro: {}'.format(self.nome, response['message']))
                        logging.error('{}: enviar_ordem_venda - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))            
                    else:
                        ordemFiltro = Ordem()
                        ordemFiltro.id = response['data']['code']
                        ordemErro = self.obter_ordem_por_id(ativo_parte, ordemFiltro)
                        logging.error('{}: enviar_ordem_venda - status: {} / {} code: {}'.format(self.nome, ordemErro.status, ordem.status, response['message']))
                        logging.error('{}: enviar_ordem_venda - ordem que enviei:  qtd {} / tipo {} / preco {}'.format(self.nome, ordem.quantidade_enviada, ordem.tipo_ordem, ordem.preco_enviado))
                    

        except Exception as erro:
                Logger.loga_erro('enviar_ordem_venda','Corretora', erro, self.nome)
        
        return ordem

    def cancelar_ordem(self,ativo_parte='btc',idOrdem=0):
        try:
            if self.nome == 'MercadoBitcoin':
                return MercadoBitcoin(ativo_parte).cancelar_ordem(idOrdem)
            elif self.nome == 'BrasilBitcoin':
                return BrasilBitcoin(ativo_parte).cancelar_ordem(idOrdem)
            elif self.nome == 'Binance':
                return Binance(ativo_parte).cancelar_ordem(idOrdem)
            elif self.nome == 'BitcoinTrade':
                return BitcoinTrade(ativo_parte).cancelar_ordem(idOrdem)
                        
        except Exception as erro:
            Logger.loga_erro('cancelar_ordem','Corretora', erro, self.nome)

  
    def __obter_moedas_negociaveis(self):

        moedas_negociaveis = []
        try:
            if self.nome == 'BrasilBitcoin':
                return BrasilBitcoin().obter_moedas_negociaveis()
            elif self.nome == 'Binance':
                return Binance().obter_moedas_negociaveis()
        except Exception as erro:
            Logger.loga_erro('__obter_moedas_negociaveis','Corretora', erro, self.nome)

        return moedas_negociaveis

    def __carregar_ordem_books(self,ativo_parte,ativo_contraparte,ignorar_quantidades_pequenas = False, ignorar_ordens_fantasmas = False):
        try:
            retorno_book ={'asks':[],'bids':[]}
            retorno_book_sem_tratar ={'asks':[],'bids':[]}
            
            if ignorar_quantidades_pequenas:
                minimo_que_posso_comprar = Util.retorna_menor_valor_compra(ativo_parte)
                minimo_que_posso_vender = Util.retorna_menor_quantidade_venda(ativo_parte)

            if self.nome == 'MercadoBitcoin':
                retorno_book = MercadoBitcoin(ativo_parte,ativo_contraparte).obterBooks()
                while 'bids' not in retorno_book.keys():
                    retorno_book = MercadoBitcoin(ativo_parte,ativo_contraparte).obterBooks()
                    logging.warning('{}: {} nao foi encontrado no book, vai tentar novamente'.format('MercadoBitcoin','bids'))
                    time.sleep(Util.frequencia()) #se der pau esperamos um pouco mais
            
            elif self.nome == 'BrasilBitcoin': 
                time.sleep(0.5)
                retorno_book_sem_tratar = BrasilBitcoin(ativo_parte,ativo_contraparte).obterBooks()
                while 'sell' not in retorno_book_sem_tratar.keys():
                    retorno_book_sem_tratar = BrasilBitcoin(ativo_parte,ativo_contraparte).obterBooks()
                    logging.warning('{}: {} nao foi encontrado no book, vai tentar novamente'.format('BrasilBitcoin','sell'))
                    time.sleep(Util.frequencia()) #se der pau esperamos um pouco mais
                for preco_no_livro in retorno_book_sem_tratar['sell']:#Brasil precisa ter retorno tratado para ficar igual a mercado, dai o restantes dos metodos vai por osmose
                    retorno_book['asks'].append([preco_no_livro['preco'],preco_no_livro['quantidade']])
                for preco_no_livro in retorno_book_sem_tratar['buy']:
                    retorno_book['bids'].append([preco_no_livro['preco'],preco_no_livro['quantidade']])
              
            elif self.nome == 'BitcoinTrade': 
                retorno_book_sem_tratar = BitcoinTrade(ativo_parte,ativo_contraparte).obterBooks()
                while 'data' not in retorno_book_sem_tratar.keys():
                    retorno_book_sem_tratar = BitcoinTrade(ativo_parte,ativo_contraparte).obterBooks()
                    logging.warning('{}: {} nao foi encontrado no book, vai tentar novamente'.format('BitcoinTrade','data'))
                    time.sleep(Util.frequencia()) #se der pau esperamos um pouco mais
                for preco_no_livro in retorno_book_sem_tratar['data']['asks']:#BT precisa ter retorno tratado para ficar igual a mercado, dai o restantes dos metodos vai por osmose
                    retorno_book['asks'].append([preco_no_livro['unit_price'],preco_no_livro['amount']])
                for preco_no_livro in retorno_book_sem_tratar['data']['bids']:
                    retorno_book['bids'].append([preco_no_livro['unit_price'],preco_no_livro['amount']])

            elif self.nome == 'Binance':
                retorno_book_sem_tratar = Binance(ativo_parte,ativo_contraparte).obterBooks()
                for preco_no_livro in retorno_book_sem_tratar['asks']:
                    retorno_book['asks'].append([float(preco_no_livro[0]),float(preco_no_livro[1])])
                for preco_no_livro in retorno_book_sem_tratar['bids']:
                    retorno_book['bids'].append([float(preco_no_livro[0]),float(preco_no_livro[1])])

            if ignorar_ordens_fantasmas:
                
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

            if ignorar_quantidades_pequenas:
                
                for preco_no_livro in retorno_book['asks'][:5]:
                    indice = retorno_book['asks'].index(preco_no_livro)
                    if float(preco_no_livro[1])*float(preco_no_livro[0]) < minimo_que_posso_comprar: #vamos ignorar se menor que valor minimo que posso comprar
                        preco_no_livro.append('DESCONSIDERAR')
                        preco_no_livro.append('QTD PEQUENA')

                for preco_no_livro in retorno_book['bids'][:5]:
                    indice = retorno_book['bids'].index(preco_no_livro)
                    if float(preco_no_livro[1]) < minimo_que_posso_vender: #vamos ignorar se menor que valor minimo que posso vender
                        preco_no_livro.append('DESCONSIDERAR')
                        preco_no_livro.append('QTD PEQUENA')
            
            for preco_no_livro in retorno_book['asks']:
                if 'DESCONSIDERAR' not in preco_no_livro:
                    self.livro.book['asks'].append(preco_no_livro)
            
            for preco_no_livro in retorno_book['bids']:
                if 'DESCONSIDERAR' not in preco_no_livro:
                    self.livro.book['bids'].append(preco_no_livro)

            return retorno_book

        except Exception as erro:
            Logger.loga_erro('__carregar_ordem_books','Corretora', erro, self.nome)
            
