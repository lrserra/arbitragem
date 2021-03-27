import os
import json
import requests
from datetime import datetime

class Util:
    
    def adicionar_linha_no_saldo(linhaRegistro):
        header = 'MOEDA|SALDO|DATA'
        nomeArquivo = 'Saldo.txt'
        
        if os.path.exists(nomeArquivo):
            append_write = 'a' # append if already exists
            arquivo = open(nomeArquivo,append_write)
        else:
            append_write = 'w' # make a new file if not
            arquivo = open(nomeArquivo,append_write)
            arquivo.writelines(header + '\n')

        arquivo.writelines(linhaRegistro + '\n')
        arquivo.close()

    def adicionar_linha_em_operacoes(moeda,corretora,c_v,preco,quantidade,pnl,estrategia,data):
        #header = 'MOEDA|CORRETORA|PRECO|C/V|QUANTIDADE|PNL|ESTRATEGIA|DATA'
        
        data_to_send={}

        data_to_send['moeda'] = moeda
        data_to_send['corretora'] = corretora
        data_to_send['c_v'] = c_v
        data_to_send['preco'] = preco
        data_to_send['quantidade'] = quantidade
        data_to_send['pnl'] = pnl
        data_to_send['estrategia'] = estrategia
        data_to_send['data'] = data

        requests.post("https://hook.integromat.com/rxcekfvix72yoe20vefs9b7mdloohjo9", json = data_to_send)

    def obterCredenciais():
        with open('appsettings.json') as f:
            return json.load(f)

    def obter_saldo_inicial():
        '''
        retorna dicionario com saldo inicial de cada moeda
        '''
        with open('appsettings.json') as f:
            return json.load(f)["saldo_inicial"]

    def obter_balancear_carteira():
        '''
        retorna dicionario com moedas a balancear cripto
        '''
        with open('appsettings.json') as f:
            return json.load(f)["balancear_carteira"]

    def obter_lista_de_moedas():
        '''
        retorna a lista de moedas que nosso script vai negociar
        '''
        with open('appsettings.json') as f:
            return json.load(f)["lista_de_moedas"]

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
        with open('appsettings.json') as f:
            return json.load(f)[moeda]["valor_minima_compra"]

    def retorna_menor_quantidade_venda(moeda):
        '''
        retorna a menor quantidade possivel que vc pode operar na mercado bitcoin
        '''
        with open('appsettings.json') as f:
            return json.load(f)[moeda]["quantidade_minima_venda"]

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
