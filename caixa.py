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

            CorretoraMaisLiquida.atualizar_saldo()
            CorretoraMenosLiquida.atualizar_saldo()

            saldo_inicial['brl'] = saldo_inicial['brl'] + (CorretoraMaisLiquida.saldoBRL + CorretoraMenosLiquida.saldoBRL) #para não contar duas vezes esse cara
            saldo_inicial[moeda] = CorretoraMaisLiquida.saldoCrypto + CorretoraMenosLiquida.saldoCrypto
            
            logging.warning('saldo inicial em {}: {}'.format(moeda,round(saldo_inicial[moeda],4)))
            Util.adicionar_linha_no_saldo('{}|{}|{}'.format(moeda,round(saldo_inicial[moeda],4),datetime.now()))

        logging.warning('saldo inicial em reais: {}'.format(round(saldo_inicial['brl']/len(lista_de_moedas),2)))
        Util.adicionar_linha_no_saldo('{}|{}|{}'.format('BRL',round(saldo_inicial['brl']/len(lista_de_moedas),2),datetime.now()))

        return saldo_inicial


    def zera_o_pnl_em_cripto(lista_de_moedas,corretora_mais_liquida,corretora_menos_liquida):
        '''
        ao longo do dia, nós pagamos corretagem em cripto, então uma vez ao dia é bom comprar essa quantidade novamente
        '''
        saldo_inicial = Util.obter_saldo_inicial()
        saldo_final = {}

        #verifica saldo final, para comparar com inicial
        for moeda in lista_de_moedas:
        
            # Instancia das corretoras por ativo
            CorretoraMaisLiquida = Corretora(corretora_mais_liquida, moeda)
            CorretoraMenosLiquida = Corretora(corretora_menos_liquida, moeda)

            #inicialmente cancela todas ordens abertas na brasil
            CorretoraMenosLiquida.cancelar_todas_ordens(moeda)
            time.sleep(1)

            CorretoraMaisLiquida.atualizar_saldo()
            CorretoraMenosLiquida.atualizar_saldo()

            saldo_final['brl'] = (CorretoraMaisLiquida.saldoBRL + CorretoraMenosLiquida.saldoBRL)/len(lista_de_moedas) #para não contar duas vezes esse cara
            saldo_final[moeda] = CorretoraMaisLiquida.saldoCrypto + CorretoraMenosLiquida.saldoCrypto

            pnl_em_moeda = round(saldo_final[moeda] - saldo_inicial[moeda],2)
            quantidade_a_zerar = round(abs(pnl_em_moeda),2)

            if pnl_em_moeda > 0 and quantidade_a_zerar > Util.retorna_menor_quantidade_venda(moeda):
                if CorretoraMaisLiquida.ordem.preco_venda > CorretoraMenosLiquida.ordem.preco_venda: #vamos vender na corretora que paga mais
                    logging.info('caixa vai vender {} {} na {} para zerar o pnl'.format(quantidade_a_zerar,moeda,CorretoraMaisLiquida.nome))
                    CorretoraMaisLiquida.ordem.quantidade_negociada = quantidade_a_zerar
                    CorretoraMaisLiquida.ordem.tipo_ordem = 'market'
                    CorretoraMaisLiquida.enviar_ordem_venda(CorretoraMaisLiquida.ordem)
                else:
                    logging.info('caixa vai vender {} {} na {} para zerar o pnl'.format(quantidade_a_zerar,moeda,CorretoraMenosLiquida.nome))
                    CorretoraMenosLiquida.ordem.quantidade_negociada = quantidade_a_zerar
                    CorretoraMenosLiquida.ordem.tipo_ordem = 'market'
                    CorretoraMenosLiquida.enviar_ordem_venda(CorretoraMaisLiquida.ordem)

            elif pnl_em_moeda < 0 and quantidade_a_zerar > CorretoraMaisLiquida.ordem.preco_compra*Util.retorna_menor_valor_compra(moeda):
                if CorretoraMaisLiquida.ordem.preco_compra < CorretoraMenosLiquida.ordem.preco_compra: #vamos comprar na corretora que esta mais barato
                    logging.info('caixa vai comprar {} {} na {} para zerar o pnl'.format(quantidade_a_zerar,moeda,CorretoraMaisLiquida.nome))
                    CorretoraMaisLiquida.ordem.quantidade_negociada = quantidade_a_zerar
                    CorretoraMaisLiquida.ordem.tipo_ordem = 'market'
                    CorretoraMaisLiquida.enviar_ordem_compra(CorretoraMaisLiquida.ordem)#zerando o risco na mercado bitcoin
                else:
                    logging.info('caixa vai comprar {} {} na {} para zerar o pnl'.format(quantidade_a_zerar,moeda,CorretoraMenosLiquida.nome))
                    CorretoraMenosLiquida.ordem.quantidade_negociada = quantidade_a_zerar
                    CorretoraMenosLiquida.ordem.tipo_ordem = 'market'
                    CorretoraMenosLiquida.enviar_ordem_compra(CorretoraMaisLiquida.ordem)#zerando o risco na mercado bitcoin

            else:
                logging.info('caixa não precisa zerar pnl de {} por ora'.format(moeda))

        return True