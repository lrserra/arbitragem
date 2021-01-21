import requests
import locale
import time
from datetime import datetime
from corretora import Corretora
from util import Util
from arbitragem import Arbitragem
from leilao import Leilao
#from coreTelegram import Telegram

#ativos = ['btc', 'eth', 'xrp', 'ltc']
ativo = 'xrp'
i = 1

locale.setlocale(locale.LC_MONETARY, 'pt_BR.UTF-8')

mercadoBitcoin = Corretora('MercadoBitcoin', ativo)
brasilBitcoin = Corretora('BrasilBitcoin', ativo)

mercadoBitcoin.atualizarSaldo()
brasilBitcoin.atualizarSaldo()

saldo_brl_inicial = mercadoBitcoin.saldoBRL+brasilBitcoin.saldoBRL
saldo_cripto_inicial = mercadoBitcoin.saldoCrypto+brasilBitcoin.saldoCrypto

print('Saldo Inicial BRL: '+ str(round(saldo_brl_inicial,1)))
print('Saldo Inicial Cripto: '+ str(round(saldo_cripto_inicial,1)))

idOrdem = 0
qtdExecutada = 0

while i <= 20000:
    try:
        # Instancia das corretoras por ativo
        mercadoBitcoin = Corretora('MercadoBitcoin', ativo)
        brasilBitcoin = Corretora('BrasilBitcoin', ativo)

        retornoCompra = Arbitragem.run(mercadoBitcoin, brasilBitcoin, ativo, True)
        retornoVenda = Arbitragem.run(brasilBitcoin, mercadoBitcoin, ativo, True)   

        if retornoCompra['sucesso'] or retornoVenda['sucesso']:

            mercadoBitcoin.atualizarSaldo()
            brasilBitcoin.atualizarSaldo()

            print('Total PnL BRL: '+ str(round(mercadoBitcoin.saldoBRL+brasilBitcoin.saldoBRL-saldo_brl_inicial,1)))
            print('Total PnL Cripto: '+ str(round(mercadoBitcoin.saldoCrypto+brasilBitcoin.saldoCrypto-saldo_cripto_inicial,1)))
            
    except Exception as erro:
        print('deu algum ruim na arbitragem!')
        print(erro)

    
    try:
        me_executaram = Leilao.zera_risco_e_cancela_ordens(brasilBitcoin, mercadoBitcoin, ativo, True, idOrdem)
        
        if me_executaram:

            mercadoBitcoin.atualizarSaldo()
            brasilBitcoin.atualizarSaldo()
            
            print('Total PnL BRL: '+ str(round(mercadoBitcoin.saldoBRL+brasilBitcoin.saldoBRL-saldo_brl_inicial,1)))
            print('Total PnL Cripto: '+ str(round(mercadoBitcoin.saldoCrypto+brasilBitcoin.saldoCrypto-saldo_cripto_inicial,1)))
        

        mercadoBitcoin = Corretora('MercadoBitcoin', ativo) #atualizar os books aqui pra mandar a proxima ordem pro leilao
        brasilBitcoin = Corretora('BrasilBitcoin', ativo) #atualizar os books aqui pra mandar a proxima ordem pro leilao

        retorno_leilao_compra = Leilao.run(brasilBitcoin, mercadoBitcoin, ativo, True)
        idOrdem = retorno_leilao_compra['idOrdem'] #para cancelar depois
    
    except Exception as erro:
        print('deu algum ruim no leilao')
        print(erro)    

    i += 1
    time.sleep(60)


