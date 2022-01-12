
from datetime import datetime
import logging

class Logger:

    def cria_arquivo_log(arquivo):
        '''
        cria um arquivo com os logs
        '''
        logging.basicConfig(filename=arquivo+'.log', level=logging.INFO,
                            format='[%(asctime)s][%(levelname)s][%(message)s]')
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        logging.getLogger().addHandler(console)

    def loga_info(texto):
        '''
        adiciona uma linha no log com level info
        '''
        logging.info(texto)

    def loga_warning(texto):
        '''
        adiciona uma linha no log com level warning
        '''
        logging.warning(texto)

    def loga_erro(metodo,classe,erro,corretora=''):
        '''
        Retorna uma descrição de erro padrão podendo parametrizar o método, a corretora e a mensagem de erro.
        '''
        if corretora == '':
            texto_final = 'Método: {} Classe: {} Erro: {}.'.format(metodo,classe,erro)
        else:
            texto_final = 'Método: {} Classe: {} Corretora: {} Erro: {}.'.format(metodo,classe,corretora,erro)
        return logging.error(texto_final)

    def retorna_erros_objeto_exception(mensagem, erro):
        '''
        escrever todos os erros logado no objeto exception na sequencia
        '''
        retorno = mensagem + ' | '
        i=0
        
        while i < erro.args.__len__():
            if i == 0: 
                retorno += str(datetime.now()) + str(erro.args[i]) + ' | '
            else:
                retorno += str(erro.args[i]) + ' | '
                print(erro.args[i])
            i += 1
        
        return retorno
