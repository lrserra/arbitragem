 
import time
import logging
from datetime import datetime
from corretora import Corretora
from util import Util
from ordem import Ordem

class Leilao:

    def compra(corretoraParte, corretoraContraparte, ativo, executarOrdens = False):

        retorno_venda_corretora_parte = Ordem()
        
        try:
            # Lista de moedas que está rodando de forma parametrizada
            qtd_de_moedas = len(Util.obter_lista_de_moedas())

            # Soma do saldo total em reais
            saldoTotalBRL = corretoraParte.saldoBRL + corretoraContraparte.saldoBRL
            
            # Valida se existe oportunidade de leilão
            if ((corretoraParte.ordem.preco_compra-0.01) >= 1.01 * corretoraContraparte.ordem.preco_compra):
                
                # Gostaria de vender no leilão pelo 1/4 do que eu tenho de saldo em crypto
                gostaria_de_vender = corretoraParte.saldoCrypto / 4
                maximo_que_consigo_zerar = corretoraContraparte.saldoBRL / (qtd_de_moedas*corretoraContraparte.ordem.preco_compra * 1.01)
                qtdNegociada = min(gostaria_de_vender,maximo_que_consigo_zerar)

                # Nao pode ter saldo na mercado de menos de um real
                if (qtdNegociada*(corretoraParte.ordem.preco_compra-0.01) > Util.retorna_menor_valor_compra(ativo) and corretoraContraparte.saldoBRL > Util.retorna_menor_valor_compra(ativo)):
                    
                    corretoraParte.ordem.preco_venda = corretoraParte.ordem.preco_compra - 0.01
                    logging.info('Leilão compra vai enviar ordem de venda de {} limitada a {}'.format(ativo,corretoraParte.ordem.preco_venda))

                    if executarOrdens and qtdNegociada > Util.retorna_menor_quantidade_venda(ativo):
                        corretoraParte.ordem.quantidade_negociada = qtdNegociada
                        corretoraParte.ordem.tipo_ordem = 'limited'
                        retorno_venda_corretora_parte = corretoraParte.enviar_ordem_venda(corretoraParte.ordem)  
            else:
                logging.info('leilao compra de {} nao vale a pena, {} é menor que 1.01*{}'.format(ativo,(corretoraParte.ordem.preco_compra-0.01),corretoraContraparte.ordem.preco_compra))

        except Exception as erro:
                msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de leilão, método: compra. Msg Corretora:', erro)
                raise Exception(msg_erro)

        return retorno_venda_corretora_parte

    def venda(corretoraParte, corretoraContraparte, ativo, executarOrdens = False):

        retorno_compra_corretora_parte = Ordem()

        try:
            qtd_de_moedas = len(Util.obter_lista_de_moedas())

            saldoTotalBRL = corretoraParte.saldoBRL + corretoraContraparte.saldoBRL
            
            # 0.99 = 1 - Soma das corretagens
            if ((corretoraParte.ordem.preco_venda+0.01) <= 0.99 * corretoraContraparte.ordem.preco_venda):
                
                gostaria_de_comprar = corretoraParte.saldoBRL / (qtd_de_moedas * corretoraParte.ordem.preco_venda + 0.01)
                maximo_que_consigo_zerar = corretoraContraparte.saldoCrypto / 4
                
                # Mínimo entre o que eu gostaria de comprar com o máximo que consigo zerar na outra ponta
                qtdNegociada = min(gostaria_de_comprar,maximo_que_consigo_zerar)
                
                # Se quantidade negociada maior que a quantidade mínima permitida de venda
                if qtdNegociada > Util.retorna_menor_quantidade_venda(ativo):

                    logging.info('leilao venda de vai enviar ordem de venda de {} limitada a {}'.format(ativo,corretoraParte.ordem.preco_venda))
                    corretoraParte.ordem.preco_compra = corretoraParte.ordem.preco_venda + 0.01 
                    if executarOrdens:
                        corretoraParte.ordem.quantidade_negociada = qtdNegociada
                        corretoraParte.ordem.tipo_ordem = 'limited'    
                        retorno_compra_corretora_parte = corretoraParte.enviar_ordem_compra(corretoraParte.ordem)
                
            else:
                logging.info('leilao venda de {} nao vale a pena, {} é maior que 0.99*{}'.format(ativo,(corretoraParte.ordem.preco_venda+0.01),corretoraContraparte.ordem.preco_venda))
        except Exception as erro:
                msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de leilão, método: venda. Msg Corretora:', erro)
                raise Exception(msg_erro)
        
        return retorno_compra_corretora_parte

    #def cancela_ordens_e_compra_na_mercado(corretoraParte, corretoraContraparte, ativo, executarOrdens = False, idOrdem = 0, status='new'):
    def cancela_ordens_e_compra_na_mercado(corretoraParte, corretoraContraparte, ativo, executarOrdens, ordem_leilao_compra):

        retorno_compra = Ordem()
        cancelou = False

        try:
        
            corretoraParte.carregar_ordem_books()
            corretoraContraparte.carregar_ordem_books()
        
            if ordem_leilao_compra.status == corretoraParte.descricao_status_executado and ordem_leilao_compra.id == False: # verifica se a ordem foi executada totalmente (Nesse caso o ID = False)
                
                preco_executado = ordem_leilao_compra.preco_executado
                
                logging.info('leilao compra vai zerar ordem executada {} de {} na outra corretora'.format(ordem_leilao_compra.id,ativo))
                corretoraContraparte.ordem.quantidade_negociada = round(ordem_leilao_compra.quantidade_executada,8)
                corretoraContraparte.ordem.tipo_ordem = 'market'
                retorno_compra = corretoraContraparte.enviar_ordem_compra(corretoraContraparte.ordem)
                
            elif ordem_leilao_compra.id > 0:

                ordem = corretoraParte.obter_ordem_por_id(ordem_leilao_compra.id)
                
                if (ordem_leilao_compra.preco_venda != corretoraParte.ordem.preco_compra):
                    
                    logging.info('leilao compra vai cancelar ordem {} de {} pq nao sou o primeiro da fila'.format(ordem_leilao_compra.id,ativo))
                    corretoraParte.cancelar_ordem(ordem_leilao_compra.id)
                    cancelou = True

                elif (ordem.quantidade_executada > 0):
                    
                    logging.info('leilao compra vai cancelar ordem {} de {} pq fui executado'.format(ordem_leilao_compra.id,ativo))
                    corretoraParte.cancelar_ordem(ordem_leilao_compra.id)
                    cancelou = True
                
                elif (ordem_leilao_compra.preco_venda < 1.01 * corretoraContraparte.ordem.preco_compra):
                    
                    logging.info('leilao compra vai cancelar ordem {} de {} pq o pnl esta dando negativo'.format(ordem_leilao_compra.id,ativo))
                    corretoraParte.cancelar_ordem(ordem_leilao_compra.id)
                    cancelou = True

                if executarOrdens and ordem.quantidade_executada * corretoraParte.ordem.preco_compra > Util.retorna_menor_valor_compra(ativo): #mais de xxx reais executado
                    
                    # Zera o risco na outra corretora com uma operação à mercado
                    corretoraContraparte.ordem.quantidade_negociada = round(ordem.quantidade_executada,8)
                    corretoraContraparte.ordem.tipo_ordem = 'market'
                    retorno_compra = corretoraContraparte.enviar_ordem_compra(corretoraContraparte.ordem)
                                
        except Exception as erro:
            msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de leilão, método: cancela_ordens_e_compra_na_mercado.', erro)
            raise Exception(msg_erro)

        return retorno_compra, cancelou

    def cancela_ordens_e_vende_na_mercado(corretoraParte:Corretora, corretoraContraparte:Corretora, ativo, executarOrdens, ordem_leilao_venda):

        retorno_venda = Ordem()
        cancelou = False

        try:
    
            corretoraParte.carregar_ordem_books()
            corretoraContraparte.carregar_ordem_books()
             
            if ordem_leilao_venda.status == corretoraParte.descricao_status_executado and ordem_leilao_venda.id == False:

                corretoraContraparte.ordem.quantidade_negociada = ordem_leilao_venda.quantidade_executada
                corretoraContraparte.ordem.tipo_ordem = 'market'
                retorno_venda = corretoraContraparte.enviar_ordem_venda(corretoraContraparte.ordem)
        
            elif ordem_leilao_venda.id > 0:
                
                ordem = corretoraParte.obter_ordem_por_id(ordem_leilao_venda.id)             
                qtd_executada = ordem.quantidade_executada
                preco_executado = ordem_leilao_venda.preco_executado
            
                if (ordem_leilao_venda.preco_compra != corretoraParte.ordem.preco_venda):
                    
                    logging.info('leilao venda vai cancelar ordem {} de {} pq nao sou o primeiro da fila'.format(ordem_leilao_venda.id,ativo))
                    corretoraParte.cancelar_ordem(ordem_leilao_venda.id)
                    cancelou = True
                
                elif (ordem.quantidade_executada >0):
                    
                    logging.info('leilao venda vai cancelar ordem {} de {} pq fui executado'.format(ordem_leilao_venda.id,ativo))
                    corretoraParte.cancelar_ordem(ordem_leilao_venda.id)
                    cancelou = True

                elif (ordem_leilao_venda.preco_compra > 0.99 * corretoraContraparte.ordem.preco_venda):
                    
                    logging.info('leilao venda vai cancelar ordem {} de {} pq o pnl esta dando negativo'.format(ordem_leilao_venda.id,ativo))
                    corretoraParte.cancelar_ordem(ordem_leilao_venda.id)
                    cancelou = True
            
                if executarOrdens and ordem.quantidade_executada > Util.retorna_menor_quantidade_venda(ativo): 
                    
                    logging.info('leilao venda vai zerar ordem executada {} de {} na outra corretora'.format(ordem_leilao_venda.id,ativo))
                    corretoraContraparte.ordem.quantidade_negociada = round(ordem.quantidade_executada,8)
                    corretoraContraparte.ordem.tipo_ordem = 'market'
                    retorno_venda = corretoraContraparte.enviar_ordem_venda(corretoraContraparte.ordem)
                
        except Exception as erro:
            msg_erro = Util.retorna_erros_objeto_exception('Erro na estratégia de leilão, método: cancela_ordens_e_vende_na_mercado.', erro)
            raise Exception(msg_erro)
        
        return retorno_venda,cancelou


