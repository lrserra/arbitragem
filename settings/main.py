import json
import logging
import sys,os
root_path = os.getcwd()
sys.path.append(root_path)
from uteis.googleSheets import GoogleSheets
from uteis.util import Util
from atualiza import Settings

logging.basicConfig(filename='settings.log', level=logging.INFO,
                    format='[%(asctime)s][%(levelname)s][%(message)s]')
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
logging.getLogger().addHandler(console)


current_path = os.path.dirname(os.path.realpath(__file__))

planilha = Util.retorna_campo_de_json(current_path+"/rasp.json","sheet_name")
google_client = GoogleSheets()

Settings.atualiza_broker_settings(google_client,planilha,current_path)


