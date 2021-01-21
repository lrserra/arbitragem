import time
from datetime import datetime
from corretora import Corretora
from util import Util

class Leilao:

    def run(corretoraParte, corretoraContraparte, ativo, executarOrdens = False):

        #ja considerando que não ha arbitragem
        #ja considerando que cancelou as ordens
        logList = {'sucesso': False, 'idOrdem': 0 }

        corretoraParte.atualizarSaldo()
        corretoraContraparte.atualizarSaldo()
        saldoTotalBRL = corretoraParte.saldoBRL + corretoraContraparte.saldoBRL
          
        #corretoraParte tem que ser Brasil, pq la a liquidez é menor e mais facil de fazer leilão
        if ((corretoraParte.precoCompra-0.01) >= 1.01 * corretoraContraparte.precoCompra):# o preço que eu posso vender é maior doq o preço que posso comprar
            
            gostaria_de_vender = corretoraParte.saldoCrypto/2
            maximo_que_consigo_zerar = corretoraContraparte.saldoBRL*corretoraContraparte.precoCompra*1.01
            qtdNegociada = min(gostaria_de_vender,maximo_que_consigo_zerar)

            if corretoraParte.saldoBRL < (saldoTotalBRL/10): #eh pra ser deseperado aqui, tenho menos em reais doq um decimo do totalbrl
                #quando estou desesperado uso a regra do pnl zero
                corretoraParte.precoVenda = 0.01+corretoraContraparte.precoCompra*1.01
                vendaCorretoraParte = corretoraParte.enviarOrdemVenda(qtdNegociada, 'limited') #ta certo isso lucas?
                logList['idOrdem'] = vendaCorretoraParte['data']['id']

            else:#todos outros casos
                corretoraParte.precoVenda = corretoraParte.precoCompra - 0.01 #quando não estou desesperado, uso a regra do um centavo
                vendaCorretoraParte = corretoraParte.enviarOrdemVenda(qtdNegociada, 'limited') #ta certo isso lucas?
                logList['idOrdem'] = vendaCorretoraParte['data']['id']

        return logList

    def zera_risco_e_cancela_ordens(corretoraParte, corretoraContraparte, ativo, executarOrdens = False, idOrdem = 0):

        if idOrdem > 0:#verifica se tem ordem sendo executada
            ordem = corretoraParte.obterOrdemPorId(idOrdem)
            corretoraParte.cancelarOrdem(idOrdem)
            
            if ordem['data']['executed']*corretoraParte.precoCompra > 1: #mais de um real executado
                
                corretoraContraparte.enviarOrdemCompra(ordem['data']['executed'], 'market')#zerando o risco na mercado bitcoin
                return True
        
            corretoraParte.atualizarSaldo()
            corretoraContraparte.atualizarSaldo()
        
        return False