import sys,os,uuid
from uteis.google import Google
root_path = os.getcwd()
sys.path.append(root_path)

from datetime import datetime
from construtores.ordem import Ordem
from construtores.corretora import Corretora
from uteis.settings import Settings
from uteis.converters import Converters
from uteis.logger import Logger

if __name__ == "__main__":

        
    from caixa import Caixa
    from datetime import datetime
    from uteis.settings import Settings
    from uteis.logger import Logger

    Logger.cria_arquivo_log('Caixa')
    Logger.loga_info('iniciando script caixa...')

    settings_client = Settings()
    instance = settings_client.retorna_campo_de_json('rasp','instance')

    moedas_com_saldo_no_caixa = settings_client.retorna_campo_de_json_como_dicionario('strategy','caixa','lista_de_moedas','#')

    lista_para_zerar = [moeda for moeda in moedas_com_saldo_no_caixa.keys()]
    
    caixa_ligada = settings_client.retorna_campo_de_json('strategy','caixa','ligada').lower() == 'true'
    compra_ligada = settings_client.retorna_campo_de_json('strategy','caixa','compra').lower() == 'true'
    venda_ligada = settings_client.retorna_campo_de_json('strategy','caixa','venda').lower() == 'true'

    corretora_mais_liquida = settings_client.retorna_campo_de_json('app',str(instance),'corretora_mais_liquida')
    corretora_menos_liquida = settings_client.retorna_campo_de_json('app',str(instance),'corretora_menos_liquida')
    
    CorretoraMaisLiquida = Corretora(corretora_mais_liquida)
    CorretoraMenosLiquida = Corretora(corretora_menos_liquida)

    if 'btc' in settings_client.retorna_campo_de_json_como_lista('app',str(instance),'white_list','#'):
        cancelei_todas = Caixa.atualiza_saldo_inicial(lista_para_zerar,CorretoraMaisLiquida,CorretoraMenosLiquida)
        if cancelei_todas and caixa_ligada:
            Caixa().zera_o_pnl_de_todas_moedas(lista_para_zerar,moedas_com_saldo_no_caixa,CorretoraMaisLiquida,CorretoraMenosLiquida,False,compra_ligada,venda_ligada)
        
        CorretoraMaisLiquida.atualizar_saldo()
        CorretoraMenosLiquida.atualizar_saldo()

        Caixa.envia_position_google(lista_para_zerar,CorretoraMaisLiquida,CorretoraMenosLiquida)
    else:
        Logger.loga_warning('nao vou zerar nada pq nao sou o rasp primario!!')

