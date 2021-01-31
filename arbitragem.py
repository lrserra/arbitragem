import requests
import time
import logging
from datetime import datetime
from corretora import Corretora
from ordem import Ordem
from util import Util

class Arbitragem:

    def processar(corretoraCompra:Corretora, corretoraVenda:Corretora, ativo, executarOrdens = False):
        existe_arbitragem = True
        indexOrdem = 0
        pnl = 0
        retorno_compra = Ordem()
        retorno_venda = Ordem()
        
        # Obtendo a maior e menor quantidade de compra e venda entre as corretoras
        maiorQtd = max(corretoraCompra.ordem.quantidade_compra, corretoraVenda.ordem.quantidade_venda)
        menorQtd = min(corretoraCompra.ordem.quantidade_compra, corretoraVenda.ordem.quantidade_venda)
        
        # Na estratégia, consideramos negociar a partir da menor quantidade
        qtdNegociada = menorQtd

        while existe_arbitragem and (menorQtd < maiorQtd):

            try:
            # Verifica se existe arbitragem entre as corretoras
                if corretoraCompra.ordem.preco_compra < corretoraVenda.ordem.preco_venda:               

                    # Verifica em termos financeiros levando em conta as corretagens de compra e venda, se a operação vale a pena
                    financeiroCorretagem = corretoraCompra.obter_financeiro_corretagem_compra_por_corretora(qtdNegociada) + corretoraVenda.obter_financeiro_corretagem_venda_por_corretora(qtdNegociada)
                    pnl = corretoraVenda.obter_amount_venda(qtdNegociada) - corretoraCompra.obter_amount_compra(qtdNegociada)

                    # Teste se o financeiro com a corretagem é menor que o pnl da operação
                    if financeiroCorretagem < pnl:
                        # Condição para que verificar se o saldo em reais e crypto são suficientes para a operação
                        if (corretoraCompra.saldoBRL >= corretoraCompra.obter_amount_compra(qtdNegociada) and corretoraCompra.obter_amount_compra(qtdNegociada) > Util.retorna_menor_valor_compra(ativo)) and (corretoraVenda.saldoCrypto >= qtdNegociada and qtdNegociada > Util.retorna_menor_quantidade_venda(ativo)):

                            if executarOrdens:
                                # Atualiza a quantidade negociada e o tipo de ordem 
                                corretoraCompra.ordem.quantidade_negociada = qtdNegociada
                                corretoraVenda.ordem.quantidade_negociada = qtdNegociada
                                corretoraCompra.ordem.tipo_ordem = 'market'
                                corretoraVenda.ordem.tipo_ordem = 'market'
                                logging.info('arbitragem vai comprar {}{} @{} na {} e vender @{} na {}'.format(round(qtdNegociada,4),ativo,round(corretoraCompra.ordem.preco_compra,4),corretoraCompra.nome,round(corretoraVenda.ordem.preco_venda,4),corretoraVenda.nome))
                                retorno_compra = corretoraCompra.enviar_ordem_compra(corretoraCompra.ordem)
                                retorno_venda = corretoraVenda.enviar_ordem_venda(corretoraVenda.ordem)

                                corretoraCompra.atualizar_saldo()
                                corretoraVenda.atualizar_saldo()

                            indexOrdem += 1

                            # Trecho que verifica se a pena ir para a próxima ordem do book dado critério de preço atendido
                            if corretoraCompra.ordem.quantidade_compra <  corretoraVenda.ordem.quantidade_venda:
                                corretoraCompra.obter_ordem_book_por_indice(indexOrdem)
                                qtdNegociada = min(corretoraCompra.ordem.quantidade_compra, (corretoraVenda.ordem.quantidade_venda - menorQtd))
                            else:
                                corretoraVenda.obter_ordem_book_por_indice(indexOrdem)
                                qtdNegociada = min(corretoraVenda.ordem.quantidade_venda, (corretoraCompra.ordem.quantidade_compra - menorQtd))

                            menorQtd += min(corretoraCompra.ordem.quantidade_compra, corretoraVenda.ordem.quantidade_venda) 

                        else:
                            logging.info('arbitragem nao vai enviar ordem de {} porque saldo {} nao é suficiente'.format(ativo,round(corretoraCompra.saldoBRL,2)))
                            existe_arbitragem = False
                    else:
                        logging.info('arbitragem nao vai enviar ordem de {} porque pnl ({}) é menor que corretagem ({})'.format(ativo,round(pnl,2),round(financeiroCorretagem,2)))
                        existe_arbitragem = False
                else:
                    logging.info('arbitragem nao vai enviar ordem de {} porque preco compra ({}) é maior que preco venda ({})'.format(ativo,round(corretoraCompra.ordem.preco_compra,2),round(corretoraVenda.ordem.preco_venda,2)))
                    existe_arbitragem = False
            except Exception as erro:
                msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de arbitragem, método: processar.', erro)
                raise Exception(msg_erro)
        
        return retorno_venda, pnl
