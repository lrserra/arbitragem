from corretora import Corretora

fileHandle = open(r'Z:\leilao\Saldo.txt', 'r')

pnl = 0
saldo_inicial ={}
saldo_final ={}

for line in fileHandle:
    fields = line.split('|')
    
    if fields[0] != 'MOEDA':
        if fields[0] not in saldo_inicial.keys():
            saldo_inicial[fields[0]] = float(fields[1])

        saldo_final[fields[0]] = float(fields[1])
    
fileHandle.close()

pnl_total = 0

for moeda in saldo_final.keys():
    pnl_em_cripto = round(saldo_final[moeda]-saldo_inicial[moeda],3)
    if moeda != 'BRL':
        pnl_em_reais = pnl_em_cripto*Corretora('MercadoBitcoin', moeda).ordem.preco_venda
    else:
        pnl_em_reais = pnl_em_cripto
    pnl_total += pnl_em_reais
    print('Pnl de {} é de {} reais'.format(moeda.upper(),pnl_em_reais))

print('------------------------')
print('Pnl TOTAL é de {} reais'.format(pnl_total))

#-------------------------------------------------------------#

#saldo
#calcula pnl
fileHandle = open(r'Z:\arb\Operacoes.txt', 'r')

pnl_arbitragem = {}

for line in fileHandle:
    fields = line.split('|')
    
    if fields[0] != 'MOEDA':
        if fields[0] not in pnl_arbitragem.keys():
            pnl_arbitragem[fields[0]] = float(fields[5])
        else:
            pnl_arbitragem[fields[0]] += float(fields[5])
    
fileHandle.close()

fileHandle = open(r'Y:\leilao\Operacoes.txt', 'r')

pnl_leilao = {}

for line in fileHandle:
    fields = line.split('|')
    
    if fields[0] != 'MOEDA':
        if fields[0] not in pnl_leilao.keys():
            pnl_leilao[fields[0]] = float(fields[6])
        else:
            pnl_leilao[fields[0]] += float(fields[6])
    
fileHandle.close()

pnl_total = 0

for moeda in pnl_leilao.keys():
    pnl_da_cripto = round(pnl_leilao[moeda]+pnl_arbitragem[moeda],2)
    pnl_total += pnl_da_cripto
    print('Pnl de {} de Leilao é de {} reais'.format(moeda.upper(),round(pnl_leilao[moeda],2)))
    print('Pnl de {} de Arbitragem é de {} reais'.format(moeda.upper(),round(pnl_arbitragem[moeda],2)))

print('------------------------')
print('Pnl TOTAL é de {} reais'.format(round(pnl_total,2)))