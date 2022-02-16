import uuid, time
from datetime import datetime
from construtores.corretora import Corretora
from construtores.ordem import Ordem
from uteis.converters import Converters
from uteis.google import Google
from uteis.matematica import Matematica
from uteis.logger import Logger
from uteis.settings import Settings

if __name__ == "__main__":

    #bibliotecas do python
    from datetime import datetime, timedelta
    
    #bibliotecas nossas
    from construtores.corretora import Corretora
    from leilao_rapido import Leilao
    from uteis.settings import Settings
    from uteis.logger import Logger

    Logger.cria_arquivo_log('Leilao')
    Logger.loga_info('iniciando script leilao...')

    #essa parte executa apenas uma vez
    #step 1
    settings_client = Settings()
    instance = settings_client.retorna_campo_de_json('rasp','instance')

    white_list = settings_client.retorna_campo_de_json_como_lista('app',str(instance),'white_list','#')
    lista_de_moedas_no_leilao = settings_client.retorna_campo_de_json_como_lista('strategy','leilao','lista_de_moedas','#')
    lista_de_moedas = [moeda for moeda in lista_de_moedas_no_leilao if moeda in white_list]
    black_list = []
    
    qtd_de_moedas = len(lista_de_moedas)
    leilao_ligada = settings_client.retorna_campo_de_json('strategy','leilao','ligada').lower() == 'true'
    compra_ligada = settings_client.retorna_campo_de_json('strategy','leilao','compra').lower() == 'true'
    venda_ligada = settings_client.retorna_campo_de_json('strategy','leilao','venda').lower() == 'true'

    corretora_mais_liquida = settings_client.retorna_campo_de_json('app',str(instance),'corretora_mais_liquida')
    corretora_menos_liquida = settings_client.retorna_campo_de_json('app',str(instance),'corretora_menos_liquida')

    incremento_leilao = settings_client.retorna_campo_de_json_como_dicionario('broker','incremento_leilao','lista_de_moedas','#')

    corretoraZeragem = Corretora(corretora_mais_liquida)
    corretoraLeilao = Corretora(corretora_menos_liquida)
    corretoraLeilao.cancelar_todas_ordens(white_list)
  
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
    #essa parte faz a cada x minutos
    ordens_abertas = {}
    while leilao_ligada:

        #step 2: else só pode ir ao proximo step se tem ordens abertas
        qtd_ordens_abertas = 0
        ordens_enviadas = {}

        lista_de_moedas = [moeda for moeda in lista_de_moedas if (moeda not in black_list)] #atualiza lista conforme blacklist

        while qtd_ordens_abertas==0:
            
            time.sleep(2)
            corretoraZeragem.atualizar_saldo()
            corretoraLeilao.atualizar_saldo()       

            for moeda in lista_de_moedas:
                
                Logger.loga_info('******************************************************************')                
                ordem_enviada = Ordem()
                #carrego os books de ordem mais recentes, a partir daqui precisamos ser rapidos
                time.sleep(0.5)
                corretoraLeilao.atualizar_book(moeda,'brl')
                corretoraZeragem.atualizar_book(moeda,'brl')

                #define quantidade minima de caixa e moeda para enviarmos o trade
                #essa parte é importante pq apenas as ordens enviadas aqui serão utilizadas no proximo passo
                fracao_do_caixa = round(corretoraLeilao.saldo['brl']/(corretoraLeilao.saldo['brl']+corretoraZeragem.saldo['brl']),6)
                fracao_da_moeda = round(corretoraLeilao.saldo[moeda]/(corretoraLeilao.saldo[moeda]+corretoraZeragem.saldo[moeda]),6)
                
                if venda_ligada and fracao_do_caixa < 0.995 and fracao_da_moeda > 0.025 and ('{}_{}'.format(moeda,'sell') not in ordens_abertas.keys()):
                    ordem_enviada = Leilao.envia_leilao_compra(corretoraLeilao,corretoraZeragem,moeda,qtd_de_moedas)
                    if ordem_enviada.id != 0: #se colocar uma nova ordem, vamos logar como ordem enviada
                        ordens_enviadas['{}_{}'.format(moeda,'sell')]={'id':ordem_enviada.id,'price':ordem_enviada.preco_enviado,'amount':ordem_enviada.quantidade_enviada}
                else:
                    Logger.loga_info('leilao rapido de compra nao enviara ordem de {} porque a fracao de caixa {} é maior que 99% ou a fracao de moeda {} é menor que 5%'.format(moeda,fracao_do_caixa*100,fracao_da_moeda*100))  
                 
                if compra_ligada and fracao_do_caixa > 0.005 and fracao_da_moeda < 0.975 and ('{}_{}'.format(moeda,'buy') not in ordens_abertas.keys()):
                    ordem_enviada = Leilao.envia_leilao_venda(corretoraLeilao,corretoraZeragem,moeda,qtd_de_moedas)
                    if ordem_enviada.id != 0: #se colocar uma nova ordem, vamos logar como ordem enviada
                       ordens_enviadas['{}_{}'.format(moeda,'buy')]={'id':ordem_enviada.id,'price':ordem_enviada.preco_enviado,'amount':ordem_enviada.quantidade_enviada}                       
                else:
                    Logger.loga_info('leilao rapido de venda nao enviara ordem de {} porque a fracao de caixa {} é menor que 1% ou a fracao de moeda {} é maior que 95%'.format(moeda,fracao_do_caixa*100,fracao_da_moeda*100))
            
            for ordem_aberta in corretoraLeilao.obter_todas_ordens_abertas(): #vamos montar um dic com as ordens abertas
                if ordem_aberta['coin'].lower() in lista_de_moedas:
                    ordens_abertas['{}_{}'.format(ordem_aberta['coin'].lower(),ordem_aberta['type'].lower())]={'id':ordem_aberta['id'],'price':ordem_aberta['price'],'amount':ordem_aberta['amount']}
            for ordem_enviada in ordens_enviadas.keys():
                if ordem_enviada not in ordens_abertas.keys():
                    Logger.loga_warning('ordem enviada {} nao esta na lista de ordem abertas e sera adicionada para zeragem!'.format(ordem_enviada))
                    ordens_abertas[ordem_enviada]=ordens_enviadas[ordem_enviada]
            
            qtd_ordens_abertas = len(ordens_abertas.keys())
            
        #step 3: essa parte faz em loop de 3 minuto
        agora = datetime.now() 
        proximo_ciclo = agora + timedelta(minutes=3)
        Logger.loga_info('proximo ciclo até: {} '.format(proximo_ciclo))
        Logger.loga_warning('no proximo ciclo serao consideradas apenas as seguintes {} ordens:'.format(qtd_ordens_abertas))
        Logger.loga_warning('Ordens abertas: ' + Leilao.monta_string_de_ordens(ordens_abertas))

        while agora < proximo_ciclo and qtd_ordens_abertas > 0:
            
            ordens_enviadas = {}
            time.sleep(2)
            corretoraLeilao.atualizar_saldo()
            corretoraZeragem.atualizar_saldo()

            Logger.loga_info('**************************************************')
            Logger.loga_info('Ordens abertas: ' + Leilao.monta_string_de_ordens(ordens_abertas))

            moedas_abertas = list(set([ordem_aberta.split('_')[0] for ordem_aberta in ordens_abertas.keys()]))
  
            for moeda in moedas_abertas:
                ordens_abertas_dessa_moeda = [ordem_aberta for ordem_aberta in ordens_abertas.keys() if ordem_aberta.split('_')[0] == moeda]

                time.sleep(0.5)
                corretoraZeragem.atualizar_book(moeda,'brl')
                corretoraLeilao.atualizar_book(moeda,'brl')

                for ordem_aberta in ordens_abertas_dessa_moeda:

                    ordem_leilao = Ordem()
                    ordem_leilao.id = ordens_abertas[ordem_aberta]['id']
                    ordem_leilao.preco_enviado = float(ordens_abertas[ordem_aberta]['price'])
                    ordem_leilao.quantidade_enviada = float(ordens_abertas[ordem_aberta]['amount'])
                    
                    direcao = ordem_aberta.split('_')[1]
                                    
                    if direcao == 'buy':

                        ordem_enviada, pnl_real = Leilao.atualiza_leilao_de_venda(corretoraLeilao,corretoraZeragem,moeda,ordem_leilao,qtd_de_moedas)
                        if ordem_enviada.id != 0:
                            ordens_enviadas['{}_{}'.format(moeda,'buy')]={'id':ordem_enviada.id,'price':ordem_enviada.preco_enviado,'amount':ordem_enviada.quantidade_enviada}
                        if pnl_real < -10: #menor pnl aceitavel, do contrario fica de castigo
                            black_list.append(moeda)   
                            Logger.loga_warning('Leilao: a moeda {} vai ser adicionado ao blacklist porque deu pnl {} menor que {}'.format(moeda,round(pnl_real,2),-10))
                            
                    elif direcao =='sell':
                        
                        ordem_enviada, pnl_real = Leilao.atualiza_leilao_de_compra(corretoraLeilao,corretoraZeragem,moeda,ordem_leilao,qtd_de_moedas)
                        if ordem_enviada.id != 0:
                            ordens_enviadas['{}_{}'.format(moeda,'sell')]={'id':ordem_enviada.id,'price':ordem_enviada.preco_enviado,'amount':ordem_enviada.quantidade_enviada}
                        if pnl_real < -10: #menor pnl aceitavel, do contrario fica de castigo
                            black_list.append(moeda)   
                            Logger.loga_warning('Leilao: a moeda {} vai ser adicionado ao blacklist porque deu pnl {} menor que {}'.format(moeda,round(pnl_real,2),-10))
                        
            #step4: ir ao step 2
            ordens_abertas = {}
            Logger.loga_info('**************************************************')
            for ordem_aberta in corretoraLeilao.obter_todas_ordens_abertas(): #vamos montar um dic com as ordens abertas
                if ordem_aberta['coin'].lower() in lista_de_moedas:
                    #Logger.loga_info('Ordem Aberta: Moeda - {} / Direcao - {} / ID - {} / Price - {} / Qtd - {}'.format(ordem_aberta['coin'].lower(),ordem_aberta['type'].lower(),ordem_aberta['id'],round(float(ordem_aberta['price']),4),round(float(ordem_aberta['amount']),8)))
                    ordens_abertas['{}_{}'.format(ordem_aberta['coin'].lower(),ordem_aberta['type'].lower())]={'id':ordem_aberta['id'],'price':ordem_aberta['price'],'amount':ordem_aberta['amount']}

            for ordem_enviada in ordens_enviadas.keys():
                
                moeda = ordem_enviada.split('_')[0]
                direcao = ordem_enviada.split('_')[1]
                id = ordens_enviadas[ordem_enviada]['id']
                preco_enviado = round(float(ordens_enviadas[ordem_enviada]['price']),4)
                quantidade_enviada = round(float(ordens_enviadas[ordem_enviada]['amount']),8)
                #Logger.loga_info('Ordem Enviada: Moeda - {} / Direcao - {} / ID - {} / Price - {} / Qtd - {}'.format(moeda,direcao,id,preco_enviado,quantidade_enviada))
                
                if ordem_enviada not in ordens_abertas.keys():
                    Logger.loga_warning('Ordem Enviada {} nao esta na lista de ordem abertas e sera adicionada para zeragem!'.format(ordem_enviada))
                    ordens_abertas[ordem_enviada]=ordens_enviadas[ordem_enviada]
            
            qtd_ordens_abertas = len(ordens_abertas.keys())
            agora = datetime.now() 


