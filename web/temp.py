#!/usr/bin/python
# -*- coding: latin-1 -*-

import pandas as pd

# load stuffs
df = pd.read_csv('data/data.csv', encoding='cp1252', parse_dates=[
    'Início', 'Término', 'Conclusão'], dayfirst=True)

marks = [f'{i}: {i}' for i in df['Início'].dt.year.unique()]

print(marks)
