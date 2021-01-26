import json

class Util:
    
    def escreverArquivoComQuebraDeLinha(nomeArquivo, linhaRegistro, header):
        arquivo = open(nomeArquivo, 'r')
        conteudo = arquivo.readlines()
        if len(conteudo) == 0:
                conteudo.append(header + '\n')
        conteudo.append(linhaRegistro + '\n')
        arquivo = open(nomeArquivo, 'w')
        arquivo.writelines(conteudo) 
        arquivo.close()

    def escreverArquivoCashList(self, linhaRegistro):
        header = 'COIN|BROKER|SALDOBRL|SALDOCRYPTO|TIMESTAMP'
        nomeArquivo = 'CashList.txt'
        self.escreverArquivoComQuebraDeLinha(nomeArquivo, linhaRegistro, header)

    def escreverArquivoOperacao(self, nomeArquivo, linhaRegistro):
        header = 'COIN|BROKER|C/V|BID|QUANTITY|FINCORRETAGEM|PNL|TIMESTAMP'
        self.escreverArquivoComQuebraDeLinha(nomeArquivo, linhaRegistro, header)

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



    
    