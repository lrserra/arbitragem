import time
import logging
from datetime import datetime
from corretora import Corretora
from util import Util

class Leilao:

    def compra(corretoraParte, corretoraContraparte, ativo, executarOrdens = False, idOrdem = 0):

        #ja considerando que cancelou as ordens
        logList = {'sucesso': False, 'idOrdem': 0, 'status': '' }
        
        try:
            # Lista de moedas que está rodando de forma parametrizada
            qtd_de_moedas = len(Util.obter_lista_de_moedas())

            # Atualiza o saldo de crypto e BRL nas corretoras
            corretoraParte.atualizar_saldo()
            corretoraContraparte.atualizar_saldo()

            # Soma do saldo total em reais
            saldoTotalBRL = corretoraParte.saldoBRL + corretoraContraparte.saldoBRL
            
            #corretoraParte tem que ser Brasil, pq la a liquidez é menor e mais facil de fazer leilão
            #o preço que eu posso vender é maior doq o preço que posso comprar
            if ((corretoraParte.ordem.preco_compra-0.01) >= 1.01 * corretoraContraparte.ordem.preco_compra):
                

                # Gostaria de vender no leilão pelo 1/4 do que eu tenho de saldo em crypto
                gostaria_de_vender = corretoraParte.saldoCrypto/4
                maximo_que_consigo_zerar = corretoraContraparte.saldoBRL/(qtd_de_moedas*corretoraContraparte.ordem.preco_compra*1.01)
                qtdNegociada = min(gostaria_de_vender,maximo_que_consigo_zerar)

                # Nao pode ter saldo na mercado de menos de um real
                if (qtdNegociada>0) and (qtdNegociada*(corretoraParte.ordem.preco_compra-0.01)>Util.retorna_menor_valor_compra(ativo) and corretoraContraparte.saldoBRL > Util.retorna_menor_valor_compra(ativo)):
                    
                    if corretoraParte.saldoBRL < (saldoTotalBRL/8): #eh pra ser deseperado aqui, tenho menos em reais doq um oitavo do totalbrl
                        #quando estou desesperado uso a regra do pnl zero
                        corretoraParte.ordem.preco_venda = 0.01+corretoraContraparte.ordem.preco_compra*1.01 #pnl zero

                    else:#todos outros casos
                        corretoraParte.ordem.precoVenda = corretoraParte.ordem.preco_compra - 0.01 #quando não estou desesperado, pnl maximo
                    logging.info('leilao compra vai enviar ordem de venda de {} limitada DESESPERADA a {}'.format(ativo,corretoraParte.precoVenda))
                    corretoraParte.ordem.quantidade_negociada = qtdNegociada
                    corretoraParte.ordem.tipo_ordem = 'limited'
                    vendaCorretoraParte = corretoraParte.enviar_ordem_venda(corretoraParte.ordem) 

                    logList['idOrdem'] = vendaCorretoraParte['data']['id']
                    logList['status'] = vendaCorretoraParte['data']['status']


                else:#todos outros casos
                    corretoraParte.precoVenda = corretoraParte.precoCompra - 0.01 #quando não estou desesperado, pnl maximo
                    logging.info('leilao compra vai enviar ordem de venda de {} limitada NORMAL a {}'.format(ativo,corretoraParte.precoVenda))
                    vendaCorretoraParte = corretoraParte.enviarOrdemVenda(qtdNegociada, 'limited') 
                    logList['idOrdem'] = vendaCorretoraParte['data']['id']
            else:
                logging.info('leilao compra de {} nao vale a pena, {} é menor que 1.01*{}'.format(ativo,(corretoraParte.precoCompra-0.01),corretoraContraparte.precoCompra))

        except Exception as erro:
                msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de leilão, método: compra. Msg Corretora: {}. - '.format(vendaCorretoraParte['message']), erro)
                raise Exception(msg_erro)


        return logList

    def venda(corretoraParte, corretoraContraparte, ativo, executarOrdens = False, idOrdem = 0):

        #ja considerando que cancelou as ordens
        logList = {'sucesso': False, 'idOrdem': 0 }
        try:
            qtd_de_moedas = len(Util.obter_lista_de_moedas())

            corretoraParte.atualizar_saldo()
            corretoraContraparte.atualizar_saldo()

            saldoTotalBRL = corretoraParte.saldoBRL + corretoraContraparte.saldoBRL
            

            #corretoraParte tem que ser Brasil, pq la a liquidez é menor e mais facil de fazer leilão
            if ((corretoraParte.ordem.preco_venda+0.01) <= 0.99 * corretoraContraparte.ordem.preco_venda):# o preço que eu posso comprar é menor doq o preço que posso vender
                
                gostaria_de_comprar = corretoraParte.saldoBRL/(qtd_de_moedas*corretoraParte.ordem.preco_venda+0.01)
                maximo_que_consigo_zerar = corretoraContraparte.saldoCrypto/4
                
                # Mínimo entre o que eu gostaria de comprar com o máximo que consigo zerar na outra ponta
                qtdNegociada = min(gostaria_de_comprar,maximo_que_consigo_zerar)
                
                # Se quantidade negociada maior que zero e maior que a quantidade mínima permitida de venda
                if qtdNegociada > 0 and qtdNegociada > Util.retorna_menor_quantidade_venda(ativo):

                    if corretoraContraparte.saldoBRL < (saldoTotalBRL/8): #eh pra ser deseperado aqui, tenho menos em reais na mercado doq um decimo do totalbrl
                        #quando estou desesperado uso a regra do pnl zero
                        logging.info('leilao venda de vai enviar ordem de compra de {} limitada DESESPERADA a {}'.format(ativo,corretoraParte.ordem.preco_compra))
                    
                        corretoraParte.ordem.preco_compra = corretoraContraparte.ordem.preco_venda*0.99-0.01

                    else:#todos outros casos
                      logging.info('leilao venda de vai enviar ordem de venda de {} limitada NORMAL a {}'.format(ativo,corretoraParte.ordem.preco_venda))
                    
                        corretoraParte.ordem.preco_compra = corretoraParte.ordem.preco_venda + 0.01 #quando não estou desesperado, uso a regra do um centavo
                    
                    corretoraParte.ordem.quantidade_negociada = qtdNegociada
                    corretoraParte.ordem.tipo_ordem = 'limited'    
                    CompraCorretoraParte = corretoraParte.enviar_ordem_compra(corretoraParte.ordem) #ta certo isso lucas?
                    logList['idOrdem'] = CompraCorretoraParte['data']['id']
                    logList['status'] = CompraCorretoraParte['data']['status']
                else:
                     logging.info('leilao venda de {} nao vale a pena, {} é maior que 0.99*{}'.format(ativo,(corretoraParte.precoVenda+0.01),corretoraContraparte.precoVenda))
        except Exception as erro:
                msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de leilão, método: venda. Msg Corretora: {}. - '.format(CompraCorretoraParte['message']), erro)
                raise Exception(msg_erro)
        

        return logList

    def cancela_ordens_e_compra_na_mercado(corretoraParte, corretoraContraparte, ativo, executarOrdens = False, idOrdem = 0):

        logList = {'sucesso': False, 'Pnl': 0 , 'idOrdem':0}

        
        if idOrdem > 0:#verifica se tem ordem sendo executada
            ordem = corretoraParte.obter_ordem_por_id(idOrdem)
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


        try:
            # Verifica se tem ordem executada na corretora
            if idOrdem > 0:
                ordem = corretoraParte.obter_ordem_por_id(idOrdem)
                qtd_executada = float(ordem['data']['executed'])
                preco_executado = float(ordem['data']['price'])
                

                logging.info('leilao compra vai zerar ordem executada {} de {} na outra corretora'.format(idOrdem,ativo))
                corretoraContraparte.enviar_ordem_compra(qtd_executada, 'market')#zerando o risco na mercado bitcoin
                logList['sucesso'] = True
                logList['Pnl'] = qtd_executada*abs((preco_executado-corretoraContraparte.ordem.preco_compra))
                                
                return logList
        
            corretoraParte.atualizar_saldo()
            corretoraContraparte.atualizar_saldo()

                # Se houve mudança de preço ou a quantidade executa é maior que zero ou o preço executado é menor que preço de compra + corretagem, cancela  ordem
                if (preco_executado != corretoraParte.ordem.preco_compra) or (qtd_executada >0) or (preco_executado < 1.01 * corretoraContraparte.ordem.preco_compra):
                    corretoraParte.cancelar_ordem(idOrdem)
                else:
                    logList['idOrdem'] = idOrdem 
                
                # Obtém o mínimo valor que se pode comprar na corretora por moeda
                minimo_valor_que_posso_comprar = Util.retorna_menor_valor_compra(ativo)

                if executarOrdens and qtd_executada*corretoraParte.ordem.preco_compra > minimo_valor_que_posso_comprar: #mais de xxx reais executado
                    
                    # Zera o risco na outra corretora com uma operação à mercado
                    corretoraContraparte.enviar_ordem_compra(qtd_executada, 'market')
                    logList['sucesso'] = True
                    logList['Pnl'] = qtd_executada*abs((preco_executado-corretoraContraparte.ordem.preco_compra))
                                    
                    return logList
            
                corretoraParte.atualizar_saldo()
                corretoraContraparte.atualizar_saldo()
        except Exception as erro:
            msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de leilão, método: cancela_ordens_e_compra_na_mercado.', erro)
            raise Exception(msg_erro)

        
        return logList

    def cancela_ordens_e_vende_na_mercado(corretoraParte, corretoraContraparte, ativo, executarOrdens = False, idOrdem = 0):

        logList = {'sucesso': False, 'Pnl': 0 , 'idOrdem':0}


        try:  
           if idOrdem > 0:#verifica se tem ordem sendo executada
            ordem = corretoraParte.obter_ordem_por_id(idOrdem)             
            qtd_executada = float(ordem['data']['executed'])
            preco_executado = float(ordem['data']['price'])
            
            if (preco_executado != corretoraParte.ordem.preco_venda):
                logging.info('leilao venda vai cancelar ordem {} de {} pq nao sou o primeiro da fila'.format(idOrdem,ativo))
                corretoraParte.cancelarOrdem(idOrdem)
            elif (qtd_executada >0):
                logging.info('leilao venda vai cancelar ordem {} de {} pq fui executado'.format(idOrdem,ativo))
                corretoraParte.cancelarOrdem(idOrdem)
            elif (preco_executado > 0.99 * corretoraContraparte.ordem.preco_venda):
                logging.info('leilao venda vai cancelar ordem {} de {} pq o pnl esta dando negativo'.format(idOrdem,ativo))
                corretoraParte.cancelarOrdem(idOrdem)
            else:
                logList['idOrdem'] = idOrdem
           
            minima_quantidade_que_posso_vender = Util.retorna_menor_quantidade_venda(ativo)

            if executarOrdens and qtd_executada > minima_quantidade_que_posso_vender: #mais de xxx quantidade executadas
                
                logging.info('leilao venda vai zerar ordem executada {} de {} na outra corretora'.format(idOrdem,ativo))
                corretoraContraparte.enviarOrdemVenda(qtd_executada, 'market')#zerando o risco na mercado bitcoin
                logList['sucesso'] = True
                logList['Pnl'] = qtd_executada*abs((corretoraContraparte.ordem.preco_venda-preco_executado))

                if executarOrdens and qtd_executada > minima_quantidade_que_posso_vender: #mais de xxx quantidade executadas
                    
                    corretoraContraparte.enviarOrdemVenda(qtd_executada, 'market')#zerando o risco na mercado bitcoin
                    logList['sucesso'] = True
                    logList['Pnl'] = qtd_executada*abs((corretoraContraparte.ordem.preco_venda-preco_executado))

                    return logList
            
                corretoraParte.atualizar_saldo()
                corretoraContraparte.atualizar_saldo()
        except Exception as erro:
            msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de leilão, método: cancela_ordens_e_vende_na_mercado.', erro)
            raise Exception(msg_erro)
        return logList