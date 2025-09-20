#!/usr/bin/env python3
"""
Interactive dashboard for Radar/2025RZ4_observations.csv

This Dash app loads the provided CSV, parses RA/Dec into degrees,
and exposes interactive filters (date range, observatory, magnitude)
with two plots: an RA-Dec scatter and a magnitude vs time timeline.

Run with your venv python:
  & <path-to-venv>\Scripts\python.exe interactive_astronomy_dashboard_radar.py

Then open http://localhost:8050 in your browser.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output
import os
import warnings
warnings.filterwarnings('ignore')

# Path to CSV (relative to this file)
HERE = os.path.dirname(__file__)
CSV_PATH = os.path.join(HERE, '2025RZ4_observations.csv')

def load_csv(path=CSV_PATH):
    df = pd.read_csv(path)
    return df

def parse_coordinates(ra_str, dec_str):
    """Convert RA (HH MM SS) and Dec (±DD MM SS) strings to decimal degrees."""
    try:
        ra_parts = str(ra_str).strip().split()
        if len(ra_parts) == 3:
            h, m, s = map(float, ra_parts)
            ra_deg = (h + m/60.0 + s/3600.0) * 15.0
        else:
            ra_deg = float(ra_str)

        dec_parts = str(dec_str).strip().split()
        if len(dec_parts) == 3:
            d = float(dec_parts[0])
            mm = float(dec_parts[1])
            ss = float(dec_parts[2])
            sign = -1 if str(dec_str).strip().startswith('-') else 1
            dec_deg = sign * (abs(d) + mm/60.0 + ss/3600.0)
        else:
            dec_deg = float(dec_str)

        return ra_deg, dec_deg
    except Exception:
        return np.nan, np.nan

def preprocess(df):
    df = df.copy()
    # parse dates (Date_UT has fractional day in decimal days; handle simple cases)
    def parse_date(date_str):
        try:
            if '.' in str(date_str):
                date_part, frac = str(date_str).split('.')
                base = datetime.strptime(date_part, '%Y-%m-%d')
                # treat frac as fractional day
                frac_days = float('0.' + frac)
                return base + timedelta(days=frac_days)
            else:
                return datetime.strptime(str(date_str), '%Y-%m-%d')
        except Exception:
            return pd.NaT

    df['Date'] = df['Date_UT'].apply(parse_date)
    df['Magnitude'] = pd.to_numeric(df['Magn'], errors='coerce')
    df[['RA_deg', 'Dec_deg']] = df.apply(lambda r: pd.Series(parse_coordinates(r['RA'], r['Dec'])), axis=1)
    df['Observatory'] = df['Location']
    df['Date_str'] = df['Date'].dt.strftime('%Y-%m-%d %H:%M')
    df = df.dropna(subset=['Date', 'RA_deg', 'Dec_deg'])
    return df

def create_sky_map(df):
    if df.empty:
        return go.Figure()
    fig = px.scatter(df, x='RA_deg', y='Dec_deg', color='Magnitude', size='Magnitude',
                     hover_data=['Date_str', 'Location', 'Magn'],
                     color_continuous_scale='Viridis_r', labels={'RA_deg':'RA (deg)','Dec_deg':'Dec (deg)'} )
    fig.update_xaxes(autorange='reversed')
    fig.update_layout(height=500, template='plotly_dark')
    return fig

def create_timeline(df):
    if df.empty:
        return go.Figure()
    fig = px.scatter(df.sort_values('Date'), x='Date', y='Magnitude', color='Location', hover_data=['RA_deg','Dec_deg','Date_str'])
    fig.update_layout(height=350, template='plotly_dark', yaxis={'autorange':'reversed'})
    return fig

def serve():
    df_raw = load_csv()
    df = preprocess(df_raw)

    app = dash.Dash(__name__)
    app.title = '2025RZ4 Observations'

    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()

    observatory_options = [{'label': 'All', 'value': 'ALL'}] + \
        [{'label': f"{loc} - {loc}", 'value': loc} for loc in sorted(df['Location'].unique())]

    app.layout = html.Div([
        html.H2('2025RZ4 Observations (Interactive)', style={'color':'#fff'}),
        html.Div([
            html.Label('Date range', style={'color':'#ddd'}),
            dcc.DatePickerRange(id='date-range', start_date=min_date, end_date=max_date, display_format='YYYY-MM-DD')
        ], style={'marginBottom':'10px'}),

        html.Div([
            html.Label('Observatory', style={'color':'#ddd'}),
            dcc.Dropdown(id='observatory', options=observatory_options, value=['ALL'], multi=True)
        ], style={'marginBottom':'10px'}),

        html.Div([
            html.Label('Magnitude range', style={'color':'#ddd'}),
            dcc.RangeSlider(id='mag-range', min=float(df['Magnitude'].min()), max=float(df['Magnitude'].max()), step=0.1,
                            value=[float(df['Magnitude'].min()), float(df['Magnitude'].max())], marks=None)
        ], style={'marginBottom':'20px'}),

        html.Div([
            html.Div(dcc.Graph(id='sky-map'), style={'width':'49%', 'display':'inline-block'}),
            html.Div(dcc.Graph(id='timeline'), style={'width':'49%', 'display':'inline-block', 'verticalAlign':'top'})
        ]),

        html.Div(id='stats', style={'color':'#fff', 'marginTop':'10px'})
    ], style={'backgroundColor':'#0f0f1a', 'padding':'20px', 'minHeight':'100vh', 'fontFamily':'Arial'})

    @app.callback(
        [Output('sky-map', 'figure'), Output('timeline', 'figure'), Output('stats', 'children')],
        [Input('date-range', 'start_date'), Input('date-range', 'end_date'), Input('observatory', 'value'), Input('mag-range', 'value')]
    )
    def update(start_date, end_date, observatories, mag_range):
        dff = df.copy()
        if start_date:
            dff = dff[dff['Date'] >= pd.to_datetime(start_date)]
        if end_date:
            # include end date
            dff = dff[dff['Date'] <= (pd.to_datetime(end_date) + timedelta(days=1))]
        if observatories and 'ALL' not in observatories:
            dff = dff[dff['Location'].isin(observatories)]
        if mag_range:
            dff = dff[(dff['Magnitude'] >= mag_range[0]) & (dff['Magnitude'] <= mag_range[1])]

        sky = create_sky_map(dff)
        tl = create_timeline(dff)

        stats = html.Div([
            html.P(f'Total observations: {len(dff)}', style={'color':'#fff'})
        ])

        return sky, tl, stats

    return app

if __name__ == '__main__':
    app = serve()
    print('Starting Dash server at http://localhost:8050')
    # Use the new app.run() API for recent Dash versions
    try:
        app.run(host='0.0.0.0', port=8050, debug=False)
    except TypeError:
        # fallback for older versions
        app.run_server(host='0.0.0.0', port=8050, debug=False)
