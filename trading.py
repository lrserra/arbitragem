import json
import requests
from uteis.util import Util
from uteis.corretora import Corretora
from uteis.ordem import Ordem
from datetime import datetime
import time

saldo = {}
for moeda in Util.obter_lista_de_moedas():
    saldo[moeda] = 0

print(saldo)
