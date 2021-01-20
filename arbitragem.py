import requests
import time
from datetime import datetime
from corretora import Corretora
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
                            corretoraCompra.enviarOrdemCompra(qtdNegociada, 'market')
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
                        logList['ErroSaldo'] = 'Saldo insuficiente para operar o ativo {}.'.format(ativo)

                else:
                    condicao = False
                    logList['sucesso'] = False
                    logList['ErroPnl'] = 'PnL({}) menor que a corretagem({}) do ativo {}.'.format(pnl, financeiroCorretagem, ativo)

            else:
                condicao = False
                logList['sucesso'] = False

        return logList