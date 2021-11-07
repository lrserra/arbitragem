import sys,os
sys.path.append(os.getcwd())

import datetime
import time
from uteis.corretora import Corretora

#---------- TESTE DE CARREGAMENTO DE BOOKS E SALDOS ALTA FREQUENCIA----------#

class Teste_Stress:

    def carrega_books(corretora = 'BrasilBitcoin',ativo ='xrp', frequencia = 0):

        print("Testando carregar book de {} na {} a cada {} segundos".format(ativo,corretora,frequencia))
        corretora_obj = Corretora(corretora)
        
        time_inicio = datetime.datetime.now()
        time_intermediario = datetime.datetime.now()
        time_fim = datetime.datetime.now()
        i = 0
        while True:
            try:
                time.sleep(frequencia)
                time_intermediario = datetime.datetime.now()
                i+=1
                corretora_obj.book.obter_ordem_book_por_indice(ativo,'brl',0)
                pc1=corretora_obj.book.preco_compra
                pc2=corretora_obj.book.preco_compra_segundo_na_fila 
                pv1=corretora_obj.book.preco_venda
                pv2=corretora_obj.book.preco_venda_segundo_na_fila
                time_fim = datetime.datetime.now()
                print('Carregamento #{} em {}s / PCompra 1 {} / PVenda 1 {} / PCompra 2 {} / PVenda 2 {}'.format(i,time_fim-time_intermediario,pc1,pv1,pc2,pv2))
            except Exception as err:
                print('Deu pau após {} iterações e {} segundos'.format(i,time_fim-time_inicio))
                print('erro: {}'.format(err))



