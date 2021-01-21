import time
from datetime import datetime
from corretora import Corretora
from util import Util

class Leilao:

    def run(corretoraParte, corretoraContraparte, ativo, executarOrdens = False, idOrdem = 0, qtdExecutada = 0):

        #ja considerando que não ha arbitragem
        logList = {'sucesso': False, 'idOrdem': idOrdem , 'qtdExecutada': qtdExecutada}

        corretoraParte.atualizarSaldo()
        corretoraContraparte.atualizarSaldo()
        saldoTotalBRL = corretoraParte.saldoBRL + corretoraContraparte.saldoBRL
        
        if idOrdem > 0:#antes de verificar preços e condições, ja verifica se tem ordem sendo executada
            ordem = corretoraParte.obterOrdemPorId(idOrdem)
            
            if ordem['data']['executed'] > 0: #algo ja foi executado
                corretoraContraparte.enviarOrdemCompra(ordem['data']['executed'] - qtdExecutada, 'market')#zerando o risco na mercado bitcoin
                qtdExecutada += ordem['data']['executed']
                logList['qtdExecutada'] = qtdExecutada
            
            if corretoraParte.precoCompra != ordem['data']['price']: # a minha ordem não é a primeira na fila a ser comprada
                corretoraParte.cancelarOrdem(idOrdem)
                idOrdem = 0 #voltando esse ID pra zero, esta tudo cancelado, barril!
                qtdExecutada = 0 #voltando esse qty pra zero, esta tudo cancelado, barril!
                corretoraParte.atualizarSaldo()
                corretoraContraparte.atualizarSaldo()
          
        #corretoraParte tem que ser Brasil, pq la a liquidez é menor e mais facil de fazer leilão
        if (idOrdem == 0) and (corretoraParte.precoCompra >= 1.0095 * corretoraContraparte.precoCompra):#Iniciar leilão compra

            qtdNegociada = corretoraParte.saldoCrypto #o ideal era só vender oq conseguimos zerar na mercado a um preço bom, mas isso aqui é oq tem pra hoje

            if corretoraParte.saldoBRL < (saldoTotalBRL/10): #eh pra ser deseperado aqui, tenho menos em reais doq um oitavo do totalbrl
                #quando estou desesperado uso a regra do pnl zero
                corretoraParte.precoVenda = corretoraContraparte.precoCompra*1.0095
                vendaCorretoraParte = corretoraParte.enviarOrdemVenda(qtdNegociada, 'limited') #ta certo isso lucas?
                logList['idOrdem'] = vendaCorretoraParte['data']['id']

            else:#todos outros casos
                corretoraParte.precoVenda = corretoraParte.precoCompra - 0.01 #quando não estou desesperado, uso a regra do um centavo
                vendaCorretoraParte = corretoraParte.enviarOrdemVenda(qtdNegociada, 'limited') #ta certo isso lucas?
                logList['idOrdem'] = vendaCorretoraParte['data']['id']

        return logList