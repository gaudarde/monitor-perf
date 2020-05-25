import glob
import os
from datetime import datetime, timedelta
from time import sleep

import pandas as pd
import requests
import urllib3

"""setup: cria as pastas, os parâmetros do request e configurações gerais. 
Parâmetros da request.post criados com https://curl.trillworks.com/"""

if __name__ == '__main__':
    urllib3.disable_warnings()
    lista_de_pastas = ['arquivos_individuais', 'arquivos_combinados']

    def download():
        for pasta in lista_de_pastas:
            if not os.path.isdir(pasta):
                os.mkdir(pasta)

        arquivos_individuais = 'arquivos_individuais'  # Backup dos arquivos convertidos para csv

        headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://www.anp.gov.br',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Referer': 'https://www.anp.gov.br/SITE/extras/consulta_petroleo_derivados/exploracao/consultaExploPocosPerfurados/default.asp',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        r_url = 'https://www.anp.gov.br/SITE/extras/consulta_petroleo_derivados/exploracao/consultaExploPocosPerfurados/planilha.asp'

        """Cria a lista dos anos para o parâmetro data = {...} em download_list
        Teoricamente, é possível fazer fazer uma requisição com todos os dados
        mas extrapola os limites do servidor da ANP. Por organização, downloads
        são segmentados por ano"""

        # Todos os anos disponíveis na base da ANP
        download_list = list(range(1922, datetime.now().year + 1))

        # Remove os anos já baixados
        for x in [int(i.split(sep='.')[0].split('pocos')[1])
                  for i in glob.glob(f'{arquivos_individuais}/*.csv')]:
            download_list.remove(x)

        # Remove os anos em que não há dados
        for x in [1923, 1924, 1926, 1927, 1928, 1929, 1930, 1931, 1932, 1933, 1934, 1935, 1936]:
            download_list.remove(x)

        # Adiciona os anos obrigatórios (atualiza o ano passado e o ano atual)
        download_list.extend(range(datetime.now().year - 1, datetime.now().year + 1))

        # Remove anos duplicados
        download_list = list(dict.fromkeys(download_list))

        """Baixa os arquivos em formato html e converte para csv
        Os dados são exportados por meio de um script, que gera a planiha.xls.
        O código realiza a conversão de todos os arquivos para csv e mantém 
        um backup dos arquivos convertidos para consultas futuras."""

        # log
        print(f'{datetime.now()}\n'
              f' Baixando dados dos seguinte anos: \n'
              f'{download_list}')

        # Cria o parâmetro data_request para inserir os anos nos parâmetros da requisição
        for ano in download_list:
            data_request = {'Sim': 'Sim',
                            'txtDeOK': '01/01/{0}'.format(str(ano)),
                            'txtAteOK': '31/12/{0}'.format(str(ano)),
                            'txtBlocoOK': ''}

            """ Realiza a conexão, preservando a sessão cada vez que o código é 
            executado – s = requests.Session() – e insere os parâmetros na requisição
            – s.post() """

            s = requests.Session()
            r = s.post(r_url, headers=headers, data=data_request, verify=False, stream=True)

            # Baixa os arquivos no formato original (html)
            try:
                arquivo_html = f'{arquivos_individuais}/pocos{str(ano)}.html'
                with open(arquivo_html, 'wb') as output:
                    output.write(r.content)

                # Converte o arquivo html para csv
                df = pd.read_html(arquivo_html, decimal=',', encoding='latin1', thousands='.')[0]
                arquivo_csv0 = os.path.basename(arquivo_html).split('.')[0]
                arquivo_csv = f'{arquivo_csv0}.csv'
                df.to_csv(f'{arquivos_individuais}/{arquivo_csv}', index=False, header=False, encoding='latin1',
                          decimal=',')

                # log
                print(f'{ano}: {round(os.path.getsize(arquivo_html) / 1024)} kb')
                sleep(1)
            except:
                print(f'ERRO {arquivo_html}\n'
                      f'{r.status_code}')

            """Remove os arquivos html e arquivos sem dados (menos de 430 kb)"""
            os.remove(arquivo_html)
            for x in glob.glob(f'{arquivos_individuais}/*.*'):
                if os.path.getsize(x) <= 430:
                    os.remove(x)

    def merge():
        csv_list = glob.glob('arquivos_individuais/*.csv')
        df_list = []
        for csv_file in csv_list:
            print(f'Combinando {csv_file}')
            df = pd.read_csv(csv_file, encoding='cp1252')
            df_list.append(df)
            df = pd.concat(df_list, axis=0)
            df.to_csv(f"arquivos_combinados/pocos_{datetime.today().strftime('%m_%d_%Y')}.csv", encoding='cp1252')

    try:
        last_update = datetime.fromtimestamp(os.path.getmtime(
            'arquivos_individuais/pocos2020.csv')).strftime('%d/%m/%Y')

        if not datetime.today().strftime('%d/%m/%Y') == last_update:
            download()
            merge()
    except:
        download()
        merge()
        pass

