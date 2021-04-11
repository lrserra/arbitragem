import json
import requests
from uteis.util import Util
from uteis.corretora import Corretora
from uteis.ordem import Ordem
from datetime import datetime
import time


corretoraMercadoBTC = Corretora('Novadax')
print(corretoraMercadoBTC.atualizar_saldo())
