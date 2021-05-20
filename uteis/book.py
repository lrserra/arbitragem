from corretoras.mercadoBitcoin import MercadoBitcoin
from corretoras.brasilBitcoin import BrasilBitcoin
from corretoras.bitcoinTrade import BitcoinTrade
from corretoras.novadaxCorretora import Novadax
from uteis.util import Util
import time
import logging

class Book:
    def __init__(self,nome):

        self.ativo_parte = ''
        self.ativo_contraparte =''
        self.nome = nome
        self.preco_compra = 0.0
        self.preco_venda = 0.0
        self.preco_compra_segundo_na_fila = 0.0
        self.preco_venda_segundo_na_fila = 0.0
        self.quantidade_compra = 0.0
        self.quantidade_venda = 0.0

    def obter_ordem_book_por_indice(self,ativo_parte,ativo_contraparte='brl',indice = 0,ignorar_quantidades_pequenas = False, ignorar_ordens_fantasmas = False):
        
        try:
            self.__carregar_ordem_books(ativo_parte,ativo_contraparte,ignorar_quantidades_pequenas,ignorar_ordens_fantasmas)
            
            self.preco_compra = float(self.book['asks'][indice][0])
            self.quantidade_compra = float(self.book['asks'][indice][1])
            self.preco_venda = float(self.book['bids'][indice][0])
            self.quantidade_venda = float(self.book['bids'][indice][1])

            self.preco_compra_segundo_na_fila = float(self.book['asks'][indice+1][0])
            self.preco_venda_segundo_na_fila = float(self.book['bids'][indice+1][0])
                
        except Exception as erro:
            raise Exception(erro)

    #metodo privado   
    def __carregar_ordem_books(self,ativo_parte,ativo_contraparte,ignorar_quantidades_pequenas = False, ignorar_ordens_fantasmas = False):
        try:
            retorno_book ={'asks':[],'bids':[]}
            retorno_book_sem_tratar ={'asks':[],'bids':[]}
            self.book={'asks':[],'bids':[]}

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

            elif self.nome == 'Novadax':
                while 'data' not in retorno_book_sem_tratar.keys():
                    retorno_book_sem_tratar = Novadax(ativo_parte,ativo_contraparte).obterBooks()
                    logging.warning('{}: {} nao foi encontrado no book, vai tentar novamente'.format('Novadax','data'))
                    time.sleep(Util.frequencia()) #se der pau esperamos um pouco mais
                for preco_no_livro in retorno_book_sem_tratar['data']['asks']:#Novadax precisa ter retorno tratado para ficar igual a mercado, dai o restantes dos metodos vai por osmose
                    retorno_book['asks'].append([float(preco_no_livro[0]),float(preco_no_livro[1])])
                for preco_no_livro in retorno_book_sem_tratar['data']['bids']:
                    retorno_book['bids'].append([float(preco_no_livro[0]),float(preco_no_livro[1])])

            if ignorar_ordens_fantasmas:
                
                for preco_no_livro in retorno_book['bids'][:20]:#apenas olhamos as 20 primeiras ordens
                    indice = retorno_book['bids'].index(preco_no_livro)
                    if float(preco_no_livro[0]) > float(retorno_book['asks'][indice][0]): #o preco de venda tem que ser menor que o de compra
                        preco_no_livro.append('DESCONSIDERAR')

            if ignorar_quantidades_pequenas:
                
                for preco_no_livro in retorno_book['asks'][:20]:#apenas olhamos as 20 primeiras ordens
                    indice = retorno_book['asks'].index(preco_no_livro)
                    if float(preco_no_livro[1])*float(preco_no_livro[0]) < minimo_que_posso_comprar: #vamos ignorar se menor que valor minimo que posso comprar
                        preco_no_livro.append('DESCONSIDERAR')
                        

                for preco_no_livro in retorno_book['bids'][:20]:#apenas olhamos as 20 primeiras ordens
                    indice = retorno_book['bids'].index(preco_no_livro)
                    if float(preco_no_livro[1]) < minimo_que_posso_vender: #vamos ignorar se menor que valor minimo que posso vender
                        preco_no_livro.append('DESCONSIDERAR')
            
            for preco_no_livro in retorno_book['asks'][:20]:#apenas olhamos as 20 primeiras ordens
                if 'DESCONSIDERAR' not in preco_no_livro:
                    self.book['asks'].append(preco_no_livro)
            
            for preco_no_livro in retorno_book['bids'][:20]:#apenas olhamos as 20 primeiras ordens
                if 'DESCONSIDERAR' not in preco_no_livro:
                    self.book['bids'].append(preco_no_livro)


        except Exception as erro:
            raise Exception(erro)

    def obter_preco_medio_de_venda(self,qtd_a_vender):
        try:
            precos = self.book
            qtd_vendida = 0
            preco_medio = 0
            linha = 0
            lista_de_precos = precos['bids']
            while qtd_vendida <qtd_a_vender:
                if linha >= len(lista_de_precos):
                    return round(preco_medio/qtd_vendida,4)
                else:
                    vou_vender_nessa_linha = min(lista_de_precos[linha][1],qtd_a_vender-qtd_vendida)
                    qtd_vendida += vou_vender_nessa_linha
                    preco_medio += lista_de_precos[linha][0]*vou_vender_nessa_linha
                    linha +=1
            return round(preco_medio/qtd_vendida,4)
           
        except Exception as erro:
            raise Exception(erro)
    
    def obter_preco_medio_de_compra(self,qtd_a_comprar):
        try:
            precos = self.book
            qtd_comprada = 0
            preco_medio = 0
            linha = 0
            lista_de_precos = precos['asks']
            
            while qtd_comprada <qtd_a_comprar:
                if linha >= len(lista_de_precos):
                    return round(preco_medio/qtd_comprada,4)
                else:
                    vou_comprar_nessa_linha = min(lista_de_precos[linha][1],qtd_a_comprar-qtd_comprada)
                    qtd_comprada += vou_comprar_nessa_linha
                    preco_medio += lista_de_precos[linha][0]*vou_comprar_nessa_linha
                    linha +=1
            return round(preco_medio/qtd_comprada,4)

        except Exception as erro:
            raise Exception(erro)

    def obter_quantidade_acima_de_preco_venda(self,preco_venda):
        try:
            precos = self.book
            linha = 0
            qtd_venda = 0
            lista_de_precos = precos['bids']
            preco = lista_de_precos[linha][0]
            
            while preco > preco_venda:
                qtd_venda = qtd_venda+ lista_de_precos[linha][1]
                linha +=1
                if linha>=len(lista_de_precos):
                    return qtd_venda
                preco = lista_de_precos[linha][0]

            return qtd_venda
            
        except Exception as erro:
            raise Exception(erro)


    def obter_quantidade_abaixo_de_preco_compra(self,preco_compra):
        try:
                precos = self.book
                linha = 0
                qtd_compra = 0
                lista_de_precos = precos['asks']
                preco = lista_de_precos[linha][0]
                
                while preco < preco_compra:
                    
                    qtd_compra = qtd_compra+ lista_de_precos[linha][1]
                    linha +=1
                    if linha>=len(lista_de_precos):
                        return qtd_compra
                    preco = lista_de_precos[linha][0]
                   
                return qtd_compra
            
        except Exception as erro:
            raise Exception(erro)