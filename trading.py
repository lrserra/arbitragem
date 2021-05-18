import json
import requests
from uteis.googleSheets import GoogleSheets
from uteis.corretora import Corretora
from uteis.ordem import Ordem
from datetime import datetime, timezone
import time

print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

corretora = 'BrasilBitcoin'

retorno = Corretora(corretora).obter_todas_ordens_abertas()
pass





