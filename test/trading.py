import sys,os
sys.path.append(os.getcwd())


from uteis.util import Util
from test.googleSheets import GoogleSheets
from uteis.corretora import Corretora
from uteis.ordem import Ordem
import time
#isso é um NOVO x2 teste do git!! AGORA VAI mesmo
corrMercado = Corretora('MercadoBitcoin')
corrBrasilBTC = Corretora('BrasilBitcoin')
corrMercado.book.obter_ordem_book_por_indice('usdc','brl',0)

corrMercado.atualizar_saldo()
print(corrMercado.saldo['xrp'])
saldo_antigo = corrMercado.saldo['xrp']

ordem = Ordem()
ordem.quantidade_enviada = 10
ordem.tipo_ordem = 'market'
ordem.ativo = 'xrp'
ordem.preco_enviado = corrMercado.book.preco_compra

corrMercado.enviar_ordem_compra(ordem,'xrp')


corrMercado.atualizar_saldo()
print(corrMercado.saldo['xrp'])
saldo_novo = corrMercado.saldo['xrp']

print(saldo_novo-saldo_antigo)

'''

corrBinance = Corretora('Binance')

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

    '''