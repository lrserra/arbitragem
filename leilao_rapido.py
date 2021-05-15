import logging
from datetime import datetime
from uteis.corretora import Corretora
from uteis.util import Util
from uteis.ordem import Ordem


if __name__ == "__main__":

    #bibliotecas do python
    import requests
    import json
    import time
    import logging
    import math
    from datetime import datetime, timedelta
    
    #bibliotecas nossas
    from uteis.util import Util
    from uteis.corretora import Corretora
    from caixa import Caixa
    from leilao_rapido import Leilao
    
    #inicializa arquivo de logs, no arquivo vai a porra toda, mas no console só os warning ou acima
    logging.basicConfig(filename='leilao_rapido.log', level=logging.INFO,
                        format='[%(asctime)s][%(levelname)s][%(message)s]')
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    logging.getLogger().addHandler(console)

    #essa parte executa apenas uma vez
    #step 1
    lista_de_moedas = Util.obter_lista_de_moedas()
    qtd_de_moedas = len(lista_de_moedas)
    corretora_mais_liquida = Util.obter_corretora_de_maior_liquidez()
    corretora_menos_liquida = Util.obter_corretora_de_menor_liquidez()
    
    '''
    nesse script vamos 
    1 - listar todas moedas que queremos negociar 
    2 - enviar ordem de leilao (se valer a pena) para todas moedas
    3 - listar ordem abertas e verificar por moeda
        a) se fui executado zerar
        b) se precisar recolocar ordem, cancela e recoloca
        c) loga pnl se executado
    4 - após um tempo x no loop (3), voltar pro (2)

    '''
    #essa parte faz a cada 5 minutos
    while True:
    
        corretoraZeragem = Corretora(corretora_mais_liquida)
        corretoraLeilao = Corretora(corretora_menos_liquida)
        
        Caixa.atualiza_saldo_inicial(lista_de_moedas,corretoraZeragem,corretoraLeilao)
        Caixa.zera_o_pnl_em_cripto(corretoraZeragem,corretoraLeilao,'',False)

        corretoraZeragem.atualizar_saldo()
        corretoraLeilao.atualizar_saldo()

        #step 2: else só pode ir ao proximo step se tem ordens abertas
        qtd_ordens_abertas = 0
        while qtd_ordens_abertas==0:

            for moeda in lista_de_moedas:
            
                #carrego os books de ordem mais recentes, a partir daqui precisamos ser rapidos
                corretoraLeilao.book.obter_ordem_book_por_indice(moeda,'brl',0,True,True)
                corretoraZeragem.book.obter_ordem_book_por_indice(moeda,'brl',0,True,True)

                #define quantidade minima de caixa para enviarmos o trade
                fracao_do_caixa = corretoraLeilao.saldo['brl']/(corretoraLeilao.saldo['brl']+corretoraZeragem.saldo['brl'])
                
                if fracao_do_caixa < 0.995:
                    Leilao.envia_leilao_compra(corretoraLeilao,corretoraZeragem,moeda,qtd_de_moedas,True)  
                
                if fracao_do_caixa > 0.005:
                    Leilao.envia_leilao_venda(corretoraLeilao,corretoraZeragem,moeda,qtd_de_moedas,True)
            
            ordens_abertas = [[ordem_aberta['id'],ordem_aberta['coin'].lower()] for ordem_aberta in corretoraLeilao.obter_todas_ordens_abertas() if ordem_aberta['coin'].lower() in lista_de_moedas]
            qtd_ordens_abertas = len(ordens_abertas)

        #step 3: essa parte faz em loop de 5 minutos
        agora = datetime.now() 
        proximo_ciclo = agora + timedelta(minutes=5)
        logging.warning('proximo ciclo até: {} '.format(proximo_ciclo))
        logging.warning('no proximo ciclo serao consideradas {} ordens'.format(qtd_ordens_abertas))
        
        while agora < proximo_ciclo and qtd_ordens_abertas > 0:
            
            agora = datetime.now() 
            ordens_abertas = [[ordem_aberta['id'],ordem_aberta['coin'].lower()] for ordem_aberta in corretoraLeilao.obter_todas_ordens_abertas() if ordem_aberta['coin'].lower() in lista_de_moedas]
            qtd_ordens_abertas = len(ordens_abertas)

            for ordem_aberta in ordens_abertas:
                cancelou = False
                ordem_leilao = Ordem()
                ordem_leilao.id = ordem_aberta[0]
                moeda = ordem_aberta[1]
                ordem_leilao = corretoraLeilao.obter_ordem_por_id(moeda,ordem_leilao)
                
                if ordem_leilao.direcao == 'compra':
                    ordem_zeragem,cancelou = Leilao.atualiza_leilao_de_venda(corretoraLeilao,corretoraZeragem,moeda,ordem_leilao,True)
                    
                    if cancelou:
                    
                        corretoraLeilao.book.obter_ordem_book_por_indice(moeda,'brl',0,True,True)
                        corretoraZeragem.book.obter_ordem_book_por_indice(moeda,'brl',0,True,True)
                        Leilao.envia_leilao_venda(corretoraLeilao,corretoraZeragem,moeda,qtd_de_moedas,True)
                        
                        #agora vai logar pnl
                        if  ordem_zeragem.id != 0:

                            vendi_a = round(ordem_zeragem.preco_executado,2)
                            comprei_a = round(ordem_leilao.preco_enviado,2)
                            quantidade = round(ordem_zeragem.quantidade_executada,4)

                            pnl = round(((vendi_a*(1-corretoraZeragem.corretagem_mercado))-(comprei_a*(1+corretoraLeilao.corretagem_limitada))) * quantidade,2)

                            logging.warning('operou leilao rapido de venda de {}! + {}brl de pnl (venda de {}{} @{} na {} e compra a @{} na {})'.format(moeda,pnl,quantidade,moeda,vendi_a,corretoraZeragem.nome,comprei_a,corretoraLeilao.nome))
                            
                            quantidade_executada_compra = ordem_leilao.quantidade_executada
                            quantidade_executada_venda = ordem_zeragem.quantidade_executada

                            Util.adicionar_linha_em_operacoes(moeda,corretoraLeilao.nome,comprei_a,quantidade_executada_compra,corretoraZeragem.nome,vendi_a,quantidade_executada_venda,pnl,'LEILAO',str(datetime.now()))

                elif ordem_leilao.direcao =='venda':
                    ordem_zeragem,cancelou = Leilao.atualiza_leilao_de_compra(corretoraLeilao,corretoraZeragem,moeda,ordem_leilao,True)
                    
                    if cancelou:
                        
                        corretoraLeilao.book.obter_ordem_book_por_indice(moeda,'brl',0,True,True)
                        corretoraZeragem.book.obter_ordem_book_por_indice(moeda,'brl',0,True,True)
                        Leilao.envia_leilao_compra(corretoraLeilao,corretoraZeragem,moeda,qtd_de_moedas,True)
                    
                    #agora vai logar pnl
                    if ordem_zeragem.id != 0:
                        
                            comprei_a = round(ordem_zeragem.preco_executado,2)
                            vendi_a = round(ordem_leilao.preco_enviado,2)
                            quantidade = round(ordem_zeragem.quantidade_executada,4)

                            pnl = round((vendi_a * (1-corretoraLeilao.corretagem_limitada) - comprei_a * (1+corretoraZeragem.corretagem_mercado)) * quantidade,2)

                            logging.warning('operou leilao rapido de compra de {}! + {}brl de pnl (compra de {}{} @{} na {} e venda a @{} na {})'.format(moeda,pnl,quantidade,moeda,comprei_a,corretoraZeragem.nome,vendi_a,corretoraLeilao.nome))
                            
                            quantidade_executada_compra = ordem_zeragem.quantidade_executada
                            quantidade_executada_venda = ordem_leilao.quantidade_executada

                            Util.adicionar_linha_em_operacoes(moeda,corretoraZeragem.nome,comprei_a,quantidade_executada_compra,corretoraLeilao.nome,vendi_a,quantidade_executada_venda,pnl,'LEILAO',str(datetime.now()))

            #step4: ir ao step 2



