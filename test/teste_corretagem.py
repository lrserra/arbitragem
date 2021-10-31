import sys,os
sys.path.append(os.getcwd())

from uteis.corretora import Corretora
from uteis.ordem import Ordem

#---------- TESTE DE CALCULO DE CORRETAGEM E QUANTIDADE LIQUIDA ----------#

class Testa_Corretagem:

    def testa_compra(corretora = 'MercadoBitcoin',ativo ='xrp', qtd = 10):

        print("Testando compra na {}".format(corretora))
        corretora_obj = Corretora(corretora)
        corretora_obj.book.obter_ordem_book_por_indice(ativo,'brl',0)

        corretora_obj.atualizar_saldo()
        saldo_antigo = corretora_obj.saldo[ativo]

        ordem = Ordem()
        ordem.quantidade_enviada = qtd
        ordem.tipo_ordem = 'market'
        ordem.ativo = ativo
        ordem.preco_enviado = corretora_obj.book.preco_compra

        print("Enviando ordem de {} de {} {}:".format('compra',ordem.quantidade_enviada,ordem.ativo))
        corretora_obj.enviar_ordem_compra(ordem,ativo)

        corretora_obj.atualizar_saldo()
        saldo_novo = corretora_obj.saldo[ativo]

        print("Saldo Antes/ Depois / Diferença: {}/ {} / {}".format(saldo_antigo,saldo_novo,abs(saldo_antigo-saldo_novo)))

    def testa_venda(corretora = 'MercadoBitcoin',ativo ='xrp', qtd = 10):

        print("Testando venda na {}".format(corretora))
        corretora_obj = Corretora(corretora)
        corretora_obj.book.obter_ordem_book_por_indice(ativo,'brl',0)

        corretora_obj.atualizar_saldo()
        saldo_antigo = corretora_obj.saldo[ativo]

        ordem = Ordem()
        ordem.quantidade_enviada = qtd
        ordem.tipo_ordem = 'market'
        ordem.ativo = ativo
        ordem.preco_enviado = corretora_obj.book.preco_venda

        print("Enviando ordem de {} de {} {}:".format('venda',ordem.quantidade_enviada,ordem.ativo))
        corretora_obj.enviar_ordem_venda(ordem,ativo)

        corretora_obj.atualizar_saldo()
        saldo_novo = corretora_obj.saldo[ativo]

        print("Saldo Antes/ Depois / Diferença: {}/ {} / {}".format(saldo_antigo,saldo_novo,abs(saldo_antigo-saldo_novo)))



