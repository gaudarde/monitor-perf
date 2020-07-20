#!/usr/bin/python
# -*- coding: latin-1 -*-

import glob
import os
from datetime import datetime

import pandas as pd

import dados
import download

if __name__ == '__main__':

    pd.set_option('display.width', 260)
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.max_rows', 500)

    if datetime.fromtimestamp(os.path.getmtime('web/data/table.csv')).date() < datetime.today().date():
        download.download()
        download.merge()
    else:
        pass

    dados.dados()

    pastas = ['web', 'web/data']
    for i in pastas:
        if not os.path.isdir(i):
            os.mkdir(i)
        else:
            pass

    arquivo = max(glob.glob('arquivos_definitivos/*.csv'), key=os.path.getctime)
    df = pd.read_csv(arquivo, encoding='cp1252', parse_dates=[
        'Data Início Perfuração', 'Data Término Perfuração', 'Data Conclusão Poço'],
                     dayfirst=True, infer_datetime_format=True)

    df.rename(columns={
        'Bacia': 'Bacia',
        'Bloco': 'Bloco',
        'Campo': 'Campo',
        'Operador': 'Operador',
        'Terra / Mar': 'Ambiente',
        'Nome Poço ANP': 'Código (ANP)',
        'Nome Poço Operador': 'Código (operador)',
        'Data Início Perfuração': 'Início',
        'Data Término Perfuração': 'Término',
        'Data Conclusão Poço': 'Conclusão',
        'Lâmina D Água': "Lâmina d'água",
        'Nome Sonda': 'Sonda',
        'Latitude': 'Latitude',
        'Longitude': 'Longitude',
        'tipo': 'Tipo',
        'objetivo': 'Objetivo',
        'Sonda (deslocamento)': 'Info',
        'ativo': 'ativo'
    }, inplace=True)

    pd.to_numeric(df['Latitude'])
    pd.to_numeric(df['Longitude'])
    df['Latitude'] = df['Latitude'].round(6)
    df['Longitude'] = df['Latitude'].round(6)

    df['Operador'].fillna('ND', inplace=True)
    df['Sonda'].fillna('ND', inplace=True)
    df['Campo'].fillna('Não declarado', inplace=True)
    df['Bloco'].fillna('Não declarado', inplace=True)
    df['Tipo'].fillna('Não declarado', inplace=True)

    # Dados reorganizados, base para gerar os gráficos (data.csv)
    dfData = df.iloc[:, [7, 8, 9, 0, 1, 2, 17, 3, 4, 10, 5, 6, 14, 15, 11, 16, 12, 13]]
    dfData.to_csv('web/data/data.csv', index=False, encoding='cp1252', decimal=',')
    dfData.to_csv('web/assets/data.csv', index=False, encoding='cp1252', decimal=',')
    print(f'df data.csv (todas as colunas)\n'
          f'{dfData.head()}\n')

    # Dados para a tabela (data.csv)
    dfTable = df.iloc[:, [7, 8, 0, 17, 3, 4, 10, 5, 15, 11, 16]]
    dfTable.to_csv('web/data/table.csv', index=False, encoding='cp1252', decimal=',')
    print(f'df table.csv (tabela)\n'
          f'{dfTable.head()}\n')
