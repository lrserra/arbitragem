import json
import logging
from uteis.googleSheets import GoogleSheets
from uteis.util import Util

class Configuracao:

    def atualizar_worksheet_settings():
        try:

            # Obter a lista moedas em operação
            white_list = Util.obter_lista_de_moedas()

            # Abrir o arquivo de configuração para uso
            arquivo = open("worksheetsettings.json", "r")
            conteudo = json.load(arquivo) # Carrega os dados do Json

            # Obter quantidades de moedas da planilha
            quantidade_moeda = GoogleSheets().ler_quantidade_moeda()
            quantidade_minima_compra, quantidade_minima_venda = GoogleSheets().ler_minimo_negociacao()

            # Manipulação do arquivo atualizando as quantidades conforme planilha
            for moeda in white_list:
                conteudo[moeda]['saldo_inicial'] = quantidade_moeda[moeda]
                logging.warning('Configuracao: Saldo inicial da moeda {}: {}'.format(moeda, quantidade_moeda[moeda]))
                conteudo[moeda]['valor_minima_compra'] = quantidade_minima_compra[moeda]
                logging.warning('Configuracao: Qtd minima compra da moeda {}: {}'.format(moeda, quantidade_minima_compra[moeda]))
                conteudo[moeda]['quantidade_minima_venda'] = quantidade_minima_venda[moeda]
                logging.warning('Configuracao: Qtd minima venda da moeda {}: {}'.format(moeda, quantidade_minima_venda[moeda]))

            arquivo.close() # Fecha o arquivo que estava aberto como somente leitura

            arquivo = open("worksheetsettings.json", "w") # Sobrescreve o arquivo
            json.dump(conteudo, arquivo) # Salva o Json no arquivo
            arquivo.close() # Fecha o arquivo

            logging.warning('Configuracao: Quantidades atualizadas com sucesso.')
        except Exception as erro:
            logging.error(Util.descricao_erro_padrao().format('atualizar_quantidades_moedas', 'N/A', erro))


if __name__ == "__main__":
    import logging
    from configuracao import Configuracao

    logging.basicConfig(filename='Configuracao.log', level=logging.INFO,
                        format='[%(asctime)s][%(levelname)s][%(message)s]')
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    logging.getLogger().addHandler(console)

    Configuracao.atualizar_worksheet_settings()

