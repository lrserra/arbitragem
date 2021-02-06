import json
from datetime import datetime

class Util:
    
    def adicionar_linha_no_relatorio(self,nomeArquivo, linhaRegistro, header):
        
        raiz = self.obter_caminho_para_relatorios()
        
        arquivo = open(raiz+nomeArquivo, 'w+')
        conteudo = arquivo.readlines()
        if len(conteudo) == 0:
                conteudo.append(header + '\n')
        conteudo.append(linhaRegistro + '\n')
        
        arquivo = open(raiz+nomeArquivo, 'w')
        arquivo.writelines(conteudo) 
        arquivo.close()

    def adicionar_linha_no_saldo(self,linhaRegistro):
        header = 'DATA|MOEDA|SALDOBRL|SALDOCRYPTO'
        nomeArquivo = 'Saldo.txt'
        self.adicionar_linha_no_relatorio(nomeArquivo, linhaRegistro, header)

    def adicionar_linha_em_operacoes(self,linhaRegistro):
        header = 'DATA|MOEDA|CORRETORA|C/V|PRECO|QUANTIDADE|PNL'
        nomeArquivo = 'Operacoes.txt'
        self.adicionar_linha_no_relatorio(nomeArquivo, linhaRegistro, header)

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

    def obter_caminho_para_relatorios(self):
        '''
        retorna o caminho onde os relatorios devem ser salvos
        '''
        with open('appsettings.json') as f:
            return json.load(f)["caminho_relatorios"]

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
