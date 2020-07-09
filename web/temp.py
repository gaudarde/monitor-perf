#!/usr/bin/python
# -*- coding: latin-1 -*-

import pandas as pd

# load stuffs
df = pd.read_csv('data/data.csv', encoding='cp1252', parse_dates=[
    'Início', 'Término', 'Conclusão'], index_col='Início')

OffshoreMonthly = df[df['Ambiente'] == 'MAR'].resample('M').count()
OnshoreMonthly = df[df['Ambiente'] == 'TERRA'].resample('M').count()

print(OffshoreMonthly.head())
