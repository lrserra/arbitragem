import logging
from datetime import datetime
from uteis.corretora import Corretora
from uteis.ordem import Ordem
from uteis.util import Util
from uteis.googleSheets import GoogleSheets

class Arbitragem:

    def simples(corretoraCompra:Corretora, corretoraVenda:Corretora, ativo, executarOrdens = False):
        
        fiz_arb = False
        
        corretora_mais_liquida = Util.obter_corretora_de_maior_liquidez()

        try:
            pnl = 0
            ordem_compra = corretoraCompra.ordem
            ordem_venda = corretoraVenda.ordem

            corretoraCompra.atualizar_saldo()
            corretoraVenda.atualizar_saldo()

            #carrego os books de ordem mais recentes, a partir daqui precisamos ser rapidos!!! é a hora do show!!
            if corretoraCompra.nome == corretora_mais_liquida: #dou preferencia pra carregar os preços da mais liquida por ultimo
                corretoraVenda.book.obter_ordem_book_por_indice(ativo,'brl',0,True,True)
                corretoraCompra.book.obter_ordem_book_por_indice(ativo,'brl',0,True,True)
            else:
                corretoraCompra.book.obter_ordem_book_por_indice(ativo,'brl',0,True,True)
                corretoraVenda.book.obter_ordem_book_por_indice(ativo,'brl',0,True,True)


            preco_de_compra = corretoraCompra.book.preco_compra #primeiro no book de ordens
            preco_de_venda = corretoraVenda.book.preco_venda #primeiro no book de ordens

            #se tiver arbitragem, a magica começa!
            if preco_de_compra < preco_de_venda: 

                quantidade_de_compra = corretoraCompra.book.quantidade_compra #qtd no book de ordens
                quantidade_de_venda = corretoraVenda.book.quantidade_venda #qtd no book de ordens

                colchao_de_liquidez = 0.98

                quanto_posso_comprar = colchao_de_liquidez*corretoraCompra.saldo['brl']/corretoraCompra.book.preco_venda #saldo em reais * colchão
                quanto_posso_vender = colchao_de_liquidez*corretoraVenda.saldo[ativo] #saldo em cripto * colchão

                # Obtendo a menor quantidade de compra e venda entre as corretoras que tenho saldo para negociar
                qtdNegociada = min(quantidade_de_compra, quantidade_de_venda,quanto_posso_comprar,quanto_posso_vender)
            
                # Verifica em termos financeiros levando em conta as corretagens de compra e venda, se a operação vale a pena
                vou_pagar = qtdNegociada*preco_de_compra*(1+corretoraCompra.corretagem_mercado)
                vou_ganhar = qtdNegociada*preco_de_venda*(1-corretoraVenda.corretagem_mercado)

                pnl = vou_ganhar - vou_pagar
                
                #define pnl minimo para aceitarmos o trade
                fracao_do_caixa = corretoraCompra.saldo['brl']/(corretoraCompra.saldo['brl']+corretoraVenda.saldo['brl'])
                pnl_minimo = 1 if fracao_do_caixa<0.2 else 0.1 # se eu tenho pouca grana na corretoracompra, então só faz o trade se der um bambá bom
                pnl_minimo = 10 if fracao_do_caixa<0.05 else pnl_minimo # se tenho muito pouco caixa nao é pra usar na arb nem fodendo

                if qtdNegociada !=0:
                    # Teste se o financeiro com a corretagem é menor que o pnl da operação
                    if pnl>pnl_minimo:#nao vamos o trade por menos que o pnl minimo
                        # Condição para que verificar se o saldo em reais e crypto são suficientes para a operação
                        if (vou_pagar > Util.retorna_menor_valor_compra(ativo)) and (qtdNegociada > Util.retorna_menor_quantidade_venda(ativo)):
                            #se tenho saldo, prossigo
                            if (corretoraCompra.saldo['brl'] >= vou_pagar) and (corretoraVenda.saldo[ativo] >= qtdNegociada): 
                                
                                fiz_arb = True
                                if executarOrdens:
                                    # Atualiza ordem de compra
                                    ordem_compra.quantidade_enviada = qtdNegociada
                                    ordem_compra.preco_enviado = preco_de_compra
                                    ordem_compra.tipo_ordem = 'market'

                                    # Atualiza ordem de venda
                                    if corretoraCompra.nome == 'MercadoBitcoin':
                                        ordem_venda.quantidade_enviada = qtdNegociada #quando vc compra na mercado, ele compra um pouco a mais e pega pra ele de corretagem, é só vender a mesma qtd
                                    else:
                                        ordem_venda.quantidade_enviada = qtdNegociada*(1-corretoraCompra.corretagem_mercado)
                                    ordem_venda.preco_enviado = preco_de_venda
                                    ordem_venda.tipo_ordem = 'market'

                                    quero_comprar_a = round(preco_de_compra,4)
                                    quero_vender_a = round(preco_de_venda,4)

                                    #efetivamente envia as ordens
                                    if corretoraCompra.nome == corretora_mais_liquida:
                                        logging.info('arbitragem vai comprar primeiro {}{} @{} na {} e vender depois @{} na {} que tem {} de saldo'.format(round(qtdNegociada,4),ativo,quero_comprar_a,corretoraCompra.nome,quero_vender_a,corretoraVenda.nome,corretoraVenda.saldo[ativo]))
                                        ordem_compra = corretoraCompra.enviar_ordem_compra(ordem_compra,ativo)
                                        ordem_venda = corretoraVenda.enviar_ordem_venda(ordem_venda,ativo)
                                    else:
                                        logging.info('arbitragem vai vender primeiro {}{} @{} na {} que tem {} de saldo e comprar depois @{} na {}'.format(round(qtdNegociada,4),ativo,quero_vender_a,corretoraVenda.nome,corretoraVenda.saldo[ativo],quero_comprar_a,corretoraCompra.nome))
                                        ordem_venda = corretoraVenda.enviar_ordem_venda(ordem_venda,ativo)
                                        ordem_compra = corretoraCompra.enviar_ordem_compra(ordem_compra,ativo)

                                    realmente_paguei = qtdNegociada*ordem_compra.preco_executado*(1+corretoraCompra.corretagem_mercado)
                                    realmente_ganhei = qtdNegociada*ordem_venda.preco_executado*(1-corretoraVenda.corretagem_mercado)

                                    if ordem_compra.preco_executado== 0 or ordem_venda.preco_executado ==0:
                                        pnl_real = 0
                                    else:
                                        pnl_real = realmente_ganhei - realmente_paguei

                                    comprei_a = round(ordem_compra.preco_executado,4)
                                    vendi_a = round(ordem_venda.preco_executado,4)

                                    quantidade_executada_compra = ordem_compra.quantidade_executada
                                    quantidade_executada_venda = ordem_venda.quantidade_executada

                                    GoogleSheets().escrever_operacao([ativo,corretoraCompra.nome,comprei_a,quantidade_executada_compra,corretoraVenda.nome,vendi_a,quantidade_executada_venda,pnl_real,'ARBITRAGEM',Util.excel_date(datetime.now())])
                                
                                    if ordem_compra.status != ordem_compra.descricao_status_executado:
                                        logging.error('arbitragem NAO zerou a compra na {}, o status\status executado veio {}\{}'.format(corretoraCompra.nome,ordem_compra.status,ordem_compra.descricao_status_executado))
                                    else:
                                        logging.info('operou arb de {}! com {}brl de pnl estimado com compra de {}{} @{} na {}'.format(ativo,round(pnl/2,2),round(ordem_compra.quantidade_enviada,4),ativo,quero_comprar_a,corretoraCompra.nome))
                                        logging.warning('operou arb de {}! com {}brl de pnl real com compra de {}{} @{} na {}'.format(ativo,round(pnl_real/2,2),round(ordem_compra.quantidade_enviada,4),ativo,ordem_compra.preco_executado,corretoraCompra.nome))
                                        
                                    if ordem_venda.status != ordem_venda.descricao_status_executado:
                                        logging.error('arbitragem NAO zerou a venda na {}, o status\status executado veio {}\{}'.format(corretoraVenda.nome,ordem_venda.status,ordem_venda.descricao_status_executado))
                                    else: 
                                        logging.info('operou arb de {}! com {}brl de pnl estimado com venda de {}{} @{} na {}'.format(ativo,round(pnl/2,2),round(ordem_venda.quantidade_enviada,4),ativo,quero_vender_a,corretoraVenda.nome))
                                        logging.warning('operou arb de {}! com {}brl de pnl real com venda de {}{} @{} na {}'.format(ativo,round(pnl_real/2,2),round(ordem_venda.quantidade_enviada,4),ativo,ordem_venda.preco_executado,corretoraVenda.nome))
                                                                            
                            else:
                                logging.info('arbitragem nao vai enviar ordem de {} porque saldo em reais {} ou saldo em cripto {} nao é suficiente'.format(ativo,round(corretoraCompra.saldo['brl'],2),corretoraVenda.saldo[ativo]))
                        else: 
                            logging.info('arbitragem nao vai enviar ordem de {} porque qtde {} nao é maior que a minima {} ou o valor a pagar {} nao é maior que o minimo {}'.format(ativo,qtdNegociada,Util.retorna_menor_quantidade_venda(ativo),vou_pagar,Util.retorna_menor_valor_compra(ativo)))
                    else:
                        logging.info('arbitragem nao vai enviar ordem de {} porque o pnl estimado: {}=({}-{}) nao é maior que nosso pnl minimo: {}'.format(ativo,round(pnl,2),round(vou_pagar,2),round(vou_ganhar,2),round(pnl_minimo,2)))
                        
                else:
                    logging.info('acabaram as {} na {} ou acabou o saldo em brl na {}'.format(ativo,corretoraVenda.nome,corretoraCompra.nome))
            else:
                logging.info('arbitragem nao vai enviar ordem de {} porque preco compra {} na {} é maior que preco venda {} na {}'.format(ativo,round(preco_de_compra,2),corretoraCompra.nome,round(preco_de_venda,2),corretoraVenda.nome))
                

        except Exception as erro:
            msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de arbitragem, método: simples.', erro)
            raise Exception(msg_erro)

    def paridade_compra(corretoraCompra:Corretora, corretoraVenda:Corretora, ativo, paridade, executarOrdens = False):
        
        #corretora compra é a novadax
        try:
            pnl = 0
            ordem_compra = corretoraCompra.ordem
            ordem_venda = corretoraVenda.ordem

            corretoraCompra.atualizar_saldo()
            corretoraVenda.atualizar_saldo()

            google_sheets = GoogleSheets()

            #compra em paridade em brl
            corretoraCompra.book.obter_ordem_book_por_indice(paridade,'brl')
            corretoraVenda.book.obter_ordem_book_por_indice(paridade,'brl')

            preco_paridade_brl = max(corretoraCompra.book.preco_compra,corretoraVenda.book.preco_compra)#vamos ser conservadores nesse preço da paridade

            #carrego os books de ordem mais recentes, a partir daqui precisamos ser rapidos!!! é a hora do show!!
            #compra em paridade
            corretoraCompra.book.obter_ordem_book_por_indice(ativo,paridade)
            preco_ativo_paridade = corretoraCompra.book.preco_compra

            #venda em brl
            corretoraVenda.book.obter_ordem_book_por_indice(ativo,'brl')
            
            preco_de_compra = preco_paridade_brl * preco_ativo_paridade #(paridade/brl)*(ativo/paridade)--->na compra
            preco_de_venda = corretoraVenda.book.preco_venda #ativo/brl --->na venda

            #se tiver arbitragem, a magica começa!
            if preco_de_compra < preco_de_venda: 

                quantidade_de_compra = corretoraCompra.book.quantidade_compra #qtd no book de ordens
                quantidade_de_venda = corretoraVenda.book.quantidade_venda #qtd no book de ordens

                quanto_posso_comprar = corretoraCompra.saldo[paridade]/(corretoraCompra.book.preco_compra*(1+max(corretoraCompra.corretagem_mercado,corretoraVenda.corretagem_mercado))) #saldo em reais
                quanto_posso_vender = corretoraVenda.saldo[ativo]*(1-corretoraVenda.corretagem_mercado) #saldo em cripto

                # Obtendo a menor quantidade de compra e venda entre as corretoras que tenho saldo para negociar
                qtdNegociada = min(quantidade_de_compra, quantidade_de_venda,quanto_posso_comprar,quanto_posso_vender)
            
                # Verifica em termos financeiros levando em conta as corretagens de compra e venda, se a operação vale a pena
                vou_pagar_em_paridade = qtdNegociada*preco_ativo_paridade*(1+max(corretoraCompra.corretagem_mercado,corretoraVenda.corretagem_mercado))#sendo conservador
                vou_pagar = qtdNegociada*preco_de_compra*(1+corretoraCompra.corretagem_mercado)
                vou_ganhar = qtdNegociada*preco_de_venda*(1-corretoraVenda.corretagem_mercado)

                pnl = vou_ganhar - vou_pagar

                if qtdNegociada !=0:
                    # Teste se o financeiro com a corretagem é menor que o pnl da operação
                    if pnl>0.05:#nao vamos fazer o trade por menos de 5 centavos
                        # Condição para que verificar se o saldo em reais e crypto são suficientes para a operação
                        if (vou_pagar > Util.retorna_menor_valor_compra(ativo)) and (qtdNegociada > Util.retorna_menor_quantidade_venda(ativo)):
                            #se tenho saldo, prossigo
                            if (corretoraCompra.saldo[paridade] >= vou_pagar_em_paridade) and (corretoraVenda.saldo[ativo] >= qtdNegociada): 
                            
                                # Atualiza ordem de compra
                                ordem_compra.quantidade_enviada = qtdNegociada
                                ordem_compra.preco_enviado = preco_ativo_paridade
                                ordem_compra.tipo_ordem = 'market'

                                # Atualiza ordem de venda
                                ordem_venda.quantidade_enviada = qtdNegociada
                                ordem_venda.preco_enviado = preco_de_venda
                                ordem_venda.tipo_ordem = 'market'

                                quero_comprar_a = round(preco_de_compra,4)
                                quero_vender_a = round(preco_de_venda,4)

                                logging.info('arbitragem vai comprar {}{} @{} na {} e vender @{} na {} que tem {} de saldo'.format(round(qtdNegociada,4),ativo,quero_comprar_a,corretoraCompra.nome,quero_vender_a,corretoraVenda.nome,corretoraVenda.saldo[ativo]))
                            
                                if executarOrdens:
                                    #efetivamente envia as ordens
                                    ordem_compra = corretoraCompra.enviar_ordem_compra(ordem_compra,ativo,paridade)
                                    ordem_venda = corretoraVenda.enviar_ordem_venda(ordem_venda,ativo)
                                    Caixa.zera_o_pnl_em_cripto(corretoraCompra,corretoraVenda,paridade) #aqui é o pulo gato onde zeramos o pnl feito em paridade

                                    realmente_paguei = qtdNegociada*ordem_compra.preco_executado*(1+corretoraCompra.corretagem_mercado)
                                    realmente_ganhei = qtdNegociada*ordem_venda.preco_executado*(1-corretoraVenda.corretagem_mercado)

                                    pnl_real = realmente_ganhei - realmente_paguei
                                
                                    if ordem_compra.status != ordem_compra.descricao_status_executado:
                                        logging.error('arbitragem paridade NAO zerou na {}, o status\status executado veio {}\{}'.format(corretoraCompra.nome,ordem_compra.status,ordem_compra.descricao_status_executado))
                                    else:
                                        logging.info('operou arb paridade de {}! + {}brl de pnl estimado com compra de {}{} @{} na {}'.format(ativo,round(pnl/2,2),round(qtdNegociada,4),ativo,quero_comprar_a,corretoraCompra.nome))
                                        logging.warning('operou arb paridade de {}! + {}brl de pnl real com compra de {}{} @{} na {}'.format(ativo,round(pnl_real/2,2),round(qtdNegociada,4),ativo,ordem_compra.preco_executado,corretoraCompra.nome))
                                        google_sheets.escrever_operacao(['{}|{}|{}|C|{}|{}|{}|{}'.format(ativo,corretoraCompra.nome,ordem_compra.preco_executado,round(qtdNegociada,4),pnl_real/2,'ARBITRAGEM',Util.excel_date(datetime.now()))])
                                        
                                    if ordem_venda.status != ordem_venda.descricao_status_executado:
                                        logging.error('arbitragem paridade NAO zerou na {}, o status veio {}\{}'.format(corretoraVenda.nome,ordem_venda.status,ordem_venda.descricao_status_executado))
                                    else: 
                                        logging.info('operou arb paridade de {}! + {}brl de pnl estimado com venda de {}{} @{} na {}'.format(ativo,round(pnl/2,2),round(qtdNegociada,4),ativo,quero_vender_a,corretoraVenda.nome))
                                        logging.warning('operou arb paridade de {}! + {}brl de pnl real com venda de {}{} @{} na {}'.format(ativo,round(pnl_real/2,2),round(qtdNegociada,4),ativo,ordem_venda.preco_executado,corretoraVenda.nome))
                                        google_sheets.escrever_operacao(['{}|{}|{}|V|{}|{}|{}|{}'.format(ativo,corretoraVenda.nome,ordem_venda.preco_executado,round(qtdNegociada,4),pnl_real/2,'ARBITRAGEM', Util.excel_date(datetime.now()))])
                                    
                                    
                            else:
                                logging.info('arbitragem paridade nao vai enviar ordem de {} porque saldo em {} {} ou saldo em {} {} nao é suficiente'.format(ativo,paridade,round(corretoraCompra.saldo[paridade],6),ativo,corretoraVenda.saldo[ativo]))
                        else:
                            logging.info('arbitragem paridade nao vai enviar ordem de {} porque quantidade negociada {} nao é maior que a quantidade minima {}'.format(ativo,qtdNegociada,Util.retorna_menor_quantidade_venda(ativo)))
                    else:
                        logging.info('arbitragem paridade nao vai enviar ordem de {} porque vou pagar {} e só vou ganhar {}'.format(ativo,round(vou_pagar,2),round(vou_ganhar,2)))
                        
                else:
                    logging.info('acabaram as {} na {} ou acabou o saldo em {} na {}'.format(ativo,corretoraVenda.nome,paridade,corretoraCompra.nome))
            else:
                logging.info('arbitragem paridade nao vai enviar ordem de {} porque preco compra {} na {} é maior que preco venda {} na {}'.format(ativo,round(preco_de_compra,2),corretoraCompra.nome,round(preco_de_venda,2),corretoraVenda.nome))
                

        except Exception as erro:
            msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de arbitragem, método: paridade_compra', erro)
            raise Exception(msg_erro)

    def paridade_venda(corretoraCompra:Corretora, corretoraVenda:Corretora, ativo, paridade, executarOrdens = False):
        
        #corretora venda é a novadax
        #corretora compra é ordem simples
        try:
            pnl = 0
            ordem_compra = corretoraCompra.ordem
            ordem_venda = corretoraVenda.ordem

            corretoraCompra.atualizar_saldo()
            corretoraVenda.atualizar_saldo()

            google_sheets = GoogleSheets()

            #preços da paridade em brl
            corretoraCompra.book.obter_ordem_book_por_indice(paridade,'brl')
            corretoraVenda.book.obter_ordem_book_por_indice(paridade,'brl')

            preco_paridade_brl = min(corretoraCompra.book.preco_venda,corretoraVenda.book.preco_venda)#vamos ser conservadores nesse preço da paridade

            #carrego os books de ordem mais recentes, a partir daqui precisamos ser rapidos!!! é a hora do show!!
            #venda em paridade
            corretoraVenda.book.obter_ordem_book_por_indice(ativo,paridade)
            preco_ativo_paridade = corretoraVenda.book.preco_venda

            #compra em brl
            corretoraCompra.book.obter_ordem_book_por_indice(ativo,'brl')
            
            preco_de_venda = preco_paridade_brl * preco_ativo_paridade #(paridade/brl)*(ativo/paridade)--->na venda
            preco_de_compra = corretoraCompra.book.preco_compra #ativo/brl --->na compra

            #se tiver arbitragem, a magica começa!
            if preco_de_compra < preco_de_venda: 

                quantidade_de_compra = corretoraCompra.book.quantidade_compra #qtd no book de ordens
                quantidade_de_venda = corretoraVenda.book.quantidade_venda #qtd no book de ordens

                quanto_posso_comprar = corretoraCompra.saldo['brl']/(preco_de_compra*(1+corretoraCompra.corretagem_mercado)) #saldo em reais
                quanto_posso_vender = corretoraVenda.saldo[ativo]*(1-corretoraVenda.corretagem_mercado) #saldo em cripto

                # Obtendo a menor quantidade de compra e venda entre as corretoras que tenho saldo para negociar
                qtdNegociada = min(quantidade_de_compra, quantidade_de_venda,quanto_posso_comprar,quanto_posso_vender)
            
                # Verifica em termos financeiros levando em conta as corretagens de compra e venda, se a operação vale a pena
                vou_pagar = qtdNegociada*preco_de_compra*(1+corretoraCompra.corretagem_mercado)
                vou_ganhar = qtdNegociada*preco_de_venda*(1-corretoraVenda.corretagem_mercado)*((1-max(corretoraCompra.corretagem_mercado,corretoraVenda.corretagem_mercado)))
                
                pnl = vou_ganhar - vou_pagar

                if qtdNegociada !=0:#devo estar sem saldo se isso acontecer

                    # Teste se o financeiro com a corretagem é menor que o pnl da operação
                    if pnl>0.05:#nao vamos fazer o trade por menos de 5 centavos

                        # Condição para que verificar se o saldo em reais e crypto são suficientes para a operação
                        if (vou_pagar > Util.retorna_menor_valor_compra(ativo)) and (qtdNegociada > Util.retorna_menor_quantidade_venda(ativo)):
                            #se tenho saldo, prossigo
                            if (corretoraCompra.saldo['brl'] >= vou_pagar) and (corretoraVenda.saldo[ativo] >= qtdNegociada): 
                            
                                # Atualiza ordem de compra
                                ordem_compra.quantidade_enviada = qtdNegociada
                                ordem_compra.preco_enviado = preco_de_compra#normal, em brl
                                ordem_compra.tipo_ordem = 'market'

                                # Atualiza ordem de venda
                                ordem_venda.quantidade_enviada = qtdNegociada
                                ordem_venda.preco_enviado = preco_ativo_paridade#aqui é na paridade
                                ordem_venda.tipo_ordem = 'market'

                                quero_comprar_a = round(preco_de_compra,4)
                                quero_vender_a = round(preco_de_venda,4)

                                logging.info('arbitragem vai comprar {}{} @{} na {} e vender @{} na {} que tem {} de saldo'.format(round(qtdNegociada,4),ativo,quero_comprar_a,corretoraCompra.nome,quero_vender_a,corretoraVenda.nome,corretoraVenda.saldo[ativo]))
                            
                                if executarOrdens:
                                    #efetivamente envia as ordens
                                    ordem_compra = corretoraCompra.enviar_ordem_compra(ordem_compra,ativo)
                                    ordem_venda = corretoraVenda.enviar_ordem_venda(ordem_venda,ativo,paridade)
                                    Caixa.zera_o_pnl_em_cripto(corretoraCompra,corretoraVenda,paridade) #aqui é o pulo gato onde zeramos o pnl feito em paridade

                                    realmente_paguei = qtdNegociada*ordem_compra.preco_executado*(1+corretoraCompra.corretagem_mercado)
                                    realmente_ganhei = qtdNegociada*ordem_venda.preco_executado*(1-corretoraVenda.corretagem_mercado)

                                    pnl_real = realmente_ganhei - realmente_paguei
                                
                                    if ordem_compra.status != ordem_compra.descricao_status_executado:
                                        logging.error('arbitragem paridade NAO zerou na {}, o status\status executado veio {}\{}'.format(corretoraCompra.nome,ordem_compra.status,ordem_compra.descricao_status_executado))
                                    else:
                                        logging.info('operou arb paridade de {}! + {}brl de pnl estimado com compra de {}{} @{} na {}'.format(ativo,round(pnl/2,2),round(qtdNegociada,4),ativo,quero_comprar_a,corretoraCompra.nome))
                                        logging.warning('operou arb paridade de {}! + {}brl de pnl real com compra de {}{} @{} na {}'.format(ativo,round(pnl_real/2,2),round(qtdNegociada,4),ativo,ordem_compra.preco_executado,corretoraCompra.nome))
                                        google_sheets.escrever_operacao(['{}|{}|{}|C|{}|{}|{}|{}'.format(ativo,corretoraCompra.nome,ordem_compra.preco_executado,round(qtdNegociada,4),pnl_real/2,'ARBITRAGEM', Util.excel_date(datetime.now()))])
                                        
                                    if ordem_venda.status != ordem_venda.descricao_status_executado:
                                        logging.error('arbitragem paridade NAO zerou na {}, o status veio {}\{}'.format(corretoraVenda.nome,ordem_venda.status,ordem_venda.descricao_status_executado))
                                    else: 
                                        logging.info('operou arb paridade de {}! + {}brl de pnl estimado com venda de {}{} @{} na {}'.format(ativo,round(pnl/2,2),round(qtdNegociada,4),ativo,quero_vender_a,corretoraVenda.nome))
                                        logging.warning('operou arb paridade de {}! + {}brl de pnl real com venda de {}{} @{} na {}'.format(ativo,round(pnl_real/2,2),round(qtdNegociada,4),ativo,ordem_venda.preco_executado,corretoraVenda.nome))
                                        google_sheets.escrever_operacao(['{}|{}|{}|V|{}|{}|{}|{}'.format(ativo,corretoraVenda.nome,ordem_venda.preco_executado,round(qtdNegociada,4),pnl_real/2,'ARBITRAGEM', Util.excel_date(datetime.now()))])
                                    
                                    
                            else:
                                logging.info('arbitragem paridade nao vai enviar ordem de {} porque saldo em {} {} ou saldo em {} {} nao é suficiente'.format(ativo,paridade,round(corretoraCompra.saldo[paridade],6),ativo,corretoraVenda.saldo[ativo]))
                        else:
                            logging.info('arbitragem paridadenao vai enviar ordem de {} porque quantidade negociada {} nao é maior que a quantidade minima {}'.format(ativo,qtdNegociada,Util.retorna_menor_quantidade_venda(ativo)))
                    else:
                        logging.info('arbitragem paridade nao vai enviar ordem de {} porque vou pagar {} e só vou ganhar {}'.format(ativo,round(vou_pagar,2),round(vou_ganhar,2)))
                        
                else:
                    logging.info('acabaram as {} na {} ou acabou o saldo em {} na {}'.format(ativo,corretoraVenda.nome,paridade,corretoraCompra.nome))
            else:
                logging.info('arbitragem paridade nao vai enviar ordem de {} porque preco compra {} na {} é maior que preco venda {} na {}'.format(ativo,round(preco_de_compra,2),corretoraCompra.nome,round(preco_de_venda,2),corretoraVenda.nome))
                

        except Exception as erro:
            msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de arbitragem, método: paridade_venda', erro)
            raise Exception(msg_erro)
    

if __name__ == "__main__":

    from datetime import datetime
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
    
    CorretoraMaisLiquida = Corretora(corretora_mais_liquida)
    CorretoraMenosLiquida = Corretora(corretora_menos_liquida)

    while True:
        for moeda in lista_de_moedas:
            try:
                # Instancia das corretoras 
                CorretoraMaisLiquida = Corretora(corretora_mais_liquida)
                CorretoraMenosLiquida = Corretora(corretora_menos_liquida)

                # Roda a arbitragem nas 2 corretoras

                tem_arb = True
                while tem_arb:
                    tem_arb = Arbitragem.simples(CorretoraMaisLiquida, CorretoraMenosLiquida, moeda, True)
                
                tem_arb = True
                while tem_arb:
                    tem_arb = Arbitragem.simples(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True)   
                                
            except Exception as erro:        
                logging.error(erro) 
            
        
        
