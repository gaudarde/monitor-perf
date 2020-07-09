import glob
import os
from datetime import datetime

import numpy as np
import pandas as pd


def dados():
    pd.set_option('display.width', 260)
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.max_rows', 500)

    arquivo = max(glob.glob('arquivos_combinados/*.csv'), key=os.path.getctime)

    print(f'Trabalhando com {arquivo}')

    df = pd.read_csv(
        arquivo,
        encoding='cp1252',
        dayfirst=True,
        converters={
            'Código Poço': lambda x: str(x)},
        parse_dates=[
            'Data Início Perfuração',
            'Data Término Perfuração',
            'Data Conclusão Poço'],
        index_col='Código Poço'
    )

    df = df.drop([df.columns[0]], axis='columns')

    '''Alterações para corrigir e uniformizar data das tabelas de poços'''

    df['Nome Poço ANP'].replace(r'\W|\s|_', '', regex=True, inplace=True)
    df['Nome Poço Operador'].replace(r'\W|\s|_', '', regex=True, inplace=True)
    df['Profundidade Vertical'] = df['Profundidade Vertical'].abs()

    df['Lâmina D Água'].fillna(0, inplace=True)

    '''Inclusão das coordenadas decimais'''

    df['Latitude Base Definitiva'].fillna(df['Latitude Base Provisória'], inplace=True)
    dfLat = df['Latitude Base Definitiva']
    df['LatHora'] = dfLat.str.extract(r'(-[0-9]{2}|[0-9]{2})')
    df['LatHora'] = pd.to_numeric(df['LatHora'])
    df['LatMinuto'] = dfLat.str.extract(r'(:[0-9]{2})')
    df['LatMinuto'].replace(':', '', regex=True, inplace=True)
    df['LatMinuto'] = pd.to_numeric(df['LatMinuto']) / 60
    df['LatSegundo'] = dfLat.str.extract(r'([0-9]{2},[0-9]{3})')
    df['LatSegundo'].replace(':', '', regex=True, inplace=True)
    df['LatSegundo'].replace(',', '.', regex=True, inplace=True)
    df['LatSegundo'] = pd.to_numeric(df['LatSegundo']) / 3600
    df['LatSinal'] = np.where(df.LatHora > 0, 1, -1)
    df['Latitude'] = (df.LatMinuto + df.LatSegundo + df.LatHora.abs()) * df.LatSinal
    df['Longitude Base Definitiva'].fillna(df['Longitude Base Provisória'], inplace=True)
    dfLong = df['Longitude Base Definitiva']
    df['LongHora'] = dfLong.str.extract(r'(-[0-9]{2}|[0-9]{2})')
    df['LongHora'] = pd.to_numeric(df['LongHora'])
    df['LongMinuto'] = dfLong.str.extract(r'(:[0-9]{2})')
    df['LongMinuto'].replace(':', '', regex=True, inplace=True)
    df['LongMinuto'] = pd.to_numeric(df['LongMinuto']) / 60
    df['LongSegundo'] = dfLong.str.extract(r'([0-9]{2},[0-9]{3})')
    df['LongSegundo'].replace(':', '', regex=True, inplace=True)
    df['LongSegundo'].replace(',', '.', regex=True, inplace=True)
    df['LongSegundo'] = pd.to_numeric(df['LongSegundo']) / 3600
    df['LongSinal'] = np.where(df.LongHora > 0, 1, -1)
    df['Longitude'] = (df.LongMinuto + df.LongSegundo + df.LongHora.abs()) * df.LongSinal

    '''Filtra colunas para os data finais'''

    df.drop(columns=[
        'LatHora',
        'LatMinuto',
        'LatSegundo',
        'LatSinal',
        'LongHora',
        'LongMinuto',
        'LongSegundo',
        'LongSinal',
        'Latitude Base Provisória',
        'Longitude Base Provisória',
        'Latitude Base Definitiva',
        'Longitude Base Definitiva',
        'Latitude Fundo',
        'Longitude Fundo',
        'Cota Altimétrica',
        'Profundidade Sondador',
        'Profundidade Medida',
        'Profundidade Vertical',
        'Mesa Rotativa'], inplace=True)

    '''Inclusão de data adicionais'''

    tipos = {
        '1': 'pioneiro',
        '2': 'estratigráfico',
        '3': 'extensão',
        '4': 'pioneiro adjacente',
        '5': 'jazida mais raza',
        '6': 'jazida mais profunda',
        '7': 'produção',
        '8': 'injeção',
        '9': 'especial',
    }

    df['tipo'] = df['Nome Poço ANP'].str[:1]
    df['tipo'].replace(tipos, inplace=True)

    objetivos = {
        'pioneiro': 'exploração',
        'estratigráfico': 'exploração',
        'extensão': 'exploração',
        'pioneiro adjacente': 'exploração',
        'jazida mais raza': 'exploração',
        'jazida mais profunda': 'exploração',
        'produção': 'produção',
        'injeção': 'produção',
        'especial': 'N.D.',
    }

    df.loc[df['Campo'].isna(), 'objetivo'] = 'exploração'
    df['objetivo'].fillna(df['tipo'], inplace=True)
    df['objetivo'].replace(objetivos, inplace=True)

    df.loc[df.groupby('Nome Sonda')['Data Início Perfuração'].idxmax(), 'Sonda (deslocamento)'] = "Última posição"
    df['Sonda (deslocamento)'].fillna('Sonda Deslocada', inplace=True)
    df.loc[df['Nome Sonda'].isna(), 'Sonda (deslocamento)'] = 'N.D.'

    df.loc[df['Campo'].isna(), 'Ativo'] = df['Bloco']
    df.loc[df['Bloco'].isna(), 'Ativo'] = df['Campo']
    '''ativo_ = f'{df.Campo} ({df.bloco})'
    df['ativo'].fillna(ativo_)'''

    # todo Identificar os poços repetidos
    '''df['ID'] = df['Nome Poço ANP'].str.extract(r'([A-Z]+[0-9]+)')
    df.loc[df['Terra / Mar'] == 'TERRA', 'UF'] = df['Nome Poço ANP'].str[-2:]
    df.loc[df['Terra / Mar'] == 'MAR', 'UF'] = df['Nome Poço ANP'].str[-3:-1]
    print(df['UF'].unique())
    df['temp'] = df['Nome Poço ANP']'''

    carimbo = str(datetime.now().year) + '_' + str(datetime.now().month) + '_' + str(datetime.now().day)
    df.to_csv(f'arquivos_definitivos/monitor_epbr_{carimbo}.csv', index=False, encoding='cp1252')
