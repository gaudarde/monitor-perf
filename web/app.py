#!/usr/bin/python
# -*- coding: latin-1 -*-

import os
from datetime import datetime

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
import plotly.io as pio

# load stuffs
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
df = pd.read_csv('data/data.csv', encoding='cp1252', parse_dates=[
    'Início', 'Término', 'Conclusão'], index_col='Início')

OffshoreMonthly = df[df['Ambiente'] == 'MAR'].resample('M').count()
OnshoreMonthly = df[df['Ambiente'] == 'TERRA'].resample('M').count()
dfTable = pd.read_csv('data/table.csv', encoding='cp1252', parse_dates=['Início', 'Término'])
dfTable.sort_values(by=['Início'], ascending=False, inplace=True)

# styles

pio.templates.default = "ggplot2"

body = {
    'backgroundColor': '#f9f9f9',
}

header = {
    'backgroundColor': '#fafafa',
    'padding': '20px',
    'border': 'solid 5px white'
}

logo = {
    'borderRadius': '12px',
    'backgroundColor': 'white',
    'margin': '10px',
    'padding': '15px',
    'boxShadow': '2px 2px 2px lightgrey',
    'width': '250px',
    'height': 'auto',
    'position': 'relative',
    'left': '22.5%',
}

text = {
    'borderRadius': '12px',
    'backgroundColor': 'white',
    'margin': '0px',
    'padding': '3px',
    'boxShadow': '2px 2px 2px lightgrey',
    'width': '200px',
    'height': 'auto',
    'position': 'relative',
    'left': '30%',
    'top': '33%',
    'textAlign': 'center',
    'fontFamily': 'Verdana, sans-serif',
    'fontSize': '12px',
    'fontWeight': '900',
}

B = {
    'borderRadius': '12px',
    'backgroundColor': '#f9f9f9',
    'margin': '0px',
    'padding': '3px',
    'boxShadow': '2px 2px 2px lightgrey',
    'width': 'auto',
    'height': 'auto',
    'position': 'relative',
    'left': '0%',
    'top': '0%',
    'textAlign': 'center',
    'fontFamily': 'Verdana, sans-serif',
    'fontSize': '12px',
    'fontWeight': '900',
}

graphs = {
    'borderRadius': '12px',
    'backgroundColor': 'white',
    'margin': '15px',
    'padding': '0px',
    'boxShadow': '2px 2px 2px lightgrey',
    'height': 'auto',
    'position': 'relative',
    'textAlign': 'center',
    'fontFamily': 'Verdana, sans-serif',
    'fontSize': '12px',
    'fontWeight': '900',
}

cards = {
    'borderRadius': '12px',
    'backgroundColor': 'white',
    'margin': '15px',
    'padding': '3px',
    'boxShadow': '2px 2px 2px lightgrey',
    'height': 'auto',
    'position': 'relative',
    'textAlign': 'left',
    'fontFamily': 'Verdana, sans-serif',
    'fontSize': '12px',
    'fontWeight': '900',
}

# quick calcs
lastUpdate = datetime.fromtimestamp(os.path.getmtime('data/table.csv')).strftime('%d-%m-%Y')
fileSize = round(os.path.getsize('data/data.csv') * 1e-6, 2)
latestYear = dfTable['Início'].dt.year.max()
offshoreWells = sum((dfTable['Ambiente'] == 'MAR') & (dfTable['Início'].dt.year == latestYear))
onshoreWells = sum((dfTable['Ambiente'] == 'TERRA') & (dfTable['Início'].dt.year == latestYear))

# quick formats
dfTable['Início'] = dfTable['Início'].dt.strftime('%d/%m/%Y')
dfTable['Término'] = dfTable['Término'].dt.strftime('%d/%m/%Y')

# sample data table
dataTable = dash_table.DataTable(
    id='sample-table',
    columns=[{"name": i, "id": i} for i in dfTable.columns],
    data=dfTable.to_dict('records'),
    page_size=20,
    style_table={},
    style_header={
        'backgroundColor': '#395C6B',
        'fontWeight': '900',
        'fontSize': '15px',
        'fontFamily': 'Verdana, sans-serif',
        'color': '#fafafa',
        'textAlign': 'center',
        'paddingLeft': '12px',
        'paddingRight': '12px',
        'border': '1px white',
    },
    style_cell={
        'width': '80px',
        'maxWidth': '80px',
        'minWidth': '80px',
        'whiteSpace': 'normal',
        'textAlign': 'center',
        'fontSize': '14px',
        'fontFamily': 'Verdana, sans-serif',
        'border': '1px solid white',
    },
    style_data_conditional=[
        {'if': {'row_index': 'odd'}, 'backgroundColor': '#D7E4EA'},
        {'if': {'row_index': 'even'}, 'backgroundColor': '#FAFAFA'},
    ],
)

# offshore well
figOffshoreWells = px.bar(OffshoreMonthly, x=OffshoreMonthly.index, y='Código (ANP)')
figOffshoreWells.update_layout(
    title='Perfuração offshore',
    xaxis_title='meses',
    yaxis_title='poços',
    font=dict(
        family='Verdana, sans-serif',
        size=12,
    )
)

# onshore well
figOnshoreeWells = px.bar(OnshoreMonthly, x=OnshoreMonthly.index, y='Código (ANP)')
figOnshoreeWells.update_layout(
    title='Perfuração onshore',
    xaxis_title='meses',
    yaxis_title='poços',
)

app.layout = html.Div(style=body, children=[
    dbc.Container(
        [
            # row header
            dbc.Row(children=[
                dbc.Col(html.Div(
                    html.Img(
                        src=app.get_asset_url('monitor-logo.png'),
                        id='monitor-logo',
                        style=logo,
                    ),
                ), md=6, sm=12),
                dbc.Col(html.Div(
                    f'ATUALIDO EM {lastUpdate}',
                    style=text
                ), md=6, sm=12),
            ]),

            # row summary
            dbc.Row(children=[
                dbc.Col(html.Div('controls', style=graphs), md=6),

                # card offshore
                dbc.Col(html.Div([
                    html.P(f'# poços offshore ({latestYear})'),
                    html.P(offshoreWells)
                ],
                    style=cards), md=3),

                # card onshore
                dbc.Col(html.Div([
                    html.P(f'# poços onshore ({latestYear})'),
                    html.P(onshoreWells)
                ],
                    style=cards), md=3),
            ]),

            # row main-graphs
            dbc.Row(children=[

                dbc.Col(html.Div(
                    dcc.Graph(
                        figure=figOffshoreWells,
                        id='offshore-wells'
                    ), style=graphs), md=8),

                dbc.Col(html.Div('figOffshoreWell.show()', style=graphs), md=4),

                dbc.Col(html.Div(dcc.Graph(
                    figure=figOnshoreeWells,
                    id='onshore-wells'
                ), style=graphs), md=8),

                dbc.Col(html.Div('onshore-rigs', style=graphs), md=4),
            ]),

            # row sample data table
            dbc.Row(children=[
                dbc.Col(html.Div('map', style=graphs), xs=12),
                dbc.Col(html.A(f'Tabela  de poços (csv, {fileSize} MB)',
                               style=graphs,
                               href='data/data.csv'), sm=12, md=4),
                dbc.Col(html.Div(dataTable, id='data_table'), md=12),
            ]),
        ]
    )])

if __name__ == '__main__':
    app.run_server(debug=True)
