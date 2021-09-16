from uteis.util import Util
from uteis.googleSheets import GoogleSheets
from uteis.corretora import Corretora
import time

corrBinance = Corretora('Binance')
corrMercado = Corretora('MercadoBitcoin')
corrBrasilBTC = Corretora('BrasilBitcoin')

google_sheets = GoogleSheets()

while True:
    lista_de_moedas = ['ada', 'doge', 'usdt', 'btc', 'eth', 'xrp', 'ltc']
    
    for moeda in lista_de_moedas:
        corrBinance.book.obter_ordem_book_por_indice(moeda, Util.CCYBRL())
        if moeda not in ['ada','doge','usdt']:
            corrMercado.book.obter_ordem_book_por_indice(moeda, Util.CCYBRL())
        else:
            corrMercado.book.preco_compra = 0
            corrMercado.book.preco_venda = 0
        corrBrasilBTC.book.obter_ordem_book_por_indice(moeda, Util.CCYBRL())

        google_sheets.escrever("Jericoacoara", 'Binance', [moeda,corrBinance.nome,corrBinance.book.preco_compra,corrBinance.book.preco_venda,corrMercado.nome,corrMercado.book.preco_compra,corrMercado.book.preco_venda,corrBrasilBTC.nome,corrBrasilBTC.book.preco_compra,corrBrasilBTC.book.preco_venda])
    
    time.sleep(60)