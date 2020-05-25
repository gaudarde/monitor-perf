import pandas as pd
import numpy as np
import datetime
import re

if __name__ == '__main__':
    pd.set_option('display.max_columns', 30)
    pd.set_option('display.max_rows', 500)

    df = pd.read_csv(
        'arquivos_combinados/pocos_05_17_2020.csv',
        encoding='cp1252',
        dayfirst=True,
        converters={
            'Código Poço': lambda x: str(x)},
        parse_dates=[
            'Data Início Perfuração',
            'Data Término Perfuração',
            'Data Conclusão Poço'],
        index_col=1
    )

    df = df.drop([df.columns[0]], axis='columns')

    '''Alterações para corrigir e uniformizar dados das tabelas de poços'''

    df['Nome Poço ANP'].replace(r'\W|\s|_', '', regex=True, inplace=True)
    df['Nome Poço Operador'].replace(r'\W|\s|_', '', regex=True, inplace=True)
    df['Profundidade Vertical'] = df['Profundidade Vertical'].abs()

    df['Lâmina D Água'].fillna(0, inplace=True)

    '''Inclusão das coordenadas decimais'''

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

    '''Filtra colunas para os dados finais'''

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

    '''Inclusão de dados adicionais'''

    objetivos = {
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

    df['objetivo'] = df['Nome Poço ANP'].str[:1]
    df['objetivo'].replace(objetivos, inplace=True)

    #TODO
    """
    Identificar qual a única posição da sonda e gerar coluna InfoSonda
    df['InfoSonda'] = df.groupby(['Nome Sonda'])['Data Início Perfuração'].transform('max')
    """
    df.sort_values(by=['Data Início Perfuração'], ascending=False).head(50)

