from datetime import datetime
import os
from uteis.googleSheets import GoogleSheets
 
#GoogleSheets().limpa_operacoes()
GoogleSheets().limpa_saldo()

directory_path = os.getcwd() #pega diretorio raiz
foldername = 'log_backup_'+datetime.now().strftime('%Y%m%d')

root_folder = directory_path+'//Logs//'
if not os.path.isdir(root_folder):
    os.mkdir(root_folder) #cria diretorio se nao existe

destination_folder = root_folder+foldername
if not os.path.isdir(destination_folder):
    os.mkdir(destination_folder) #cria diretorio se nao existe

#lista arquivos que vamos copiar
list_of_files = os.listdir(directory_path)
list_of_logs = [file for file in list_of_files if file.endswith('log')]
list_of_texts = [file for file in list_of_files if file.endswith('txt')]

for file_name in list_of_logs + list_of_texts:
    os.replace(directory_path+'//'+file_name,destination_folder+'//'+file_name)
     

