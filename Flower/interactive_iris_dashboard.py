#!/usr/bin/env python3
"""
Interactive Iris dashboard

Left: scatter plot (SepalLength vs SepalWidth) colored by species.
Right: data table showing filtered rows. Selection in the plot highlights rows in the table.

Run:
  & <venv>\Scripts\python.exe Flower\interactive_iris_dashboard.py
Open: http://localhost:8051
"""

import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output, State
from dash import dash_table
import os

HERE = os.path.dirname(__file__)
CSV_PATH = os.path.join(HERE, 'Iris.csv')

def load_data(path=CSV_PATH):
    df = pd.read_csv(path)
    # Normalize species naming
    df['Species'] = df['Species'].str.replace('Iris-', '')
    return df

def create_app():
    df = load_data()
    app = dash.Dash(__name__)
    app.title = 'Iris Explorer'

    species_options = [{'label': s, 'value': s} for s in sorted(df['Species'].unique())]

    app.layout = html.Div([
        html.H2('Iris Dataset Explorer', style={'textAlign':'center'}),
        html.Div([
            html.Div([
                html.Label('Species'),
                dcc.Dropdown(id='species-filter', options=species_options, value=[o['value'] for o in species_options], multi=True),
                dcc.Graph(id='scatter', clear_on_unhover=True)
            ], style={'width':'60%', 'display':'inline-block', 'verticalAlign':'top'}),

            html.Div([
                html.Label('Data Table'),
                dash_table.DataTable(
                    id='table',
                    columns=[{'name':c, 'id':c} for c in df.columns],
                    data=df.to_dict('records'),
                    page_size=15,
                    filter_action='native',
                    sort_action='native',
                    row_selectable='multi',
                    selected_rows=[],
                    style_table={'height':'600px', 'overflowY':'auto'},
                    style_cell={'textAlign':'left', 'minWidth':'100px', 'whiteSpace':'normal'}
                )
            ], style={'width':'38%', 'display':'inline-block', 'paddingLeft':'2%'}),
        ], style={'padding':'10px 20px'})
    ], style={'fontFamily':'Arial', 'backgroundColor':'white'})

    @app.callback(
        Output('scatter', 'figure'),
        Input('species-filter', 'value')
    )
    def update_scatter(selected_species):
        dff = df[df['Species'].isin(selected_species)]
        fig = px.scatter(dff, x='SepalLengthCm', y='SepalWidthCm', color='Species', hover_data=['Id'],
                         title=f'Sepal Length vs Width ({len(dff)} rows)')
        return fig

    @app.callback(
        Output('table', 'data'),
        Input('species-filter', 'value')
    )
    def update_table(selected_species):
        dff = df[df['Species'].isin(selected_species)]
        return dff.to_dict('records')

    return app

if __name__ == '__main__':
    app = create_app()
    print('Starting Iris dashboard at http://localhost:8051')
    app.run(host='0.0.0.0', port=8051, debug=False)
