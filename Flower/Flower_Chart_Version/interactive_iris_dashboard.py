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
import numpy as np
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
    # serve the Dash app under the path /iris/
    prefix = '/iris/'
    app = dash.Dash(__name__, requests_pathname_prefix=prefix)
    app.title = 'Iris Explorer'

    # User-provided palette
    PALETTE = ['#B2EDFC', '#59A1D5', '#6973A7', '#969BB8', '#2C497B']
    # Map species to the first three palette colors to make changes obvious
    species_list = sorted(df['Species'].unique())
    COLOR_MAP = {species_list[i]: PALETTE[i] for i in range(min(len(species_list), len(PALETTE)))}

    species_options = [{'label': s, 'value': s} for s in sorted(df['Species'].unique())]

    app.layout = html.Div([
        html.H2('Iris Dataset Explorer', style={'textAlign':'center', 'color':'white'}),
        html.Div([
            html.Div([
                html.Label('Species'),
                dcc.Dropdown(id='species-filter', options=species_options, value=[o['value'] for o in species_options], multi=True),
                dcc.Graph(id='scatter', clear_on_unhover=True),
                html.Div([html.Label('Animated Scatter')], style={'marginTop':'8px'}),
                dcc.Graph(id='animated-scatter')
            ], style={'width':'60%', 'display':'inline-block', 'verticalAlign':'top'}),

            html.Div([
                html.Label('Distribution (Rose Chart)'),
                html.Div([
                    html.Label('Group by', style={'marginRight':'8px'}),
                    dcc.Dropdown(
                        id='group-by',
                        options=[
                            {'label':'Species', 'value':'Species'},
                            {'label':'SepalLength (bins)', 'value':'SepalLength'},
                            {'label':'SepalWidth (bins)', 'value':'SepalWidth'}
                        ],
                        value='Species',
                        clearable=False,
                        style={'width':'70%'}
                    )
                ], style={'display':'flex', 'alignItems':'center', 'marginBottom':'8px'}),

                dcc.Graph(id='rose-chart')
            ], style={'width':'38%', 'display':'inline-block', 'paddingLeft':'2%'}),
        ], style={'padding':'10px 20px'})
    ], style={'fontFamily':'Arial', 'backgroundColor':'black', 'color':'white', 'height':'100vh'})

    @app.callback(
        Output('scatter', 'figure'),
        Input('species-filter', 'value')
    )
    def update_scatter(selected_species):
        dff = df[df['Species'].isin(selected_species)]
        # use explicit color map for species so colors are predictable
        # Create layered scatter to simulate a glow: larger pale markers under smaller solid markers
        fig = px.scatter(dff, x='SepalLengthCm', y='SepalWidthCm', color='Species', hover_data=['Id'],
                         title=f'Sepal Length vs Width ({len(dff)} rows)',
                         color_discrete_map=COLOR_MAP,
                         template='plotly_dark')

        # Update marker styling for glow: add outline and slightly larger trace behind each species
        for trace in fig.data:
            # main marker
            trace.marker.line.width = 1
            trace.marker.line.color = 'rgba(0,0,0,0.6)'
            trace.marker.size = 10
            # emulate glow by adding a faint larger marker using marker.symbol and opacity
            # Plotly traces do not support two marker sizes per-trace easily; instead increase 'marker.opacity' slightly
            trace.marker.opacity = 0.95

        fig.update_layout(paper_bgcolor='black', plot_bgcolor='black', font_color='white')
        fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.07)', zeroline=False, color='white')
        fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.07)', zeroline=False, color='white')
        return fig

    @app.callback(
        Output('rose-chart', 'figure'),
        [Input('species-filter', 'value'), Input('group-by', 'value')]
    )
    def update_rose(selected_species, group_by):
        dff = df[df['Species'].isin(selected_species)]

        if group_by == 'Species':
            counts = dff['Species'].value_counts().sort_index()
            categories = counts.index.tolist()
            values = counts.values.tolist()
            theta = categories
        else:
            # create bins for numeric columns
            if group_by == 'SepalLength':
                col = 'SepalLengthCm'
            else:
                col = 'SepalWidthCm'

            bins = 6
            labels = []
            dff['bin'] = pd.cut(dff[col], bins=bins)
            counts = dff['bin'].value_counts().sort_index()
            categories = [str(i) for i in counts.index]
            values = counts.values.tolist()
            theta = categories

        # polar bar (rose) chart
        theta = [str(c) for c in categories]
        if group_by == 'Species':
            fig = px.bar_polar(
                r=values,
                theta=theta,
                color=theta,
                template='plotly_dark',
                color_discrete_map=COLOR_MAP
            )
        else:
            color_seq = PALETTE * ((len(values) // len(PALETTE)) + 1)
            fig = px.bar_polar(
                r=values,
                theta=theta,
                color=theta,
                template='plotly_dark',
                color_discrete_sequence=color_seq
            )

        # Make bars have a subtle glow by increasing alpha and adding a thin white edge
        for t in fig.data:
            if hasattr(t, 'marker'):
                # slightly translucent fill
                t.marker.opacity = 0.9
                # add thin edge
                try:
                    t.marker.line = dict(color='rgba(255,255,255,0.12)', width=1)
                except Exception:
                    pass

        fig.update_layout(title=f'Distribution by {group_by} (n={len(dff)})', showlegend=False,
                          paper_bgcolor='black', plot_bgcolor='black', font_color='white')
        fig.update_traces(selector=dict(type='barpolar'))
        return fig
        return fig

    @app.callback(
        Output('animated-scatter', 'figure'),
        Input('species-filter', 'value')
    )
    def update_animated(selected_species):
        dff = df[df['Species'].isin(selected_species)]
        # build base fig
        base = px.scatter(dff, x='SepalLengthCm', y='SepalWidthCm', color='Species',
                          color_discrete_map=COLOR_MAP, template='plotly_dark')
        # create frames that pulse marker sizes
        frames = []
        steps = 20
        for t in range(steps):
            scale = 1.0 + 0.3 * np.sin(2 * np.pi * (t / steps))
            # update sizes per point
            frame_data = []
            for sp in sorted(dff['Species'].unique()):
                sub = dff[dff['Species'] == sp]
                frame_data.append({
                    'type': 'scatter',
                    'x': sub['SepalLengthCm'].tolist(),
                    'y': sub['SepalWidthCm'].tolist(),
                    'marker': {'size': [10 * scale] * len(sub), 'color': COLOR_MAP.get(sp)},
                    'mode': 'markers'
                })
            frames.append({'data': frame_data, 'name': str(t)})

        animated = base
        animated.frames = frames
        # add play button
        animated.update_layout(
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [{
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {'frame': {'duration': 80, 'redraw': True}, 'fromcurrent': True}]
                }]
            }],
            paper_bgcolor='black', plot_bgcolor='black', font_color='white'
        )
        return animated

    return app

if __name__ == '__main__':
        app = create_app()
        # add a lightweight index page on the Flask server that links to the Dash app
        @app.server.route('/')
        def index():
                return '''
                <html>
                    <head><title>Iris Dash Index</title></head>
                    <body style="background-color:black;color:white;font-family:Arial;">
                        <h2>Iris Dashboards</h2>
                        <ul>
                            <li><a href="/iris/" style="color:#B2EDFC">Interactive Iris Explorer (dark)</a></li>
                        </ul>
                    </body>
                </html>
                '''

        start_url = 'http://localhost:8051/iris/'
        print(f'Starting Iris dashboard at {start_url}')
        app.run(host='0.0.0.0', port=8051, debug=False)
