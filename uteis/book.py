from corretoras.mercadoBitcoin import MercadoBitcoin
from corretoras.brasilBitcoin import BrasilBitcoin
from corretoras.bitcoinTrade import BitcoinTrade
from corretoras.novadaxCorretora import Novadax
from corretoras.bitRecife import BitRecife
from uteis.util import Util
import time

class Book:
    def __init__(self,nome):

        self.ativo_parte = ''
        self.ativo_contraparte =''
        self.nome = nome
        self.preco_compra = 0.0
        self.preco_venda = 0.0
        self.quantidade_compra = 0.0
        self.quantidade_venda = 0.0

    def obter_ordem_book_por_indice(self,ativo_parte,ativo_contraparte='brl',indice = 0,ignorar_quantidades_pequenas = False, ignorar_ordens_fantasmas = False):
        
        try:
            self.__carregar_ordem_books(ativo_parte,ativo_contraparte)
            indice_inicial = indice

            if ignorar_quantidades_pequenas:
                minimo_que_posso_comprar = Util.retorna_menor_valor_compra(ativo_parte)
                minimo_que_posso_vender = Util.retorna_menor_quantidade_venda(ativo_parte)

            if self.nome == 'MercadoBitcoin':

                if ignorar_ordens_fantasmas:
                    
                    indice = indice_inicial
                    while float(self.book['bids'][indice][0]) > float(self.book['asks'][indice][0]): #o preco de venda tem queser menor que o de compra
                        self.book['bids'][indice].append('DESCONSIDERAR')
                        indice+=1

                    indice = indice_inicial
                    while float(self.book['asks'][indice][0]) < float(self.book['bids'][indice][0]): #o preco de compra tem queser maior que o de venda
                        self.book['asks'][indice].append('DESCONSIDERAR')
                        indice+=1
                    

                if ignorar_quantidades_pequenas:
                    indice = indice_inicial
                    while float(self.book['asks'][indice][1])*float(self.book['asks'][indice][0]) < minimo_que_posso_comprar: #vamos ignorar se menor que valor minimo que posso comprar
                        self.book['asks'][indice].append('DESCONSIDERAR')
                        indice+=1

                    indice = indice_inicial
                    while float(self.book['bids'][indice][1]) < minimo_que_posso_vender: #vamos ignorar se menor que valor minimo que posso vender
                        self.book['bids'][indice].append('DESCONSIDERAR')
                        indice+=1

                indice = indice_inicial
                while 'DESCONSIDERAR' in self.book['asks'][indice]:
                    indice+=1
                self.preco_compra = float(self.book['asks'][indice][0])
                self.quantidade_compra = float(self.book['asks'][indice][1])
            
                indice = indice_inicial
                while 'DESCONSIDERAR' in self.book['asks'][indice]:
                    indice+=1
                self.preco_venda = float(self.book['bids'][indice][0])
                self.quantidade_venda = float(self.book['bids'][indice][1])
            
            elif self.nome == 'BrasilBitcoin':
                if ignorar_quantidades_pequenas:
                    while float(self.book['sell'][indice]['quantidade'])*float(self.book['sell'][indice]['preco']) < minimo_que_posso_comprar: #vamos ignorar se menor que valor minimo que posso comprar
                        indice+=1
                    while float(self.book['buy'][indice]['quantidade']) < minimo_que_posso_vender: #vamos ignorar se menor que valor minimo que posso vender
                        indice+=1

                self.preco_compra = float(self.book['sell'][indice]['preco'])
                self.quantidade_compra = float(self.book['sell'][indice]['quantidade'])
                self.preco_venda = float(self.book['buy'][indice]['preco'])
                self.quantidade_venda = float(self.book['buy'][indice]['quantidade'])
                
            elif self.nome == 'BitcoinTrade':

                #retry para a BT barreada
                while 'data' not in self.book.keys():
                    time.sleep(3)
                    self.__carregar_ordem_books(ativo_parte,ativo_contraparte)

                if ignorar_quantidades_pequenas:
                    while float(self.book['data']['asks'][indice]['amount'])*float(self.book['data']['asks'][indice]['unit_price']) < minimo_que_posso_comprar: #vamos ignorar se menor que valor minimo que posso comprar
                        indice+=1
                    while float(self.book['data']['bids'][indice]['amount']) < minimo_que_posso_vender: #vamos ignorar se menor que valor minimo que posso vender
                        indice+=1

                self.preco_compra = float(self.book['data']['asks'][indice]['unit_price'])
                self.quantidade_compra = float(self.book['data']['asks'][indice]['amount'])
                self.preco_venda = float(self.book['data']['bids'][indice]['unit_price'])
                self.quantidade_venda = float(self.book['data']['bids'][indice]['amount'])
                
            elif self.nome == 'Novadax':
                if ignorar_quantidades_pequenas:
                    while float(self.book['data']['asks'][indice][1])*float(self.book['data']['asks'][indice][0]) < minimo_que_posso_comprar: #vamos ignorar se menor que valor minimo que posso comprar
                        indice+=1
                    while float(self.book['data']['bids'][indice][1]) < minimo_que_posso_vender: #vamos ignorar se menor que valor minimo que posso vender
                        indice+=1

                self.preco_compra = float(self.book['data']['asks'][indice][0])
                self.quantidade_compra = float(self.book['data']['asks'][indice][1])
                self.preco_venda = float(self.book['data']['bids'][indice][0])
                self.quantidade_venda = float(self.book['data']['bids'][indice][1])

            elif self.nome == 'BitRecife':
                if ignorar_quantidades_pequenas:
                    while float(self.book['result']['sell'][indice]['Quantity'])*float(self.book['result']['sell'][indice]['Rate']) < minimo_que_posso_comprar: #vamos ignorar se menor que valor minimo que posso comprar
                        indice+=1
                    while float(self.book['result']['buy'][indice]['Quantity']) < minimo_que_posso_vender: #vamos ignorar se menor que valor minimo que posso vender
                        indice+=1

                self.preco_compra = float(self.book['result']['sell'][indice]['Rate'])
                self.quantidade_compra = float(self.book['result']['sell'][indice]['Quantity'])
                self.preco_venda = float(self.book['result']['buy'][indice]['Rate'])
                self.quantidade_venda = float(self.book['result']['buy'][indice]['Quantity'])
                
        except Exception as erro:
            raise Exception(erro)

    #metodo privado   
    def __carregar_ordem_books(self,ativo_parte,ativo_contraparte):
        try:
            time.sleep(1)
            if self.nome == 'MercadoBitcoin':
                self.book = MercadoBitcoin(ativo_parte,ativo_contraparte).obterBooks()

            elif self.nome == 'BrasilBitcoin':
                self.book = BrasilBitcoin(ativo_parte,ativo_contraparte).obterBooks()

            elif self.nome == 'BitcoinTrade':
                self.book = BitcoinTrade(ativo_parte,ativo_contraparte).obterBooks()
             
            elif self.nome == 'Novadax':
                self.book = Novadax(ativo_parte,ativo_contraparte).obterBooks()

            elif self.nome == 'BitRecife':
                self.book = BitRecife().obterBooks(ativo_parte,ativo_contraparte)
        except Exception as erro:
            raise Exception(erro)

    def obter_preco_medio_de_venda(self,qtd_a_vender):
        try:
            if self.nome == 'MercadoBitcoin':
                precos = self.book
                qtd_vendida = 0
                preco_medio = 0
                linha = 0
                lista_de_precos = precos['bids']
                while qtd_vendida <qtd_a_vender:
                    vou_vender_nessa_linha = min(lista_de_precos[linha][1],qtd_a_vender-qtd_vendida)
                    qtd_vendida += vou_vender_nessa_linha
                    preco_medio += lista_de_precos[linha][0]*vou_vender_nessa_linha
                    linha +=1
                return round(preco_medio/qtd_vendida,4)
            
            elif self.nome == 'BrasilBitcoin':
                pass
            elif self.nome == 'BitcoinTrade':
                pass   
        except Exception as erro:
            raise Exception(erro)
    
    def obter_preco_medio_de_compra(self,qtd_a_comprar):
        try:
            if self.nome == 'MercadoBitcoin':
                precos = self.book
                qtd_a_comprar = 2
                qtd_comprada = 0
                preco_medio = 0
                linha = 0
                lista_de_precos = precos['asks']
                
                while qtd_comprada <qtd_a_comprar:
                    vou_comprar_nessa_linha = min(lista_de_precos[linha][1],qtd_a_comprar-qtd_comprada)
                    qtd_comprada += vou_comprar_nessa_linha
                    preco_medio += lista_de_precos[linha][0]*vou_comprar_nessa_linha
                    linha +=1
                return round(preco_medio/qtd_comprada,4)
            
            elif self.nome == 'BrasilBitcoin':
                pass
            elif self.nome == 'BitcoinTrade':
                pass   
        except Exception as erro:
            raise Exception(erro)

    def obter_quantidade_acima_de_preco_venda(self,preco_venda):
        try:
            if self.nome == 'MercadoBitcoin':
                precos = self.book
                linha = 0
                qtd_venda = 0
                lista_de_precos = precos['bids']
                preco = lista_de_precos[linha][0]
                
                while preco > preco_venda:
                    preco = lista_de_precos[linha][0]
                    qtd_venda = qtd_venda+ lista_de_precos[linha][1]
                    linha +=1
                    preco = lista_de_precos[linha][0]
                
                return qtd_venda
            
            elif self.nome == 'BrasilBitcoin':
                pass
            elif self.nome == 'BitcoinTrade':
                pass   
        except Exception as erro:
            raise Exception(erro)


    def obter_quantidade_abaixo_de_preco_compra(self,preco_compra):
        try:
            if self.nome == 'MercadoBitcoin':
                precos = self.book
                linha = 0
                qtd_compra = 0
                lista_de_precos = precos['asks']
                preco = lista_de_precos[linha][0]
                
                while preco < preco_compra:
                    preco = lista_de_precos[linha][0]
                    qtd_compra = qtd_compra+ lista_de_precos[linha][1]
                    linha +=1
                    preco = lista_de_precos[linha][0]
                
                return qtd_compra
            
            elif self.nome == 'BrasilBitcoin':
                pass
            elif self.nome == 'BitcoinTrade':
                pass   
        except Exception as erro:
            raise Exception(erro)