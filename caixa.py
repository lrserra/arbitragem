import logging
from datetime import datetime
from uteis.corretora import Corretora
from uteis.util import Util
from uteis.googleSheets import GoogleSheets
import uuid

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
        except Exception as err:
            logging.error('erro no cancelamento de todas ordens: ' + err)
        
        CorretoraMaisLiquida.atualizar_saldo()
        CorretoraMenosLiquida.atualizar_saldo()
        

        for moeda in lista_de_moedas+['brl']:
            
            saldo_inicial[moeda] = round(CorretoraMaisLiquida.saldo[moeda] + CorretoraMenosLiquida.saldo[moeda],4)
            porcentagem_mais_liquida = round(100*CorretoraMaisLiquida.saldo[moeda]/saldo_inicial[moeda],0)
            porcentagem_menos_liquida = round(100*CorretoraMenosLiquida.saldo[moeda]/saldo_inicial[moeda],0)
            
            logging.warning('saldo inicial em {}: {} ({}% na {} e {}% na {})'.format(moeda,saldo_inicial[moeda],porcentagem_mais_liquida,CorretoraMaisLiquida.nome,porcentagem_menos_liquida,CorretoraMenosLiquida.nome))
            
        return cancelei_todas

    
    def envia_saldo_google(CorretoraMaisLiquida:Corretora,CorretoraMenosLiquida:Corretora):
        '''
        da uma limpada nos registros de saldo do google +
        envia nova linha de saldo para planilha do google
        '''
        saldo = {}
        preco_venda = {}

        lista_de_moedas_hardcoded = Util.obter_lista_de_moedas()+[Util.CCYBRL()]
        
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
        
        CorretoraMaisLiquida.book.obter_ordem_book_por_indice('usdc','brl',0,False,False)
        preco_venda['usdc']=CorretoraMaisLiquida.book.preco_venda

        logging.warning('caixa vai enviar saldo para o google')
        GoogleSheets().escrever_saldo([saldo['brl'],saldo['btc'],saldo['eth'],saldo['xrp'],saldo['ltc'],saldo['bch'],saldo['ada'],saldo['usdt'],saldo['doge'],saldo['btc']*preco_venda['btc'],saldo['eth']*preco_venda['eth'],saldo['xrp']*preco_venda['xrp'],saldo['ltc']*preco_venda['ltc'],saldo['bch']*preco_venda['bch'],saldo['ada']*preco_venda['ada'],saldo['usdt']*preco_venda['usdt'],saldo['doge']*preco_venda['doge'],CorretoraMaisLiquida.saldo['brl'],CorretoraMaisLiquida.saldo['btc'],CorretoraMaisLiquida.saldo['eth'],CorretoraMaisLiquida.saldo['xrp'],CorretoraMaisLiquida.saldo['ltc'],CorretoraMaisLiquida.saldo['bch'],CorretoraMaisLiquida.saldo['ada'],CorretoraMaisLiquida.saldo['usdt'],CorretoraMaisLiquida.saldo['doge'], Util.excel_date(datetime.now()),preco_venda['usdc']])


    def zera_o_pnl_de_todas_moedas(self,lista_de_moedas,CorretoraMaisLiquida:Corretora,CorretoraMenosLiquida:Corretora,atualizar_saldo=True):
        '''
        ao longo do dia, nós pagamos corretagem em cripto, então é bom comprar essa quantidade novamente
        '''
        saldo_inicial = Util.obter_saldo_inicial_configuracao()
        saldo_final = {}

        google_sheets = GoogleSheets()

        if atualizar_saldo:
            CorretoraMaisLiquida.atualizar_saldo()
            CorretoraMenosLiquida.atualizar_saldo()

        moedas_para_zerar = lista_de_moedas
        #verifica saldo final, para comparar com inicial
        for moeda in moedas_para_zerar:

            saldo_final[moeda] = CorretoraMaisLiquida.saldo[moeda] + CorretoraMenosLiquida.saldo[moeda]

            pnl_em_moeda = round(float(saldo_final[moeda]) - float(saldo_inicial[moeda]),4)
            quantidade_a_zerar = round(abs(pnl_em_moeda),4)

            if CorretoraMaisLiquida.saldo[moeda]==0:
                logging.warning('saldo de {} na {} esta zerado e por seguranca nao vamos zerar caixa'.format(moeda,CorretoraMaisLiquida.nome))
                quantidade_a_zerar = 0

            elif CorretoraMenosLiquida.saldo[moeda]==0:
                logging.warning('saldo de {} na {} esta zerado e por seguranca nao vamos zerar caixa'.format(moeda,CorretoraMenosLiquida.nome))
                quantidade_a_zerar = 0

            #carrego os books de ordem mais recentes
            CorretoraMaisLiquida.book.obter_ordem_book_por_indice(moeda,Util.CCYBRL(),0,True,True)
            colchao_de_liquidez = 0.98

            if pnl_em_moeda > 0 and quantidade_a_zerar > Util.retorna_menor_quantidade_venda(moeda):

                #carrego os books de ordem mais recentes
                CorretoraMenosLiquida.book.obter_ordem_book_por_indice(moeda,Util.CCYBRL(),0,True,True)

                if CorretoraMaisLiquida.book.obter_preco_medio_de_venda(quantidade_a_zerar) > CorretoraMenosLiquida.book.obter_preco_medio_de_venda(quantidade_a_zerar): #vamos vender na corretora que paga mais e que tenha saldo
                    #A mais liquida é a mais vantajosa para vender    
                    quantidade_a_vender_na_mais_cara = min(quantidade_a_zerar,colchao_de_liquidez*CorretoraMaisLiquida.saldo[moeda])
                    quantidade_que_restou = quantidade_a_zerar-quantidade_a_vender_na_mais_cara
                    if quantidade_a_vender_na_mais_cara>Util.retorna_menor_quantidade_venda(moeda):    
                        self.zera_o_pnl_de_uma_moeda('venda',quantidade_a_vender_na_mais_cara,moeda,CorretoraMaisLiquida,google_sheets)
                    if quantidade_que_restou>Util.retorna_menor_quantidade_venda(moeda):
                        self.zera_o_pnl_de_uma_moeda('venda',quantidade_que_restou,moeda,CorretoraMenosLiquida,google_sheets)
                
                elif CorretoraMaisLiquida.book.obter_preco_medio_de_venda(quantidade_a_zerar) < CorretoraMenosLiquida.book.obter_preco_medio_de_venda(quantidade_a_zerar):
                    #A menos liquida é a mais vantajosa para vender    
                    quantidade_a_vender_na_mais_cara = min(quantidade_a_zerar,colchao_de_liquidez*CorretoraMenosLiquida.saldo[moeda])
                    quantidade_que_restou = quantidade_a_zerar-quantidade_a_vender_na_mais_cara
                    if quantidade_a_vender_na_mais_cara>Util.retorna_menor_quantidade_venda(moeda):
                        self.zera_o_pnl_de_uma_moeda('venda',quantidade_a_vender_na_mais_cara,moeda,CorretoraMenosLiquida,google_sheets)
                    if quantidade_que_restou>Util.retorna_menor_quantidade_venda(moeda):
                        self.zera_o_pnl_de_uma_moeda('venda',quantidade_que_restou,moeda,CorretoraMaisLiquida,google_sheets)

            elif pnl_em_moeda < 0 and quantidade_a_zerar*CorretoraMaisLiquida.book.preco_compra > Util.retorna_menor_valor_compra(moeda):
            
                #carrego os books de ordem mais recentes
                CorretoraMenosLiquida.book.obter_ordem_book_por_indice(moeda,Util.CCYBRL(),0,True,True)

                if CorretoraMaisLiquida.book.obter_preco_medio_de_compra(quantidade_a_zerar) < CorretoraMenosLiquida.book.obter_preco_medio_de_compra(quantidade_a_zerar): #vamos comprar na corretora que esta mais barato e que tenha saldo
                    #A mais liquida é a mais vantajosa para comprar
                    quantidade_a_comprar_na_mais_barata = min(quantidade_a_zerar,colchao_de_liquidez*CorretoraMaisLiquida.saldo['brl']/CorretoraMaisLiquida.book.obter_preco_medio_de_compra(quantidade_a_zerar))
                    quantidade_que_restou = quantidade_a_zerar - quantidade_a_comprar_na_mais_barata
                    if quantidade_a_comprar_na_mais_barata*CorretoraMenosLiquida.book.obter_preco_medio_de_compra(quantidade_a_zerar)>Util.retorna_menor_valor_compra(moeda):
                        self.zera_o_pnl_de_uma_moeda('compra',quantidade_a_comprar_na_mais_barata,moeda,CorretoraMaisLiquida,google_sheets)
                    if quantidade_que_restou*CorretoraMenosLiquida.book.obter_preco_medio_de_compra(quantidade_a_zerar)>Util.retorna_menor_valor_compra(moeda):
                        self.zera_o_pnl_de_uma_moeda('compra',quantidade_que_restou,moeda,CorretoraMenosLiquida,google_sheets)

                elif CorretoraMaisLiquida.book.obter_preco_medio_de_compra(quantidade_a_zerar) > CorretoraMenosLiquida.book.obter_preco_medio_de_compra(quantidade_a_zerar):
                    #A menos liquida é a mais vantajosa para comprar
                    quantidade_a_comprar_na_mais_barata = min(quantidade_a_zerar,colchao_de_liquidez*CorretoraMenosLiquida.saldo['brl']/CorretoraMenosLiquida.book.obter_preco_medio_de_compra(quantidade_a_zerar))
                    quantidade_que_restou = quantidade_a_zerar - quantidade_a_comprar_na_mais_barata
                    if quantidade_a_comprar_na_mais_barata*CorretoraMaisLiquida.book.obter_preco_medio_de_compra(quantidade_a_zerar)>Util.retorna_menor_valor_compra(moeda):
                        self.zera_o_pnl_de_uma_moeda('compra',quantidade_a_comprar_na_mais_barata,moeda,CorretoraMenosLiquida,google_sheets)
                    if quantidade_que_restou*CorretoraMaisLiquida.book.obter_preco_medio_de_compra(quantidade_a_zerar)>Util.retorna_menor_valor_compra(moeda):
                        self.zera_o_pnl_de_uma_moeda('compra',quantidade_que_restou,moeda,CorretoraMaisLiquida,google_sheets)

            else:
                logging.warning('caixa não precisa zerar pnl de {} por ora'.format(moeda))
                

        return True

    def zera_o_pnl_de_uma_moeda(self,direcao,quantidade_a_zerar,moeda,corretora:Corretora,google_sheets:GoogleSheets):

        if direcao == 'venda':
            
            logging.warning('caixa vai vender {} {} na {} para zerar o pnl'.format(round(quantidade_a_zerar,4),moeda,corretora.nome))
            
            corretora.ordem.quantidade_enviada = quantidade_a_zerar
            corretora.ordem.tipo_ordem = 'market'
            corretora.ordem.preco_enviado = corretora.book.preco_venda
            
            ordem_venda = corretora.enviar_ordem_venda(corretora.ordem,moeda)
            vendi_a = ordem_venda.preco_executado
            quantidade_executada_venda = ordem_venda.quantidade_executada
            financeiro_venda = vendi_a * quantidade_executada_venda

            google_sheets.escrever_operacao([moeda,'',0,0,corretora.nome,vendi_a,quantidade_executada_venda,0,'CAIXA', Util.excel_date(datetime.now()),0,financeiro_venda])
            google_sheets.escrever_spot([Util.excel_date(datetime.now()),uuid.uuid4(),'CAIXA',moeda,corretora.nome,'VENDA',vendi_a,quantidade_executada_venda,financeiro_venda,0,'FALSE'])
            corretora.atualizar_saldo()
        
        elif direcao == 'compra':

            logging.warning('caixa vai comprar {} {} na {} para zerar o pnl'.format(quantidade_a_zerar,moeda,corretora.nome))
        
            corretora.ordem.quantidade_enviada = quantidade_a_zerar
            corretora.ordem.tipo_ordem = 'market'
            corretora.ordem.preco_enviado = corretora.book.preco_compra
            
            ordem_compra = corretora.enviar_ordem_compra(corretora.ordem,moeda)
            comprei_a = ordem_compra.preco_executado
            quantidade_executada_compra = ordem_compra.quantidade_executada
            financeiro_compra = comprei_a * quantidade_executada_compra

            google_sheets.escrever_operacao([moeda,corretora.nome,comprei_a,quantidade_executada_compra,'',0,0,0,'CAIXA', Util.excel_date(datetime.now()),financeiro_compra,0])
            google_sheets.escrever_spot([Util.excel_date(datetime.now()),uuid.uuid4(),'CAIXA',moeda,corretora.nome,'COMPRA',comprei_a,quantidade_executada_compra,financeiro_compra,0,'FALSE'])
            corretora.atualizar_saldo()

        return True


