from mercadoBitcoin import MercadoBitcoin
from brasilBitcoin import BrasilBitcoin
from bitcoinTrade import BitcoinTrade
from novadaxCorretora import Novadax

class Book:
    def __init__(self,nome):

        self.ativo_parte = ''
        self.ativo_contraparte =''
        self.nome = nome
        self.preco_compra = 0.0
        self.preco_venda = 0.0
        self.quantidade_compra = 0.0
        self.quantidade_venda = 0.0

    def obter_ordem_book_por_indice(self,ativo_parte,ativo_contraparte='brl',indice = 0):
        
        try:
            self.__carregar_ordem_books(ativo_parte,ativo_contraparte)

            if self.nome == 'MercadoBitcoin':
                self.preco_compra = float(self.book['asks'][indice][0])
                self.quantidade_compra = float(self.book['asks'][indice][1])
                self.preco_venda = float(self.book['bids'][indice][0])
                self.quantidade_venda = float(self.book['bids'][indice][1])
                
            elif self.nome == 'BrasilBitcoin':
                self.preco_compra = float(self.book['sell'][indice]['preco'])
                self.quantidade_compra = float(self.book['sell'][indice]['quantidade'])
                self.preco_venda = float(self.book['buy'][indice]['preco'])
                self.quantidade_venda = float(self.book['buy'][indice]['quantidade'])
                
            elif self.nome == 'BitcoinTrade':
                self.preco_compra = float(self.book['data']['asks'][indice]['unit_price'])
                self.quantidade_compra = float(self.book['data']['asks'][indice]['amount'])
                self.preco_venda = float(self.book['data']['bids'][indice]['unit_price'])
                self.quantidade_venda = float(self.book['data']['bids'][indice]['amount'])
                
            elif self.nome == 'Novadax':
                self.preco_compra = float(self.book['data']['asks'][indice][0])
                self.quantidade_compra = float(self.book['data']['asks'][indice][1])
                self.preco_venda = float(self.book['data']['bids'][indice][0])
                self.quantidade_venda = float(self.book['data']['bids'][indice][1])
                
        except Exception as erro:
            raise Exception(erro)

    #metodo privado   
    def __carregar_ordem_books(self,ativo_parte,ativo_contraparte):
        try:
            if self.nome == 'MercadoBitcoin':
                self.book = MercadoBitcoin(ativo_parte,ativo_contraparte).obterBooks()

            elif self.nome == 'BrasilBitcoin':
                self.book = BrasilBitcoin(ativo_parte,ativo_contraparte).obterBooks()

            elif self.nome == 'BitcoinTrade':
                self.book = BitcoinTrade(ativo_parte,ativo_contraparte).obterBooks()
             
            elif self.nome == 'Novadax':
                self.book = Novadax(ativo_parte,ativo_contraparte).obterBooks()
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