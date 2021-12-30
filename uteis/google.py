import sys,os,time
from datetime import datetime,timedelta

root_path = os.getcwd()
sys.path.append(root_path)

from uteis.settings import Settings
from uteis.logger import Logger
from uteis.converters import Converters

class Google:
    def __init__(self):
        self.settings = Settings()
        self.google = self.settings.retorna_google_client()

    def ler(self, planilha, aba, descricao_range):
        '''
        retorna um range especifico de uma planilha do google sheets
        '''
        try:
            sheet = self.google.open(planilha).worksheet(aba)
            data = sheet.get(descricao_range)
            return data

        except Exception as erro:
            Logger.loga_erro('ler','Google',erro)

    def atualiza_strategy_settings(self,planilha,instance_rasp):
        '''
        atualiza o json strategy
        '''
        try:
            strategy_json = {}
            strategy_settings = self.ler(planilha,'settings','settings_strategy')
            header = strategy_settings[0]
            for linha in strategy_settings[1:]:
                instance_strategy = int(linha[0])
                strategy = linha[1]
                if instance_strategy == instance_rasp:
                    strategy_json[strategy]={}
                    for campo in header[2:]:
                        strategy_json[strategy][campo]=linha[header.index(campo)]
                
            self.settings.salva_json(strategy_json,'strategy')

        except Exception as erro:
            Logger.loga_erro('atualiza_app_settings','Google',erro)

    def atualiza_app_settings(self,planilha):
        '''
        atualiza o json app
        '''
        try:
            app_json = {}
            app_settings = self.ler(planilha,'settings','settings_app')
            header = app_settings[0]
            for linha in app_settings[1:]:
                instance = int(linha[0])
                app_json[instance]={}
                for campo in header[1:]:
                    app_json[instance][campo]=linha[header.index(campo)]
            
            self.settings.salva_json(app_json,'app')

        except Exception as erro:
            Logger.loga_erro('atualiza_app_settings','Google',erro)
        
    def atualiza_broker_settings(self,planilha):
        '''
        atualiza o json de brokers
        '''
        try:
            broker_json = {}
            broker_settings = self.ler(planilha,'settings','settings_broker')
            header = broker_settings[0]
            for corretora in header[1:]:
                broker_json[corretora]={}
                for linha in broker_settings[1:]:
                    campo = linha[0]
                    broker_json[corretora][campo] = linha[header.index(corretora)]

            self.settings.salva_json(broker_json,'broker')

        except Exception as erro:
            Logger.loga_erro('atualiza_broker_settings','Google',erro)
    
    def comprime_position(self,planilha):
        '''
        comprime linhas da planilha na aba position
        '''
        try:
            sheet = self.google.open(planilha).worksheet('position')
            data = sheet.col_values(1)
            linhas_a_deletar = []
            today_date = datetime.now()
            for row in data:
                current_index = data.index(row)
                if row.find('/')!=-1 and current_index<len(data)-1:
                    
                    current_date = datetime.strptime(row, '%m/%d/%Y %H:%M:%S')
                    next_date = datetime.strptime(data[current_index+1], '%m/%d/%Y %H:%M:%S') if data[current_index+1].find('/')!=-1 else 0
                    
                    if next_date !=0:
                        if current_date.day==today_date.day and current_date.month == today_date.month and current_date.year == today_date.year:
                            pass #hj nao apaga
                        else:
                            if next_date.day == current_date.day:
                                linhas_a_deletar.append([current_index+1,current_date]) #vamos deixar só ultimo de cada dia

            for linha_a_deletar in reversed(linhas_a_deletar):
                Logger.loga_info('deletando a linha {} com data {}'.format(linha_a_deletar[0],linha_a_deletar[1]))
                time.sleep(1)
                sheet.delete_row(linha_a_deletar[0])
       
            linhas_a_excluir = []
            todos_dados = sheet.get_all_records()#da uma ultima limada nas linhas vazias, pra deixar bonitinho
            for linha in todos_dados:
                linha['ROW'] = todos_dados.index(linha)+2
                if linha['DATA'] == '':
                    linhas_a_excluir.append(linha['ROW'])
            for linha_a_deletar in reversed(linhas_a_excluir): #da uma primeira limada
                Logger.loga_info('deletando a linha vazia {}'.format(linha_a_deletar))
                time.sleep(1)
                sheet.delete_row(linha_a_deletar)

        except Exception as erro:
            Logger.loga_erro('comprime_position','Google',erro)

    def comprime_spot(self,planilha):
        '''
        comprime linhas da planilha na aba spot
        '''
        try:
            sheet = self.google.open(planilha).worksheet('spot')
            todos_dados = sheet.get_all_records()
            
            today_date = datetime.now()
            today_minus_30_date = today_date - timedelta(days=30)

            compressao_diaria =[]
            linhas_a_excluir = []
            linhas_a_adicionar = []

            for linha in todos_dados:
                linha['ROW'] = todos_dados.index(linha)+2
                linha['PNL'] = Converters.string_para_float(linha['PNL'])
                linha['FINANCEIRO'] = Converters.string_para_float(linha['FINANCEIRO'])
                if linha['DATA'] == '' or linha['FINANCEIRO']==0 or abs(linha['PNL']/linha['FINANCEIRO'])>0.4:
                    linhas_a_excluir.append(linha['ROW'])
            for linha_a_deletar in reversed(linhas_a_excluir): #da uma primeira limada
                Logger.loga_warning('deletando a linha vazia {}'.format(linha_a_deletar))
                time.sleep(1)
                sheet.delete_row(linha_a_deletar)

            linhas_a_excluir = []
            todos_dados = sheet.get_all_records()
            today_date = datetime.now()
            for linha in todos_dados:
                linha['DATA'] = datetime.strptime(linha['DATA'], '%m/%d/%Y %H:%M:%S')
                linha['ROW'] = todos_dados.index(linha)+2
                linha['PNL'] = Converters.string_para_float(linha['PNL'])
                linha['FINANCEIRO'] = Converters.string_para_float(linha['FINANCEIRO'])
                linha['QUANTIDADE'] = Converters.string_para_float(linha['QUANTIDADE'])
                linha['PRECO'] = Converters.string_para_float(linha['PRECO'])
                linha['PRECO ESTIMADO'] = Converters.string_para_float(linha['PRECO ESTIMADO'])
                linha['PNL ESTIMADO'] = Converters.string_para_float(linha['PNL ESTIMADO'])
                linha['TAXA CORRETAGEM'] = Converters.string_para_float(linha['TAXA CORRETAGEM'])
                linha['FINANCEIRO CORRETAGEM'] = Converters.string_para_float(linha['FINANCEIRO CORRETAGEM'])
                linha['FALTOU MOEDA'] = Converters.string_para_float(linha['FALTOU MOEDA'])
                if linha['DATA'] > today_minus_30_date and linha['DATA'].day != today_date.day:
                    compressao_diaria.append(linha)
            
            for linha in compressao_diaria:
                trades_a_comprimir_nesse_dia = [row for row in compressao_diaria if row['DATA'].day==linha['DATA'].day and row['DATA'].month==linha['DATA'].month]
                corretoras = list(set([row['CORRETORA'] for row in trades_a_comprimir_nesse_dia if row['CORRETORA']!='']))
                estrategias = list(set([row['ESTRATEGIA'] for row in trades_a_comprimir_nesse_dia]))
                moedas = list(set([row['MOEDA'] for row in trades_a_comprimir_nesse_dia]))
                direcoes = list(set([row['DIREÇÃO'] for row in trades_a_comprimir_nesse_dia]))
                
                for corretora in corretoras:
                    for estrategia in estrategias:
                        for moeda in moedas:
                            for direcao in direcoes:
                                #cria trade comprimido e escreve
                                compressed_trade = []
                                trades_a_comprimir = [trade for trade in trades_a_comprimir_nesse_dia if trade['CORRETORA'] == corretora and trade['MOEDA']==moeda and trade['ESTRATEGIA']==estrategia and trade['DIREÇÃO'] == direcao]

                                if len(trades_a_comprimir)>1:
                                    data = trades_a_comprimir[0]['DATA']
                                    trade_id = trades_a_comprimir[0]['ID']
                                    precos = [row['PRECO'] for row in trades_a_comprimir]
                                    preco = sum(precos)/len(precos)
                                    quantidade = sum([row['QUANTIDADE'] for row in trades_a_comprimir])
                                    financeiro = sum([row['FINANCEIRO'] for row in trades_a_comprimir])
                                    pnl = sum([row['PNL'] for row in trades_a_comprimir])
                                    precos_estimados = [row['PRECO ESTIMADO'] for row in trades_a_comprimir]
                                    preco_estimado = sum(precos_estimados)/len(precos_estimados)
                                    pnl_estimado = sum([row['PNL ESTIMADO'] for row in trades_a_comprimir])
                                    taxas_corretagem = [row['TAXA CORRETAGEM'] for row in trades_a_comprimir]
                                    taxa_corretagem = sum(taxas_corretagem)/len(taxas_corretagem)
                                    financeiro_corretagem = sum([row['FINANCEIRO CORRETAGEM'] for row in trades_a_comprimir])
                                    faltaram_moedas = [row['FALTOU MOEDA'] for row in trades_a_comprimir]
                                    faltou_moeda = sum(faltaram_moedas)/len(faltaram_moedas)

                                    compressed_trade.append(Converters.datetime_para_excel_date(data))
                                    compressed_trade.append(trade_id)
                                    compressed_trade.append(estrategia)
                                    compressed_trade.append(moeda)
                                    compressed_trade.append(corretora)
                                    compressed_trade.append(direcao)
                                    compressed_trade.append(preco)
                                    compressed_trade.append(quantidade)
                                    compressed_trade.append(financeiro)
                                    compressed_trade.append(pnl)
                                    compressed_trade.append(preco_estimado)
                                    compressed_trade.append(pnl_estimado)
                                    compressed_trade.append(taxa_corretagem)
                                    compressed_trade.append(financeiro_corretagem)
                                    compressed_trade.append(faltou_moeda)
                                    compressed_trade.append(True)

                                    linhas_a_adicionar.append(compressed_trade)
                                    linhas_a_excluir = linhas_a_excluir + [linha['ROW'] for linha in trades_a_comprimir]
                                    
                for trade in trades_a_comprimir_nesse_dia:
                    #remove da lista de compressao diaria, todos ja foram comprimidos quando necessario
                    compressao_diaria.remove(trade)
        
        except Exception as erro:
            Logger.loga_erro('comprime_spot','Google',erro)

        
        Logger.loga_warning('(linhas a deletar / linhas a adicionar), ({}/{})'.format(len(linhas_a_excluir),len(linhas_a_adicionar)))
        i = 1
        for linha_a_excluir in reversed(sorted(linhas_a_excluir)):
            Logger.loga_info('deletando a linha {} da planilha, ({}/{})'.format(linha_a_excluir,i,len(linhas_a_excluir)))
            time.sleep(1)
            try:
                sheet.delete_row(linha_a_excluir)
            except Exception as erro:
                Logger.loga_erro('delete_row - comprime_spot','Google',erro)
            i+=1
        i = 1
        time.sleep(151) if len(linhas_a_excluir)>0 else time.sleep(1)#para o api do google continuar de graça
        for linha_a_adicionar in linhas_a_adicionar:
            Logger.loga_info('adicionando uma linha comprimida id {}, ({}/{})'.format(linha_a_adicionar[1],i,len(linhas_a_adicionar)))
            time.sleep(3)
            try:
                sheet.insert_row(linha_a_adicionar, sorted(linhas_a_excluir)[0]+1, value_input_option='USER_ENTERED')
            except Exception as erro:
                Logger.loga_erro('insert_row - comprime_spot','Google',erro)
            i+=1

        linhas_a_excluir = []
        todos_dados = sheet.get_all_records()#da uma ultima limada nas linhas vazias, pra deixar bonitinho
        for linha in todos_dados:
            linha['ROW'] = todos_dados.index(linha)+2
            linha['PNL'] = Converters.string_para_float(linha['PNL'])
            linha['FINANCEIRO'] = Converters.string_para_float(linha['FINANCEIRO'])
            if linha['DATA'] == '' or linha['FINANCEIRO']==0 or abs(linha['PNL']/linha['FINANCEIRO'])>0.4:
                linhas_a_excluir.append(linha['ROW'])
        for linha_a_deletar in reversed(linhas_a_excluir):
            Logger.loga_info('deletando a linha vazia {}'.format(linha_a_deletar))
            time.sleep(1)
            sheet.delete_row(linha_a_deletar)












