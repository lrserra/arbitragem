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