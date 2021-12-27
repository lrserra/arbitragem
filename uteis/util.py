
import json
import math
import requests, logging
from datetime import datetime

class Util:

    def trunca_171(moeda,qtd,numero_magico = 0):
        
        if moeda in ['ada','xrp','usdt','doge']:
            qtd_final = math.trunc(qtd*1000)/1000 #trunca na terceira
            qtd_final = qtd_final +0.001*numero_magico/1000 #mete o 171
        elif moeda in ['bch','ltc','eth','btc']:
            qtd_final = math.trunc(qtd*100000)/100000 #trunca na quinta
            qtd_final = qtd_final +0.00001*numero_magico/1000 #mete o 171
        else:
            qtd_final = qtd 

        return qtd_final

    def eh_171(qtd):
        return str(qtd)[-3:]=='171'
    
    def trunca_moeda(moeda,qtd):
        '''
        metodo pensado para se adequar ao padrão Binance
        '''
        if moeda in ['doge','xrp']:
            qtd_final = math.trunc(qtd)
        elif moeda in ['ada','usdt']:
            qtd_final = math.trunc(qtd*10)/10
        elif moeda in ['ltc']:
            qtd_final = math.trunc(qtd*1000)/1000 
        elif moeda in ['eth']:
            qtd_final = math.trunc(qtd*10000)/10000
        elif moeda in ['btc']:
            qtd_final = math.trunc(qtd*100000)/100000
        else:
            qtd_final = qtd 

        return qtd_final

    def to_float(number):
        
        try:
            return float(number) if number != '' else ''

        except Exception as err:
            
            import locale
            point = locale.localeconv()['decimal_point']
            sep = locale.localeconv()['thousands_sep']
            if point == ',':
                return locale.atof(number.replace(' ', sep).replace('.', sep))
            elif point == '.':
                return locale.atof(number.replace(' ', sep).replace(',', sep))
            else:
                return number
            

    def excel_date(date1):
        temp = datetime(1899, 12, 30)    # Note, not 31st Dec but 30th!
        delta = date1 - temp
        return float(delta.days) + (float(delta.seconds) / 86400)

    def descricao_erro_padrao():
        '''
        Retorna uma descrição de erro padrão podendo parametrizar o método, a corretora e a mensagem de erro.
        '''
        return 'Erro no método {}, corretora {}. Erro: {}.'

    def CCYBRL():
        return 'brl'
    def CCYBTC():
        return 'btc'
    def CCYETH():
        return 'eth'
    def CCYXRP():
        return 'xrp'
    def CCYLTC():
        return 'ltc'
    def CCYBCH():
        return 'bch'

    def adicionar_linha_no_saldo(qtd_brl,qtd_btc,qtd_eth,qtd_xrp,qtd_ltc,qtd_bch,qtd_usdt,qtd_dai,qtd_eos,qtd_btc_brl,qtd_eth_brl,qtd_xrp_brl,qtd_ltc_brl,qtd_bch_brl,qtd_usdt_brl,qtd_dai_brl,qtd_eos_brl,qtd_brl_mais_liquida,qtd_btc_mais_liquida,qtd_eth_mais_liquida,qtd_xrp_mais_liquida,qtd_ltc_mais_liquida,qtd_bch_mais_liquida,qtd_usdt_mais_liquida,qtd_dai_mais_liquida,qtd_eos_mais_liquida,data):
        
        #dados que serão enviados ao webhook
        data_to_send={}

        data_to_send['qtd_brl'] = round(qtd_brl,4)
        data_to_send['qtd_btc'] = round(qtd_btc,4)
        data_to_send['qtd_eth'] = round(qtd_eth,4)
        data_to_send['qtd_xrp'] = round(qtd_xrp,4)
        data_to_send['qtd_ltc'] = round(qtd_ltc,4)
        data_to_send['qtd_bch'] = round(qtd_bch,4)
        data_to_send['qtd_usdt'] = round(qtd_usdt,4)
        data_to_send['qtd_dai'] = round(qtd_dai,4)
        data_to_send['qtd_eos'] = round(qtd_eos,4)
        data_to_send['qtd_btc_brl'] = round(qtd_btc_brl,4)
        data_to_send['qtd_eth_brl'] = round(qtd_eth_brl,4)
        data_to_send['qtd_xrp_brl'] = round(qtd_xrp_brl,4)
        data_to_send['qtd_ltc_brl'] = round(qtd_ltc_brl,4)
        data_to_send['qtd_bch_brl'] = round(qtd_bch_brl,4)
        data_to_send['qtd_usdt_brl'] = round(qtd_usdt_brl,4)
        data_to_send['qtd_dai_brl'] = round(qtd_dai_brl,4)
        data_to_send['qtd_eos_brl'] = round(qtd_eos_brl,4)
        data_to_send['qtd_brl_mais_liquida'] = round(qtd_brl_mais_liquida,4)
        data_to_send['qtd_btc_mais_liquida'] = round(qtd_btc_mais_liquida,4)
        data_to_send['qtd_eth_mais_liquida'] = round(qtd_eth_mais_liquida,4)
        data_to_send['qtd_xrp_mais_liquida'] = round(qtd_xrp_mais_liquida,4)
        data_to_send['qtd_ltc_mais_liquida'] = round(qtd_ltc_mais_liquida,4)
        data_to_send['qtd_bch_mais_liquida'] = round(qtd_bch_mais_liquida,4)
        data_to_send['qtd_usdt_mais_liquida'] = round(qtd_usdt_mais_liquida,4)
        data_to_send['qtd_dai_mais_liquida'] = round(qtd_dai_mais_liquida,4)
        data_to_send['qtd_eos_mais_liquida'] = round(qtd_eos_mais_liquida,4)
        data_to_send['data'] = str(data)

        #pega o webhook no appsettings
        webhook = ''
        with open('appsettings.json') as f:
            webhook = json.load(f)["integromat"]["saldo"]

        #envia post 
        try:
            requests.post(webhook, json = data_to_send)
        except:
            pass

    def adicionar_linha_em_operacoes(moeda,corretora_compra,preco_compra,quantidade_compra,corretora_venda,preco_venda,quantidade_venda,pnl,estrategia,data):
        #header = 'MOEDA|CORRETORA|PRECO|C/V|QUANTIDADE|PNL|ESTRATEGIA|DATA'
        
        data_to_send={}

        data_to_send['moeda'] = moeda
        data_to_send['corretora_compra'] = corretora_compra
        data_to_send['preco_compra'] = preco_compra
        data_to_send['quantidade_compra'] = quantidade_compra
        data_to_send['financeiro_compra'] = preco_compra*quantidade_compra
        data_to_send['corretora_venda'] = corretora_venda
        data_to_send['preco_venda'] = preco_venda
        data_to_send['quantidade_venda'] = quantidade_venda
        data_to_send['financeiro_venda'] = preco_venda*quantidade_venda
        data_to_send['pnl'] = pnl
        data_to_send['estrategia'] = estrategia
        data_to_send['data'] = data

        #pega o webhook no appsettings
        webhook = ''
        with open('appsettings.json') as f:
            webhook = json.load(f)["integromat"]["operacoes"]
        
        #envia post
        try:
            requests.post(webhook, json = data_to_send)
        except:
            pass

    def obterCredenciais():
        with open('appsettings.json') as f:
            return json.load(f)

    def obter_saldo_inicial_configuracao():
        '''
        retorna dicionario com saldo inicial de cada moeda de acordo com
        a configuração da planilha
        '''
        saldo_inicial = {}
        with open('worksheetsettings.json') as f:
            dic_completo = json.load(f)

        for moeda in dic_completo.keys():
            saldo_inicial[moeda] = dic_completo[moeda]['saldo_inicial']

        return saldo_inicial

    def obter_white_list():
        '''
        retorna a lista de moedas que nosso script vai negociar
        '''
        with open('appsettings.json') as f:
            return json.load(f)["lista_de_moedas"]
    
    def dicionario_simples_para_string(dicionario={},separador='#'):
        '''
        converte um dicionario para uma string
        '''
        string_final = ''
        for chave in dicionario.keys():
            string_final += separador+ chave + ':' + str(dicionario[chave])
        return string_final
    
    def dicionario_duplo_para_string(dicionario={},separador_principal='#',separador_secundario='//'):
        '''
        converte um dicionario para uma string
        '''
        string_final = ''
        for chave_principal in dicionario.keys():
            string_final += separador_principal + chave_principal
            for chave_secundaria in dicionario[chave_principal].keys():
                string_final += separador_secundario+ chave_secundaria + ':' + str(dicionario[chave_principal][chave_secundaria])
        return string_final

    def obter_lista_de_moedas(estrategia_status=''):
        '''
        retorna a lista de moedas que nosso script vai negociar
        '''
        lista_de_moedas = []
        if estrategia_status == '':
            return ['btc','eth','xrp','ltc','bch','ada','doge','usdt']

        with open('worksheetsettings.json') as f:
            dic_completo = json.load(f)
            for moeda in dic_completo.keys():
                if dic_completo[moeda][estrategia_status] == 'LIGADO':
                    lista_de_moedas.append(str(moeda).lower())
        
        return lista_de_moedas

    def obter_corretora_de_maior_liquidez():
        '''
        retorna a corretora de maior liquidez
        '''
        with open('appsettings.json') as f:
            return json.load(f)["corretora_de_maior_liquidez"]
    
    def obter_corretora_de_menor_liquidez():
        '''
        retorna a corretora de menor liquidez
        '''
        with open('appsettings.json') as f:
            return json.load(f)["corretora_de_menor_liquidez"]

    def frequencia():
        '''
        retorna a frequencia que o script precisa rodar intraday após a execução de cada moeda
        '''
        with open('appsettings.json') as f:
            return json.load(f)["frequencia"]
    
    def retorna_menor_valor_compra(moeda):
        '''
        retorna o menor valor possivel que vc pode operar na mercado bitcoin
        '''
        valor_minimo_compra = {}
        with open('worksheetsettings.json') as f:
            dic_completo = json.load(f)

        return float(dic_completo[moeda]['valor_minimo_compra'])

    def retorna_menor_quantidade_venda(moeda):
        '''
        retorna a menor quantidade possivel que vc pode operar na mercado bitcoin
        '''
        quantidade_minima_venda = {}
        with open('worksheetsettings.json') as f:
            dic_completo = json.load(f)

        return float(dic_completo[moeda]['quantidade_minima_venda'])

    def retorna_config_google_api():
        '''
        retorna a menor quantidade possivel que vc pode operar na mercado bitcoin
        '''
        with open('appsettings.json') as f:
            return json.load(f)["google_api"]

    def formatar_data_relatorio(date):
        retorno = datetime(date.year, date.month, date.day, date.hour, date.minute, date.second)
        return retorno

    def retorna_erros_objeto_exception(mensagem, erro):
        '''
        escrever todos os erros logado no objeto exception na sequencia
        '''
        retorno = mensagem + ' | '
        i=0
        
        while i < erro.args.__len__():
            if i == 0: 
                retorno += str(datetime.now()) + str(erro.args[i]) + ' | '
            else:
                retorno += str(erro.args[i]) + ' | '
                print(erro.args[i])
            i += 1
        
        return retorno
