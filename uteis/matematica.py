
import sys,os, math
root_path = os.getcwd()
sys.path.append(root_path)

from datetime import datetime
from uteis.settings import Settings
from uteis.converters import Converters

class Matematica:
    def __init__(self):
        self.numero_magico = (171 - datetime.now().day)/1000
        self.settings_client = Settings()

    def trunca(self,qtd,moeda='',corretora=''):
        '''
        trunca de acordo com o padrão da corretora escolhida
        '''
        if moeda=='' or corretora =='':
            return math.trunc(qtd)
        else:
            regra_trunc = self.settings_client.retorna_campo_de_json('broker',corretora,'truncate')
            dic_trunc = Converters.string_para_dicionario(regra_trunc,'#')
            casa_trunc = float(dic_trunc[moeda])
            return math.trunc(qtd*10**casa_trunc)/10**casa_trunc

    def adiciona_numero_magico(self,qtd,moeda='',corretora=''):
        '''
        trunca e depois adiciona um numero magico
        '''
        if moeda=='' or corretora =='':
            return self.trunca(qtd) + self.numero_magico
        else:
            regra_trunc = self.settings_client.retorna_campo_de_json('broker',corretora,'truncate')
            dic_trunc = Converters.string_para_dicionario(regra_trunc,'#')
            casa_trunc = float(dic_trunc[moeda])
            return self.trunca(qtd,moeda,corretora) + (1/10**casa_trunc)*self.numero_magico

    def tem_numero_magico(self,qtd):
        '''
        verifica se o numero tem a marca do numero magico
        '''
        return str(qtd)[-3:]==str(self.numero_magico)
  

