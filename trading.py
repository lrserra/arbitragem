import json
import requests
from uteis.googleSheets import GoogleSheets
from uteis.corretora import Corretora
from uteis.ordem import Ordem
from datetime import datetime
import time

GoogleSheets().escrever_saldo(['saldo', 20])
GoogleSheets().escrever_operacao(['operacao', 20])


