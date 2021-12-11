import json
import logging, datetime
from uteis.googleSheets import GoogleSheets
from uteis.util import Util

class Configuracao:

    def atualizar_worksheet_settings():
        try:

            # Obter a lista moedas em operação
            white_list = Util.obter_white_list()

            # Abrir o arquivo de configuração para uso
            arquivo = open("worksheetsettings.json", "r")
            conteudo = json.load(arquivo) # Carrega os dados do Json

            # Obter quantidades de moedas da planilha
            quantidade_moeda = GoogleSheets().ler_quantidade_moeda()
            quantidade_minima_compra, quantidade_minima_venda = GoogleSheets().ler_minimo_negociacao()
            arbitragem_status = GoogleSheets().ler_status_arbitragem()
            leilao_status = GoogleSheets().ler_status_leilao()
            zeragem_status = GoogleSheets().ler_status_zeragem()

            # Manipulação do arquivo atualizando as paradas conforme planilha
            for moeda in white_list:
                conteudo[moeda]['saldo_inicial'] = quantidade_moeda[moeda]
                logging.warning('Configuracao: Saldo inicial da moeda {}: {}'.format(moeda, quantidade_moeda[moeda]))
                conteudo[moeda]['valor_minimo_compra'] = quantidade_minima_compra[moeda]
                logging.warning('Configuracao: Qtd minima compra da moeda {}: {}'.format(moeda, quantidade_minima_compra[moeda]))
                conteudo[moeda]['quantidade_minima_venda'] = quantidade_minima_venda[moeda]
                logging.warning('Configuracao: Qtd minima venda da moeda {}: {}'.format(moeda, quantidade_minima_venda[moeda]))
                conteudo[moeda]['arbitragem_status'] = arbitragem_status[moeda]
                logging.warning('Configuracao: arbitragem {} para a moeda {}'.format(arbitragem_status[moeda],moeda))
                conteudo[moeda]['leilao_status'] = leilao_status[moeda]
                logging.warning('Configuracao: leilao {} para a moeda {}'.format(leilao_status[moeda],moeda))
                conteudo[moeda]['zeragem_status'] = zeragem_status[moeda]
                logging.warning('Configuracao: zeragem {} para a moeda {}'.format(zeragem_status[moeda],moeda))

            arquivo.close() # Fecha o arquivo que estava aberto como somente leitura

            arquivo = open("worksheetsettings.json", "w") # Sobrescreve o arquivo
            json.dump(conteudo, arquivo) # Salva o Json no arquivo
            arquivo.close() # Fecha o arquivo

            logging.warning('Configuracao: Todas paradas atualizadas com sucesso.')
        except Exception as erro:
            logging.error(Util.descricao_erro_padrao().format('atualizar_quantidades_moedas', 'N/A', erro))


if __name__ == "__main__":
    import logging, time
    from configuracao import Configuracao

    logging.basicConfig(filename='Configuracao.log', level=logging.INFO,
                        format='[%(asctime)s][%(levelname)s][%(message)s]')
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    logging.getLogger().addHandler(console)

    GoogleSheets().limpa_saldo()
    GoogleSheets().limpa_operacoes()
    
    while True:
        Configuracao.atualizar_worksheet_settings()
        time.sleep(5*60)


