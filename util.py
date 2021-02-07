import os
import json
from datetime import datetime

class Util:
    
    def adicionar_linha_no_saldo(linhaRegistro):
        header = 'MOEDA|SALDO|DATA'
        nomeArquivo = 'Saldo.txt'
        
        if not os.path.exists(nomeArquivo):#cria o arquivo se ele não existe
            open(nomeArquivo, 'w').close()

        arquivo = open(nomeArquivo, 'r+')#le para ver se esta vazio
        
        conteudo = arquivo.readlines()
        if len(conteudo) == 0:
                conteudo.append(header + '\n')
        conteudo.append(linhaRegistro + '\n')
        arquivo.close()
        
        arquivo = open(nomeArquivo, 'a+')#escreve conteudo em modo append
        arquivo.writelines(conteudo) 
        arquivo.close()

    def adicionar_linha_em_operacoes(linhaRegistro):
        header = 'MOEDA|CORRETORA|C/V|PRECO|QUANTIDADE|PNL|ESTRATEGIA|DATA'
        nomeArquivo = 'Operacoes.txt'
        
        if not os.path.exists(nomeArquivo):#cria o arquivo se ele não existe
            open(nomeArquivo, 'w').close()
        
        arquivo = open(nomeArquivo, 'r+')#le para ver se esta vazio
        conteudo = arquivo.readlines()
        if len(conteudo) == 0:
                conteudo.append(header + '\n')
        conteudo.append(linhaRegistro + '\n')
        arquivo.close()
        
        arquivo = open(nomeArquivo, 'a+')#escreve conteudo em modo append
        arquivo.writelines(conteudo) 
        arquivo.close()

    def obterCredenciais():
        with open('appsettings.json') as f:
            return json.load(f)

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
