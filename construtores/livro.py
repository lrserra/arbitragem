import sys

class Livro:
    def __init__(self):

        self.ativo_parte = ''
        self.ativo_contraparte ='brl'
        self.preco_compra = sys.maxsize
        self.preco_venda = 1/sys.maxsize
        self.preco_compra_segundo_na_fila = sys.maxsize
        self.preco_venda_segundo_na_fila = 1/sys.maxsize
        self.quantidade_compra = 0.0
        self.quantidade_venda = 0.0
        self.book={'asks':[[sys.maxsize,sys.maxsize]],'bids':[[1/sys.maxsize,sys.maxsize]]}

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