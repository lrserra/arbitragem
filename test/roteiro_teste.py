from uteis.corretora import Corretora
from uteis.ordem import Ordem
from uteis.util import Util

# 1 ---------- TESTE DE ORDENS LIMITADAS ----------#

# 1.1 ORDEM COMPRA: ENVIAR ORDEM DE COMPRA LIMITADA PARA TODAS AS MOEDAS DIVIDINDO O PREÇO POR 2 (UTILIZAR QUANTIDADE MÍNIMA)
# 1.1.0 ORDEM VENDA: ENVIAR ORDEM DE VENDA LIMITADA PARA TODAS AS MOEDAS MULTIPLICANDO O PREÇO POR 2 (UTILIZAR PREÇO MÍNIMO)

# 1.1.1 OBTENDO LISTA DE MOEDAS
lista_de_moedas = Util.obter_lista_de_moedas()

# 1.1.2 OBTENDO AS CORRETORAS DE MAIOR E MENOR LIQUIDEZ PARAMETRIZADAS
corretora_mais_liquida = Util.obter_corretora_de_maior_liquidez()
corretora_menos_liquida = Util.obter_corretora_de_menor_liquidez()

CorretoraMaisLiquida = Corretora(corretora_mais_liquida)
CorretoraMenosLiquida = Corretora(corretora_menos_liquida)

# 1.1.3 CRIAÇÃO DA ORDEM LIMITADA DE COMPRA E VENDA

for moeda in lista_de_moedas:
    # 1.1.4 COMPRA
    ordem_compra_limitada = Ordem()
    
    preco = Util.retorna_menor_valor_compra(moeda)
    quantidade = Util.retorna_menor_quantidade_venda(moeda)

    ordem_compra_limitada.quantidade_enviada = 1
    ordem_compra_limitada.preco_enviado = preco / 2
    ordem_compra_limitada.tipo_ordem = 'limit'

    retorno_ordem_compra_corretora_mais_liquida = CorretoraMaisLiquida.enviar_ordem_compra(ordem_compra_limitada, moeda)
    retorno_ordem_compra_corretora_menos_liquida = CorretoraMenosLiquida.enviar_ordem_compra(ordem_compra_limitada, moeda)

    if retorno_ordem_compra_corretora_mais_liquida.id != 0:
        print("1.1.4: INSERIR ORDEM LIMITADA DE COMPRA DO ATIVO {} NA CORRETORA {}: OK".format(moeda.upper(), CorretoraMaisLiquida.nome))    
    else:
        print("1.1.4: INSERIR ORDEM LIMITADA DE COMPRA DO ATIVO {} NA CORRETORA {}: NOT OK".format(moeda.upper(), CorretoraMaisLiquida.nome))

    if retorno_ordem_compra_corretora_menos_liquida.id != 0:
        print("1.1.4: INSERIR ORDEM LIMITADA DE COMPRA DO ATIVO {} NA CORRETORA {}: OK".format(moeda.upper(), CorretoraMenosLiquida.nome))    
    else:
        print("1.1.4: INSERIR ORDEM LIMITADA DE COMPRA DO ATIVO {} NA CORRETORA {}: NOT OK".format(moeda.upper(), CorretoraMenosLiquida.nome))    

    # 1.1.5 VENDA
    ordem_venda_limitada = Ordem()

    ordem_venda_limitada.quantidade_enviada = quantidade
    ordem_venda_limitada.preco_enviado = preco * 100000
    ordem_venda_limitada.tipo_ordem = 'limit'
    
    retorno_ordem_venda_corretora_mais_liquida = CorretoraMaisLiquida.enviar_ordem_venda(ordem_venda_limitada, moeda)
    retorno_ordem_venda_corretora_menos_liquida = CorretoraMenosLiquida.enviar_ordem_venda(ordem_venda_limitada, moeda)

    if retorno_ordem_venda_corretora_mais_liquida.id != 0:
        print("1.1.5: INSERIR ORDEM LIMITADA DE VENDA DO ATIVO {} NA CORRETORA {}: OK".format(moeda.upper(), CorretoraMaisLiquida.nome))    
    else:
        print("1.1.5: INSERIR ORDEM LIMITADA DE VENDA DO ATIVO {} NA CORRETORA {}: NOT OK".format(moeda.upper(), CorretoraMaisLiquida.nome))    
    
    if retorno_ordem_venda_corretora_menos_liquida.id != 0:
        print("1.1.5: INSERIR ORDEM LIMITADA DE VENDA DO ATIVO {} NA CORRETORA {}: OK".format(moeda.upper(), CorretoraMenosLiquida.nome))    
    else:
        print("1.1.5: INSERIR ORDEM LIMITADA DE VENDA DO ATIVO {} NA CORRETORA {}: NOT OK".format(moeda.upper(), CorretoraMenosLiquida.nome))    

    # 1.1.6 CANCELAR TODAS AS ORDENS DE COMPRA E VENDA INSERIDAS PARA A MOEDA EM QUESTÃO
    CorretoraMaisLiquida.cancelar_todas_ordens(moeda)
    CorretoraMenosLiquida.cancelar_todas_ordens(moeda)

