import time
from datetime import datetime
from corretora import Corretora
from util import Util

class Leilao:

    def compra(corretoraParte, corretoraContraparte, ativo, executarOrdens = False):

        #ja considerando que cancelou as ordens
        logList = {'sucesso': False, 'idOrdem': 0 }

        qtd_de_moedas = len(Util.obter_lista_de_moedas())

        corretoraParte.atualizarSaldo()
        corretoraContraparte.atualizarSaldo()

        saldoTotalBRL = corretoraParte.saldoBRL + corretoraContraparte.saldoBRL
          
        #corretoraParte tem que ser Brasil, pq la a liquidez é menor e mais facil de fazer leilão
        if ((corretoraParte.precoCompra-0.01) >= 1.01 * corretoraContraparte.precoCompra):# o preço que eu posso vender é maior doq o preço que posso comprar
            
            gostaria_de_vender = corretoraParte.saldoCrypto/4
            maximo_que_consigo_zerar = corretoraContraparte.saldoBRL/(qtd_de_moedas*corretoraContraparte.precoCompra*1.01)
            qtdNegociada = min(gostaria_de_vender,maximo_que_consigo_zerar)

            if (qtdNegociada>0) and (maximo_que_consigo_zerar>1):
                
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

    def venda(corretoraParte, corretoraContraparte, ativo, executarOrdens = False):

        #ja considerando que cancelou as ordens
        logList = {'sucesso': False, 'idOrdem': 0 }

        qtd_de_moedas = len(Util.obter_lista_de_moedas())

        corretoraParte.atualizarSaldo()
        corretoraContraparte.atualizarSaldo()

        saldoTotalBRL = corretoraParte.saldoBRL + corretoraContraparte.saldoBRL
          
        #corretoraParte tem que ser Brasil, pq la a liquidez é menor e mais facil de fazer leilão
        if ((corretoraParte.precoVenda+0.01) <= 0.99 * corretoraContraparte.precoVenda):# o preço que eu posso comprar é menor doq o preço que posso vender
            
            gostaria_de_comprar = corretoraParte.saldoBRL/(qtd_de_moedas*corretoraParte.precoVenda+0.01)
            maximo_que_consigo_zerar = corretoraContraparte.saldoCrypto/4
            qtdNegociada = min(gostaria_de_comprar,maximo_que_consigo_zerar)
            
            if (qtdNegociada > 0) and (gostaria_de_comprar>1):

                if corretoraContraparte.saldoBRL < (saldoTotalBRL/10): #eh pra ser deseperado aqui, tenho menos em reais na mercado doq um decimo do totalbrl
                    #quando estou desesperado uso a regra do pnl zero
                    corretoraParte.precoCompra = corretoraContraparte.precoVenda*0.99-0.01
                    CompraCorretoraParte = corretoraParte.enviarOrdemCompra(qtdNegociada, 'limited') #ta certo isso lucas?
                    logList['idOrdem'] = CompraCorretoraParte['data']['id']

                else:#todos outros casos
                    corretoraParte.precoCompra = corretoraParte.precoVenda + 0.01 #quando não estou desesperado, uso a regra do um centavo
                    CompraCorretoraParte = corretoraParte.enviarOrdemCompra(qtdNegociada, 'limited') #ta certo isso lucas?
                    logList['idOrdem'] = CompraCorretoraParte['data']['id']

        return logList

    def cancela_ordens_e_compra_na_mercado(corretoraParte, corretoraContraparte, ativo, executarOrdens = False, idOrdem = 0):

        if idOrdem > 0:#verifica se tem ordem sendo executada
            ordem = corretoraParte.obterOrdemPorId(idOrdem)
            corretoraParte.cancelarOrdem(idOrdem)
            
            if executarOrdens and ordem['data']['executed']*corretoraParte.precoCompra > 1: #mais de um real executado
                
                corretoraContraparte.enviarOrdemCompra(ordem['data']['executed'], 'market')#zerando o risco na mercado bitcoin
                return True
        
            corretoraParte.atualizarSaldo()
            corretoraContraparte.atualizarSaldo()
        
        return False

    def cancela_ordens_e_vende_na_mercado(corretoraParte, corretoraContraparte, ativo, executarOrdens = False, idOrdem = 0):

        if idOrdem > 0:#verifica se tem ordem sendo executada
            ordem = corretoraParte.obterOrdemPorId(idOrdem)
            corretoraParte.cancelarOrdem(idOrdem)
            
            if executarOrdens and ordem['data']['executed']*corretoraParte.precoVenda > 1: #mais de um real executado
                
                corretoraContraparte.enviarOrdemVenda(ordem['data']['executed'], 'market')#zerando o risco na mercado bitcoin
                return True
        
            corretoraParte.atualizarSaldo()
            corretoraContraparte.atualizarSaldo()
        
        return False