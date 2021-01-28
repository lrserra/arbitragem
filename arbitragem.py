import requests
import time
import logging
from datetime import datetime
from corretora import Corretora
from ordem import Ordem
from util import Util

class Arbitragem:

    def run(corretoraCompra, corretoraVenda, ativo, executarOrdens = False):
        condicao = True
        ordem = 0
        
        logList = {'sucesso': False, 'ErroPnl':'--', 'ErroSaldo':'--', 'logVenda':'--', 'logCompra': '--'}
        
        maiorQtd = max(corretoraCompra.qtdCompra, corretoraVenda.qtdVenda)
        menorQtd = min(corretoraCompra.qtdCompra, corretoraVenda.qtdVenda)
        qtdNegociada = menorQtd

        while condicao and (menorQtd < maiorQtd):

            if corretoraCompra.precoCompra < corretoraVenda.precoVenda:               

                financeiroCorretagem = corretoraCompra.obterFinanceiroCorretagemCompraPorCorretora(qtdNegociada) + corretoraVenda.obterFinanceiroCorretagemVendaPorCorretora(qtdNegociada)
                pnl = corretoraVenda.obterAmountVenda(qtdNegociada) - corretoraCompra.obterAmountCompra(qtdNegociada)

                if financeiroCorretagem < pnl:
                    
                    corretoraCompra.atualizarSaldo()
                    corretoraVenda.atualizarSaldo()

                    #Implementar ordem fracionada
                    if corretoraCompra.saldoBRL >= corretoraCompra.obterAmountCompra(qtdNegociada) and corretoraVenda.saldoCrypto >= qtdNegociada:

                        logCompra = [ativo, corretoraCompra.nome, 'C', corretoraCompra.precoCompra, qtdNegociada, financeiroCorretagem, pnl, datetime.now()]

                        logVenda = [ativo, corretoraVenda.nome, 'V', corretoraVenda.precoVenda, qtdNegociada, financeiroCorretagem, pnl, datetime.now()]

                        logList['sucesso'] = True
                        logList['logCompra'] = logCompra
                        logList['logVenda'] = logVenda
                        logList['Pnl'] = pnl

                        if executarOrdens:
                            logging.info('arbitragem envia ordem de compra a marcado da quantidade {}'.format(qtdNegociada))
                            corretoraCompra.enviarOrdemCompra(qtdNegociada, 'market')
                            logging.info('arbitragem envia ordem de venda a marcado da quantidade {}'.format(qtdNegociada))
                            corretoraVenda.enviarOrdemVenda(qtdNegociada, 'market')

                        # Atualizando a carteira
                        corretoraCompra.saldoBRL -= corretoraCompra.obterAmountCompra(qtdNegociada)
                        corretoraCompra.saldoCrypto += qtdNegociada
                   
                        corretoraVenda.saldoBRL += corretoraVenda.obterAmountVenda(qtdNegociada)
                        corretoraVenda.saldoCrypto -= qtdNegociada
                        ordem += 1

                        if corretoraCompra.qtdCompra <  corretoraVenda.qtdVenda:
                            corretoraCompra.carregarBooks(ativo, ordem)
                            qtdNegociada = min(corretoraCompra.qtdCompra, (corretoraVenda.qtdVenda - menorQtd))
                        else:
                            corretoraVenda.carregarBooks(ativo, ordem)
                            qtdNegociada = min(corretoraVenda.qtdVenda, (corretoraCompra.qtdCompra - menorQtd))

                        menorQtd += min(corretoraCompra.qtdCompra, corretoraVenda.qtdVenda) 

                    else:
                        condicao = False
                        logList['sucesso'] = False
                        logList['ErroSaldo'] = 'arbitragem deu saldo insuficiente para operar o ativo {}.'.format(ativo)
                        logging.info(logList['ErroSaldo'])

                else:
                    condicao = False
                    logList['sucesso'] = False
                    logList['ErroPnl'] = 'arbitragem deu que PnL({}) menor que a corretagem({}) do ativo {}.'.format(pnl, financeiroCorretagem, ativo)
                    logging.info(logList['ErroPnl'])

            else:
                condicao = False
                logList['sucesso'] = False

        return logList

    def processar(corretoraCompra:Corretora, corretoraVenda:Corretora, ativo, executarOrdens = False):
        condicao = True
        indexOrdem = 0
        
        logList = {'sucesso': False, 'ErroPnl':'--', 'ErroSaldo':'--', 'logVenda':'--', 'logCompra': '--'}
        
        # Obtendo a maior e menor quantidade de compra e venda entre as corretoras
        maiorQtd = max(corretoraCompra.ordem.quantidade_compra, corretoraVenda.ordem.quantidade_venda)
        menorQtd = min(corretoraCompra.ordem.quantidade_compra, corretoraVenda.ordem.quantidade_venda)
        
        # Na estratégia, consideramos negociar a partir da menor quantidade
        qtdNegociada = menorQtd

        while condicao and (menorQtd < maiorQtd):

            try:
            # Verifica se existe arbitragem entre as corretoras
                if corretoraCompra.ordem.preco_compra < corretoraVenda.ordem.preco_venda:               

                    # Verifica em termos financeiros levando em conta as corretagens de compra e venda, se a operação vale a pena
                    financeiroCorretagem = corretoraCompra.obter_financeiro_corretagem_compra_por_corretora(qtdNegociada) + corretoraVenda.obter_financeiro_corretagem_venda_por_corretora(qtdNegociada)
                    pnl = corretoraVenda.obter_amount_venda(qtdNegociada) - corretoraCompra.obter_amount_compra(qtdNegociada)

                    # Teste se o financeiro com a corretagem é menor que o pnl da operação
                    if financeiroCorretagem < pnl:
                        
                        # Atualiza o saldo de crypto e BRL nas corretoras
                        corretoraCompra.atualizar_saldo()
                        corretoraVenda.atualizar_saldo()

                        # Condição para que verificar se o saldo em reais e crypto são suficientes para a operação
                        if corretoraCompra.saldoBRL >= corretoraCompra.obter_amount_compra(qtdNegociada) and corretoraVenda.saldoCrypto >= qtdNegociada:

                            logList['sucesso'] = True
                            logList['Pnl'] = pnl

                            if executarOrdens:
                                # Atualiza a quantidade negociada e o tipo de ordem 
                                corretoraCompra.ordem.quantidade_negociada = qtdNegociada
                                corretoraVenda.ordem.quantidade_negociada = qtdNegociada
                                corretoraCompra.ordem.tipo_ordem = 'market'
                                corretoraVenda.ordem.tipo_ordem = 'market'

                                corretoraCompra.enviar_ordem_compra(corretoraCompra.ordem)
                                corretoraVenda.enviar_ordem_venda(corretoraVenda.ordem)

                            # Atualizando a carteira
                            corretoraCompra.saldoBRL -= corretoraCompra.obter_amount_compra(qtdNegociada)
                            corretoraCompra.saldoCrypto += qtdNegociada
                    
                            corretoraVenda.saldoBRL += corretoraVenda.obter_amount_venda(qtdNegociada)
                            corretoraVenda.saldoCrypto -= qtdNegociada
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
                            condicao = False
                            logList['sucesso'] = False
                            logList['ErroSaldo'] = 'Saldo insuficiente para operar o ativo {}.'.format(ativo)

                    else:
                        condicao = False
                        logList['sucesso'] = False
                        logList['ErroPnl'] = 'PnL({}) menor que a corretagem({}) do ativo {}.'.format(pnl, financeiroCorretagem, ativo)

                else:
                    condicao = False
                    logList['sucesso'] = False
            except Exception as erro:
                msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de arbitragem, método: processar.', erro)
                raise Exception(msg_erro)
        return logList
