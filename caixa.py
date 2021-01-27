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

            CorretoraMaisLiquida.atualizarSaldo()
            CorretoraMenosLiquida.atualizarSaldo()

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

            CorretoraMaisLiquida.atualizarSaldo()
            CorretoraMenosLiquida.atualizarSaldo()

            saldo_final['brl'] = (CorretoraMaisLiquida.saldoBRL + CorretoraMenosLiquida.saldoBRL)/len(lista_de_moedas) #para não contar duas vezes esse cara
            saldo_final[moeda] = CorretoraMaisLiquida.saldoCrypto + CorretoraMenosLiquida.saldoCrypto

        #zerar saldo_final[moeda] - saldo_inicial[moeda]
        for moeda in lista_de_moedas:
            
            pnl_em_moeda = abs(saldo_final[moeda]-saldo_inicial[moeda])

            if pnl_em_moeda >0:
                logging.info('caixa vai zerar {} de pnl em {}'.format(round(pnl_em_moeda,4),moeda))
            else:
                logging.info('caixa não precisa zerar de pnl em {} por ora'.format(moeda))


        return True