if __name__ == "__main__":

        
    from caixa import Caixa
    from datetime import datetime

    logging.basicConfig(filename='Caixa.log', level=logging.INFO,
                        format='[%(asctime)s][%(levelname)s][%(message)s]')
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    logging.getLogger().addHandler(console)

    #essa parte executa apenas uma vez
    white_list = Util.obter_white_list()
    lista_para_zerar = [moeda for moeda in Util.obter_lista_de_moedas('zeragem_status') if moeda in white_list]
    
    corretora_mais_liquida = Util.obter_corretora_de_maior_liquidez()
    corretora_menos_liquida = Util.obter_corretora_de_menor_liquidez()

    # Instancia das corretoras por ativo
    CorretoraMaisLiquida = Corretora(corretora_mais_liquida)
    CorretoraMenosLiquida = Corretora(corretora_menos_liquida)

    cancelei_todas = Caixa.atualiza_saldo_inicial(lista_para_zerar,CorretoraMaisLiquida,CorretoraMenosLiquida)
    if cancelei_todas:
        Caixa.zera_o_pnl_de_todas_moedas(Caixa(),lista_para_zerar,CorretoraMaisLiquida,CorretoraMenosLiquida,False)
    
    CorretoraMaisLiquida.atualizar_saldo()
    CorretoraMenosLiquida.atualizar_saldo()

    Caixa.envia_saldo_google(CorretoraMaisLiquida,CorretoraMenosLiquida)