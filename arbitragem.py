
import requests
import time
import logging
from datetime import datetime
from corretora import Corretora
from ordem import Ordem
from util import Util

class Arbitragem:

    def processar(corretoraCompra:Corretora, corretoraVenda:Corretora, ativo, executarOrdens = False):
        
        pnl = 0
        retorno_compra = Ordem()
        retorno_venda = Ordem()
        
        # Obtendo a menor quantidade de compra e venda entre as corretoras que tenho saldo para negociar
        qtdNegociada = min(corretoraCompra.ordem.quantidade_compra, corretoraVenda.ordem.quantidade_venda,corretoraCompra.saldoBRL/corretoraCompra.ordem.preco_venda,corretoraVenda.saldoCrypto)
        
        try:
            # Verifica se existe arbitragem entre as corretoras
            if corretoraCompra.ordem.preco_compra < corretoraVenda.ordem.preco_venda:               

                # Verifica em termos financeiros levando em conta as corretagens de compra e venda, se a operação vale a pena
                financeiroCorretagem = corretoraCompra.obter_financeiro_corretagem_compra_por_corretora(qtdNegociada) + corretoraVenda.obter_financeiro_corretagem_venda_por_corretora(qtdNegociada)
                pnl = corretoraVenda.obter_amount_venda(qtdNegociada) - corretoraCompra.obter_amount_compra(qtdNegociada)

                # Teste se o financeiro com a corretagem é menor que o pnl da operação
                if financeiroCorretagem < pnl:
                    # Condição para que verificar se o saldo em reais e crypto são suficientes para a operação
                    if (corretoraCompra.obter_amount_compra(qtdNegociada) > Util.retorna_menor_valor_compra(ativo)) and (qtdNegociada > Util.retorna_menor_quantidade_venda(ativo)):
                        
                        if (corretoraCompra.saldoBRL >= corretoraCompra.obter_amount_compra(qtdNegociada)) and (corretoraVenda.saldoCrypto >= qtdNegociada): 
                            
                            if executarOrdens:
                                # Atualiza a quantidade negociada e o tipo de ordem 
                                corretoraCompra.ordem.quantidade_negociada = qtdNegociada
                                corretoraVenda.ordem.quantidade_negociada = qtdNegociada
                                corretoraCompra.ordem.tipo_ordem = 'market'
                                corretoraVenda.ordem.tipo_ordem = 'market'

                                comprei_a = round(corretoraCompra.ordem.preco_compra,4)
                                vendi_a = round(corretoraVenda.ordem.preco_venda,4)

                                logging.info('arbitragem vai comprar {}{} @{} na {} e vender @{} na {}'.format(round(qtdNegociada,4),ativo,comprei_a,corretoraCompra.nome,vendi_a,corretoraVenda.nome))
                                retorno_compra = corretoraCompra.enviar_ordem_compra(corretoraCompra.ordem)
                                retorno_venda = corretoraVenda.enviar_ordem_venda(corretoraVenda.ordem)
                                

                                if retorno_compra.status != retorno_compra.descricao_status_executado:
                                    logging.error('arbitragem NAO zerou na {}'.format(corretoraCompra.nome))
                                else:
                                    logging.warning('operou arb de {}! + {}brl de pnl com compra de {}{} @{} na {}'.format(ativo,round(pnl/2,2),round(qtdNegociada,4),ativo,comprei_a,corretoraCompra.nome))
                                    Util.adicionar_linha_em_operacoes('{}|{}|{}|C|{}|{}|{}|{}'.format(ativo,corretoraCompra.nome,comprei_a,round(qtdNegociada,4),pnl,'ARBITRAGEM',datetime.now()))
                                    
                                if retorno_venda.status != retorno_venda.descricao_status_executado:
                                    logging.error('arbitragem NAO zerou na {}'.format(corretoraVenda.nome))
                                else: 
                                    logging.warning('operou arb de {}! + {}brl de pnl com venda de {}{} @{} na {}'.format(ativo,round(pnl/2,2),round(qtdNegociada,4),ativo,vendi_a,corretoraVenda.nome))
                                    Util.adicionar_linha_em_operacoes('{}|{}|{}|V|{}|{}|{}|{}'.format(ativo,corretoraVenda.nome,vendi_a,round(qtdNegociada,4),pnl,'ARBITRAGEM',datetime.now()))
                                
                                corretoraCompra.atualizar_saldo()
                                corretoraVenda.atualizar_saldo()
                           
                        else:
                            logging.info('arbitragem nao vai enviar ordem de {} porque saldo em reais {} ou saldo em cripto {} nao é suficiente'.format(ativo,round(corretoraCompra.saldoBRL,2),corretoraVenda.saldoCrypto))
                    else:
                        logging.info('arbitragem nao vai enviar ordem de {} porque {} nao é maior que a quantidade minima'.format(ativo,qtdNegociada))
                else:
                    logging.info('arbitragem nao vai enviar ordem de {} porque pnl ({}) é menor que corretagem ({})'.format(ativo,round(pnl,2),round(financeiroCorretagem,2)))
                    
            else:
                logging.info('arbitragem nao vai enviar ordem de {} porque preco compra ({}) é maior que preco venda ({})'.format(ativo,round(corretoraCompra.ordem.preco_compra,2),round(corretoraVenda.ordem.preco_venda,2)))
                
        except Exception as erro:
            msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de arbitragem, método: processar.', erro)
            raise Exception(msg_erro)
        
if __name__ == "__main__":

    from datetime import datetime, timedelta
    from caixa import Caixa
    from arbitragem import Arbitragem
    

    logging.basicConfig(filename='arbitragem.log', level=logging.INFO,
                        format='[%(asctime)s][%(levelname)s][%(message)s]')
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    logging.getLogger().addHandler(console)

    #essa parte executa apenas uma vez
    lista_de_moedas = Util.obter_lista_de_moedas()
    corretora_mais_liquida = Util.obter_corretora_de_maior_liquidez()
    corretora_menos_liquida = Util.obter_corretora_de_menor_liquidez()


    #atualiza saldo inicial nesse dicionario
    Caixa.atualiza_saldo_inicial(lista_de_moedas,corretora_mais_liquida,corretora_menos_liquida)

    hour = 1
    while hour <= 720:
        #essa parte executa uma vez por hora
        agora = datetime.now() 
        proxima_hora = agora + timedelta(hours=1)
        logging.warning('proxima atualizacao: {}'.format(proxima_hora))
        
        while agora < proxima_hora:
            #essa parte executa diversas vezes

            for moeda in lista_de_moedas:
                try:
                    # Instancia das corretoras por ativo
                    CorretoraMaisLiquida = Corretora(corretora_mais_liquida, moeda)
                    CorretoraMenosLiquida = Corretora(corretora_menos_liquida, moeda)

                    # Atualiza o saldo de crypto e de BRL nas corretoras
                    CorretoraMaisLiquida.atualizar_saldo()
                    CorretoraMenosLiquida.atualizar_saldo()

                    # Roda a arbitragem nas 2 corretoras
                    Arbitragem.processar(CorretoraMaisLiquida, CorretoraMenosLiquida, moeda, True)
                    Arbitragem.processar(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True)   
                                   
                except Exception as erro:        
                    logging.error(erro) 
                
                time.sleep(Util.frequencia())

            agora = datetime.now() 

        hour = hour+1
        
        Caixa.atualiza_saldo_inicial(lista_de_moedas,corretora_mais_liquida,corretora_menos_liquida)