class Leilao:

    def monta_string_de_ordens(ordens_abertas):
        '''
        monta uma string com base nas ordens abertas para mostrar no log
        '''
        retorno = ''
        for ordem in ordens_abertas.keys():
            retorno += '* ' +ordem 
        return retorno

    def envia_leilao_compra(corretoraLeilao:Corretora, corretoraZeragem:Corretora, ativo, qtd_de_moedas):
        '''
        envia ordem limitada de venda se tiver leilao aberto
        '''
        try:
            ordem = Ordem()
            
            preco_que_vou_vender = corretoraLeilao.livro.preco_compra-0.01 #primeiro no book de ordens - incremento
            preco_de_zeragem = corretoraZeragem.livro.preco_compra # zeragem no primeiro book de ordens

            # Valida se existe oportunidade de leilão
            if (preco_que_vou_vender*(1-corretoraLeilao.corretagem_limitada) >= (1+corretoraZeragem.corretagem_mercado) * preco_de_zeragem):
                # Gostaria de vender no leilão 0.4 do que eu tenho de saldo em crypto
                gostaria_de_vender = corretoraLeilao.saldo[ativo] *0.5
                maximo_que_consigo_zerar = corretoraZeragem.saldo['brl'] / (qtd_de_moedas*preco_de_zeragem)
                #se vc for executada nessa quantidade inteira, talvez nao tera lucro
                maximo_que_zero_com_lucro = corretoraZeragem.livro.obter_quantidade_abaixo_de_preco_compra(preco_que_vou_vender*(1-corretoraLeilao.corretagem_limitada)*(1-corretoraZeragem.corretagem_mercado))
                qtdNegociada = min(gostaria_de_vender,maximo_que_consigo_zerar,maximo_que_zero_com_lucro)
                
                Logger.loga_info('Leilão compra rapida aberta: Moeda - {} /Quantidade-{} /Preco- {} /Preço Zeragem {} / Saldos brl {} e {} Saldo {}: {} e {}'.format(ativo,round(qtdNegociada,2),round(preco_que_vou_vender,2),round(preco_de_zeragem,2),round(corretoraLeilao.saldo['brl'],2),round(corretoraZeragem.saldo['brl'],2),ativo,round(corretoraLeilao.saldo[ativo],4),round(corretoraZeragem.saldo[ativo],4)))
                
                if (qtdNegociada*preco_que_vou_vender > corretoraZeragem.valor_minimo_compra[ativo]):
                    
                    if qtdNegociada > corretoraLeilao.quantidade_minima_venda[ativo]:
                        ordem = Ordem(ativo,qtdNegociada,preco_que_vou_vender,'limited')
                        ordem = corretoraLeilao.enviar_ordem_venda(ordem) 
                else:
                    financeiro_venda = qtdNegociada*preco_que_vou_vender
                    financeiro_venda_minimo = corretoraZeragem.valor_minimo_compra[ativo]
                    zeragem_compra = corretoraZeragem.saldo['brl']
                    zeragem_compra_minimo = corretoraZeragem.valor_minimo_compra[ativo]
                    Logger.loga_info('leilao de compra nao executado para moeda {}, pois o financeiro venda: {} < que financeiro venda minimo: {}, ou zeragem compra: {} < zeragem compra minimo: {}'.format(ativo,round(financeiro_venda,2),round(financeiro_venda_minimo,2),round(zeragem_compra,2),round(zeragem_compra_minimo,2)))   
            else:
                Logger.loga_info('leilao compra de {} nao vale a pena, (1+corretagem)*{} é menor que (1-corretagem)*{}'.format(ativo,preco_que_vou_vender,preco_de_zeragem))

        except Exception as erro:
           Logger.loga_erro('envia_leilao_compra','Leilao',erro)

        return ordem

    def envia_leilao_venda(corretoraLeilao:Corretora, corretoraZeragem:Corretora, ativo, qtd_de_moedas):
        '''
        envia ordem limitada de compra na corretora de baixa liquidez
        '''
        try:
            ordem = Ordem()
            preco_que_vou_comprar = corretoraLeilao.livro.preco_venda+0.01 #primeiro no book de ordens + incremento
            preco_de_zeragem = corretoraZeragem.livro.preco_venda # zeragem no primeiro book de ordens

            # Valida se existe oportunidade de leilão
            if preco_que_vou_comprar*(1+corretoraLeilao.corretagem_limitada) <= preco_de_zeragem*(1-corretoraZeragem.corretagem_mercado):
                                               
                gostaria_de_comprar = corretoraLeilao.saldo['brl'] / (qtd_de_moedas * preco_que_vou_comprar)
                maximo_que_consigo_zerar = corretoraZeragem.saldo[ativo] *0.5
                #se vc for executada nessa quantidade inteira, talvez nao tera lucro
                maximo_que_zero_com_lucro = corretoraZeragem.livro.obter_quantidade_acima_de_preco_venda(preco_que_vou_comprar*(1+corretoraLeilao.corretagem_limitada)*(1+corretoraZeragem.corretagem_mercado))
                qtdNegociada = min(gostaria_de_comprar,maximo_que_consigo_zerar,maximo_que_zero_com_lucro)
                
                Logger.loga_info('Leilão venda rapida aberta: Moeda - {} /Quantidade-{} /Preco- {} /Preço Zeragem {} / Saldos brl {} e {} Saldo {}: {} e {}'.format(ativo,round(qtdNegociada,2),round(preco_que_vou_comprar,2),round(preco_de_zeragem,2),round(corretoraLeilao.saldo['brl'],2),round(corretoraZeragem.saldo['brl'],2),ativo,round(corretoraLeilao.saldo[ativo],4),round(corretoraZeragem.saldo[ativo],4)))
                
                # Se quantidade negociada maior que a quantidade mínima permitida de venda
                if qtdNegociada > corretoraLeilao.quantidade_minima_venda[ativo]:

                    ordem = Ordem(ativo,qtdNegociada,preco_que_vou_comprar,'limited')
                    ordem = corretoraLeilao.enviar_ordem_compra(ordem)
                else:
                    quantidade_compra = qtdNegociada
                    quantidade_venda_minimo = corretoraLeilao.quantidade_minima_venda[ativo]
                    Logger.loga_info('leilao de venda nao executado para moeda {} pois nao tem quantidades disponiveis suficientes para venda: {}<{}'.format(ativo,quantidade_compra,quantidade_venda_minimo)) 
            else:
                Logger.loga_info('leilao venda de {} nao vale a pena, {} é maior que 0.99*{}'.format(ativo,preco_que_vou_comprar,preco_de_zeragem))
        except Exception as erro:
                Logger.loga_erro('envia_leilao_venda','Leilao',erro)
        
        return ordem

    def zera_leilao_de_compra(corretoraLeilao:Corretora, corretoraZeragem:Corretora, ativo, ordem_antiga:Ordem):
        '''
        zera leilao de compra se executado
        '''
        ordem_zeragem = Ordem()
        pnl = 0
        #1: executada completamente
        if ordem_antiga.foi_executada_completamente: # verifica se a ordem foi executada totalmente (Nesse caso o ID = False)
            
            Logger.loga_info('Leilao compra vai zerar na {} ordem executada completamente {} de {}'.format(corretoraZeragem.nome,ordem_antiga.id,ativo))
            ordem_zeragem = Ordem(ativo,ordem_antiga.quantidade_executada,corretoraZeragem.livro.preco_compra,'market')
            ordem_zeragem = corretoraZeragem.enviar_ordem_compra(ordem_zeragem)
            
        #2: executada parcialmente, mais que o valor minimo
        elif ordem_antiga.quantidade_executada * corretoraZeragem.livro.preco_compra > 0:
        
            if ordem_antiga.quantidade_executada * corretoraZeragem.livro.preco_compra > corretoraZeragem.valor_minimo_compra[ativo]: #mais de xxx reais executado
            
                Logger.loga_info('Leilao compra vai zerar na {} {} da ordem executada {} de {}'.format(corretoraZeragem.nome,round(ordem_antiga.quantidade_executada,4),ordem_antiga.id,ativo))
                ordem_zeragem = Ordem(ativo,ordem_antiga.quantidade_executada,corretoraZeragem.livro.preco_compra,'market')
                ordem_zeragem = corretoraZeragem.enviar_ordem_compra(ordem_zeragem)

            else:
                fui_executado = round(ordem_antiga.quantidade_executada * corretoraZeragem.livro.preco_compra,4)
                valor_minimo = round(corretoraZeragem.valor_minimo_compra[ativo],4)
                Logger.loga_info('Leilao compra de {} nao vai fazer nada porque fui executado em {} reais que é menos que o valor minimo de {} reais'.format(ativo,fui_executado,valor_minimo))
                    
        #agora vai logar pnl
        if ordem_zeragem.id != 0:
                    
            comprei_a = round(ordem_zeragem.preco_executado,2)
            vendi_a = round(ordem_antiga.preco_enviado,2)
            quantidade = round(ordem_zeragem.quantidade_enviada,6)

            financeiro_compra = comprei_a * (1+corretoraZeragem.corretagem_mercado) * quantidade
            financeiro_venda = vendi_a * (1-corretoraLeilao.corretagem_limitada)* quantidade

            queria_comprar_a = round(ordem_zeragem.preco_enviado,2)
            financeiro_compra_estimado = queria_comprar_a* (1+corretoraZeragem.corretagem_mercado) * quantidade
            custo_corretagem_compra = corretoraZeragem.corretagem_mercado*financeiro_compra
            custo_corretagem_venda = corretoraLeilao.corretagem_limitada*financeiro_venda

            pnl = round((financeiro_venda -financeiro_compra),2)
            pnl_estimado = round((financeiro_venda -financeiro_compra_estimado),2)

            eh_171 =1 if Matematica().tem_numero_magico(ordem_antiga.quantidade_executada,corretoraLeilao.nome) else 0

            Logger.loga_warning('Leilao rapido de compra de {}! + {}brl de pnl (compra de {}{} @{} na {} e venda a @{} na {})'.format(ativo,pnl,quantidade,ativo,comprei_a,corretoraZeragem.nome,vendi_a,corretoraLeilao.nome))
            
            quantidade_executada_compra = ordem_zeragem.quantidade_executada
            quantidade_executada_venda = ordem_antiga.quantidade_executada
            
            settings_client = Settings()
            planilha = settings_client.retorna_campo_de_json('rasp','sheet_name')
            google_client = Google()
            trade_time = Converters.datetime_para_excel_date(datetime.now())
            trade_id = str(uuid.uuid4())
            google_client.escrever(planilha,'spot',[trade_time,trade_id,'LEILAO',ativo,corretoraZeragem.nome,'COMPRA',comprei_a,quantidade_executada_compra,financeiro_compra,pnl/2,queria_comprar_a,pnl_estimado/2,corretoraZeragem.corretagem_mercado,custo_corretagem_compra,eh_171,'FALSE'])
            google_client.escrever(planilha,'spot',[trade_time,trade_id,'LEILAO',ativo,corretoraLeilao.nome,'VENDA',vendi_a,quantidade_executada_venda,financeiro_venda,pnl/2,vendi_a,pnl_estimado/2,corretoraLeilao.corretagem_limitada,custo_corretagem_venda,eh_171,'FALSE'])

            corretoraZeragem.atualizar_saldo()
            corretoraLeilao.atualizar_saldo()
            Logger.loga_info('leilao compra atualizou o saldo na corretora leilao e zeragem pois foi executado, Saldo brl: {}/{} Saldo {}: {}/{}'.format(round(corretoraLeilao.saldo['brl'],2),round(corretoraZeragem.saldo['brl'],2),ativo,round(corretoraLeilao.saldo[ativo],4),round(corretoraZeragem.saldo[ativo],4)))
        return pnl

    def atualiza_leilao_de_compra(corretoraLeilao:Corretora, corretoraZeragem:Corretora, ativo, ordem_antiga:Ordem, qtd_de_moedas):
        '''
        atualiza ordem no leilao de compra
        '''
        ordem_enviada = Ordem()
        cancelou = False
        pnl = 0
        
        try:
            #1: nao sou o primeiro da fila
            if (ordem_antiga.preco_enviado != corretoraLeilao.livro.preco_compra) or (corretoraLeilao.livro.preco_compra_segundo_na_fila - ordem_antiga.preco_enviado > 0.02):
                
                Logger.loga_info('Leilao compra vai cancelar ordem {} de {} pq meu preco {} nao é o primeiro da fila {} na {} ou é mais de 2 centavos menor que {}'.format(ordem_antiga.id,ativo,ordem_antiga.preco_enviado,corretoraLeilao.livro.preco_compra,corretoraLeilao.nome,corretoraLeilao.livro.preco_compra_segundo_na_fila))
                ordem_antiga = corretoraLeilao.obter_ordem_por_id(ordem_antiga)
                cancelou = corretoraLeilao.cancelar_ordem(ordem_antiga)
                pnl = Leilao.zera_leilao_de_compra(corretoraLeilao,corretoraZeragem,ativo,ordem_antiga)

                if (abs(corretoraLeilao.livro.preco_compra_segundo_na_fila - ordem_antiga.preco_enviado) > 0.02):
                    corretoraLeilao.atualizar_book(ativo,'brl') #nesse caso especifico é melhor atualizar o book de ordens
                if cancelou:
                    ordem_enviada = Leilao.envia_leilao_compra(corretoraLeilao,corretoraZeragem,ativo,qtd_de_moedas)
                return ordem_enviada, pnl

            #2: estou sem saldo para zerar
            corretoraZeragem.atualizar_saldo()
            if (corretoraZeragem.saldo['brl'] < ordem_antiga.quantidade_enviada*ordem_antiga.preco_enviado):
                
                Logger.loga_info('Leilao compra vai cancelar ordem {} de {} pq meu saldo brl {} nao consegue comprar {}'.format(ordem_antiga.id,ativo,corretoraZeragem.saldo['brl'],ordem_antiga.quantidade_enviada*ordem_antiga.preco_enviado))
                ordem_antiga = corretoraLeilao.obter_ordem_por_id(ordem_antiga)
                cancelou = corretoraLeilao.cancelar_ordem(ordem_antiga)
                pnl = Leilao.zera_leilao_de_compra(corretoraLeilao,corretoraZeragem,ativo,ordem_antiga)
                
                if cancelou:
                    ordem_enviada = Leilao.envia_leilao_compra(corretoraLeilao,corretoraZeragem,ativo,qtd_de_moedas)
                return ordem_enviada, pnl

            #3: esta dando pnl negativo para zerar tudo
            if (ordem_antiga.preco_enviado*(1-corretoraLeilao.corretagem_limitada) < (1+corretoraZeragem.corretagem_mercado) * corretoraZeragem.livro.obter_preco_medio_de_compra(ordem_antiga.quantidade_enviada)):
                
                Logger.loga_info('Leilao compra vai cancelar ordem {} de {} pq o pnl esta dando negativo'.format(ordem_antiga.id,ativo))
                ordem_antiga = corretoraLeilao.obter_ordem_por_id(ordem_antiga)
                cancelou = corretoraLeilao.cancelar_ordem(ordem_antiga)
                pnl = Leilao.zera_leilao_de_compra(corretoraLeilao,corretoraZeragem,ativo,ordem_antiga)
                
                if cancelou:
                    ordem_enviada = Leilao.envia_leilao_compra(corretoraLeilao,corretoraZeragem,ativo,qtd_de_moedas)
                return ordem_enviada, pnl
            #4: fui executado
            ordem_antiga = corretoraLeilao.obter_ordem_por_id(ordem_antiga)
            if (ordem_antiga.foi_executada_completamente or ordem_antiga.quantidade_executada * corretoraZeragem.livro.preco_compra > 0):
                
                Logger.loga_info('Leilao compra vai cancelar ordem {} de {} pq fui executado'.format(ordem_antiga.id,ativo))
                cancelou = corretoraLeilao.cancelar_ordem(ordem_antiga)
                pnl = Leilao.zera_leilao_de_compra(corretoraLeilao,corretoraZeragem,ativo,ordem_antiga)

                if cancelou:
                    ordem_enviada = Leilao.envia_leilao_compra(corretoraLeilao,corretoraZeragem,ativo,qtd_de_moedas)
                return ordem_enviada, pnl 

            Logger.loga_info('Leilao nao precisou cancelar a ordem {} de {} e colocar outra'.format(ordem_antiga.id,ativo))
            return ordem_antiga, pnl

        except Exception as erro:
           Logger.loga_erro('atualiza_leilao_de_compra','Leilao', erro)

    def zera_leilao_de_venda(corretoraLeilao:Corretora, corretoraZeragem:Corretora, ativo, ordem_antiga:Ordem):
        '''
        zera leilao de venda se executado
        '''
        ordem_zeragem = Ordem()
        pnl = 0
        #1: executada completamente
        if ordem_antiga.foi_executada_completamente:# verifica se a ordem foi executada totalmente (Nesse caso o ID = False)
            
            Logger.loga_info('Leilao venda vai zerar ordem executada completamente {} de {} na outra corretora'.format(ordem_antiga.id,ativo))
            ordem_zeragem = Ordem(ativo,ordem_antiga.quantidade_executada,corretoraZeragem.livro.preco_venda,'market')
            ordem_zeragem = corretoraZeragem.enviar_ordem_venda(ordem_zeragem)
            
        #2: executada parcialmente, mais que o valor minimo
        elif ordem_antiga.quantidade_executada > 0:
        
            if ordem_antiga.quantidade_executada > corretoraZeragem.quantidade_minima_venda[ativo]: 
            
                Logger.loga_info('Leilao venda vai zerar na {} {} da ordem executada {} de {}'.format(corretoraZeragem.nome,round(ordem_antiga.quantidade_executada,4),ordem_antiga.id,ativo))
                ordem_zeragem = Ordem(ativo,ordem_antiga.quantidade_executada,corretoraZeragem.livro.preco_venda,'market')
                ordem_zeragem = corretoraZeragem.enviar_ordem_venda(ordem_zeragem)
                
            else:
                fui_executado = round(ordem_antiga.quantidade_executada,4)
                valor_minimo = round(corretoraZeragem.quantidade_minima_venda[ativo],4)
                Logger.loga_info('Leilao venda de {} nao vai fazer nada porque fui executado em {} que é menos que o valor minimo de {}'.format(ativo,fui_executado,valor_minimo))

        if  ordem_zeragem.id != 0:

            vendi_a = round(ordem_zeragem.preco_executado,2)
            comprei_a = round(ordem_antiga.preco_enviado,2)
            quantidade = round(ordem_zeragem.quantidade_enviada,6)

            financeiro_compra = comprei_a*(1+corretoraLeilao.corretagem_limitada)* quantidade
            financeiro_venda = vendi_a*(1-corretoraZeragem.corretagem_mercado)* quantidade

            queria_vender_a = round(ordem_zeragem.preco_enviado,2)
            financeiro_venda_estimado = queria_vender_a* (1+corretoraZeragem.corretagem_mercado) * quantidade
            custo_corretagem_compra = corretoraLeilao.corretagem_limitada*financeiro_compra
            custo_corretagem_venda = corretoraZeragem.corretagem_mercado*financeiro_venda

            pnl = round((financeiro_venda-financeiro_compra),2)
            pnl_estimado = round((financeiro_venda_estimado -financeiro_compra),2)

            eh_171 = 1 if Matematica().tem_numero_magico(ordem_antiga.quantidade_executada,corretoraLeilao.nome) else 0

            Logger.loga_warning('operou leilao rapido de venda de {}! + {}brl de pnl (venda de {}{} @{} na {} e compra a @{} na {})'.format(ativo,pnl,quantidade,ativo,vendi_a,corretoraZeragem.nome,comprei_a,corretoraLeilao.nome))
            
            quantidade_executada_compra = ordem_antiga.quantidade_executada
            quantidade_executada_venda = ordem_zeragem.quantidade_executada
            
            settings_client = Settings()
            planilha = settings_client.retorna_campo_de_json('rasp','sheet_name')
            google_client = Google()
            trade_time = Converters.datetime_para_excel_date(datetime.now())
            trade_id = str(uuid.uuid4())
            google_client.escrever(planilha,'spot',[trade_time,trade_id,'LEILAO',ativo,corretoraLeilao.nome,'COMPRA',comprei_a,quantidade_executada_compra,financeiro_compra,pnl/2,comprei_a,pnl_estimado/2,corretoraLeilao.corretagem_limitada,custo_corretagem_compra,eh_171,'FALSE'])
            google_client.escrever(planilha,'spot',[trade_time,trade_id,'LEILAO',ativo,corretoraZeragem.nome,'VENDA',vendi_a,quantidade_executada_venda,financeiro_venda,pnl/2,queria_vender_a,pnl_estimado/2,corretoraZeragem.corretagem_mercado,custo_corretagem_venda,eh_171,'FALSE'])

            corretoraZeragem.atualizar_saldo()
            corretoraLeilao.atualizar_saldo()
            Logger.loga_info('leilao venda atualizou o saldo na corretora leilao e zeragem pois foi executado, Saldo brl: {}/{} Saldo {}: {}/{}'.format(round(corretoraLeilao.saldo['brl'],2),round(corretoraZeragem.saldo['brl'],2),ativo,round(corretoraLeilao.saldo[ativo],4),round(corretoraZeragem.saldo[ativo],4)))
        return pnl

    def atualiza_leilao_de_venda(corretoraLeilao:Corretora, corretoraZeragem:Corretora, ativo, ordem_antiga:Ordem, qtd_de_moedas):
        '''
        atualiza ordem no leilao de venda
        '''
        ordem_enviada = Ordem()
        cancelou = False
        pnl = 0
        
        try:
            #1: nao sou o primeiro da fila
            if (ordem_antiga.preco_enviado != corretoraLeilao.livro.preco_venda) or (ordem_antiga.preco_enviado -corretoraLeilao.livro.preco_venda_segundo_na_fila > 0.02):
                
                Logger.loga_info('Leilao venda vai cancelar ordem {} de {} pq meu preco {} nao é o primeiro da fila {} na {} ou é mais de 2 centavos maior que {}'.format(ordem_antiga.id,ativo,ordem_antiga.preco_enviado,corretoraLeilao.livro.preco_venda,corretoraLeilao.nome,corretoraLeilao.livro.preco_venda_segundo_na_fila))
                ordem_antiga = corretoraLeilao.obter_ordem_por_id(ordem_antiga)
                cancelou = corretoraLeilao.cancelar_ordem(ordem_antiga)
                pnl = Leilao.zera_leilao_de_venda(corretoraLeilao,corretoraZeragem,ativo,ordem_antiga)

                if (abs(ordem_antiga.preco_enviado -corretoraLeilao.livro.preco_venda_segundo_na_fila) > 0.02):
                    corretoraLeilao.atualizar_book(ativo,'brl') #nesse caso especifico é melhor atualizar o book de ordens
                if cancelou:
                    ordem_enviada = Leilao.envia_leilao_venda(corretoraLeilao,corretoraZeragem,ativo,qtd_de_moedas)
                return ordem_enviada, pnl
                
            #2: estou sem saldo para zerar
            corretoraZeragem.atualizar_saldo()
            if (corretoraZeragem.saldo[ativo] < ordem_antiga.quantidade_enviada):
                
                Logger.loga_info('Leilao venda vai cancelar ordem {} de {} pq meu saldo em cripto {} é menor que oq eu queria vender {}'.format(ordem_antiga.id,ativo,corretoraZeragem.saldo[ativo],ordem_antiga.quantidade_enviada))
                ordem_antiga = corretoraLeilao.obter_ordem_por_id(ordem_antiga)
                cancelou = corretoraLeilao.cancelar_ordem(ordem_antiga)
                pnl = Leilao.zera_leilao_de_venda(corretoraLeilao,corretoraZeragem,ativo,ordem_antiga)
                
                if cancelou:
                    ordem_enviada = Leilao.envia_leilao_venda(corretoraLeilao,corretoraZeragem,ativo,qtd_de_moedas)
                return ordem_enviada, pnl

            #3: esta dando pnl negativo para zerar tudo    
            if (ordem_antiga.preco_enviado*(1+corretoraLeilao.corretagem_limitada) >  corretoraZeragem.livro.obter_preco_medio_de_venda(ordem_antiga.quantidade_enviada)*(1-corretoraZeragem.corretagem_mercado)):
                
                Logger.loga_info('Leilao venda vai cancelar ordem {} de {} pq o pnl esta dando negativo'.format(ordem_antiga.id,ativo))
                ordem_antiga = corretoraLeilao.obter_ordem_por_id(ordem_antiga)
                cancelou = corretoraLeilao.cancelar_ordem(ordem_antiga)
                pnl = Leilao.zera_leilao_de_venda(corretoraLeilao,corretoraZeragem,ativo,ordem_antiga)

                if cancelou:
                    ordem_enviada = Leilao.envia_leilao_venda(corretoraLeilao,corretoraZeragem,ativo,qtd_de_moedas)
                return ordem_enviada, pnl

            #4: fui executado
            ordem_antiga = corretoraLeilao.obter_ordem_por_id(ordem_antiga)
            if (ordem_antiga.foi_executada_completamente or ordem_antiga.quantidade_executada > 0):
                
                Logger.loga_info('Leilao venda vai cancelar ordem {} de {} pq fui executado'.format(ordem_antiga.id,ativo))
                cancelou = corretoraLeilao.cancelar_ordem(ordem_antiga)
                pnl = Leilao.zera_leilao_de_venda(corretoraLeilao,corretoraZeragem,ativo,ordem_antiga)

                if cancelou:
                    ordem_enviada = Leilao.envia_leilao_venda(corretoraLeilao,corretoraZeragem,ativo,qtd_de_moedas)
                return ordem_enviada, pnl 

            Logger.loga_info('Leilao nao precisou cancelar a ordem {} de {} e colocar outra'.format(ordem_antiga.id,ativo))
            return ordem_antiga, pnl

        except Exception as erro:
            Logger.loga_erro('atualiza_leilao_de_venda','Leilao', erro)
        


