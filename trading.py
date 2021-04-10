import json
import requests
from uteis.util import Util
from uteis.corretora import Corretora
from uteis.ordem import Ordem
from datetime import datetime
import time


corretora_mais_liquida = Util.obter_corretora_de_maior_liquidez()
corretora_menos_liquida = Util.obter_corretora_de_menor_liquidez()

CorretoraMaisLiquida = Corretora(corretora_mais_liquida)
CorretoraMenosLiquida = Corretora(corretora_menos_liquida)

CorretoraMaisLiquida.cancelar_todas_ordens('xrp')
CorretoraMenosLiquida.cancelar_todas_ordens('xrp')