class Leilao:

    def envia_leilao_compra(corretoraLeilao:Corretora, corretoraZeragem:Corretora, ativo, qtd_de_moedas, executarOrdens = False):

            retorno_venda_corretora_leilao = Ordem()
            
            try:
                preco_que_vou_vender = corretoraLeilao.book.preco_compra-0.01 #primeiro no book de ordens - 1 centavo
                preco_de_zeragem = corretoraZeragem.book.preco_compra # zeragem no primeiro book de ordens

                # Valida se existe oportunidade de leilão
                if (preco_que_vou_vender*(1-corretoraLeilao.corretagem_limitada) >= (1+corretoraZeragem.corretagem_mercado) * preco_de_zeragem):
                    
                    logging.info('leilao de compra aberta para moeda {} no preço de venda {} e preço de zeragem {}'.format(ativo,round(preco_que_vou_vender,2),round(preco_de_zeragem,2)))                                

                    # Gostaria de vender no leilão pelo 1/4 do que eu tenho de saldo em crypto
                    gostaria_de_vender = corretoraLeilao.saldo[ativo] / 4
                    maximo_que_consigo_zerar = corretoraZeragem.saldo['brl'] / (qtd_de_moedas*preco_de_zeragem)
                    #se vc for executada nessa quantidade inteira, talvez nao tera lucro
                    maximo_que_zero_com_lucro = corretoraZeragem.book.obter_quantidade_abaixo_de_preco_compra(preco_que_vou_vender)
                    qtdNegociada = min(gostaria_de_vender,maximo_que_consigo_zerar,maximo_que_zero_com_lucro)

                    # Nao pode ter saldo na mercado de menos de um real
                    if (qtdNegociada*preco_que_vou_vender > Util.retorna_menor_valor_compra(ativo) and corretoraZeragem.saldo['brl'] > Util.retorna_menor_valor_compra(ativo)):
                        
                        
                        if executarOrdens and qtdNegociada > Util.retorna_menor_quantidade_venda(ativo):
                            
                            logging.info('Leilão compra rapida vai enviar ordem de venda de {} limitada a {}'.format(ativo,preco_que_vou_vender))
                            corretoraLeilao.ordem.preco_enviado = preco_que_vou_vender
                            corretoraLeilao.ordem.quantidade_enviada = qtdNegociada
                            corretoraLeilao.ordem.tipo_ordem = 'limited'
                            retorno_venda_corretora_leilao = corretoraLeilao.enviar_ordem_venda(corretoraLeilao.ordem,ativo) 
                    else:
                        financeiro_venda = qtdNegociada*preco_que_vou_vender
                        financeiro_venda_minimo = Util.retorna_menor_valor_compra(ativo)
                        zeragem_compra = corretoraZeragem.saldo['brl']
                        zeragem_compra_minimo = Util.retorna_menor_valor_compra(ativo)
                        logging.info('leilao de compra nao executado para moeda {}, pois o financeiro venda: {} < que financeiro venda minimo: {}, ou zeragem compra: {} < zeragem compra minimo: {}'.format(ativo,round(financeiro_venda,2),round(financeiro_venda_minimo,2),round(zeragem_compra,2),round(zeragem_compra_minimo,2)))   
                else:
                    logging.info('leilao compra de {} nao vale a pena, (1+corretagem)*{} é menor que (1-corretagem)*{}'.format(ativo,preco_que_vou_vender,preco_de_zeragem))

            except Exception as erro:
                    msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de leilão, método: compra. Msg Corretora:', erro)
                    raise Exception(msg_erro)

            return retorno_venda_corretora_leilao

    def envia_leilao_venda(corretoraLeilao:Corretora, corretoraZeragem:Corretora, ativo, qtd_de_moedas , executarOrdens = False):

        retorno_compra_corretora_leilao = Ordem()

        try:

            preco_que_vou_comprar = corretoraLeilao.book.preco_venda+0.01 #primeiro no book de ordens + 1 centavo
            preco_de_zeragem = corretoraZeragem.book.preco_venda # zeragem no primeiro book de ordens

            # Valida se existe oportunidade de leilão
            if preco_que_vou_comprar*(1+corretoraLeilao.corretagem_limitada) <= preco_de_zeragem*(1-corretoraZeragem.corretagem_mercado):
                logging.info('leilao de venda aberta para moeda {} no preço de compra {} e preço de zeragem {}'.format(ativo,round(preco_que_vou_comprar,2),round(preco_de_zeragem,2)))                   

                gostaria_de_comprar = corretoraLeilao.saldo['brl'] / (qtd_de_moedas * preco_que_vou_comprar)
                maximo_que_consigo_zerar = corretoraZeragem.saldo[ativo] / 4
                #se vc for executada nessa quantidade inteira, talvez nao tera lucro
                maximo_que_zero_com_lucro = corretoraZeragem.book.obter_quantidade_acima_de_preco_venda(preco_que_vou_comprar)
                qtdNegociada = min(gostaria_de_comprar,maximo_que_consigo_zerar,maximo_que_zero_com_lucro)

                # Se quantidade negociada maior que a quantidade mínima permitida de venda
                if qtdNegociada > Util.retorna_menor_quantidade_venda(ativo):

                    if executarOrdens:

                        logging.info('leilao venda rapida vai enviar ordem de venda de {} limitada a {}'.format(ativo,preco_que_vou_comprar))
                        corretoraLeilao.ordem.preco_enviado = preco_que_vou_comprar
                        corretoraLeilao.ordem.quantidade_enviada = qtdNegociada
                        corretoraLeilao.ordem.tipo_ordem = 'limited'    
                        retorno_compra_corretora_leilao = corretoraLeilao.enviar_ordem_compra(corretoraLeilao.ordem,ativo)
                else:
                    quantidade_compra = qtdNegociada
                    quantidade_venda_minimo = Util.retorna_menor_quantidade_venda(ativo)
                    logging.info('leilao de venda nao executado para moeda {} pois nao tem quantidades disponiveis suficientes para venda: {}<{}'.format(ativo,quantidade_compra,quantidade_venda_minimo)) 
            else:
                logging.info('leilao venda de {} nao vale a pena, {} é maior que 0.99*{}'.format(ativo,preco_que_vou_comprar,preco_de_zeragem))
        except Exception as erro:
                msg_erro = Util.retorna_erros_objeto_exception('o, método: venda. Msg Corretora:', erro)
                raise Exception(msg_erro)
        
        return retorno_compra_corretora_leilao

    def atualiza_leilao_de_compra(corretoraLeilao:Corretora, corretoraZeragem:Corretora, ativo, ordem, executarOrdens):

        retorno_compra = Ordem()
        cancelou = False

        try:
            #IMPORTANTE ->qualquer uma dessas condições que for verdade, pode executar e sair do metodo

            #1: executada completamente
            if executarOrdens and ordem.status == corretoraLeilao.descricao_status_executado: # verifica se a ordem foi executada totalmente (Nesse caso o ID = False)
                
                cancelou = True
                if corretoraZeragem.nome == 'MercadoBitcoin':
                    corretoraZeragem.ordem.quantidade_enviada = ordem.quantidade_executada #quando vc compra na mercado, ele compra um pouco a mais e pega pra ele de corretagem, é só vender a mesma qtd
                else:
                    corretoraZeragem.ordem.quantidade_enviada = ordem.quantidade_executada/(1-corretoraZeragem.corretagem_mercado)
                corretoraZeragem.ordem.tipo_ordem = 'market'
                retorno_compra = corretoraZeragem.enviar_ordem_compra(corretoraZeragem.ordem,ativo)
                logging.info('LC1: leilao compra vai zerar ordem executada completamente {} de {} na outra corretora'.format(ordem.id,ativo))
                
                return retorno_compra, cancelou 
            
            #2: executada parcialmente, mais que o valor minimo
            
            corretoraZeragem.book.obter_ordem_book_por_indice(ativo,'brl',0,True,True)
  
            if executarOrdens and ordem.quantidade_executada * corretoraZeragem.book.preco_compra > 0:
            
                if ordem.quantidade_executada * corretoraZeragem.book.preco_compra > Util.retorna_menor_valor_compra(ativo): #mais de xxx reais executado
                
                    logging.info('LC2: leilao compra vai cancelar ordem {} de {} pq fui executado mais que o valor minimo'.format(ordem.id,ativo))
                    cancelou =corretoraLeilao.cancelar_ordem(ativo,ordem.id)

                    # Zera o risco na outra corretora com uma operação à mercado
                    if corretoraZeragem.nome == 'MercadoBitcoin':
                        corretoraZeragem.ordem.quantidade_enviada = ordem.quantidade_executada #quando vc compra na mercado, ele compra um pouco a mais e pega pra ele de corretagem, é só vender a mesma qtd
                    else:
                        corretoraZeragem.ordem.quantidade_enviada = ordem.quantidade_executada/(1-corretoraZeragem.corretagem_mercado)
                    
                    corretoraZeragem.ordem.preco_enviado = float(ordem.preco_executado)
                    corretoraZeragem.ordem.tipo_ordem = 'market'
                    retorno_compra = corretoraZeragem.enviar_ordem_compra(corretoraZeragem.ordem,ativo)

                    return retorno_compra, cancelou 
                else:
                    fui_executado = round(ordem.quantidade_executada * corretoraZeragem.book.preco_compra,4)
                    valor_minimo = round(Util.retorna_menor_valor_compra(ativo),4)
                    logging.info('LC6: leilao compra de {} nao vai fazer nada porque fui executado em {} reais que é menos que o valor minimo de {} reais'.format(ativo,fui_executado,valor_minimo))
                        
            corretoraLeilao.book.obter_ordem_book_por_indice(ativo,'brl',0,True,True) 
            #3: nao sou o primeiro da fila
            if (ordem.preco_enviado != corretoraLeilao.book.preco_compra):
                
                logging.info('LC3: leilao compra vai cancelar ordem {} de {} pq nao sou o primeiro da fila na {}'.format(ordem.id,ativo,corretoraLeilao.nome))
                cancelou = corretoraLeilao.cancelar_ordem(ativo,ordem.id)

                return retorno_compra, cancelou
                
            corretoraZeragem.atualizar_saldo()
            #4: estou sem saldo para zerar
            if (corretoraZeragem.saldo['brl'] < ordem.quantidade_enviada*ordem.preco_enviado):
                
                logging.info('LC4: leilao compra vai cancelar ordem {} de {} pq meu saldo brl {} nao consegue comprar {}'.format(ordem.id,ativo,corretoraZeragem.saldo['brl'],ordem.quantidade_enviada*ordem.preco_enviado))
                cancelou =corretoraLeilao.cancelar_ordem(ativo,ordem.id)

                return retorno_compra, cancelou

            #5: esta dando pnl negativo para zerar tudo
            if (ordem.preco_enviado*(1-corretoraLeilao.corretagem_limitada) < (1+corretoraZeragem.corretagem_mercado) * corretoraZeragem.book.obter_preco_medio_de_compra(ordem.quantidade_enviada)):
                
                logging.info('LC5: leilao compra vai cancelar ordem {} de {} pq o pnl esta dando negativo'.format(ordem.id,ativo))
                cancelou =corretoraLeilao.cancelar_ordem(ativo,ordem.id)

                return retorno_compra, cancelou
                
                            
        except Exception as erro:
            msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de leilão rapido, método: atualiza_leilao_de_compra. (Ativo: {} | Quant: {})'.format(ativo, corretoraZeragem.ordem.quantidade_enviada), erro)
            raise Exception(msg_erro)

        return retorno_compra, cancelou

    def atualiza_leilao_de_venda(corretoraLeilao:Corretora, corretoraZeragem:Corretora, ativo, ordem, executarOrdens):

        retorno_venda = Ordem()
        cancelou = False

        try:
    
            #IMPORTANTE ->qualquer uma dessas condições que for verdade, pode executar e sair do metodo

            #1: executada completamente
            if executarOrdens and ordem.status == corretoraLeilao.descricao_status_executado:
                
                cancelou = True
                corretoraZeragem.ordem.quantidade_enviada = ordem.quantidade_executada*(1-corretoraLeilao.corretagem_limitada)
                corretoraZeragem.ordem.tipo_ordem = 'market'
                retorno_venda = corretoraZeragem.enviar_ordem_venda(corretoraZeragem.ordem,ativo)
                logging.info('LV1: leilao venda vai zerar ordem executada completamente {} de {} na outra corretora'.format(ordem.id,ativo))
                
                return retorno_venda,cancelou

            #2: executada parcialmente, mais que o valor minimo
            if executarOrdens and ordem.quantidade_executada > 0:
            
                if ordem.quantidade_executada > Util.retorna_menor_quantidade_venda(ativo): 
                
                    logging.info('LV2: leilao venda vai cancelar ordem {} de {} pq fui executado mais que o valor minimo'.format(ordem.id,ativo,Util.retorna_menor_quantidade_venda(ativo)))
                    cancelou = corretoraLeilao.cancelar_ordem(ativo,ordem.id)
                
                    logging.info('LV2: leilao venda vai zerar na {} ordem executada {} de {}'.format(corretoraZeragem.nome,ordem.id,ativo))
                    corretoraZeragem.ordem.quantidade_enviada = ordem.quantidade_executada*(1-corretoraLeilao.corretagem_limitada)             
                    corretoraZeragem.ordem.tipo_ordem = 'market'
                    retorno_venda = corretoraZeragem.enviar_ordem_venda(corretoraZeragem.ordem,ativo)
                    
                    return retorno_venda,cancelou
                else:
                    fui_executado = round(ordem.quantidade_executada,4)
                    valor_minimo = round(Util.retorna_menor_quantidade_venda(ativo),4)
                    logging.info('LV6: leilao venda de {} nao vai fazer nada porque fui executado em {} que é menos que o valor minimo de {}'.format(ativo,fui_executado,valor_minimo))

            
            
            corretoraLeilao.book.obter_ordem_book_por_indice(ativo,'brl',0,True,True)
            #3: nao sou o primeiro da fila
            if (ordem.preco_enviado != corretoraLeilao.book.preco_venda):
                
                logging.info('LV3: leilao venda vai cancelar ordem {} de {} pq nao sou o primeiro da fila na {}'.format(ordem.id,ativo,corretoraLeilao.nome))
                cancelou = corretoraLeilao.cancelar_ordem(ativo,ordem.id)
                return retorno_venda,cancelou
                
            #4: estou sem saldo para zerar
            corretoraZeragem.atualizar_saldo()
            if (corretoraZeragem.saldo[ativo] < ordem.quantidade_enviada):
                
                logging.info('LV4: leilao venda vai cancelar ordem {} de {} pq meu saldo em cripto {} é menor que oq eu queria vender {}'.format(ordem.id,ativo,corretoraZeragem.saldo[ativo],ordem.quantidade_enviada))
                cancelou = corretoraLeilao.cancelar_ordem(ativo,ordem.id)
                return retorno_venda,cancelou

            corretoraZeragem.book.obter_ordem_book_por_indice(ativo,'brl',0,True,True)  
            #5: esta dando pnl negativo para zerar tudo    
            if (ordem.preco_enviado*(1+corretoraLeilao.corretagem_limitada) >  corretoraZeragem.book.obter_preco_medio_de_venda(ordem.quantidade_enviada)*(1-corretoraZeragem.corretagem_mercado)):
                
                logging.info('LV5: leilao venda vai cancelar ordem {} de {} pq o pnl esta dando negativo'.format(ordem.id,ativo))
                cancelou = corretoraLeilao.cancelar_ordem(ativo,ordem.id)
                return retorno_venda,cancelou
                
                
        except Exception as erro:
            msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de leilão rapido, método: atualiza_leilao_de_venda. (Ativo: {} | Quant: {})'.format(ativo, corretoraZeragem.ordem.quantidade_enviada), erro)
            raise Exception(msg_erro)
        
        return retorno_venda,cancelou