class Caixa:

    def __init__(self):
        pass

    def atualiza_saldo_inicial(lista_de_moedas,CorretoraMaisLiquida:Corretora,CorretoraMenosLiquida:Corretora):
        '''
        retorna dicionario com saldo inicial de cada moeda
        '''
        saldo_inicial = {}
        cancelei_todas = False
        
        try:
            CorretoraMenosLiquida.cancelar_todas_ordens()
            cancelei_todas = True
        except Exception as erro:
            Logger.loga_erro('atualiza_saldo_inicial','Caixa','erro no cancelamento de todas ordens: ' + erro)
        
        CorretoraMaisLiquida.atualizar_saldo()
        CorretoraMenosLiquida.atualizar_saldo()
        

        for moeda in lista_de_moedas+['brl']:
            
            saldo_inicial[moeda] = round(CorretoraMaisLiquida.saldo[moeda] + CorretoraMenosLiquida.saldo[moeda],4)
            porcentagem_mais_liquida = round(100*CorretoraMaisLiquida.saldo[moeda]/saldo_inicial[moeda],0)
            porcentagem_menos_liquida = round(100*CorretoraMenosLiquida.saldo[moeda]/saldo_inicial[moeda],0)
            
            Logger.loga_warning('saldo inicial em {}: {} ({}% na {} e {}% na {})'.format(moeda,saldo_inicial[moeda],porcentagem_mais_liquida,CorretoraMaisLiquida.nome,porcentagem_menos_liquida,CorretoraMenosLiquida.nome))
            
        return cancelei_todas

    def envia_position_google(white_list,CorretoraMaisLiquida:Corretora,CorretoraMenosLiquida:Corretora,atualizar_saldo = False):
        '''
        envia nova linha com position consolidada para google        
        '''
        google_client = Google()
        settings_client = Settings()
        saldo={}
        saldo_por_corretora = {}
        financeiro = {}
        financeiro_por_corretora = {}
        preco_por_corretora_venda={}
        preco_por_corretora_compra={}

        Logger.loga_warning('enviando posicao para o google')

        rasp_id = settings_client.retorna_campo_de_json('rasp','instance')
        produto = 'spot'
                
        if atualizar_saldo:
            CorretoraMaisLiquida.atualizar_saldo()
            CorretoraMenosLiquida.atualizar_saldo()
        
        for moeda in white_list+['brl']:
            saldo_por_corretora[moeda] = {}
            financeiro_por_corretora[moeda] = {}
            preco_por_corretora_compra[moeda] = {}
            preco_por_corretora_venda[moeda] = {}

        saldo['brl'] = round(CorretoraMaisLiquida.saldo['brl'] + CorretoraMenosLiquida.saldo['brl'],4)
        financeiro['brl'] = round(CorretoraMaisLiquida.saldo['brl'] + CorretoraMenosLiquida.saldo['brl'],2)
        saldo_por_corretora['brl'][CorretoraMaisLiquida.nome]=round(CorretoraMaisLiquida.saldo['brl'],4)
        saldo_por_corretora['brl'][CorretoraMenosLiquida.nome]=round(CorretoraMenosLiquida.saldo['brl'],4)
        financeiro_por_corretora['brl'][CorretoraMaisLiquida.nome]=round(CorretoraMaisLiquida.saldo['brl'],2)
        financeiro_por_corretora['brl'][CorretoraMenosLiquida.nome]=round(CorretoraMenosLiquida.saldo['brl'],2)
        preco_por_corretora_venda['brl'][CorretoraMaisLiquida.nome] = 1
        preco_por_corretora_compra['brl'][CorretoraMaisLiquida.nome] = 1
        preco_por_corretora_venda['brl'][CorretoraMenosLiquida.nome] = 1
        preco_por_corretora_compra['brl'][CorretoraMenosLiquida.nome] = 1

        for moeda in white_list:
            CorretoraMaisLiquida.atualizar_book(moeda,'brl')
            CorretoraMenosLiquida.atualizar_book(moeda,'brl')
            saldo[moeda] = round(CorretoraMaisLiquida.saldo[moeda] + CorretoraMenosLiquida.saldo[moeda],4)
            financeiro[moeda] = round(saldo[moeda]*CorretoraMaisLiquida.livro.preco_venda,2)
            saldo_por_corretora[moeda][CorretoraMaisLiquida.nome]=round(CorretoraMaisLiquida.saldo[moeda],4)
            saldo_por_corretora[moeda][CorretoraMenosLiquida.nome]=round(CorretoraMenosLiquida.saldo[moeda],4)
            financeiro_por_corretora[moeda][CorretoraMaisLiquida.nome] = round(saldo_por_corretora[moeda][CorretoraMaisLiquida.nome]*CorretoraMaisLiquida.livro.preco_venda,2)
            financeiro_por_corretora[moeda][CorretoraMenosLiquida.nome] = round(saldo_por_corretora[moeda][CorretoraMenosLiquida.nome]*CorretoraMenosLiquida.livro.preco_venda,2)
            preco_por_corretora_venda[moeda][CorretoraMaisLiquida.nome]=CorretoraMaisLiquida.livro.preco_venda
            preco_por_corretora_compra[moeda][CorretoraMaisLiquida.nome]=CorretoraMaisLiquida.livro.preco_compra
            preco_por_corretora_venda[moeda][CorretoraMenosLiquida.nome]=CorretoraMenosLiquida.livro.preco_venda
            preco_por_corretora_compra[moeda][CorretoraMenosLiquida.nome]=CorretoraMenosLiquida.livro.preco_compra

        planilha = settings_client.retorna_campo_de_json('rasp','sheet_name')
        google_client.escrever(planilha,'position',[Converters.datetime_para_excel_date(datetime.now())
                                        ,rasp_id
                                        ,produto
                                        ,Converters.dicionario_simples_para_string(saldo)
                                        ,Converters.dicionario_duplo_para_string(saldo_por_corretora)
                                        ,Converters.dicionario_simples_para_string(financeiro)
                                        ,Converters.dicionario_duplo_para_string(financeiro_por_corretora)
                                        ,Converters.dicionario_duplo_para_string(preco_por_corretora_venda)
                                        ,Converters.dicionario_duplo_para_string(preco_por_corretora_compra)])

        return True
   
    def zera_o_pnl_de_todas_moedas(self,lista_de_moedas,saldo_inicial,CorretoraMaisLiquida:Corretora,CorretoraMenosLiquida:Corretora,atualizar_saldo=True,compra_ligada=True,venda_ligada=True):
        '''
        ao longo do dia, nós pagamos corretagem em cripto, então é bom comprar essa quantidade novamente
        '''
        if atualizar_saldo:
            CorretoraMaisLiquida.atualizar_saldo()
            CorretoraMenosLiquida.atualizar_saldo()

        saldo_final = {}

        #verifica saldo final, para comparar com inicial
        for moeda in lista_de_moedas:

            try:
                saldo_final[moeda] = CorretoraMaisLiquida.saldo[moeda] + CorretoraMenosLiquida.saldo[moeda]

                pnl_em_moeda = round(float(saldo_final[moeda]) - float(saldo_inicial[moeda]),6)
                quantidade_a_zerar = round(abs(pnl_em_moeda),6)

                if CorretoraMaisLiquida.saldo[moeda]==0 and moeda in CorretoraMaisLiquida.moedas_negociaveis:
                    Logger.loga_info('saldo de {} na {} esta zerado e por seguranca nao vamos zerar caixa'.format(moeda,CorretoraMaisLiquida.nome))
                    quantidade_a_zerar = 0

                elif CorretoraMenosLiquida.saldo[moeda]==0 and moeda in CorretoraMenosLiquida.moedas_negociaveis:
                    Logger.loga_info('saldo de {} na {} esta zerado e por seguranca nao vamos zerar caixa'.format(moeda,CorretoraMenosLiquida.nome))
                    quantidade_a_zerar = 0

                #carrego os books de ordem mais recentes
                CorretoraMaisLiquida.atualizar_book(moeda,'brl')
                
                #precisa vender e dá pra vender em alguma corretora
                if pnl_em_moeda > 0 and quantidade_a_zerar > min(CorretoraMaisLiquida.quantidade_minima_venda[moeda],CorretoraMenosLiquida.quantidade_minima_venda[moeda]):

                    #carrego os books de ordem mais recentes
                    CorretoraMenosLiquida.atualizar_book(moeda,'brl')

                    if CorretoraMaisLiquida.livro.obter_preco_medio_de_venda(quantidade_a_zerar) > CorretoraMenosLiquida.livro.obter_preco_medio_de_venda(quantidade_a_zerar) or moeda not in CorretoraMenosLiquida.moedas_negociaveis: #vamos vender na corretora que paga mais e que tenha saldo
                        #A mais liquida é a mais vantajosa para vender    
                        quantidade_a_vender_na_mais_cara = min(quantidade_a_zerar,CorretoraMaisLiquida.saldo[moeda])
                        quantidade_que_restou = quantidade_a_zerar-quantidade_a_vender_na_mais_cara if quantidade_a_vender_na_mais_cara > CorretoraMaisLiquida.quantidade_minima_venda[moeda] else min(quantidade_a_zerar,CorretoraMenosLiquida.saldo[moeda]) #pode ser que seja menor que a qtd minima em uma corretora mas não em outra
                        if quantidade_a_vender_na_mais_cara>CorretoraMaisLiquida.quantidade_minima_venda[moeda] and moeda in CorretoraMaisLiquida.moedas_negociaveis and compra_ligada:    
                            self.zera_o_pnl_de_uma_moeda('venda',quantidade_a_vender_na_mais_cara,moeda,CorretoraMaisLiquida)
                        if quantidade_que_restou>CorretoraMenosLiquida.quantidade_minima_venda[moeda] and moeda in CorretoraMenosLiquida.moedas_negociaveis and venda_ligada:
                            self.zera_o_pnl_de_uma_moeda('venda',quantidade_que_restou,moeda,CorretoraMenosLiquida)
                    
                    elif CorretoraMaisLiquida.livro.obter_preco_medio_de_venda(quantidade_a_zerar) < CorretoraMenosLiquida.livro.obter_preco_medio_de_venda(quantidade_a_zerar) or moeda not in CorretoraMaisLiquida.moedas_negociaveis:
                        #A menos liquida é a mais vantajosa para vender    
                        quantidade_a_vender_na_mais_cara = min(quantidade_a_zerar,CorretoraMenosLiquida.saldo[moeda])
                        quantidade_que_restou = quantidade_a_zerar-quantidade_a_vender_na_mais_cara if quantidade_a_vender_na_mais_cara > CorretoraMenosLiquida.quantidade_minima_venda[moeda] else min(quantidade_a_zerar,CorretoraMaisLiquida.saldo[moeda]) #pode ser que seja menor que a qtd minima em uma corretora mas não em outra
                        if quantidade_a_vender_na_mais_cara>CorretoraMenosLiquida.quantidade_minima_venda[moeda] and moeda in CorretoraMenosLiquida.moedas_negociaveis and venda_ligada:
                            self.zera_o_pnl_de_uma_moeda('venda',quantidade_a_vender_na_mais_cara,moeda,CorretoraMenosLiquida)
                        if quantidade_que_restou>CorretoraMaisLiquida.quantidade_minima_venda[moeda] and moeda in CorretoraMaisLiquida.moedas_negociaveis and compra_ligada:
                            self.zera_o_pnl_de_uma_moeda('venda',quantidade_que_restou,moeda,CorretoraMaisLiquida)

                #precisa comprar e dá pra comprar em alguma corretora
                elif pnl_em_moeda < 0 and quantidade_a_zerar*CorretoraMaisLiquida.livro.preco_compra > min(CorretoraMaisLiquida.valor_minimo_compra[moeda],CorretoraMenosLiquida.valor_minimo_compra[moeda]):
                
                    #carrego os books de ordem mais recentes
                    CorretoraMenosLiquida.atualizar_book(moeda,'brl')

                    if CorretoraMaisLiquida.livro.obter_preco_medio_de_compra(quantidade_a_zerar) < CorretoraMenosLiquida.livro.obter_preco_medio_de_compra(quantidade_a_zerar) or moeda not in CorretoraMenosLiquida.moedas_negociaveis: #vamos comprar na corretora que esta mais barato e que tenha saldo
                        #A mais liquida é a mais vantajosa para comprar
                        quantidade_posso_comprar_na_mais_barata = CorretoraMaisLiquida.saldo['brl']/CorretoraMaisLiquida.livro.obter_preco_medio_de_compra(quantidade_a_zerar)
                        quantidade_posso_comprar_na_mais_cara = CorretoraMenosLiquida.saldo['brl']/CorretoraMenosLiquida.livro.obter_preco_medio_de_compra(quantidade_a_zerar)
                        quantidade_a_comprar_na_mais_barata = min(quantidade_a_zerar,quantidade_posso_comprar_na_mais_barata)
                        financeiro_a_comprar_na_mais_barata = quantidade_a_comprar_na_mais_barata*CorretoraMaisLiquida.livro.obter_preco_medio_de_compra(quantidade_a_comprar_na_mais_barata)
                        quantidade_que_restou = quantidade_a_zerar - quantidade_a_comprar_na_mais_barata if financeiro_a_comprar_na_mais_barata > CorretoraMaisLiquida.valor_minimo_compra[moeda] else min(quantidade_a_zerar,quantidade_posso_comprar_na_mais_cara)
                        financeiro_que_restou = 0 if quantidade_que_restou==0 else quantidade_que_restou*CorretoraMenosLiquida.livro.obter_preco_medio_de_compra(quantidade_que_restou)
                        if financeiro_a_comprar_na_mais_barata>CorretoraMaisLiquida.valor_minimo_compra[moeda] and moeda in CorretoraMaisLiquida.moedas_negociaveis and venda_ligada:
                            self.zera_o_pnl_de_uma_moeda('compra',quantidade_a_comprar_na_mais_barata,moeda,CorretoraMaisLiquida)
                        if financeiro_que_restou>CorretoraMenosLiquida.valor_minimo_compra[moeda] and moeda in CorretoraMenosLiquida.moedas_negociaveis and compra_ligada:
                            self.zera_o_pnl_de_uma_moeda('compra',quantidade_que_restou,moeda,CorretoraMenosLiquida)

                    elif CorretoraMaisLiquida.livro.obter_preco_medio_de_compra(quantidade_a_zerar) > CorretoraMenosLiquida.livro.obter_preco_medio_de_compra(quantidade_a_zerar) or moeda not in CorretoraMaisLiquida.moedas_negociaveis:
                        #A menos liquida é a mais vantajosa para comprar
                        quantidade_posso_comprar_na_mais_barata = CorretoraMenosLiquida.saldo['brl']/CorretoraMenosLiquida.livro.obter_preco_medio_de_compra(quantidade_a_zerar)
                        quantidade_posso_comprar_na_mais_cara = CorretoraMaisLiquida.saldo['brl']/CorretoraMaisLiquida.livro.obter_preco_medio_de_compra(quantidade_a_zerar)                        
                        quantidade_a_comprar_na_mais_barata = min(quantidade_a_zerar,quantidade_posso_comprar_na_mais_barata)
                        financeiro_a_comprar_na_mais_barata = quantidade_a_comprar_na_mais_barata*CorretoraMenosLiquida.livro.obter_preco_medio_de_compra(quantidade_a_comprar_na_mais_barata)
                        quantidade_que_restou = quantidade_a_zerar - quantidade_a_comprar_na_mais_barata if financeiro_a_comprar_na_mais_barata > CorretoraMenosLiquida.valor_minimo_compra[moeda] else min(quantidade_a_zerar,quantidade_posso_comprar_na_mais_cara)
                        financeiro_que_restou = 0 if quantidade_que_restou==0 else quantidade_que_restou*CorretoraMaisLiquida.livro.obter_preco_medio_de_compra(quantidade_que_restou)
                        if financeiro_a_comprar_na_mais_barata>CorretoraMenosLiquida.valor_minimo_compra[moeda] and moeda in CorretoraMenosLiquida.moedas_negociaveis and compra_ligada:
                            self.zera_o_pnl_de_uma_moeda('compra',quantidade_a_comprar_na_mais_barata,moeda,CorretoraMenosLiquida)
                        if financeiro_que_restou>CorretoraMaisLiquida.valor_minimo_compra[moeda] and moeda in CorretoraMaisLiquida.moedas_negociaveis and venda_ligada:
                            self.zera_o_pnl_de_uma_moeda('compra',quantidade_que_restou,moeda,CorretoraMaisLiquida)

                else:
                    Logger.loga_warning('caixa não precisa zerar pnl de {} por ora'.format(moeda))
            
            except Exception as erro:
                Logger.loga_erro('zera_o_pnl_de_todas_moedas','Caixa','erro na moeda {}: {}'.format(moeda,erro))       

        return True

    def zera_o_pnl_de_uma_moeda(self,direcao,quantidade_a_zerar,moeda,corretora:Corretora):

        settings_client = Settings()
        planilha = settings_client.retorna_campo_de_json('rasp','sheet_name')
        
        google_client = Google()
        ordem = Ordem()
        
        if direcao == 'venda':
            
            Logger.loga_warning('caixa vai vender {} {} na {} para zerar o pnl'.format(round(quantidade_a_zerar,4),moeda,corretora.nome))
            
            ordem = Ordem(moeda,quantidade_a_zerar,corretora.livro.preco_venda,'market')
            ordem_venda = corretora.enviar_ordem_venda(ordem)
            vendi_a = ordem_venda.preco_executado
            quantidade_executada_venda = ordem_venda.quantidade_executada
            financeiro_venda = vendi_a * quantidade_executada_venda
            financeiro_corretagem = corretora.corretagem_mercado*financeiro_venda

            trade_time = Converters.datetime_para_excel_date(datetime.now())
            trade_id = str(uuid.uuid4())
            
            google_client.escrever(planilha,'spot',[trade_time,trade_id,'CAIXA',moeda,corretora.nome,'VENDA',vendi_a,quantidade_executada_venda,financeiro_venda,0,corretora.livro.preco_venda,0,corretora.corretagem_mercado,financeiro_corretagem,0,'FALSE'])
            corretora.atualizar_saldo()
        
        elif direcao == 'compra':

            Logger.loga_warning('caixa vai comprar {} {} na {} para zerar o pnl'.format(quantidade_a_zerar,moeda,corretora.nome))
        
            ordem = Ordem(moeda,quantidade_a_zerar,corretora.livro.preco_compra,'market')
            ordem_compra = corretora.enviar_ordem_compra(ordem)
            comprei_a = ordem_compra.preco_executado
            quantidade_executada_compra = ordem_compra.quantidade_executada
            financeiro_compra = comprei_a * quantidade_executada_compra
            financeiro_corretagem = corretora.corretagem_mercado*financeiro_compra

            trade_time = Converters.datetime_para_excel_date(datetime.now())
            trade_id = str(uuid.uuid4())

            google_client.escrever(planilha,'spot',[trade_time,trade_id,'CAIXA',moeda,corretora.nome,'COMPRA',comprei_a,quantidade_executada_compra,financeiro_compra,0,corretora.livro.preco_compra,0,corretora.corretagem_mercado,financeiro_corretagem,0,'FALSE'])
            corretora.atualizar_saldo()

        return True


