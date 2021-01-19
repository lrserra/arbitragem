import requests
import time
from datetime import datetime
from corretora import Corretora
from util import Util
from coreTelegram import Telegram

mercadoBitcoin = Corretora('MercadoBitcoin', 'eth')
brasilBitcoin = Corretora('BrasilBitcoin', 'eth')

mercadoBitcoin.atualizarSaldo()
brasilBitcoin.atualizarSaldo()

msg = 'Saldo em Reais na Mercado BTC: ' + str(mercadoBitcoin.saldoBRL)

Telegram.enviarMensagem(msg)


