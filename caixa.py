import logging
from corretora import Corretora
from datetime import datetime
from util import Util
import time

class Caixa:
    
    def atualiza_saldo_inicial(lista_de_moedas,corretora_mais_liquida,corretora_menos_liquida):
        '''
        retorna dicionario com saldo inicial de cada moeda
        '''

        saldo_inicial = {}
        saldo_inicial['brl'] = 0

        for moeda in lista_de_moedas:
            
            # Instancia das corretoras por ativo
            CorretoraMaisLiquida = Corretora(corretora_mais_liquida, moeda)
            CorretoraMenosLiquida = Corretora(corretora_menos_liquida, moeda)

            #inicialmente cancela todas ordens abertas na brasil
            CorretoraMenosLiquida.cancelar_todas_ordens(moeda)
            time.sleep(1)

            CorretoraMaisLiquida.atualizar_saldo()
            CorretoraMenosLiquida.atualizar_saldo()

            saldo_inicial['brl'] = saldo_inicial['brl'] + (CorretoraMaisLiquida.saldoBRL + CorretoraMenosLiquida.saldoBRL) #para não contar duas vezes esse cara
            saldo_inicial[moeda] = CorretoraMaisLiquida.saldoCrypto + CorretoraMenosLiquida.saldoCrypto
            
            logging.warning('saldo inicial em {}: {}'.format(moeda,round(saldo_inicial[moeda],4)))
            Util.adicionar_linha_no_saldo('{}|{}|{}'.format(moeda,round(saldo_inicial[moeda],4),datetime.now()))

        logging.warning('saldo inicial em reais: {}'.format(round(saldo_inicial['brl']/len(lista_de_moedas),2)))
        Util.adicionar_linha_no_saldo('{}|{}|{}'.format('BRL',round(saldo_inicial['brl']/len(lista_de_moedas),2),datetime.now()))

        return saldo_inicial


    def zera_o_pnl_em_cripto(corretora_mais_liquida,corretora_menos_liquida):
        '''
        ao longo do dia, nós pagamos corretagem em cripto, então uma vez ao dia é bom comprar essa quantidade novamente
        '''
        saldo_inicial = Util.obter_saldo_inicial()
        saldo_final = {}

        #verifica saldo final, para comparar com inicial
        for moeda in saldo_inicial.keys():
        
            # Instancia das corretoras por ativo
            CorretoraMaisLiquida = Corretora(corretora_mais_liquida, moeda)
            CorretoraMenosLiquida = Corretora(corretora_menos_liquida, moeda)

            #inicialmente cancela todas ordens abertas na brasil
            CorretoraMenosLiquida.cancelar_todas_ordens(moeda)
            time.sleep(1)

            CorretoraMaisLiquida.atualizar_saldo()
            CorretoraMenosLiquida.atualizar_saldo()

            saldo_final[moeda] = CorretoraMaisLiquida.saldoCrypto + CorretoraMenosLiquida.saldoCrypto

            pnl_em_moeda = round(saldo_final[moeda] - saldo_inicial[moeda],4)
            quantidade_a_zerar = round(abs(pnl_em_moeda),4)

            if pnl_em_moeda > 0 and quantidade_a_zerar > Util.retorna_menor_quantidade_venda(moeda):
                if (CorretoraMaisLiquida.ordem.preco_venda > CorretoraMenosLiquida.ordem.preco_venda) and (CorretoraMaisLiquida.saldoCrypto>quantidade_a_zerar): #vamos vender na corretora que paga mais e que tenha saldo
                    logging.info('caixa vai vender {} {} na {} para zerar o pnl'.format(quantidade_a_zerar,moeda,CorretoraMaisLiquida.nome))
                    CorretoraMaisLiquida.ordem.quantidade_negociada = quantidade_a_zerar
                    CorretoraMaisLiquida.ordem.tipo_ordem = 'market'
                    CorretoraMaisLiquida.enviar_ordem_venda(CorretoraMaisLiquida.ordem)
                else:
                    logging.info('caixa vai vender {} {} na {} para zerar o pnl'.format(quantidade_a_zerar,moeda,CorretoraMenosLiquida.nome))
                    CorretoraMenosLiquida.ordem.quantidade_negociada = quantidade_a_zerar
                    CorretoraMenosLiquida.ordem.tipo_ordem = 'market'
                    CorretoraMenosLiquida.enviar_ordem_venda(CorretoraMenosLiquida.ordem)

            elif pnl_em_moeda < 0 and quantidade_a_zerar*CorretoraMaisLiquida.ordem.preco_compra > Util.retorna_menor_valor_compra(moeda):
                if (CorretoraMaisLiquida.ordem.preco_compra < CorretoraMenosLiquida.ordem.preco_compra) and (CorretoraMaisLiquida.saldoBRL>quantidade_a_zerar*CorretoraMaisLiquida.ordem.preco_compra): #vamos comprar na corretora que esta mais barato e que tenha saldo
                    logging.info('caixa vai comprar {} {} na {} para zerar o pnl'.format(quantidade_a_zerar,moeda,CorretoraMaisLiquida.nome))
                    CorretoraMaisLiquida.ordem.quantidade_negociada = quantidade_a_zerar
                    CorretoraMaisLiquida.ordem.tipo_ordem = 'market'
                    CorretoraMaisLiquida.enviar_ordem_compra(CorretoraMaisLiquida.ordem)#zerando o risco na mercado bitcoin
                else:
                    logging.info('caixa vai comprar {} {} na {} para zerar o pnl'.format(quantidade_a_zerar,moeda,CorretoraMenosLiquida.nome))
                    CorretoraMenosLiquida.ordem.quantidade_negociada = quantidade_a_zerar
                    CorretoraMenosLiquida.ordem.tipo_ordem = 'market'
                    CorretoraMenosLiquida.enviar_ordem_compra(CorretoraMenosLiquida.ordem)#zerando o risco na mercado bitcoin

            else:
                logging.info('caixa não precisa zerar pnl de {} por ora'.format(moeda))

        return True

    
    def rebalanceia_carteiras(corretora_mais_liquida,corretora_menos_liquida):
        '''
        esse metodo vai transferir cripto entre as carteiras, para balancear novamente as quantidades
        '''
        balancear_carteira = Util.obter_balancear_carteira()
        quantidade_de_cripto = {}

        for moeda in balancear_carteira.keys():
        
            # Instancia das corretoras por ativo
            CorretoraMaisLiquida = Corretora(corretora_mais_liquida, moeda)
            CorretoraMenosLiquida = Corretora(corretora_menos_liquida, moeda)

            CorretoraMaisLiquida.atualizar_saldo()
            CorretoraMenosLiquida.atualizar_saldo()

            quantidade_de_cripto[moeda] = round(CorretoraMaisLiquida.saldoCrypto + CorretoraMenosLiquida.saldoCrypto,4)
            
            if balancear_carteira[moeda] == 'sempre': #a transferencia de cripto é barata, então toca o barco

                if CorretoraMaisLiquida.saldoCrypto < 0.1*quantidade_de_cripto[moeda]:
                    #a quantidade a transferir é o minimo entre 50% da posição em cripto ou oq consigo recomprar
                    quantidade_a_transferir = round(min(0.5*quantidade_de_cripto[moeda],CorretoraMenosLiquida.saldoBRL/CorretoraMaisLiquida.ordem.preco_venda),4)
                    logging.warning('tenho menos de 10% de {} na {}, vou sacar {} da {}'.format(moeda,CorretoraMaisLiquida.nome,quantidade_a_transferir,CorretoraMenosLiquida.nome))
                    CorretoraMenosLiquida.ordem.quantidade_transferencia = quantidade_a_transferir
                    retorno = CorretoraMenosLiquida.transferir_crypto(CorretoraMenosLiquida.ordem,CorretoraMaisLiquida.nome)

                elif CorretoraMenosLiquida.saldoCrypto < 0.1*quantidade_de_cripto[moeda]:
                    #a quantidade a transferir é o minimo entre 50% da posição em cripto ou oq consigo recomprar
                    quantidade_a_transferir = round(min(0.5*quantidade_de_cripto[moeda],CorretoraMaisLiquida.saldoBRL/CorretoraMenosLiquida.ordem.preco_venda),4)
                    logging.warning('tenho menos de 10% de {} na {}, vou sacar {} da {}'.format(moeda,CorretoraMenosLiquida.nome,quantidade_a_transferir,CorretoraMaisLiquida.nome))
                    CorretoraMaisLiquida.ordem.quantidade_transferencia = quantidade_a_transferir
                    retorno = CorretoraMaisLiquida.transferir_crypto(CorretoraMaisLiquida.ordem,CorretoraMenosLiquida.nome)
                
                else:
                    logging.info('nao preciso transferir {} ainda'.format(moeda))

            elif balancear_carteira[moeda] == 'quando_ha_arbitragem': #apenas se realmente necessario

                if CorretoraMaisLiquida.saldoCrypto < 0.1*quantidade_de_cripto[moeda]:
                    
                    if CorretoraMenosLiquida.ordem.preco_compra < CorretoraMaisLiquida.ordem.preco_venda: #ta rolando arbitragem
                        #a quantidade a transferir é o minimo entre 50% da posição em cripto ou oq consigo recomprar
                        quantidade_a_transferir = round(min(0.5*quantidade_de_cripto[moeda],CorretoraMenosLiquida.saldoBRL/CorretoraMaisLiquida.ordem.preco_venda),4)
                        # Verifica em termos financeiros levando em conta as corretagens de compra e venda, se a operação vale a pena
                        financeiroCorretagem = CorretoraMenosLiquida.obter_financeiro_corretagem_compra_por_corretora(quantidade_a_transferir) + CorretoraMaisLiquida.obter_financeiro_corretagem_venda_por_corretora(quantidade_a_transferir)
                        pnl = CorretoraMaisLiquida.obter_amount_venda(quantidade_a_transferir) - CorretoraMenosLiquida.obter_amount_compra(quantidade_a_transferir)
                        # Teste se o financeiro com a corretagem é menor que o pnl da operação
                        if financeiroCorretagem < pnl:
                            
                            logging.warning('tenho menos de 10% de {} na {}, vou sacar {} da {}'.format(moeda,CorretoraMaisLiquida.nome,quantidade_a_transferir,CorretoraMenosLiquida.nome))
                            CorretoraMenosLiquida.ordem.quantidade_transferencia = quantidade_a_transferir
                            retorno = CorretoraMenosLiquida.transferir_crypto(CorretoraMenosLiquida.ordem,CorretoraMaisLiquida.nome)
                    else:
                        logging.info('tem pouca {}, mas apenas transferimos cripto quando ha arbitragem'.format(moeda))
                elif CorretoraMenosLiquida.saldoCrypto < 0.1*quantidade_de_cripto[moeda]:
                    
                    if CorretoraMaisLiquida.ordem.preco_compra < CorretoraMenosLiquida.ordem.preco_venda: #ta rolando arbitragem
                        #a quantidade a transferir é o minimo entre 50% da posição em cripto ou oq consigo recomprar
                        quantidade_a_transferir = round(min(0.5*quantidade_de_cripto[moeda],CorretoraMaisLiquida.saldoBRL/CorretoraMenosLiquida.ordem.preco_venda),4)
                        # Verifica em termos financeiros levando em conta as corretagens de compra e venda, se a operação vale a pena
                        financeiroCorretagem = CorretoraMaisLiquida.obter_financeiro_corretagem_compra_por_corretora(quantidade_a_transferir) + CorretoraMenosLiquida.obter_financeiro_corretagem_venda_por_corretora(quantidade_a_transferir)
                        pnl = CorretoraMenosLiquida.obter_amount_venda(quantidade_a_transferir) - CorretoraMaisLiquida.obter_amount_compra(quantidade_a_transferir)
                        # Teste se o financeiro com a corretagem é menor que o pnl da operação
                        if financeiroCorretagem < pnl:
                        
                            logging.warning('tenho menos de 10% de {} na {}, vou sacar {} da {}'.format(moeda,CorretoraMenosLiquida.nome,quantidade_a_transferir,CorretoraMaisLiquida.nome))
                            CorretoraMaisLiquida.ordem.quantidade_transferencia = quantidade_a_transferir
                            retorno = CorretoraMaisLiquida.transferir_crypto(CorretoraMaisLiquida.ordem,CorretoraMenosLiquida.nome)
                    
                    else:
                        logging.info('tem pouca {}, mas apenas transferimos essa cripto quando ha arbitragem'.format(moeda))
                else:
                    logging.info('nao preciso transferir {} ainda'.format(moeda))


        return retorno

if __name__ == "__main__":

        
    from caixa import Caixa

    logging.basicConfig(filename='caixa.log', level=logging.INFO,
                        format='[%(asctime)s][%(levelname)s][%(message)s]')
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    logging.getLogger().addHandler(console)

    #essa parte executa apenas uma vez
    corretora_mais_liquida = Util.obter_corretora_de_maior_liquidez()
    corretora_menos_liquida = Util.obter_corretora_de_menor_liquidez()

    Caixa.zera_o_pnl_em_cripto(corretora_mais_liquida,corretora_menos_liquida)
   # Caixa.rebalanceia_carteiras(corretora_mais_liquida,corretora_menos_liquida)
    