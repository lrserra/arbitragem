from teste_stress import Teste_Stress

ativo = 'xrp'
frequencia = 0
corretora = 'Binance'

Teste_Stress.carrega_books(corretora,ativo,frequencia)




'''TESTE DE CORRETAGEM--> SÓ HABILITE SE FOR TESTAR (ORDENS REAIS)
from teste_corretagem import Testa_Corretagem

ativo = 'xrp'
quantidade = 30  #usa uma quantidade pequena!
lista_de_corretoras = ['Binance']

for corretora in lista_de_corretoras:

    Testa_Corretagem.testa_venda(corretora,ativo,quantidade)
    Testa_Corretagem.testa_compra(corretora,ativo,quantidade)
'''