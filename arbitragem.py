
import requests
import time
import logging
from datetime import datetime
from uteis.corretora import Corretora
from uteis.ordem import Ordem
from uteis.util import Util

class Arbitragem:

    def simples(corretoraCompra:Corretora, corretoraVenda:Corretora, ativo, executarOrdens = False):
        
        try:
            pnl = 0
            ordem_compra = corretoraCompra.ordem
            ordem_venda = corretoraVenda.ordem

            corretoraCompra.atualizar_saldo('brl')
            corretoraVenda.atualizar_saldo(ativo)

            #carrego os books de ordem mais recentes, a partir daqui precisamos ser rapidos!!! é a hora do show!!
            corretoraCompra.book.obter_ordem_book_por_indice(ativo,'brl')
            corretoraVenda.book.obter_ordem_book_por_indice(ativo,'brl')

            preco_de_compra = corretoraCompra.book.preco_compra #primeiro no book de ordens
            preco_de_venda = corretoraVenda.book.preco_venda #primeiro no book de ordens

            #se tiver arbitragem, a magica começa!
            if preco_de_compra < preco_de_venda: 

                quantidade_de_compra = corretoraCompra.book.quantidade_compra #qtd no book de ordens
                quantidade_de_venda = corretoraVenda.book.quantidade_venda #qtd no book de ordens

                quanto_posso_comprar = corretoraCompra.saldo/corretoraCompra.book.preco_venda #saldo em reais
                quanto_posso_vender = corretoraVenda.saldo #saldo em cripto

                # Obtendo a menor quantidade de compra e venda entre as corretoras que tenho saldo para negociar
                qtdNegociada = min(quantidade_de_compra, quantidade_de_venda,quanto_posso_comprar,quanto_posso_vender)
            
                # Verifica em termos financeiros levando em conta as corretagens de compra e venda, se a operação vale a pena
                vou_pagar = qtdNegociada*preco_de_compra*(1+corretoraCompra.corretagem_mercado)
                vou_ganhar = qtdNegociada*preco_de_venda*(1-corretoraVenda.corretagem_mercado)

                pnl = vou_ganhar - vou_pagar

                # Teste se o financeiro com a corretagem é menor que o pnl da operação
                if pnl>0:
                    # Condição para que verificar se o saldo em reais e crypto são suficientes para a operação
                    if (vou_pagar > Util.retorna_menor_valor_compra(ativo)) and (qtdNegociada > Util.retorna_menor_quantidade_venda(ativo)):
                        #se tenho saldo, prossigo
                        if (corretoraCompra.saldo >= vou_pagar) and (corretoraVenda.saldo >= qtdNegociada): 
                            
                            if executarOrdens:
                                # Atualiza ordem de compra
                                ordem_compra.quantidade_enviada = qtdNegociada
                                ordem_compra.tipo_ordem = 'market'

                                # Atualiza ordem de venda
                                ordem_venda.quantidade_negociada = qtdNegociada
                                ordem_venda.tipo_ordem = 'market'

                                quero_comprar_a = round(preco_de_compra,4)
                                quero_vender_a = round(preco_de_venda,4)

                                logging.info('arbitragem vai comprar {}{} @{} na {} e vender @{} na {}'.format(round(qtdNegociada,4),ativo,quero_comprar_a,corretoraCompra.nome,quero_vender_a,corretoraVenda.nome))
                                
                                #efetivamente envia as ordens
                                ordem_compra = corretoraCompra.enviar_ordem_compra(corretoraCompra.ordem,ativo)
                                ordem_venda = corretoraVenda.enviar_ordem_venda(corretoraVenda.ordem,ativo)

                                realmente_paguei = qtdNegociada*ordem_compra.preco_executado*(1+corretoraCompra.corretagem_mercado)
                                realmente_ganhei = qtdNegociada*ordem_venda.preco_executado*(1-corretoraVenda.corretagem_mercado)

                                pnl_real = realmente_paguei - realmente_ganhei
                               
                                if ordem_compra.status != ordem_compra.descricao_status_executado:
                                    logging.error('arbitragem NAO zerou na {}, o status\status executado veio {}\{}'.format(corretoraCompra.nome,ordem_compra.status,ordem_compra.descricao_status_executado))
                                else:
                                    logging.info('operou arb de {}! + {}brl de pnl estimado com compra de {}{} @{} na {}'.format(ativo,round(pnl/2,2),round(qtdNegociada,4),ativo,quero_comprar_a,corretoraCompra.nome))
                                    logging.warning('operou arb de {}! + {}brl de pnl real com compra de {}{} @{} na {}'.format(ativo,round(pnl_real/2,2),round(qtdNegociada,4),ativo,ordem_compra.preco_executado,corretoraCompra.nome))
                                    Util.adicionar_linha_em_operacoes('{}|{}|{}|C|{}|{}|{}|{}'.format(ativo,corretoraCompra.nome,comprei_a,round(qtdNegociada,4),pnl,'ARBITRAGEM',datetime.now()))
                                    
                                if ordem_venda.status != ordem_venda.descricao_status_executado:
                                    logging.error('arbitragem NAO zerou na {}, o status veio {}\{}'.format(corretoraVenda.nome,ordem_venda.status,ordem_venda.descricao_status_executado))
                                else: 
                                    logging.info('operou arb de {}! + {}brl de pnl estimado com venda de {}{} @{} na {}'.format(ativo,round(pnl/2,2),round(qtdNegociada,4),ativo,quero_vender_a,corretoraVenda.nome))
                                    logging.warning('operou arb de {}! + {}brl de pnl real com venda de {}{} @{} na {}'.format(ativo,round(pnl_real/2,2),round(qtdNegociada,4),ativo,ordem_venda.preco_executado,corretoraVenda.nome))
                                    Util.adicionar_linha_em_operacoes('{}|{}|{}|V|{}|{}|{}|{}'.format(ativo,corretoraVenda.nome,vendi_a,round(qtdNegociada,4),pnl,'ARBITRAGEM',datetime.now()))
                                
                                  
                        else:
                            logging.info('arbitragem nao vai enviar ordem de {} porque saldo em reais {} ou saldo em cripto {} nao é suficiente'.format(ativo,round(corretoraCompra.saldo,2),corretoraVenda.saldo))
                    else:
                        logging.info('arbitragem nao vai enviar ordem de {} porque quantidade negociada {} nao é maior que a quantidade minima {}'.format(ativo,qtdNegociada,Util.retorna_menor_quantidade_venda(ativo)))
                else:
                    logging.info('arbitragem nao vai enviar ordem de {} porque vou pagar ({}) e só vou ganhar ({})'.format(ativo,round(vou_pagar,2),round(vou_ganhar,2)))
                    
            else:
                logging.info('arbitragem nao vai enviar ordem de {} porque preco compra ({}) é maior que preco venda ({})'.format(ativo,round(preco_de_compra,2),round(preco_de_venda,2)))
                
        except Exception as erro:
            msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de arbitragem, método: simples.', erro)
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

    hour = 1
    while hour <= 720:
        #essa parte executa uma vez por hora
        agora = datetime.now() 
        proxima_hora = agora + timedelta(hours=1)
        logging.warning('proxima atualizacao: {}'.format(proxima_hora))
        Caixa.atualiza_saldo_inicial(lista_de_moedas,corretora_mais_liquida,corretora_menos_liquida)

        while agora < proxima_hora:
            #essa parte executa diversas vezes
            for moeda in lista_de_moedas:
                try:
                    # Instancia das corretoras 
                    CorretoraMaisLiquida = Corretora(corretora_mais_liquida)
                    CorretoraMenosLiquida = Corretora(corretora_menos_liquida)

                    # Roda a arbitragem nas 2 corretoras
                    Arbitragem.simples(CorretoraMaisLiquida, CorretoraMenosLiquida, moeda, True)
                    Arbitragem.simples(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True)   
                                   
                except Exception as erro:        
                    logging.error(erro) 
                
                time.sleep(Util.frequencia())

            agora = datetime.now() 

        hour = hour+1
        
        
