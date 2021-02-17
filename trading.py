import json
import requests
from util import Util
from corretora import Corretora

nova_dax = Corretora('Novadax', 'btc')
nova_dax.carregar_ordem_books()

print(nova_dax.book)
