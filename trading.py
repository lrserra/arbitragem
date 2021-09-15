from http import client

from binance.spot import Spot
from binance.spot.market import book_ticker
from uteis.corretora import Corretora
from corretoras.binance import Binance

corrBinance = Corretora('Binance')
corrBinance.atualizar_saldo()

# client = Spot()
# print(client.time())

# client = Spot(key='111mhhYaDk71X41XbiGswaB4ZQ6zEbf8JKRZrFANVx4bfElkwpQLhgi9bBxTklB6', secret='i8uYlRe8SMgDeZuf5nNpDcTW8UpiD2GPhLs4lIH84bhKKz9rEC4xVJTic0UTyO0p')

# # Get account information
# print(client.account())