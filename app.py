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
import plotly.graph_objects as go

# load stuffs
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
df = pd.read_csv('data/data.csv', encoding='cp1252', parse_dates=[
    'Início', 'Término', 'Conclusão'], dayfirst=True, index_col='Início')

OffshoreMonthly = df[df['Ambiente'] == 'MAR'].resample('M').count()
OnshoreMonthly = df[df['Ambiente'] == 'TERRA'].resample('M').count()

dfTable = pd.read_csv('data/table.csv', encoding='cp1252', parse_dates=['Início', 'Término'], dayfirst=True)
dfTable.sort_values(by=['Início'], ascending=False, inplace=True)

# quick calcs
lastUpdate = datetime.fromtimestamp(os.path.getmtime('data/table.csv')).strftime('%d-%m-%Y')
fileSize = round(os.path.getsize('data/data.csv') * 1e-6, 2)
latestYear = dfTable['Início'].dt.year.max()
offshoreWells = sum((dfTable['Ambiente'] == 'MAR') & (dfTable['Início'].dt.year == latestYear))
onshoreWells = sum((dfTable['Ambiente'] == 'TERRA') & (dfTable['Início'].dt.year == latestYear))

# date picker before date to str
marks = [f'{i}: str({i}),' for i in dfTable['Início'].dt.year.unique()]
dateslider = dcc.RangeSlider(
    id='year-picker',
    min=1922,
    max=2020,
    value=[1922, 2020],
    marks={1922: '1922', 2020: '2020'}
)

# quick formats
dfTable['Início'] = dfTable['Início'].dt.strftime('%d/%m/%Y')
dfTable['Término'] = dfTable['Término'].dt.strftime('%d/%m/%Y')

# offshore well
figOffshoreWells = go.Figure()
figOffshoreWells.add_trace(
    go.Scatter(
        x=OffshoreMonthly.index,
        y=OffshoreMonthly['Código (ANP)'],
        mode='lines+markers',
        line=dict(
            color='#273469',
            width=2.5,
        )
    )
)

graphConfigOffshore = {
    'displaylogo': False,
    'displayModeBar': True,
    'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d',
                               'resetScale2d', 'hoverClosestCartesian', 'hoverClosestGl2d',
                               'hoverClosestPie', 'toggleHover', 'resetViews', 'sendDataToCloud', 'toggleSpikelines',
                               'resetViewMapbox'],
    'toImageButtonOptions': {
        'filename': 'poços offshore-monitor-epbr.com.br',
        'scale': 2,
    },
    'locale': 'pt-BR',
}

figOffshoreWells.update_layout(
    title={
        'text': 'Perfuração offshore',
        'x': 0.05,
        'xanchor': 'left',
    },
    xaxis_title='meses',
    yaxis_title='poços',
    font=dict(
        family='Verdana, sans-serif',
        size=14,
    ),
    paper_bgcolor="#FAFAFF",
    margin=dict(
        pad=0,
    ),
)

# onshore well
figOnshoreWells = go.Figure()
figOnshoreWells.add_trace(
    go.Scatter(
        x=OnshoreMonthly.index,
        y=OnshoreMonthly['Código (ANP)'],
        mode='lines+markers',
        line=dict(
            color='#A5243D',
            width=2.5,
        ),
    )
)

graphConfigOnshore = {
    'displaylogo': False,
    'displayModeBar': True,
    'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d',
                               'resetScale2d', 'hoverClosestCartesian', 'hoverClosestGl2d',
                               'hoverClosestPie', 'toggleHover', 'resetViews', 'sendDataToCloud', 'toggleSpikelines',
                               'resetViewMapbox'],
    'toImageButtonOptions': {
        'filename': 'poços onshore-monitor-epbr.com.br',
        'scale': 2,
    },
    'locale': 'pt-BR',
}

figOnshoreWells.update_layout(
    title={
        'text': 'Perfuração onshore',
        'x': 0.05,
        'xanchor': 'left',
    },
    xaxis_title='meses',
    yaxis_title='poços',
    font=dict(
        family='Verdana, sans-serif',
        size=14,
    ),
    paper_bgcolor="#FAFAFF",
)

# sample data table
dataTable = dash_table.DataTable(
    id='sample-table',
    columns=[{"name": i, "id": i} for i in dfTable.columns],
    data=dfTable.to_dict('records'),
    page_size=50,
    style_table={},
    style_header={
        'backgroundColor': '#395C6B',
        'fontWeight': '900',
        'fontSize': '0.66em',
        'fontFamily': 'Verdana, sans-serif',
        'color': '#fafafa',
        'textAlign': 'center',
        'paddingLeft': '8px',
        'paddingRight': '8px',
        'border': '1px #6E8898',
    },
    style_cell={
        'width': '80px',
        'maxWidth': '80px',
        'minWidth': '80px',
        '#6E8898Space': 'normal',
        'textAlign': 'center',
        'fontSize': '0.66em',
        'fontFamily': 'Verdana, sans-serif',
        'border': '1px #6E8898',
        'whiteSpace': 'normal',
    },
    style_data_conditional=[
        {'if': {'row_index': 'odd'}, 'backgroundColor': '#D7E4EA'},
        {'if': {'row_index': 'even'}, 'backgroundColor': '#FAFAFA'},
    ],
)

