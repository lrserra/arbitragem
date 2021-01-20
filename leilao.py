import time
from datetime import datetime
from corretora import Corretora
from util import Util

class Leilao:

    def run(corretoraParte, corretoraContraparte, ativo, executarOrdens = False, idOrdem = 0, qtdExecutada = 0):

        logList = {'sucesso': False, 'ordemEnviada': False}

        corretoraParte.atualizarSaldo()
        corretoraContraparte.atualizarSaldo()

        saldoTotalCrypto = corretoraParte.saldoCrypto + corretoraContraparte.saldoCrypto
        
        if corretoraParte.saldoCrypto < (saldoTotalCrypto/2): #Iniciar leilão compra
            qtdNegociada = abs(corretoraContraparte - corretoraParte)/2

            if idOrdem > 0:
                ordem = corretoraParte.obterOrdemPorId(idOrdem)
                
                if ordem['data']['executed'] > 0:
                    corretoraContraparte.enviarOrdemCompra(ordem['data']['executed'] - qtdExecutada, 'market')
                    qtdExecutada += ordem['data']['executed']
                elif corretoraParte.precoCompra == ordem['data']['price']: # a minha ordem é a primeira na fila a ser comprada
                    if ordem['data']['executed'] > 0:
                        corretoraContraparte.enviarOrdemCompra(ordem['data']['executed'] - qtdExecutada, 'market')# compra a mercado da mesma quantidade executada na venda
                        qtdExecutada += ordem['data']['executed']
                else:
                    corretoraParte.cancelarOrdem(idOrdem)

        if corretoraParte.precoCompra >= 1.095 * corretoraContraparte.precoCompra:
            # Vender crypto na corretora parte
            corretoraParte.precoCompra = corretoraParte.precoCompra - 0.1 
            vendaCorretoraParte = corretoraParte.enviarOrdemVenda(qtdNegociada, 'limited')
            idOrdem = vendaCorretoraParte['data']['id']



    '''if retornoCompra['sucesso']== False and  retornoVenda['sucesso'] == False: #liga leilão
        if saldocripto_corretora_mercado < saldo_total_cripto/2: #liga leilao de compra
            
            qty = abs(quantidade_brasil - quantidade_mercado)/2 #sempre positivo

            #se minha ordem não é a primeira no book, cancelo minha ordem -> o meu preço é diferente da primeira ordem no book
            #se executou alguma coisa ja compra cripto no mercado a mercado
            
            if brasilBitcoin.precoCompra >= 1.095*mercadoBitcoin.precoCompra:
                #*vende cripto na brasil limitada*
                #envia ordem de venda limitada na brasil, quantidade = qty, preço = brasilBitcoin.precoCompra - 1 centavo
                
                #se tiver ordens executadas
                    #compra cripto na mercado a mercado, na quantidade executada
            else:
                #cancelar todas ordens

        elif saldocripto_corretora_brasil < saldo_total_cripto/2:

            qty = abs(quantidade_mercado - quantidade_brasil)/2

            #se minha ordem não é a primeira no book, cancelo minha ordem -> o meu preço é diferente da primeira ordem no book
            #se executou alguma coisa ja vendo cripto no mercado a mercado
            
            if brasilBitcoin.precoVenda <= (1-0.095)*mercadoBitcoin.precoVenda:
                #*compra cripto na brasil limitada*
                #envia ordem de compra limitada na brasil, quantidade = qty, preço = brasilBitcoin.precoVenda + 1 centavo
                
                #se tiver ordens executadas
                    #vende cripto na mercado a mercado
            else:
                #cancelar todas ordens
        '''