if __name__ == "__main__":

    import requests
    
    from datetime import datetime, timedelta
    from caixa import Caixa
    from leilao import Leilao
    
    #inicializa arquivo de logs, no arquivo vai a porra toda, mas no console só os warning ou acima
    logging.basicConfig(filename='leilao.log', level=logging.INFO,
                        format='[%(asctime)s][%(levelname)s][%(message)s]')
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    logging.getLogger().addHandler(console)

    #essa parte executa apenas uma vez
    lista_de_moedas = Util.obter_lista_de_moedas()
    corretora_mais_liquida = Util.obter_corretora_de_maior_liquidez()
    corretora_menos_liquida = Util.obter_corretora_de_menor_liquidez()

    retorno_ordem_leilao_compra = Ordem()
    retorno_ordem_leilao_venda = Ordem()

    dict_leilao_compra = {}
    dict_leilao_venda = {}

    for moeda in lista_de_moedas:
        dict_leilao_compra[moeda]={}
        dict_leilao_venda[moeda]={}
        dict_leilao_compra[moeda]['ordem'] = Ordem()
        dict_leilao_venda[moeda]['ordem'] = Ordem()
        dict_leilao_compra[moeda]['zeragem'] = Ordem()
        dict_leilao_venda[moeda]['zeragem'] = Ordem()
        dict_leilao_compra[moeda]['foi_cancelado'] = False
        dict_leilao_venda[moeda]['foi_cancelado'] = False

    #atualiza saldo inicial nesse dicionario
    saldo_inicial = Caixa.atualiza_saldo_inicial(lista_de_moedas,corretora_mais_liquida,corretora_menos_liquida)

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

                    #verifica se fui executado e se necessario cancelar ordens abertas            
                    dict_leilao_compra[moeda]['zeragem'], dict_leilao_compra[moeda]['foi_cancelado'] = Leilao.cancela_ordens_e_compra_na_mercado(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True, dict_leilao_compra[moeda]['ordem'])
                    
                    # Se Id diferente de zero, significa que operou leilão (fui executado)
                    if dict_leilao_compra[moeda]['zeragem'].id != 0:
                        
                        comprei_a = round(dict_leilao_compra[moeda]['zeragem'].preco_executado,2)
                        vendi_a = round(dict_leilao_compra[moeda]['ordem'].preco_venda,2)#a revisar!
                        quantidade = round(dict_leilao_compra[moeda]['zeragem'].quantidade_executada,4)

                        pnl = round(((vendi_a * 0.998) - (comprei_a * 1.007)) * quantidade,2)

                        logging.warning('operou leilao de compra de {}! + {}brl de pnl (compra de {}{} @{} na {} e venda a @{} na {})'.format(moeda,pnl,quantidade,moeda,comprei_a,CorretoraMaisLiquida.nome,vendi_a,CorretoraMenosLiquida.nome))
                        CorretoraMaisLiquida.atualizar_saldo()
                        CorretoraMenosLiquida.atualizar_saldo()
                        dict_leilao_compra[moeda]['ordem'] = Ordem() #reinicia as ordens

                    elif dict_leilao_compra[moeda]['ordem'].id == 0 or dict_leilao_compra[moeda]['foi_cancelado']: #se não ha ordens abertas ou se ordens foram canceladas, envia uma nova
                        dict_leilao_compra[moeda]['ordem']  = Leilao.compra(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True)
                        time.sleep(Util.frequencia())
                

                    dict_leilao_venda[moeda]['zeragem'], dict_leilao_venda[moeda]['foi_cancelado'] = Leilao.cancela_ordens_e_vende_na_mercado(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True, dict_leilao_venda[moeda]['ordem'])

                    # Se Id diferente de zero, significa que operou leilão (fui executado)
                    if  dict_leilao_venda[moeda]['zeragem'].id != 0:

                        vendi_a = round(dict_leilao_venda[moeda]['zeragem'].preco_executado,2)
                        comprei_a = round(dict_leilao_venda[moeda]['ordem'].preco_compra,2)
                        quantidade = round(dict_leilao_venda[moeda]['zeragem'].quantidade_executada,4)

                        pnl = round(((vendi_a*0.993)-(comprei_a*1.002)) * quantidade,2)

                        logging.warning('operou leilao de venda de {}! + {}brl de pnl (venda de {}{} @{} na {} e compra a @{} na {})'.format(moeda,pnl,quantidade,moeda,vendi_a,CorretoraMaisLiquida.nome,comprei_a,CorretoraMenosLiquida.nome))
                        CorretoraMaisLiquida.atualizar_saldo()
                        CorretoraMenosLiquida.atualizar_saldo() 
                        dict_leilao_venda[moeda]['ordem'] = Ordem() #reinicia as ordens   

                    elif dict_leilao_venda[moeda]['ordem'].id == 0 or  dict_leilao_venda[moeda]['foi_cancelado']:#se não ha ordens abertas ou se ordens foram canceladas, envia uma nova
                        dict_leilao_venda[moeda]['ordem'] = Leilao.venda(CorretoraMenosLiquida, CorretoraMaisLiquida, moeda, True)
                        time.sleep(Util.frequencia())
                    
                except Exception as erro:        
                    logging.error(erro) 
                
            agora = datetime.now() 

        #zerar o pnl e reiniciar a bagaça
        Caixa.zera_o_pnl_em_cripto(lista_de_moedas,saldo_inicial,corretora_mais_liquida,corretora_menos_liquida)
        retorno_ordem_leilao_compra = Ordem()
        retorno_ordem_leilao_venda = Ordem()

        hour = hour+1
        
        Caixa.atualiza_saldo_inicial(lista_de_moedas,corretora_mais_liquida,corretora_menos_liquida)

    