# offshore rigs
figOffshoreRigs = go.Figure()
figOffshoreRigs.add_trace(
    go.Bar(
        x=OffshoreMonthly['Sonda'],
        y=OffshoreMonthly.groupby('Sonda').count(),
    )
)

# Create controls
ambiente_options = [
    {"label": i, "value": i} for i in df['Ambiente'].unique()
]

bacias_options = [
    {"label": i, "value": i} for i in df['Bacia'].unique()
]

bloco_options = [
    {"label": i, "value": i} for i in df['Bloco'].unique()
]

campo_options = [
    {"label": i, "value": i} for i in df['Campo'].unique()
]

operador_options = [
    {"label": i, "value": i} for i in df['Operador'].unique()
]

tipo_options = [
    {"label": i, "value": i} for i in df['Tipo'].unique()
]

dropdown_bacias = dcc.Dropdown(
    options=bacias_options,
    multi=True,
    placeholder='Bacias',
    persistence=True,
    persistence_type='session'
)

dropdown_bloco = dcc.Dropdown(
    options=bloco_options,
    multi=True,
    placeholder='Blocos',
    persistence=True,
    persistence_type='session'
)

dropdown_campo = dcc.Dropdown(
    options=campo_options,
    multi=True,
    placeholder='Campos',
    persistence=True,
    persistence_type='session'
)

dropdown_operador = dcc.Dropdown(
    options=operador_options,
    multi=True,
    placeholder='Operador',
    persistence=True,
    persistence_type='session'
)

dropdown_poco = dcc.Dropdown(
    options=tipo_options,
    multi=True,
    placeholder='Tipos',
    persistence=True,
    persistence_type='session'
)

# app
app.layout = html.Div([
    dbc.Container(
        [
            # fisrt row
            dbc.Row([
                # logo
                dbc.Col(children=[
                    html.Img(
                        src=app.get_asset_url('monitor-logo.png'),
                        id='logo',
                        className='logo'
                    ),
                    html.Div(
                        f'Atualizado em: {lastUpdate}',
                        id='update-card',
                        className='update-card',
                    ),
                ], className='card col-md-3 col-sm-12'),

                # summary
                dbc.Col(children=[
                    dbc.Row([
                        html.Div(html.P(f'# offshore ({latestYear})'),
                                 className='summary-title', id='summary-title-offshore'),
                        html.Div(html.P(offshoreWells),
                                 className='summary-number', id='summary-number-offshore')
                    ]),
                ], className='summary-card col-md-3 col-sm-5'),

                dbc.Col(children=[
                    dbc.Row([
                        html.Div(html.P(f'# onshore ({latestYear})'),
                                 className='summary-title', id='summary-title-onshore'),
                        html.Div(html.P(onshoreWells),
                                 className='summary-number', id='summary-number-onshore')
                    ]),
                ], className='summary-card col-md-3 col-sm-5'),
            ], className='col-md-12'),

            # controls
            dbc.Row([

                dbc.Col([
                    html.Div(dropdown_bacias,
                             id='filter-bacia', className='dropdown'),
                    html.Div(dropdown_operador,
                             id='filter-operador', className='dropdown'),
                ], className='col-md-4'),

                dbc.Col([
                    html.Div(dropdown_campo,
                             id='filter-campo', className='dropdown'),
                    html.Div(dropdown_bloco,
                             id='filter-bloco', className='dropdown'),
                ], className='col-md-4'),

                dbc.Col([
                    html.Div(dropdown_poco,
                             id='filter-poco', className='dropdown'),
                    html.Div(dateslider,
                             className='date-picker'),
                ], className='col-md-4'),

            ], className='filter-card col-md-12'),

            # row graphs
            dbc.Row(
                dbc.Col(
                    dcc.Graph(figure=figOffshoreWells,
                              id='offshore-wells',
                              config=graphConfigOffshore),
                ), className='card col-md-12'),

            dbc.Row(
                dbc.Col(
                    dcc.Graph(figure=figOnshoreWells,
                              id='onshore-wells',
                              config=graphConfigOnshore),
                ), className='card col-md-12'),

            dbc.Row([
                html.Div(
                    html.A(f'Tabela  de poços (csv, {fileSize} MB)',
                           href=app.get_asset_url('data.csv'),
                           target='_blank'), className='table-title'
                ),

                html.Div(dataTable, id='data_table', className='table')
            ], className='card col-md-12'),
        ]
    )])

if __name__ == '__main__':
    app.run_server(debug=True)
