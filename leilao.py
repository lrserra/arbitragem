import time
import logging
from datetime import datetime
from corretora import Corretora
from util import Util

class Leilao:

    def compra(corretoraParte, corretoraContraparte, ativo, executarOrdens = False, idOrdem = 0):

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

            if (qtdNegociada>0) and (qtdNegociada*(corretoraParte.precoCompra-0.01)>Util.retorna_menor_valor_compra(ativo) and corretoraContraparte.saldoBRL>Util.retorna_menor_valor_compra(ativo)):#nao pode ter saldo na mercado de menos de um real
                
                if corretoraParte.saldoBRL < (saldoTotalBRL/8): #eh pra ser deseperado aqui, tenho menos em reais doq um oitavo do totalbrl
                    #quando estou desesperado uso a regra do pnl zero
                    corretoraParte.precoVenda = 0.01+corretoraContraparte.precoCompra*1.01 #pnl zero
                    logging.info('leilao compra vai enviar ordem de venda de {} limitada DESESPERADA a {}'.format(ativo,corretoraParte.precoVenda))
                    vendaCorretoraParte = corretoraParte.enviarOrdemVenda(qtdNegociada, 'limited') 
                    logList['idOrdem'] = vendaCorretoraParte['data']['id']

                else:#todos outros casos
                    corretoraParte.precoVenda = corretoraParte.precoCompra - 0.01 #quando não estou desesperado, pnl maximo
                    logging.info('leilao compra vai enviar ordem de venda de {} limitada NORMAL a {}'.format(ativo,corretoraParte.precoVenda))
                    vendaCorretoraParte = corretoraParte.enviarOrdemVenda(qtdNegociada, 'limited') 
                    logList['idOrdem'] = vendaCorretoraParte['data']['id']
        else:
            logging.info('leilao compra de {} nao vale a pena, {} é menor que 1.01*{}'.format(ativo,(corretoraParte.precoCompra-0.01),corretoraContraparte.precoCompra))

        return logList

    def venda(corretoraParte, corretoraContraparte, ativo, executarOrdens = False, idOrdem = 0):

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
            
            if qtdNegociada > 0 and qtdNegociada>Util.retorna_menor_quantidade_venda(ativo):

                if corretoraContraparte.saldoBRL < (saldoTotalBRL/8): #eh pra ser deseperado aqui, tenho menos em reais na mercado doq um decimo do totalbrl
                    #quando estou desesperado uso a regra do pnl zero
                    corretoraParte.precoCompra = corretoraContraparte.precoVenda*0.99-0.01
                    logging.info('leilao venda de vai enviar ordem de compra de {} limitada DESESPERADA a {}'.format(ativo,corretoraParte.precoCompra))
                    CompraCorretoraParte = corretoraParte.enviarOrdemCompra(qtdNegociada, 'limited') #ta certo isso lucas?
                    logList['idOrdem'] = CompraCorretoraParte['data']['id']

                else:#todos outros casos
                    corretoraParte.precoCompra = corretoraParte.precoVenda + 0.01 #quando não estou desesperado, uso a regra do um centavo
                    logging.info('leilao venda de vai enviar ordem de venda de {} limitada NORMAL a {}'.format(ativo,corretoraParte.precoCompra))
                    CompraCorretoraParte = corretoraParte.enviarOrdemCompra(qtdNegociada, 'limited') #ta certo isso lucas?
                    logList['idOrdem'] = CompraCorretoraParte['data']['id']
        else:
            logging.info('leilao venda de {} nao vale a pena, {} é maior que 0.99*{}'.format(ativo,(corretoraParte.precoVenda+0.01),corretoraContraparte.precoVenda))

        return logList

    def cancela_ordens_e_compra_na_mercado(corretoraParte, corretoraContraparte, ativo, executarOrdens = False, idOrdem = 0):

        logList = {'sucesso': False, 'Pnl': 0 , 'idOrdem':0}
        
        if idOrdem > 0:#verifica se tem ordem sendo executada
            ordem = corretoraParte.obterOrdemPorId(idOrdem)
            qtd_executada = float(ordem['data']['executed'])
            preco_executado = float(ordem['data']['price'])
            
            if (preco_executado != corretoraParte.precoCompra):
                logging.info('leilao compra vai cancelar ordem {} de {} pq nao sou o primeiro da fila'.format(idOrdem,ativo))
                corretoraParte.cancelarOrdem(idOrdem)
            elif (qtd_executada >0):
                logging.info('leilao compra vai cancelar ordem {} de {} pq fui executado'.format(idOrdem,ativo))
                corretoraParte.cancelarOrdem(idOrdem)
            elif (preco_executado < 1.01 * corretoraContraparte.precoCompra):
                logging.info('leilao compra vai cancelar ordem {} de {} pq o pnl esta dando negativo'.format(idOrdem,ativo))
                corretoraParte.cancelarOrdem(idOrdem)
            else:
                logList['idOrdem'] = idOrdem
            
            minimo_valor_que_posso_comprar = Util.retorna_menor_valor_compra(ativo)

            if executarOrdens and qtd_executada*corretoraParte.precoCompra > minimo_valor_que_posso_comprar: #mais de xxx reais executado
                
                logging.info('leilao compra vai zerar ordem executada {} de {} na outra corretora'.format(idOrdem,ativo))
                corretoraContraparte.enviarOrdemCompra(qtd_executada, 'market')#zerando o risco na mercado bitcoin
                logList['sucesso'] = True
                logList['Pnl'] = qtd_executada*abs((preco_executado-corretoraContraparte.precoCompra))
                                
                return logList
        
            corretoraParte.atualizarSaldo()
            corretoraContraparte.atualizarSaldo()
        
        return logList

    def cancela_ordens_e_vende_na_mercado(corretoraParte, corretoraContraparte, ativo, executarOrdens = False, idOrdem = 0):

        logList = {'sucesso': False, 'Pnl': 0 , 'idOrdem':0}

        if idOrdem > 0:#verifica se tem ordem sendo executada
            ordem = corretoraParte.obterOrdemPorId(idOrdem)             
            qtd_executada = float(ordem['data']['executed'])
            preco_executado = float(ordem['data']['price'])
            
            if (preco_executado != corretoraParte.precoVenda):
                logging.info('leilao venda vai cancelar ordem {} de {} pq nao sou o primeiro da fila'.format(idOrdem,ativo))
                corretoraParte.cancelarOrdem(idOrdem)
            elif (qtd_executada >0):
                logging.info('leilao venda vai cancelar ordem {} de {} pq fui executado'.format(idOrdem,ativo))
                corretoraParte.cancelarOrdem(idOrdem)
            elif (preco_executado > 0.99 * corretoraContraparte.precoVenda):
                logging.info('leilao venda vai cancelar ordem {} de {} pq o pnl esta dando negativo'.format(idOrdem,ativo))
                corretoraParte.cancelarOrdem(idOrdem)
            else:
                logList['idOrdem'] = idOrdem
           
            minima_quantidade_que_posso_vender = Util.retorna_menor_quantidade_venda(ativo)

            if executarOrdens and qtd_executada > minima_quantidade_que_posso_vender: #mais de xxx quantidade executadas
                
                logging.info('leilao venda vai zerar ordem executada {} de {} na outra corretora'.format(idOrdem,ativo))
                corretoraContraparte.enviarOrdemVenda(qtd_executada, 'market')#zerando o risco na mercado bitcoin
                logList['sucesso'] = True
                logList['Pnl'] = qtd_executada*abs((corretoraContraparte.precoVenda-preco_executado))

                return logList
        
            corretoraParte.atualizarSaldo()
            corretoraContraparte.atualizarSaldo()
        
        return logList