 
import time
import logging
from datetime import datetime
from corretora import Corretora
from util import Util
from ordem import Ordem

class Leilao:

    def compra(corretoraParte, corretoraContraparte, ativo, executarOrdens = False):

        retorno_venda_corretora_parte = Ordem()
        
        try:
            # Lista de moedas que está rodando de forma parametrizada
            qtd_de_moedas = len(Util.obter_lista_de_moedas())

            # Soma do saldo total em reais
            saldoTotalBRL = corretoraParte.saldoBRL + corretoraContraparte.saldoBRL
            
            # Valida se existe oportunidade de leilão
            if ((corretoraParte.ordem.preco_compra-0.01) >= 1.01 * corretoraContraparte.ordem.preco_compra):
                
                # Gostaria de vender no leilão pelo 1/4 do que eu tenho de saldo em crypto
                gostaria_de_vender = corretoraParte.saldoCrypto / 4
                maximo_que_consigo_zerar = corretoraContraparte.saldoBRL / (qtd_de_moedas*corretoraContraparte.ordem.preco_compra * 1.01)
                qtdNegociada = min(gostaria_de_vender,maximo_que_consigo_zerar)

                # Nao pode ter saldo na mercado de menos de um real
                if (qtdNegociada*(corretoraParte.ordem.preco_compra-0.01) > Util.retorna_menor_valor_compra(ativo) and corretoraContraparte.saldoBRL > Util.retorna_menor_valor_compra(ativo)):
                    
                    corretoraParte.ordem.preco_venda = corretoraParte.ordem.preco_compra - 0.01
                    logging.info('Leilão compra vai enviar ordem de venda de {} limitada a {}'.format(ativo,corretoraParte.ordem.preco_venda))

                    if executarOrdens:
                        corretoraParte.ordem.quantidade_negociada = qtdNegociada
                        corretoraParte.ordem.tipo_ordem = 'limited'
                        retorno_venda_corretora_parte = corretoraParte.enviar_ordem_venda(corretoraParte.ordem)  
            else:
                logging.info('leilao compra de {} nao vale a pena, {} é menor que 1.01*{}'.format(ativo,(corretoraParte.ordem.preco_compra-0.01),corretoraContraparte.ordem.preco_compra))

        except Exception as erro:
                msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de leilão, método: compra. Msg Corretora:', erro)
                raise Exception(msg_erro)

        return retorno_venda_corretora_parte

    def venda(corretoraParte, corretoraContraparte, ativo, executarOrdens = False):

        retorno_compra_corretora_parte = Ordem()

        try:
            qtd_de_moedas = len(Util.obter_lista_de_moedas())

            saldoTotalBRL = corretoraParte.saldoBRL + corretoraContraparte.saldoBRL
            
            # 0.99 = 1 - Soma das corretagens
            if ((corretoraParte.ordem.preco_venda+0.01) <= 0.99 * corretoraContraparte.ordem.preco_venda):
                
                gostaria_de_comprar = corretoraParte.saldoBRL / (qtd_de_moedas * corretoraParte.ordem.preco_venda + 0.01)
                maximo_que_consigo_zerar = corretoraContraparte.saldoCrypto / 4
                
                # Mínimo entre o que eu gostaria de comprar com o máximo que consigo zerar na outra ponta
                qtdNegociada = min(gostaria_de_comprar,maximo_que_consigo_zerar)
                
                # Se quantidade negociada maior que a quantidade mínima permitida de venda
                if qtdNegociada > Util.retorna_menor_quantidade_venda(ativo):

                    logging.info('leilao venda de vai enviar ordem de venda de {} limitada a {}'.format(ativo,corretoraParte.ordem.preco_venda))
                    corretoraParte.ordem.preco_compra = corretoraParte.ordem.preco_venda + 0.01 
                    if executarOrdens:
                        corretoraParte.ordem.quantidade_negociada = qtdNegociada
                        corretoraParte.ordem.tipo_ordem = 'limited'    
                        retorno_compra_corretora_parte = corretoraParte.enviar_ordem_compra(corretoraParte.ordem)
                
            else:
                logging.info('leilao venda de {} nao vale a pena, {} é maior que 0.99*{}'.format(ativo,(corretoraParte.ordem.preco_venda+0.01),corretoraContraparte.ordem.preco_venda))
        except Exception as erro:
                msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de leilão, método: venda. Msg Corretora:', erro)
                raise Exception(msg_erro)
        
        return retorno_compra_corretora_parte

    #def cancela_ordens_e_compra_na_mercado(corretoraParte, corretoraContraparte, ativo, executarOrdens = False, idOrdem = 0, status='new'):
    def cancela_ordens_e_compra_na_mercado(corretoraParte, corretoraContraparte, ativo, executarOrdens, ordem_leilao_compra):

        retorno_compra = Ordem()

        try:
            if ordem_leilao_compra.status == 'filled' and ordem_leilao_compra.id == False: # verifica se a ordem foi executada totalmente (Nesse caso o ID = False)
                
                preco_executado = ordem_leilao_compra.preco_executado
                
                logging.info('leilao compra vai zerar ordem executada {} de {} na outra corretora'.format(ordem_leilao_compra.id,ativo))
                corretoraContraparte.ordem.quantidade_negociada = ordem_leilao_compra.quantidade_executada
                corretoraContraparte.ordem.tipo_ordem = 'market'
                retorno_compra = corretoraContraparte.enviar_ordem_compra(corretoraContraparte.ordem)
                
            elif ordem_leilao_compra.id > 0:

                ordem = corretoraParte.obter_ordem_por_id(ordem_leilao_compra.id)
                
                if (ordem_leilao_compra.preco_venda != corretoraParte.ordem.preco_compra):
                    
                    logging.info('leilao compra vai cancelar ordem {} de {} pq nao sou o primeiro da fila'.format(ordem.id,ativo))
                    corretoraParte.cancelar_ordem(ordem_leilao_compra.id)

                elif (ordem.quantidade_executada > 0):
                    
                    logging.info('leilao compra vai cancelar ordem {} de {} pq fui executado'.format(ordem.id,ativo))
                    corretoraParte.cancelar_ordem(ordem_leilao_compra.id)
                
                elif (ordem_leilao_compra.preco_venda < 1.01 * corretoraContraparte.ordem.preco_compra):
                    
                    logging.info('leilao compra vai cancelar ordem {} de {} pq o pnl esta dando negativo'.format(ordem.id,ativo))
                    corretoraParte.cancelar_ordem(ordem_leilao_compra.id)

                if executarOrdens and ordem.quantidade_executada * corretoraParte.ordem.preco_compra > Util.retorna_menor_valor_compra(ativo): #mais de xxx reais executado
                    
                    # Zera o risco na outra corretora com uma operação à mercado
                    corretoraContraparte.ordem.quantidade_negociada = ordem.quantidade_executada
                    corretoraContraparte.ordem.tipo_ordem = 'market'
                    retorno_compra = corretoraContraparte.enviar_ordem_compra(corretoraContraparte.ordem)
                                
        except Exception as erro:
            msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de leilão, método: cancela_ordens_e_compra_na_mercado.', erro)
            raise Exception(msg_erro)

        return retorno_compra

    def cancela_ordens_e_vende_na_mercado(corretoraParte, corretoraContraparte, ativo, executarOrdens, ordem_leilao_venda):

        retorno_venda = Ordem()

        try:
             
            if ordem_leilao_venda.status == 'filled' and ordem_leilao_venda.id == False:

                corretoraContraparte.ordem.quantidade_negociada = ordem_leilao_venda.quantidade_executada
                corretoraContraparte.ordem.tipo_ordem = 'market'
                retorno_venda = corretoraContraparte.enviar_ordem_venda(corretoraContraparte.ordem)
        
            elif ordem_leilao_venda.id > 0:
                
                ordem = corretoraParte.obter_ordem_por_id(ordem_leilao_venda.id)             
                qtd_executada = ordem.quantidade_executada
                preco_executado = ordem_leilao_venda.preco_executado
            
                if (ordem_leilao_venda.preco_compra != corretoraParte.ordem.preco_venda):
                    
                    logging.info('leilao venda vai cancelar ordem {} de {} pq nao sou o primeiro da fila'.format(ordem.id,ativo))
                    corretoraParte.cancelar_ordem(ordem_leilao_venda.id)
                
                elif (ordem.quantidade_executada >0):
                    
                    logging.info('leilao venda vai cancelar ordem {} de {} pq fui executado'.format(ordem.id,ativo))
                    corretoraParte.cancelar_ordem(ordem_leilao_venda.id)

                elif (ordem_leilao_venda.preco_compra > 0.99 * corretoraContraparte.ordem.preco_venda):
                    
                    logging.info('leilao venda vai cancelar ordem {} de {} pq o pnl esta dando negativo'.format(ordem.id,ativo))
                    corretoraParte.cancelar_ordem(ordem_leilao_venda.id)
            
                if executarOrdens and ordem.quantidade_executada > Util.retorna_menor_quantidade_venda(ativo): 
                    
                    logging.info('leilao venda vai zerar ordem executada {} de {} na outra corretora'.format(ordem.id,ativo))
                    corretoraContraparte.ordem.quantidade_negociada = ordem.quantidade_executada
                    corretoraContraparte.ordem.tipo_ordem = 'market'
                    retorno_venda = corretoraContraparte.enviar_ordem_venda(corretoraContraparte.ordem)
                
        except Exception as erro:
            msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de leilão, método: cancela_ordens_e_vende_na_mercado.', erro)
            raise Exception(msg_erro)
        
        return retorno_venda
