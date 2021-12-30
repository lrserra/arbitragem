from datetime import datetime

class Converters:

    def string_para_float(number):
        
        try:
            return float(number) if number != '' else ''

        except Exception as err:
            
            import locale
            point = locale.localeconv()['decimal_point']
            sep = locale.localeconv()['thousands_sep']
            if point == ',':
                return locale.atof(number.replace(' ', sep).replace('.', sep))
            elif point == '.':
                return locale.atof(number.replace(' ', sep).replace(',', sep))
            else:
                return number
    
    def datetime_para_excel_date(date1):
        temp = datetime(1899, 12, 30)    # Note, not 31st Dec but 30th!
        delta = date1 - temp
        return float(delta.days) + (float(delta.seconds) / 86400)

    def string_para_dicionario(texto,delim):
        '''
        pega string com delimitador e retorna dicionario equivalente
        '''
        lista = texto.split(delim)
        dici = dict()

        for item in lista:
            res = item.split(':')
            dici[res[0]] = res[1]
        return dici
    
    def dicionario_simples_para_string(dicionario={},separador='#'):
        '''
        converte um dicionario para uma string
        '''
        string_final = ''
        for chave in dicionario.keys():
            string_final += separador+ chave + ':' + str(dicionario[chave])
        return string_final
    
    def dicionario_duplo_para_string(dicionario={},separador_principal='#',separador_secundario='//'):
        '''
        converte um dicionario para uma string
        '''
        string_final = ''
        for chave_principal in dicionario.keys():
            string_final += separador_principal + chave_principal
            for chave_secundaria in dicionario[chave_principal].keys():
                string_final += separador_secundario+ chave_secundaria + ':' + str(dicionario[chave_principal][chave_secundaria])
        return string_final
