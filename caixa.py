import logging
from datetime import datetime
from uteis.corretora import Corretora
from uteis.util import Util
import time

class Caixa:
    
    def atualiza_saldo_inicial(lista_de_moedas,CorretoraMaisLiquida:Corretora,CorretoraMenosLiquida:Corretora):
        '''
        retorna dicionario com saldo inicial de cada moeda
        '''
        saldo_inicial = {}

        CorretoraMenosLiquida.cancelar_todas_ordens()
        CorretoraMaisLiquida.atualizar_saldo()
        CorretoraMenosLiquida.atualizar_saldo()

        for moeda in lista_de_moedas+['brl']:
            
            saldo_inicial[moeda] = round(CorretoraMaisLiquida.saldo[moeda] + CorretoraMenosLiquida.saldo[moeda],4)
            porcentagem_mais_liquida = round(100*CorretoraMaisLiquida.saldo[moeda]/saldo_inicial[moeda],0)
            porcentagem_menos_liquida = round(100*CorretoraMenosLiquida.saldo[moeda]/saldo_inicial[moeda],0)
            
            logging.warning('saldo inicial em {}: {} ({}% na {} e {}% na {})'.format(moeda,saldo_inicial[moeda],porcentagem_mais_liquida,CorretoraMaisLiquida.nome,porcentagem_menos_liquida,CorretoraMenosLiquida.nome))
            
        return saldo_inicial

    def envia_saldo_google(CorretoraMaisLiquida:Corretora,CorretoraMenosLiquida:Corretora):
        '''
        envia saldo para planilha do google
        '''
        saldo = {}
        preco_venda = {}

        lista_de_moedas_hardcoded = ['brl','btc','eth','xrp','ltc','bch','usdt','dai','eos']
        
        for moeda in lista_de_moedas_hardcoded:
            if (moeda in CorretoraMaisLiquida.saldo.keys()) and (moeda in CorretoraMenosLiquida.saldo.keys()):
                
                saldo[moeda] = round(CorretoraMaisLiquida.saldo[moeda] + CorretoraMenosLiquida.saldo[moeda],4)
                
                if moeda != 'brl':
                    CorretoraMaisLiquida.book.obter_ordem_book_por_indice(moeda,'brl',0,True)
                    preco_venda[moeda] = CorretoraMaisLiquida.book.preco_venda
                else:
                    preco_venda[moeda] = 1
            else:
                CorretoraMaisLiquida.saldo[moeda] = 0
                saldo[moeda] = 0
                preco_venda[moeda] = 0

        logging.warning('caixa vai enviar saldo para o google')
        Util.adicionar_linha_no_saldo(saldo['brl'],saldo['btc'],saldo['eth'],saldo['xrp'],saldo['ltc'],saldo['bch'],saldo['btc']*preco_venda['btc'],saldo['eth']*preco_venda['eth'],saldo['xrp']*preco_venda['xrp'],saldo['ltc']*preco_venda['ltc'],saldo['bch']*preco_venda['bch'],CorretoraMaisLiquida.saldo['brl'],CorretoraMaisLiquida.saldo['btc'],CorretoraMaisLiquida.saldo['eth'],CorretoraMaisLiquida.saldo['xrp'],CorretoraMaisLiquida.saldo['ltc'],CorretoraMaisLiquida.saldo['bch'],str(datetime.now()))


    def zera_o_pnl_em_cripto(CorretoraMaisLiquida:Corretora,CorretoraMenosLiquida:Corretora,ativo='',atualizar_saldo=True):
        '''
        ao longo do dia, nós pagamos corretagem em cripto, então é bom comprar essa quantidade novamente
        '''
        saldo_inicial = Util.obter_saldo_inicial()
        saldo_final = {}

        if atualizar_saldo:
            CorretoraMaisLiquida.atualizar_saldo()
            CorretoraMenosLiquida.atualizar_saldo()

        moedas_para_zerar = saldo_inicial.keys() if ativo == '' else [ativo]
        #verifica saldo final, para comparar com inicial
        for moeda in moedas_para_zerar:

            saldo_final[moeda] = CorretoraMaisLiquida.saldo[moeda] + CorretoraMenosLiquida.saldo[moeda]

            pnl_em_moeda = round(saldo_final[moeda] - saldo_inicial[moeda],4)
            
            #para evitar erros operacionais, é melhor só zerar se temos ctz que nao é uma transf de moeda
            if abs(pnl_em_moeda)< saldo_inicial[moeda]/2:              
                quantidade_a_zerar = round(abs(pnl_em_moeda),4)
            else:
                logging.warning('caixa não vai zerar pnl de {} porque estamos transferindo cripto'.format(moeda))
                quantidade_a_zerar = 0

            #carrego os books de ordem mais recentes
            CorretoraMaisLiquida.book.obter_ordem_book_por_indice(moeda,Util.CCYBRL(),0,True,True)
            
            if pnl_em_moeda > 0 and quantidade_a_zerar > Util.retorna_menor_quantidade_venda(moeda):

                #carrego os books de ordem mais recentes
                CorretoraMenosLiquida.book.obter_ordem_book_por_indice(moeda,Util.CCYBRL(),0,True,True)

                if (CorretoraMaisLiquida.book.obter_preco_medio_de_venda(quantidade_a_zerar) > CorretoraMenosLiquida.book.obter_preco_medio_de_venda(quantidade_a_zerar) and CorretoraMaisLiquida.saldo[moeda]>quantidade_a_zerar) or (CorretoraMenosLiquida.saldo[moeda]<quantidade_a_zerar): #vamos vender na corretora que paga mais e que tenha saldo
                    logging.warning('caixa vai vender {} {} na {} para zerar o pnl'.format(quantidade_a_zerar,moeda,CorretoraMaisLiquida.nome))
                    CorretoraMaisLiquida.ordem.quantidade_enviada = min(quantidade_a_zerar,CorretoraMaisLiquida.saldo[moeda])
                    CorretoraMaisLiquida.ordem.tipo_ordem = 'market'
                    CorretoraMaisLiquida.ordem.preco_enviado = CorretoraMaisLiquida.book.preco_venda
                    
                    ordem_venda = CorretoraMaisLiquida.enviar_ordem_venda(CorretoraMaisLiquida.ordem,moeda)
                    vendi_a = ordem_venda.preco_executado
                    quantidade_executada_venda = ordem_venda.quantidade_executada

                    Util.adicionar_linha_em_operacoes(moeda,'',0,0,CorretoraMaisLiquida.nome,vendi_a,quantidade_executada_venda,0,'CAIXA',str(datetime.now()))

                    CorretoraMaisLiquida.atualizar_saldo()
                    
                elif (CorretoraMaisLiquida.book.obter_preco_medio_de_venda(quantidade_a_zerar) < CorretoraMenosLiquida.book.obter_preco_medio_de_venda(quantidade_a_zerar) and CorretoraMenosLiquida.saldo[moeda]>quantidade_a_zerar) or(CorretoraMaisLiquida.saldo[moeda]<quantidade_a_zerar):
                    logging.warning('caixa vai vender {} {} na {} para zerar o pnl'.format(quantidade_a_zerar,moeda,CorretoraMenosLiquida.nome))
                    CorretoraMenosLiquida.ordem.quantidade_enviada = min(quantidade_a_zerar,CorretoraMenosLiquida.saldo[moeda])
                    CorretoraMenosLiquida.ordem.tipo_ordem = 'market'
                    CorretoraMenosLiquida.ordem.preco_enviado = CorretoraMenosLiquida.book.preco_venda
                    
                    ordem_venda = CorretoraMenosLiquida.enviar_ordem_venda(CorretoraMenosLiquida.ordem,moeda)
                    vendi_a = ordem_venda.preco_executado
                    quantidade_executada_venda = ordem_venda.quantidade_executada

                    Util.adicionar_linha_em_operacoes(moeda,'',0,0,CorretoraMenosLiquida.nome,vendi_a,quantidade_executada_venda,0,'CAIXA',str(datetime.now()))

                    CorretoraMenosLiquida.atualizar_saldo()
                    
            elif pnl_em_moeda < 0 and quantidade_a_zerar*CorretoraMaisLiquida.book.preco_compra > Util.retorna_menor_valor_compra(moeda):
            
                #carrego os books de ordem mais recentes
                CorretoraMenosLiquida.book.obter_ordem_book_por_indice(moeda,Util.CCYBRL(),0,True,True)

                if (CorretoraMaisLiquida.book.obter_preco_medio_de_compra(quantidade_a_zerar) < CorretoraMenosLiquida.book.obter_preco_medio_de_compra(quantidade_a_zerar)) and (CorretoraMaisLiquida.saldo['brl']>quantidade_a_zerar*CorretoraMenosLiquida.book.preco_compra) or (CorretoraMenosLiquida.saldo['brl']<quantidade_a_zerar*CorretoraMenosLiquida.book.preco_compra): #vamos comprar na corretora que esta mais barato e que tenha saldo
                    logging.warning('caixa vai comprar {} {} na {} para zerar o pnl'.format(quantidade_a_zerar,moeda,CorretoraMaisLiquida.nome))
                    CorretoraMaisLiquida.ordem.quantidade_enviada = quantidade_a_zerar
                    CorretoraMaisLiquida.ordem.tipo_ordem = 'market'
                    CorretoraMaisLiquida.ordem.preco_enviado = CorretoraMaisLiquida.book.preco_compra
                    
                    ordem_compra = CorretoraMaisLiquida.enviar_ordem_compra(CorretoraMaisLiquida.ordem,moeda)
                    comprei_a = ordem_compra.preco_executado
                    quantidade_executada_compra = ordem_compra.quantidade_executada

                    Util.adicionar_linha_em_operacoes(moeda,CorretoraMaisLiquida.nome,comprei_a,quantidade_executada_compra,'',0,0,0,'CAIXA',str(datetime.now()))

                    CorretoraMaisLiquida.atualizar_saldo()
                    
                elif (CorretoraMaisLiquida.book.obter_preco_medio_de_compra(quantidade_a_zerar) > CorretoraMenosLiquida.book.obter_preco_medio_de_compra(quantidade_a_zerar)) and (CorretoraMenosLiquida.saldo['brl']>quantidade_a_zerar*CorretoraMaisLiquida.book.preco_compra) or (CorretoraMaisLiquida.saldo['brl']<quantidade_a_zerar*CorretoraMaisLiquida.book.preco_compra):
                    logging.warning('caixa vai comprar {} {} na {} para zerar o pnl'.format(quantidade_a_zerar,moeda,CorretoraMenosLiquida.nome))
                    CorretoraMenosLiquida.ordem.quantidade_enviada = quantidade_a_zerar
                    CorretoraMenosLiquida.ordem.tipo_ordem = 'market'
                    CorretoraMenosLiquida.ordem.preco_enviado = CorretoraMenosLiquida.book.preco_compra
                    
                    ordem_compra = CorretoraMenosLiquida.enviar_ordem_compra(CorretoraMenosLiquida.ordem,moeda)
                    comprei_a = ordem_compra.preco_executado
                    quantidade_executada_compra = ordem_compra.quantidade_executada

                    Util.adicionar_linha_em_operacoes(moeda,CorretoraMenosLiquida.nome,comprei_a,quantidade_executada_compra,'',0,0,0,'CAIXA',str(datetime.now()))

                    CorretoraMenosLiquida.atualizar_saldo()
                    
            else:
                logging.warning('caixa não precisa zerar pnl de {} por ora'.format(moeda))

        return True

    #necessario revisão, está desligado
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
    from datetime import datetime

    logging.basicConfig(filename='caixa.log', level=logging.INFO,
                        format='[%(asctime)s][%(levelname)s][%(message)s]')
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    logging.getLogger().addHandler(console)

    #essa parte executa apenas uma vez
    lista_de_moedas = Util.obter_lista_de_moedas()
    corretora_mais_liquida = Util.obter_corretora_de_maior_liquidez()
    corretora_menos_liquida = Util.obter_corretora_de_menor_liquidez()

    # Instancia das corretoras por ativo
    CorretoraMaisLiquida = Corretora(corretora_mais_liquida)
    CorretoraMenosLiquida = Corretora(corretora_menos_liquida)

    Caixa.atualiza_saldo_inicial(lista_de_moedas,CorretoraMaisLiquida,CorretoraMenosLiquida)
    Caixa.zera_o_pnl_em_cripto(CorretoraMaisLiquida,CorretoraMenosLiquida,'',False)
    
    CorretoraMaisLiquida.atualizar_saldo()
    CorretoraMenosLiquida.atualizar_saldo()

    Caixa.envia_saldo_google(CorretoraMaisLiquida,CorretoraMenosLiquida)