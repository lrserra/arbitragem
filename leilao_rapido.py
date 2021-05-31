import logging
from datetime import datetime
from uteis.corretora import Corretora
from uteis.util import Util
from uteis.ordem import Ordem


if __name__ == "__main__":

    #bibliotecas do python

    import logging
    from datetime import datetime, timedelta
    
    #bibliotecas nossas
    from uteis.util import Util
    from uteis.corretora import Corretora
    from uteis.googleSheets import GoogleSheets
    from caixa import Caixa
    from leilao_rapido import Leilao

    google_sheets = GoogleSheets()
    
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
    3 - listar ordem abertas e verificar por moeda (falta verificar ordens executadas completamente)
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

        Caixa.envia_saldo_google(corretoraZeragem,corretoraLeilao)

        #step 2: else só pode ir ao proximo step se tem ordens abertas
        qtd_ordens_abertas = 0
        ordens_enviadas = []

        while qtd_ordens_abertas==0:

            for moeda in lista_de_moedas:
            
                ordem_enviada = Ordem()
                #carrego os books de ordem mais recentes, a partir daqui precisamos ser rapidos
                corretoraLeilao.book.obter_ordem_book_por_indice(moeda,'brl',0,True,True)
                corretoraZeragem.book.obter_ordem_book_por_indice(moeda,'brl',0,True,True)

                #define quantidade minima de caixa e moeda para enviarmos o trade
                #essa parte é importante pq apenas as ordens enviadas aqui serão utilizadas no proximo passo
                fracao_do_caixa = round(corretoraLeilao.saldo['brl']/(corretoraLeilao.saldo['brl']+corretoraZeragem.saldo['brl']),6)
                fracao_da_moeda = round(corretoraLeilao.saldo[moeda]/(corretoraLeilao.saldo[moeda]+corretoraZeragem.saldo[moeda]),6)
                
                if fracao_do_caixa < 0.995 and fracao_da_moeda > 0.05:
                    ordem_enviada = Leilao.envia_leilao_compra(corretoraLeilao,corretoraZeragem,moeda,qtd_de_moedas,True)
                    if ordem_enviada.id != 0: #se colocar uma nova ordem, vamos logar como ordem enviada
                        ordens_enviadas.append([ordem_enviada.id,moeda])
                else:
                    logging.info('leilao rapido de compra nao enviara ordem de {} porque a fracao de caixa {} é maior que 99.5% ou a fracao de moeda {} é menor que 5%'.format(moeda,fracao_do_caixa*100,fracao_da_moeda*100))  
                 
                if fracao_do_caixa > 0.005 and fracao_da_moeda < 0.95:
                    ordem_enviada = Leilao.envia_leilao_venda(corretoraLeilao,corretoraZeragem,moeda,qtd_de_moedas,True)
                    if ordem_enviada.id != 0: #se colocar uma nova ordem, vamos logar como ordem enviada
                        ordens_enviadas.append([ordem_enviada.id,moeda])
                else:
                    logging.info('leilao rapido de venda nao enviara ordem de {} porque a fracao de caixa {} é menor que 0.5% ou a fracao de moeda {} é maior que 95%'.format(moeda,fracao_do_caixa*100,fracao_da_moeda*100))
            
            ordens_abertas = [[ordem_aberta['id'],ordem_aberta['coin'].lower()] for ordem_aberta in corretoraLeilao.obter_todas_ordens_abertas() if ordem_aberta['coin'].lower() in lista_de_moedas]
            
            for ordem_enviada in ordens_enviadas:
                if ordem_enviada not in ordens_abertas:
                    logging.warning('ordem enviada {} de {} nao esta na lista de ordem abertas e sera adicionada para zeragem!'.format(ordem_enviada[0],ordem_enviada[1]))
                    ordens_abertas.append(ordem_enviada)
            
            qtd_ordens_abertas = len(ordens_abertas)
            
        #step 3: essa parte faz em loop de 6 minutos
        agora = datetime.now() 
        proximo_ciclo = agora + timedelta(minutes=6)
        logging.warning('proximo ciclo até: {} '.format(proximo_ciclo))
        logging.warning('no proximo ciclo serao consideradas apenas {} ordens!'.format(qtd_ordens_abertas))
        
        while agora < proximo_ciclo and qtd_ordens_abertas > 0:
            
            #vamos atualizar saldo a cada ciclo, para evitar erros operacionais
            corretoraZeragem.atualizar_saldo()
            corretoraLeilao.atualizar_saldo()

            ordens_enviadas = []

            for ordem_aberta in ordens_abertas:
                
                ordem_leilao = Ordem()
                ordem_leilao.id = ordem_aberta[0]
                moeda = ordem_aberta[1]
                ordem_leilao = corretoraLeilao.obter_ordem_por_id(moeda,ordem_leilao)
                
                #a partir daqui é correria! 
                corretoraLeilao.book.obter_ordem_book_por_indice(moeda,'brl',0,True,True)
                corretoraZeragem.book.obter_ordem_book_por_indice(moeda,'brl',0,True,True)
                
                if ordem_leilao.direcao == 'compra':

                    ordem_enviada = Leilao.atualiza_leilao_de_venda(corretoraLeilao,corretoraZeragem,moeda,ordem_leilao,True,qtd_de_moedas,google_sheets)
                    if ordem_enviada.id != 0: #se colocar uma nova ordem, vamos logar como ordem enviada
                        ordens_enviadas.append([ordem_enviada.id,moeda])
                        
                elif ordem_leilao.direcao =='venda':
                    
                    ordem_enviada = Leilao.atualiza_leilao_de_compra(corretoraLeilao,corretoraZeragem,moeda,ordem_leilao,True,qtd_de_moedas,google_sheets)
                    if ordem_enviada.id != 0: #se colocar uma nova ordem, vamos logar como ordem enviada
                        ordens_enviadas.append([ordem_enviada.id,moeda])
                    
                    
            #step4: ir ao step 2
            agora = datetime.now() 
            ordens_abertas = [[ordem_aberta['id'],ordem_aberta['coin'].lower()] for ordem_aberta in corretoraLeilao.obter_todas_ordens_abertas() if ordem_aberta['coin'].lower() in lista_de_moedas]
            
            for ordem_enviada in ordens_enviadas:
                if ordem_enviada not in ordens_abertas:
                    logging.warning('ordem enviada {} de {} nao esta na lista de ordem abertas e sera adicionada para zeragem!'.format(ordem_enviada[0],ordem_enviada[1]))
                    ordens_abertas.append(ordem_enviada)
            
            qtd_ordens_abertas = len(ordens_abertas)



