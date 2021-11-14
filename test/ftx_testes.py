import sys, os

sys.path.append(os.getcwd())

from requests import Request
from uteis.util import Util
from corretoras.ftx import FtxClient

config = Util.obterCredenciais()
corretora_obj = FtxClient(config["FTX"]["Authentication"],config["FTX"]["Secret"])
retorno_account = corretora_obj.get_account_info()
print(retorno_account)

   




