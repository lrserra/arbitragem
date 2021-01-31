import logging
from corretora import Corretora
from datetime import datetime


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

            CorretoraMaisLiquida.atualizar_saldo()
            CorretoraMenosLiquida.atualizar_saldo()

            saldo_inicial['brl'] = saldo_inicial['brl'] + (CorretoraMaisLiquida.saldoBRL + CorretoraMenosLiquida.saldoBRL) #para não contar duas vezes esse cara
            saldo_inicial[moeda] = CorretoraMaisLiquida.saldoCrypto + CorretoraMenosLiquida.saldoCrypto
            
            logging.warning('saldo inicial em {}: {}'.format(moeda,round(saldo_inicial[moeda],4)))

        logging.warning('saldo inicial em reais: {}'.format(round(saldo_inicial['brl']/len(lista_de_moedas),2)))

        return saldo_inicial


    def zera_o_pnl_em_cripto(lista_de_moedas,saldo_inicial,corretora_mais_liquida,corretora_menos_liquida):
        '''
        ao longo do dia, nós pagamos corretagem em cripto, então uma vez ao dia vamos comprar essa quantidade novamente
        '''

        saldo_final = {}

        #verifica saldo final, para comparar com inicial
        for moeda in lista_de_moedas:
        
            # Instancia das corretoras por ativo
            CorretoraMaisLiquida = Corretora(corretora_mais_liquida, moeda)
            CorretoraMenosLiquida = Corretora(corretora_menos_liquida, moeda)

            #incialmente cancela todas ordens abertas na brasil
            CorretoraMenosLiquida.cancelar_todas_ordens(moeda)

            CorretoraMaisLiquida.atualizar_saldo()
            CorretoraMenosLiquida.atualizar_saldo()

            saldo_final['brl'] = (CorretoraMaisLiquida.saldoBRL + CorretoraMenosLiquida.saldoBRL)/len(lista_de_moedas) #para não contar duas vezes esse cara
            saldo_final[moeda] = CorretoraMaisLiquida.saldoCrypto + CorretoraMenosLiquida.saldoCrypto

            pnl_em_moeda = saldo_final[moeda] - saldo_inicial[moeda]
            quantidade_a_zerar = abs(pnl_em_moeda)

            if pnl_em_moeda > 0:
                if CorretoraMaisLiquida.ordem.preco_venda > CorretoraMenosLiquida.ordem.preco_venda: #vamos vender na corretora que paga mais
                    logging.info('caixa vai vender {} {} na {} para zerar o pnl'.format(round(quantidade_a_zerar,4),moeda,CorretoraMaisLiquida.ordem.nome))
                    CorretoraMaisLiquida.ordem.quantidade_negociada = quantidade_a_zerar
                    CorretoraMaisLiquida.ordem.tipo_ordem = 'market'
                    CorretoraMaisLiquida.enviar_ordem_venda(CorretoraMaisLiquida.ordem)
                else:
                    logging.info('caixa vai vender {} {} na {} para zerar o pnl'.format(round(quantidade_a_zerar,4),moeda,CorretoraMenosLiquida.ordem.nome))
                    CorretoraMenosLiquida.ordem.quantidade_negociada = quantidade_a_zerar
                    CorretoraMenosLiquida.ordem.tipo_ordem = 'market'
                    CorretoraMenosLiquida.enviar_ordem_venda(CorretoraMaisLiquida.ordem)

            elif pnl_em_moeda < 0:
                if CorretoraMaisLiquida.preco_compra < CorretoraMenosLiquida.preco_compra: #vamos comprar na corretora que esta mais barato
                    logging.info('caixa vai comprar {} {} na {} para zerar o pnl'.format(round(quantidade_a_zerar,4),moeda,CorretoraMaisLiquida.ordem.nome))
                    CorretoraMaisLiquida.ordem.quantidade_negociada = quantidade_a_zerar
                    CorretoraMaisLiquida.ordem.tipo_ordem = 'market'
                    CorretoraMaisLiquida.enviar_ordem_compra(CorretoraMaisLiquida.ordem)#zerando o risco na mercado bitcoin
                else:
                    logging.info('caixa vai comprar {} {} na {} para zerar o pnl'.format(round(quantidade_a_zerar,4),moeda,CorretoraMenosLiquida.ordem.nome))
                    CorretoraMenosLiquida.ordem.quantidade_negociada = quantidade_a_zerar
                    CorretoraMenosLiquida.ordem.tipo_ordem = 'market'
                    CorretoraMenosLiquida.enviar_ordem_compra(CorretoraMaisLiquida.ordem)#zerando o risco na mercado bitcoin

            else:
                logging.info('caixa não precisa zerar pnl de {} por ora'.format(moeda))

        return True