class Leilao:

    def envia_leilao_compra(corretoraLeilao:Corretora, corretoraZeragem:Corretora, ativo, qtd_de_moedas, executarOrdens = False):

            retorno_venda_corretora_leilao = Ordem()
            
            try:
                preco_que_vou_vender = corretoraLeilao.book.preco_compra-0.01 #primeiro no book de ordens - 1 centavo
                preco_de_zeragem = corretoraZeragem.book.preco_compra # zeragem no primeiro book de ordens

                # Valida se existe oportunidade de leilão
                if (preco_que_vou_vender*(1-corretoraLeilao.corretagem_limitada) >= (1+corretoraZeragem.corretagem_mercado) * preco_de_zeragem):
                    
                    logging.info('leilao de compra aberta para moeda {} no preço de venda {} e preço de zeragem {}'.format(ativo,round(preco_que_vou_vender,2),round(preco_de_zeragem,2)))                                
                    logging.info('leilao compra vai usar o saldo na corretora leilao e zeragem. Saldo brl: {}/{} Saldo {}: {}/{}'.format(round(corretoraLeilao.saldo['brl'],2),round(corretoraZeragem.saldo['brl'],2),ativo,round(corretoraLeilao.saldo[ativo],4),round(corretoraZeragem.saldo[ativo],4)))
                    # Gostaria de vender no leilão 0.4 do que eu tenho de saldo em crypto
                    gostaria_de_vender = corretoraLeilao.saldo[ativo] *0.4
                    maximo_que_consigo_zerar = corretoraZeragem.saldo['brl'] / (qtd_de_moedas*preco_de_zeragem)
                    #se vc for executada nessa quantidade inteira, talvez nao tera lucro
                    maximo_que_zero_com_lucro = corretoraZeragem.book.obter_quantidade_abaixo_de_preco_compra(preco_que_vou_vender*(1-corretoraLeilao.corretagem_limitada)*(1-corretoraZeragem.corretagem_mercado))
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
                logging.info('leilao venda vai usar o saldo na corretora leilao e zeragem. Saldo brl: {}/{} Saldo {}: {}/{}'.format(round(corretoraLeilao.saldo['brl'],2),round(corretoraZeragem.saldo['brl'],2),ativo,round(corretoraLeilao.saldo[ativo],4),round(corretoraZeragem.saldo[ativo],4)))
                gostaria_de_comprar = corretoraLeilao.saldo['brl'] / (qtd_de_moedas * preco_que_vou_comprar)
                maximo_que_consigo_zerar = corretoraZeragem.saldo[ativo] *0.4
                #se vc for executada nessa quantidade inteira, talvez nao tera lucro
                maximo_que_zero_com_lucro = corretoraZeragem.book.obter_quantidade_acima_de_preco_venda(preco_que_vou_comprar*(1+corretoraLeilao.corretagem_limitada)*(1+corretoraZeragem.corretagem_mercado))
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

    def atualiza_leilao_de_compra(corretoraLeilao:Corretora, corretoraZeragem:Corretora, ativo, ordem:Ordem, executarOrdens,qtd_de_moedas,google_sheets):

        ordem_enviada = Ordem()
        ordem_zeragem = Ordem()
        cancelou = False
        
        try:
            #IMPORTANTE ->qualquer uma dessas condições que for verdade, pode executar e sair do metodo

            #1: executada completamente
            if executarOrdens and ordem.status == corretoraLeilao.descricao_status_executado: # verifica se a ordem foi executada totalmente (Nesse caso o ID = False)
                
                cancelou = True
                if cancelou: #irrelevante, mas vou manter para ficar igual aos outros
                    ordem_enviada = Leilao.envia_leilao_compra(corretoraLeilao,corretoraZeragem,ativo,qtd_de_moedas,True)

                if corretoraZeragem.nome == 'MercadoBitcoin':
                    corretoraZeragem.ordem.quantidade_enviada = ordem.quantidade_executada #quando vc compra na mercado, ele compra um pouco a mais e pega pra ele de corretagem, é só vender a mesma qtd
                else:
                    corretoraZeragem.ordem.quantidade_enviada = ordem.quantidade_executada/(1-corretoraZeragem.corretagem_mercado)
                corretoraZeragem.ordem.tipo_ordem = 'market'
                logging.info('LC1: leilao compra vai zerar ordem executada completamente {} de {} na outra corretora'.format(ordem.id,ativo))
                ordem_zeragem = corretoraZeragem.enviar_ordem_compra(corretoraZeragem.ordem,ativo)
                
            #2: executada parcialmente, mais que o valor minimo
            
            elif executarOrdens and ordem.quantidade_executada * corretoraZeragem.book.preco_compra > 0:
            
                if ordem.quantidade_executada * corretoraZeragem.book.preco_compra > Util.retorna_menor_valor_compra(ativo): #mais de xxx reais executado
                
                    logging.info('LC2: leilao compra vai cancelar ordem {} de {} pq fui executado mais que o valor minimo'.format(ordem.id,ativo))
                    cancelou =corretoraLeilao.cancelar_ordem(ativo,ordem.id)
                    if cancelou:
                        ordem_enviada = Leilao.envia_leilao_compra(corretoraLeilao,corretoraZeragem,ativo,qtd_de_moedas,True)

                    # Zera o risco na outra corretora com uma operação à mercado
                    if corretoraZeragem.nome == 'MercadoBitcoin':
                        corretoraZeragem.ordem.quantidade_enviada = ordem.quantidade_executada #quando vc compra na mercado, ele compra um pouco a mais e pega pra ele de corretagem, é só vender a mesma qtd
                    else:
                        corretoraZeragem.ordem.quantidade_enviada = ordem.quantidade_executada/(1-corretoraZeragem.corretagem_mercado)
                    
                    logging.info('LC2: leilao compra vai zerar na {} ordem executada {} de {}'.format(corretoraZeragem.nome,ordem.id,ativo))
                    corretoraZeragem.ordem.preco_enviado = float(ordem.preco_executado)
                    corretoraZeragem.ordem.tipo_ordem = 'market'
                    ordem_zeragem = corretoraZeragem.enviar_ordem_compra(corretoraZeragem.ordem,ativo)

                else:
                    fui_executado = round(ordem.quantidade_executada * corretoraZeragem.book.preco_compra,4)
                    valor_minimo = round(Util.retorna_menor_valor_compra(ativo),4)
                    logging.info('LC6: leilao compra de {} nao vai fazer nada porque fui executado em {} reais que é menos que o valor minimo de {} reais'.format(ativo,fui_executado,valor_minimo))
                        
            #agora vai logar pnl
            if ordem_zeragem.id != 0:
                        
                comprei_a = round(ordem_zeragem.preco_executado,2)
                vendi_a = round(ordem.preco_enviado,2)
                quantidade = round(ordem_zeragem.quantidade_executada,4)

                pnl = round((vendi_a * (1-corretoraLeilao.corretagem_limitada) - comprei_a * (1+corretoraZeragem.corretagem_mercado)) * quantidade,2)

                logging.warning('operou leilao rapido de compra de {}! + {}brl de pnl (compra de {}{} @{} na {} e venda a @{} na {})'.format(ativo,pnl,quantidade,ativo,comprei_a,corretoraZeragem.nome,vendi_a,corretoraLeilao.nome))
                
                quantidade_executada_compra = ordem_zeragem.quantidade_executada
                quantidade_executada_venda = ordem.quantidade_executada

                google_sheets.escrever_operacao([ativo,corretoraZeragem.nome,comprei_a,quantidade_executada_compra,corretoraLeilao.nome,vendi_a,quantidade_executada_venda,pnl,'LEILAO',Util.excel_date(datetime.now())])
                corretoraZeragem.atualizar_saldo()
                corretoraLeilao.atualizar_saldo()
                logging.info('leilao compra atualizou o saldo na corretora leilao e zeragem pois foi executado, Saldo brl: {}/{} Saldo {}: {}/{}'.format(round(corretoraLeilao.saldo['brl'],2),round(corretoraZeragem.saldo['brl'],2),ativo,round(corretoraLeilao.saldo[ativo],4),round(corretoraZeragem.saldo[ativo],4)))
                return ordem_enviada

            #3: nao sou o primeiro da fila
            if (ordem.preco_enviado != corretoraLeilao.book.preco_compra) or (corretoraLeilao.book.preco_compra_segundo_na_fila - ordem.preco_enviado > 0.02):
                
                logging.info('LC3: leilao compra vai cancelar ordem {} de {} pq meu preco {} nao é o primeiro da fila {} na {} ou é mais de 2 centavos menor que {}'.format(ordem.id,ativo,ordem.preco_enviado,corretoraLeilao.book.preco_compra,corretoraLeilao.nome,corretoraLeilao.book.preco_compra_segundo_na_fila))
                cancelou = corretoraLeilao.cancelar_ordem(ativo,ordem.id)

                if (corretoraLeilao.book.preco_compra_segundo_na_fila - ordem.preco_enviado > 0.02):
                    corretoraLeilao.book.obter_ordem_book_por_indice(ativo,'brl',0,True,True) #nesse caso especifico é melhor atualizar o book de ordens
                if cancelou:
                    ordem_enviada = Leilao.envia_leilao_compra(corretoraLeilao,corretoraZeragem,ativo,qtd_de_moedas,True)
                return ordem_enviada

            corretoraZeragem.atualizar_saldo()
            #4: estou sem saldo para zerar
            if (corretoraZeragem.saldo['brl'] < ordem.quantidade_enviada*ordem.preco_enviado):
                
                logging.info('LC4: leilao compra vai cancelar ordem {} de {} pq meu saldo brl {} nao consegue comprar {}'.format(ordem.id,ativo,corretoraZeragem.saldo['brl'],ordem.quantidade_enviada*ordem.preco_enviado))
                cancelou =corretoraLeilao.cancelar_ordem(ativo,ordem.id)
                if cancelou:
                    ordem_enviada = Leilao.envia_leilao_compra(corretoraLeilao,corretoraZeragem,ativo,qtd_de_moedas,True)
                return ordem_enviada

            #5: esta dando pnl negativo para zerar tudo
            if (ordem.preco_enviado*(1-corretoraLeilao.corretagem_limitada) < (1+corretoraZeragem.corretagem_mercado) * corretoraZeragem.book.obter_preco_medio_de_compra(ordem.quantidade_enviada)):
                
                logging.info('LC5: leilao compra vai cancelar ordem {} de {} pq o pnl esta dando negativo'.format(ordem.id,ativo))
                cancelou =corretoraLeilao.cancelar_ordem(ativo,ordem.id)
                if cancelou:
                    ordem_enviada = Leilao.envia_leilao_compra(corretoraLeilao,corretoraZeragem,ativo,qtd_de_moedas,True)
                return ordem_enviada
                            
        except Exception as erro:
            msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de leilão rapido, método: atualiza_leilao_de_compra. (Ativo: {} | Quant: {})'.format(ativo, corretoraZeragem.ordem.quantidade_enviada), erro)
            raise Exception(msg_erro)

        return ordem_enviada

    def atualiza_leilao_de_venda(corretoraLeilao:Corretora, corretoraZeragem:Corretora, ativo, ordem:Ordem, executarOrdens,qtd_de_moedas,google_sheets):

        ordem_enviada = Ordem()
        ordem_zeragem = Ordem()
        cancelou = False
        
        try:
    
            #IMPORTANTE ->qualquer uma dessas condições que for verdade, pode executar e sair do metodo

            #1: executada completamente
            if executarOrdens and ordem.status == corretoraLeilao.descricao_status_executado:
                
                cancelou = True
                if cancelou: #irrelevante, mas vou manter para ficar igual aos outros
                    ordem_enviada = Leilao.envia_leilao_venda(corretoraLeilao,corretoraZeragem,ativo,qtd_de_moedas,True)

                corretoraZeragem.ordem.quantidade_enviada = ordem.quantidade_executada*(1-corretoraLeilao.corretagem_limitada)
                corretoraZeragem.ordem.tipo_ordem = 'market'
                logging.info('LV1: leilao venda vai zerar ordem executada completamente {} de {} na outra corretora'.format(ordem.id,ativo))
                ordem_zeragem = corretoraZeragem.enviar_ordem_venda(corretoraZeragem.ordem,ativo)
                
            #2: executada parcialmente, mais que o valor minimo
            elif executarOrdens and ordem.quantidade_executada > 0:
            
                if ordem.quantidade_executada > Util.retorna_menor_quantidade_venda(ativo): 
                
                    logging.info('LV2: leilao venda vai cancelar ordem {} de {} pq fui executado mais que o valor minimo'.format(ordem.id,ativo,Util.retorna_menor_quantidade_venda(ativo)))
                    cancelou = corretoraLeilao.cancelar_ordem(ativo,ordem.id)

                    if cancelou:
                        ordem_enviada = Leilao.envia_leilao_venda(corretoraLeilao,corretoraZeragem,ativo,qtd_de_moedas,True)
                
                    logging.info('LV2: leilao venda vai zerar na {} ordem executada {} de {}'.format(corretoraZeragem.nome,ordem.id,ativo))
                    corretoraZeragem.ordem.quantidade_enviada = ordem.quantidade_executada*(1-corretoraLeilao.corretagem_limitada)             
                    corretoraZeragem.ordem.tipo_ordem = 'market'
                    ordem_zeragem = corretoraZeragem.enviar_ordem_venda(corretoraZeragem.ordem,ativo)
                    
                else:
                    fui_executado = round(ordem.quantidade_executada,4)
                    valor_minimo = round(Util.retorna_menor_quantidade_venda(ativo),4)
                    logging.info('LV6: leilao venda de {} nao vai fazer nada porque fui executado em {} que é menos que o valor minimo de {}'.format(ativo,fui_executado,valor_minimo))

            if  ordem_zeragem.id != 0:

                vendi_a = round(ordem_zeragem.preco_executado,2)
                comprei_a = round(ordem.preco_enviado,2)
                quantidade = round(ordem_zeragem.quantidade_executada,4)

                pnl = round(((vendi_a*(1-corretoraZeragem.corretagem_mercado))-(comprei_a*(1+corretoraLeilao.corretagem_limitada))) * quantidade,2)

                logging.warning('operou leilao rapido de venda de {}! + {}brl de pnl (venda de {}{} @{} na {} e compra a @{} na {})'.format(ativo,pnl,quantidade,ativo,vendi_a,corretoraZeragem.nome,comprei_a,corretoraLeilao.nome))
                
                quantidade_executada_compra = ordem.quantidade_executada
                quantidade_executada_venda = ordem_zeragem.quantidade_executada

                google_sheets.escrever_operacao([ativo,corretoraLeilao.nome,comprei_a,quantidade_executada_compra,corretoraZeragem.nome,vendi_a,quantidade_executada_venda,pnl,'LEILAO', Util.excel_date(datetime.now())])
                corretoraZeragem.atualizar_saldo()
                corretoraLeilao.atualizar_saldo()
                logging.info('leilao venda atualizou o saldo na corretora leilao e zeragem pois foi executado, Saldo brl: {}/{} Saldo {}: {}/{}'.format(round(corretoraLeilao.saldo['brl'],2),round(corretoraZeragem.saldo['brl'],2),ativo,round(corretoraLeilao.saldo[ativo],4),round(corretoraZeragem.saldo[ativo],4)))
                return ordem_enviada

            #3: nao sou o primeiro da fila
            if (ordem.preco_enviado != corretoraLeilao.book.preco_venda) or (ordem.preco_enviado -corretoraLeilao.book.preco_venda_segundo_na_fila > 0.02):
                
                logging.info('LV3: leilao venda vai cancelar ordem {} de {} pq meu preco {} nao é o primeiro da fila {} na {} ou é mais de 2 centavos maior que {}'.format(ordem.id,ativo,ordem.preco_enviado,corretoraLeilao.book.preco_venda,corretoraLeilao.nome,corretoraLeilao.book.preco_venda_segundo_na_fila))
                cancelou = corretoraLeilao.cancelar_ordem(ativo,ordem.id)

                if (ordem.preco_enviado -corretoraLeilao.book.preco_venda_segundo_na_fila > 0.02):
                    corretoraLeilao.book.obter_ordem_book_por_indice(ativo,'brl',0,True,True) #nesse caso especifico é melhor atualizar o book de ordens

                if cancelou:
                    ordem_enviada = Leilao.envia_leilao_venda(corretoraLeilao,corretoraZeragem,ativo,qtd_de_moedas,True)
                return ordem_enviada
                
            #4: estou sem saldo para zerar
            corretoraZeragem.atualizar_saldo()
            if (corretoraZeragem.saldo[ativo] < ordem.quantidade_enviada):
                
                logging.info('LV4: leilao venda vai cancelar ordem {} de {} pq meu saldo em cripto {} é menor que oq eu queria vender {}'.format(ordem.id,ativo,corretoraZeragem.saldo[ativo],ordem.quantidade_enviada))
                cancelou = corretoraLeilao.cancelar_ordem(ativo,ordem.id)
                if cancelou:
                    ordem_enviada = Leilao.envia_leilao_venda(corretoraLeilao,corretoraZeragem,ativo,qtd_de_moedas,True)
                return ordem_enviada

            #5: esta dando pnl negativo para zerar tudo    
            if (ordem.preco_enviado*(1+corretoraLeilao.corretagem_limitada) >  corretoraZeragem.book.obter_preco_medio_de_venda(ordem.quantidade_enviada)*(1-corretoraZeragem.corretagem_mercado)):
                
                logging.info('LV5: leilao venda vai cancelar ordem {} de {} pq o pnl esta dando negativo'.format(ordem.id,ativo))
                cancelou = corretoraLeilao.cancelar_ordem(ativo,ordem.id)
                if cancelou:
                    ordem_enviada = Leilao.envia_leilao_venda(corretoraLeilao,corretoraZeragem,ativo,qtd_de_moedas,True)
                return ordem_enviada
                
        except Exception as erro:
            msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de leilão rapido, método: atualiza_leilao_de_venda. (Ativo: {} | Quant: {})'.format(ativo, corretoraZeragem.ordem.quantidade_enviada), erro)
            raise Exception(msg_erro)
        
        return ordem_enviada


