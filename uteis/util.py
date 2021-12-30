
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
        retorna configuracoes do google api
        '''
        with open('appsettings.json') as f:
            return json.load(f)["google_api"]
    
    def retorna_campo_de_json(arquivo, campo):
        '''
        retorna qualquer campo de um json
        '''
        with open(arquivo) as f:
            return json.load(f)[campo]

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
