import json
import requests
from uteis.googleSheets import GoogleSheets
from uteis.corretora import Corretora
from uteis.ordem import Ordem
from uteis.util import Util
from datetime import datetime, timezone
import time

'''
# Obter quantidades de moedas da planilha [0]: moeda [1]: valor
quantidade_moeda = GoogleSheets().ler_quantidade_moeda()
# Obter a lista moedas em operação
lista_de_moedas = Util.obter_lista_de_moedas()

# Abrir o arquivo de configuração para uso
arquivo = open("worksheetsettings.json", "r")
conteudo = json.load(arquivo) # Carrega os dados do Json

# Manipulação do arquivo atualizando as quantidades conforme planilha
for moeda in lista_de_moedas:
    for qtd_moeda in quantidade_moeda:
        if moeda == qtd_moeda[0]:
            conteudo['saldo_inicial'][moeda] = qtd_moeda[1]

arquivo.close() # Fecha o arquivo que estava aberto como somente leitura

arquivo = open("worksheetsettings.json", "w") # Sobrescreve o arquivo
json.dump(conteudo, arquivo) # Salva o Json no arquivo
arquivo.close() # Fecha o arquivo
'''

corretora_obj = Corretora('Novadax')
corretora_obj2 = Corretora('BitcoinTrade')








i = 0
while i<5000:
    corretora_obj.book.obter_ordem_book_por_indice('xrp','brl',0,True,True) 
    corretora_obj.atualizar_saldo() 
    corretora_obj2.book.obter_ordem_book_por_indice('xrp','brl',0,True,True) 
    corretora_obj2.atualizar_saldo() 
    i+=1
    print('#{}'.format(i))
    print(corretora_obj.book.preco_compra_segundo_na_fila)
    print(corretora_obj.saldo['brl'])
    print(corretora_obj2.book.preco_compra_segundo_na_fila)
    print(corretora_obj2.saldo['brl'])
pass


i = 0
while i<5000:
    corretora_obj.book.obter_ordem_book_por_indice('xrp','brl',0,True,True) 
    #corretora_obj2.atualizar_saldo() 
    i+=1
    print('#{}'.format(i))
    print(corretora_obj.book.preco_compra_segundo_na_fila)
    #print(corretora_obj2.saldo['brl'])
pass

