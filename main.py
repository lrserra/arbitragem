import requests
import locale
import time
from datetime import datetime
from corretora import Corretora
from util import Util
from caixa import Caixa
from arbitragem import Arbitragem
from leilao import Leilao
#from coreTelegram import Telegram

#essa parte executa apenas uma vez
lista_de_moedas = Util.obter_lista_de_moedas()
corretora_mais_liquida = Util.obter_corretora_de_maior_liquidez()
corretora_menos_liquida = Util.obter_corretora_de_menor_liquidez()

locale.setlocale(locale.LC_MONETARY, 'pt_BR.UTF-8')

day = 1
while day <= 365:
    #essa parte executa uma vez por dia
    agora = datetime.now() 
    meia_noite = datetime.now().replace(day= datetime.now().day +1,hour=0,minute=0,second=0,microsecond=0)
    
    #atualiza saldo inicial nesse dicionario
    saldo_inicial = Caixa.atualiza_saldo_inicial(lista_de_moedas,corretora_mais_liquida,corretora_menos_liquida)

    idOrdem = {}#inicializa o dic
    for moeda in lista_de_moedas:
        idOrdem[moeda]={}
        idOrdem[moeda]['compra'] = 0
        idOrdem[moeda]['venda'] = 0

    while agora < meia_noite:
        #essa parte executa diversas vezes ao dia

        for moeda in lista_de_moedas:
            try:
                # Instancia das corretoras por ativo
                CorretoraMaisLiquida = Corretora(corretora_mais_liquida, moeda)
                CorretoraMenosLiquida = Corretora(corretora_menos_liquida, moeda)

                CorretoraMaisLiquida.atualizarSaldo()
                CorretoraMenosLiquida.atualizarSaldo()

                retornoCompra = Arbitragem.run(CorretoraMaisLiquida, CorretoraMenosLiquida, moeda, True)
                retornoVenda = Arbitragem.run(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True)   

                if retornoCompra['sucesso'] or retornoVenda['sucesso']:
                    agora = datetime.now() 
                    print('{}: operou arb!'.format(agora))
                    CorretoraMaisLiquida.atualizarSaldo()
                    CorretoraMenosLiquida.atualizarSaldo()
                    
            except Exception as erro:
                print('deu algum ruim na arbitragem!')
                print(erro)

            
            try:
                me_executaram_na_compra = Leilao.cancela_ordens_e_compra_na_mercado(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True, idOrdem[moeda]['compra'])
                me_executaram_na_venda = Leilao.cancela_ordens_e_vende_na_mercado(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True, idOrdem[moeda]['venda'])

                if me_executaram_na_compra or me_executaram_na_venda:

                    agora = datetime.now() 
                    print('{}: operou leilao!'.format(agora))
                    CorretoraMaisLiquida.atualizarSaldo()
                    CorretoraMenosLiquida.atualizarSaldo()

                CorretoraMaisLiquida = Corretora(corretora_mais_liquida, moeda) #atualizar os books aqui pra mandar a proxima ordem pro leilao
                CorretoraMenosLiquida = Corretora(corretora_menos_liquida, moeda) #atualizar os books aqui pra mandar a proxima ordem pro leilao

                retorno_leilao_compra = Leilao.compra(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True)
                idOrdem[moeda]['compra'] = retorno_leilao_compra['idOrdem'] #para cancelar depois
            
                CorretoraMaisLiquida = Corretora(corretora_mais_liquida, moeda) #atualizar os books aqui pra mandar a proxima ordem pro leilao
                CorretoraMenosLiquida = Corretora(corretora_menos_liquida, moeda) #atualizar os books aqui pra mandar a proxima ordem pro leilao

                retorno_leilao_venda = Leilao.venda(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True)
                idOrdem[moeda]['venda'] = retorno_leilao_venda['idOrdem'] #para cancelar depois

            except Exception as erro:
                print('deu algum ruim no leilao')
                print(erro)    

            
            
            time.sleep(Util.frequencia())

        agora = datetime.now() 
    

    Caixa.zera_o_pnl_em_cripto(lista_de_moedas,saldo_inicial,corretora_mais_liquida,corretora_menos_liquida)

    day = day+1
    print(day)

