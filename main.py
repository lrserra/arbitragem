import requests
import locale
import time
from datetime import datetime
from corretora import Corretora
from util import Util
from arbitragem import Arbitragem
from coreTelegram import Telegram

#ativos = ['btc', 'eth', 'xrp', 'ltc']
ativos = ['eth']
i = 1

locale.setlocale(locale.LC_MONETARY, 'pt_BR.UTF-8')

while i <= 200:
    for ativo in ativos:

        # Instancia das corretoras por ativo
        mercadoBitcoin = Corretora('MercadoBitcoin', ativo)
        brasilBitcoin = Corretora('BrasilBitcoin', ativo)

        retornoCompra = Arbitragem.run(mercadoBitcoin, brasilBitcoin, ativo, True)
        retornoVenda = Arbitragem.run(brasilBitcoin, mercadoBitcoin, ativo, True)   

        mercadoBitcoin.atualizarSaldo()
        brasilBitcoin.atualizarSaldo()

        if retornoCompra['sucesso'] == 'true':
            Telegram.enviarMensagem('[' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + '] ' + mercadoBitcoin.nome + ' -> ' + brasilBitcoin.nome + ' = PnL: ' + str(retornoCompra['Pnl']))
            Telegram.enviarMensagem('[' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + '] ' + mercadoBitcoin.nome + ' -> Saldo em BRL: ' + str(locale.currency(mercadoBitcoin.saldoBRL)))
            Telegram.enviarMensagem('[' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ']' + mercadoBitcoin.nome + ' -> Saldo em {}: '.format(mercadoBitcoin.saldoCrypto))
        else:
            Telegram.enviarMensagem('[' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + '] Pnl: ' + retornoCompra['ErroPnl'] + ' | Saldo: ' + retornoCompra['ErroSaldo'])

        if retornoVenda['sucesso'] == 'true':
            Telegram.enviarMensagem('[' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + '] ' + brasilBitcoin.nome + ' -> ' + mercadoBitcoin.nome + ' = PnL: ' + str(retornoVenda['Pnl']))
            Telegram.enviarMensagem('[' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + '] ' + brasilBitcoin.nome + ' -> Saldo em BRL: ' + str(locale.currency(brasilBitcoin.saldoBRL)))
            Telegram.enviarMensagem('[' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + '] ' + brasilBitcoin.nome + ' -> Saldo em {}: '.format(brasilBitcoin.saldoCrypto))
        else:
            Telegram.enviarMensagem('[' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + '] Pnl: ' + retornoVenda['ErroPnl'] + ' | Saldo: ' + retornoVenda['ErroSaldo'])

    i += 1
    print(i)
    #time.sleep(120)


