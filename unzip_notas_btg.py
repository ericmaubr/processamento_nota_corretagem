# Projeto: Processamento Notas de Corretagem
#
# Copyright (C) Eric Daniel Mauricio
# Author: Eric Daniel Mauricio
# URL: <https://www.linkedin.com/in/ericmau/>

"""
    Processa o arquivo .zip de corretagem da Empiricus Investimentos/Vitreo e BTG.
    Coloca todos os arquivos num mesmo diretório para facilitar o controle e envio para a calculadora de IR.
    Extrai apenas os arquivos que terminam com _ALL.pdf. Desta maneira, ignora os arquivos SUMMARY.
    Utiliza como número da conta o texto que aparece antes do primeiro _ (underscore).
    Ajuda a organizar as notas para quem gerencia várias contas na Empiricus/BTG.
 
    Argumentos:
 
    -zip: arquivo .zip da corretora a ser processado
    -dir: diretório destino base onde será criado o diretório de mapeamento e consequentemente, onde os arquivos serão armazenados
    -map: arquivo de mapeamento da conta em diretório e prefixo dos arquivos destinos. Por padrão, busca no diretório corrente o arquivo map_conta.txt
 
    O formato do arquivo de mapeamento é:
    <conta> <diretório_destino> <prefixo>
 
    As linhas iniciadas por # são ignoradas.
 
    Exemplo de arquivo de mapeamento:
    # formato
    # conta diretorio prefixo_arquivo
    001234756 btg_john john

    Exemplo de execução: python unzip_notas_vitreo.py -zip "c:\notas_corretagem\notas_hoje.zip" -dir "c:\notas_corretagem\202309" 

    Nesse caso, o programa processará o arquivo c:\notas_corretagem\notas_hoje.zip e criará o diretório c:\notas_corretagem\202309 (caso não exista).
    Dentro do .zip, procurará pelos arquivos _ALL.pdf.
    Move esses arquivos para c:\notas_corretagem\202309\btg_jonh com o prefixo john.
    Por exemplo, criará um arquivo c:\notas_corretagem\202309\btg_john\john_001234756_20230901_20230916_BMF_ALL.pdf se
    houver um arquivo 001234756_20230901_20230916_BMF_ALL.pdf no .zip.
"""

from zipfile import ZipFile
import sys
import os

def cria_dir_unzip_files(dest_dir: str, zip_file: str, map_conta:dict):
    """
        Processa o arquivo .zip com as notas de corretagem, movendo os arquivos para o destino informado, com o prefixo definido.
        
        Args:
        dest_dir : str
                Diretório destino base onde os arquivos serão extraídos. 
                Vale lembrar que será criado um sub-diretório, baseado no arquivo de mapeamento.
                É nesse último diretório que arquivos estarão.
            zip_file : str 
                Arquivos de corretagem no formato .zip
            map_conta : dict 
                Mapeamento criado através da função processa_mapeamento
    """

    # verificar se o arquivo .zip existe
    if not os.path.isfile(zip_file):
        print(f"Erro: arquivo {zip_file} não encontrado.")
        return

    # cria o diretorio destino se ele não existir
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    # para evitar que o programa processasse outros arquivos do diretório que não os zipados
    # guardo os arquivos que preciso processar e os diretório que irei remover
    # os diretório a serem removidos são os criados pela extração do .zip
    # esses diretórios estarão vazios, uma vez que os arquivos serão movidos para o mesmo diretório destino
    
    files_to_process = []
    dirs_to_remove = set()

    # abre o arquivo .zip
    with ZipFile(zip_file, 'r') as zip:

        # para cada arquivo dentro do .zip faz:
        # extrai o conteúdo se o arquivo terminar em _all.pdf em dest_dir
        for file in zip.namelist():
    
##            print(f"DEBUG: ** analisando arquivo {file}")
    
            if file.lower().endswith("_all.pdf"):
                zip.extract(file, dest_dir)
                arquivo_caminho_completo = os.path.join(dest_dir, file)
                files_to_process.append(arquivo_caminho_completo)
                dirs_to_remove.add(os.path.dirname(arquivo_caminho_completo))
                
    
    # para cada arquivo extraído em files_to_process faz:
    # 1. identifica de qual conta é o arquivo (a conta está no primeiro bloco do split com separador _)
    # 2. busca no map o diretório (posição 0 da lista do mapeamento)
    # 3. busca no map o prefixo a ser inserido do arquivo (posição 1 da lista do mapeamento)
    # 4. verifica se existe o diretório destino para onde os arquivos serão movido (dest_dir + dir_conta)
    # 5. move os arquivos para o destino, adicionando o prefixo
   
    
    for file in files_to_process:
        
        filename = os.path.basename(file)   
        filename_split = filename.split("_")
        
        dir_conta = map_conta[filename_split[0]][0]
        prefixo_arq = map_conta[filename_split[0]][1]
        
        diret_conta_dest = os.path.join(dest_dir, dir_conta)
        if not os.path.exists(diret_conta_dest):
            os.mkdir(diret_conta_dest)
        
        origem = os.path.join(dest_dir, file)
        destino = os.path.join(diret_conta_dest, f"{prefixo_arq}_{filename}")
        
#        print(f'DEBUG: movendo {origem} para {destino}')
        try:
            os.rename(origem, destino)
        except FileExistsError as e:
            print(f"** Erro: Não é possível copiar o arquivo: \n{origem}\n pois \n{destino}\n já existe.")
         
       
    # 6. remove o diretório onde os arquivos estavam     
    for dir in dirs_to_remove:
        try:
#            print(f"DEBUG ** removendo diretório {dir}")
            os.rmdir(dir)
        except Exception as e:
            pass   


    
def processa_mapeamento(arquivo_map_conta: str)->dict:
    """
        Mapeia o arquivo passado como parâmetro num dicionário.
        O dicionário tem como chave o número da conta e como valores uma lista contendo na 
          primeira posição o diretório e 
          na segunda posição o prefixo a ser adicionado no arquivo
        
        Args:
            arquivo_map_conta : str
                Arquivo com o mapeamento a ser utilizado
        
        Returns : dict
            Dicionário com o mapeamento
        
    """

    mapeamento = {}

#    print("DEBUG ** Processando mapeamento das contas")

    if not os.path.isfile(arquivo_map_conta):
        print(f"Erro: arquivo {arquivo_map_conta} não encontrado.")
        return

    with open(arquivo_map_conta, 'r') as f:
    
        for linha in f:       
#            print(f"DEBUG *** linha: {linha}")
        
            if not linha.startswith("#"):
                linha_lista = linha.split()               
                mapeamento[linha_lista[0]] = [linha_lista[1], linha_lista[2]]
    
    return mapeamento

def main():


    args = sys.argv[1:]
    
    arquivo_zip = None
    dest_dir = None
    arquivo_map_conta = None
    
#processa parâmetros da command line	
    for i, arg in enumerate(args):
        if arg == '-zip':
            arquivo_zip = args[i+1]
        elif arg == '-dir':
            dest_dir = args[i+1]
        elif arg == '-map':
            arquivo_map_conta = args[i+1]


    if not arquivo_zip:
        print("Parâmetro -zip é obrigatório")
        return
        
    if not dest_dir:
        print("Parâmetro -dir é obrigatório")
        return

    if not arquivo_map_conta:
        arquivo_map_conta = "map_conta.txt"

    map_conta = processa_mapeamento(arquivo_map_conta)
#    print(f"map_conta:\n{map_conta}")

    cria_dir_unzip_files(dest_dir, arquivo_zip, map_conta)

    print("Processamento concluído.")

if __name__ == "__main__":
    main()


  