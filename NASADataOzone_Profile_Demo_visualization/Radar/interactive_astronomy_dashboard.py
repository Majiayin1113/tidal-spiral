#!/usr/bin/env python3
"""
Interactive Astronomy Data Visualization Dashboard
使用Plotly Dash创建交互式天文观测数据可视化仪表板

功能特点:
- 交互式天空图 (RA vs Dec)
- 星等时间序列图
- 动态过滤器 (日期、观测站、星等)
- 平滑动画和过渡效果
- 丰富的悬停提示信息
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def load_astronomy_data():
    """加载天文观测数据"""
    print("📊 创建小行星2025RZ4观测数据...")
    
    # 基于真实的2025RZ4观测数据
    sample_data = {
        'Date_UT': [
            '2025-09-15.378449', '2025-09-15.422793', '2025-09-15.541162',
            '2025-09-15.553495', '2025-09-15.565869', '2025-09-15.578236',
            '2025-09-15.629894', '2025-09-15.630711', '2025-09-15.98560',
            '2025-09-15.99094', '2025-09-15.99610', '2025-09-16.223720',
            '2025-09-16.234160', '2025-09-16.244610', '2025-09-16.326648',
            '2025-09-16.335037', '2025-09-17.205840', '2025-09-17.213679',
            '2025-09-17.221510'
        ],
        'RA': [
            '02 48 26.656', '02 48 45.069', '02 49 37.002', '02 49 42.032',
            '02 49 47.114', '02 49 52.149', '02 50 13.262', '02 50 13.599',
            '02 52 51.66', '02 52 53.84', '02 52 56.01', '02 54 35.300',
            '02 54 39.590', '02 54 43.840', '02 55 17.97', '02 55 21.33',
            '03 01 29.920', '03 01 33.020', '03 01 36.090'
        ],
        'Dec': [
            '-04 14 06.78', '-04 20 17.52', '-04 36 32.92', '-04 38 15.53',
            '-04 39 59.09', '-04 41 41.98', '-04 48 51.82', '-04 48 58.67',
            '-05 38 22.9', '-05 39 06.5', '-05 39 48.5', '-06 09 23.00',
            '-06 10 48.60', '-06 12 14.30', '-06 24 49.2', '-06 25 57.6',
            '-08 20 50.40', '-08 21 52.50', '-08 22 54.30'
        ],
        'Magn': [
            20.74, 21.00, 20.54, 20.36, 20.39, 20.50, 20.25, 20.31,
            20.2, 20.4, 20.2, 20.8, 20.4, 20.5, 20.4, 20.7,
            20.4, 20.9, 20.7
        ],
        'Location': [
            'I41', 'I41', 'F52', 'F52', 'F52', 'F52', 'F51', 'F51',
            'M45', 'M45', 'M45', '807', '807', '807', 'H21', 'H21',
            '807', '807', '807'
        ],
        'Ref': [
            'UES045', 'UES045', 'XES045', 'XES045', 'XES045', 'XES045',
            'VES045', 'VES045', 'XES045', 'XES045', 'XES045', 'VES045',
            'VES045', 'VES045', 'VES045', 'VES045', 'VES045', 'VES045',
            'VES045'
        ]
    }
    
    df = pd.DataFrame(sample_data)
    
    # 观测站信息
    observatory_info = {
        'I41': 'Palomar Mountain-ZTF',
        'F52': 'Pan-STARRS 2, Haleakala',
        'F51': 'Pan-STARRS 1, Haleakala',
        'M45': 'Mauna Kea-UH/Tholen NEO',
        '807': 'Cerro Tololo-DECam',
        'H21': 'NEOWISE'
    }
    
    df['Observatory_Name'] = df['Location'].map(observatory_info)
    return df

def parse_coordinates(ra_str, dec_str):
    """解析RA/Dec坐标字符串转换为度"""
    try:
        # Parse RA (HH MM SS.sss) to degrees
        ra_parts = ra_str.strip().split()
        if len(ra_parts) == 3:
            ra_hours = float(ra_parts[0])
            ra_minutes = float(ra_parts[1])
            ra_seconds = float(ra_parts[2])
            ra_degrees = (ra_hours + ra_minutes/60.0 + ra_seconds/3600.0) * 15.0
        else:
            ra_degrees = float(ra_str)
        
        # Parse Dec (+/-DD MM SS.ss) to degrees
        dec_parts = dec_str.strip().split()
        if len(dec_parts) == 3:
            dec_sign = 1 if not dec_str.startswith('-') else -1
            dec_degrees_part = abs(float(dec_parts[0]))
            dec_minutes = float(dec_parts[1])
            dec_seconds = float(dec_parts[2])
            dec_degrees = dec_sign * (dec_degrees_part + dec_minutes/60.0 + dec_seconds/3600.0)
        else:
            dec_degrees = float(dec_str)
            
        return ra_degrees, dec_degrees
    except:
        return None, None

def preprocess_astronomy_data(df):
    """清理和准备天文数据"""
    print("🔧 预处理天文数据...")
    
    df_clean = df.copy()
    
    # 转换坐标
    df_clean['RA_deg'] = 0.0
    df_clean['Dec_deg'] = 0.0
    
    for i, row in df_clean.iterrows():
        ra_deg, dec_deg = parse_coordinates(row['RA'], row['Dec'])
        if ra_deg is not None and dec_deg is not None:
            df_clean.loc[i, 'RA_deg'] = ra_deg
            df_clean.loc[i, 'Dec_deg'] = dec_deg
    
    # 转换日期格式
    def parse_date(date_str):
        try:
            if '.' in date_str:
                date_part, fraction = date_str.split('.')
                fraction_hours = float('0.' + fraction) * 24
                base_date = datetime.strptime(date_part, '%Y-%m-%d')
                return base_date + timedelta(hours=fraction_hours)
            else:
                return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return datetime.now()
    
    df_clean['Date'] = df_clean['Date_UT'].apply(parse_date)
    df_clean['Date_str'] = df_clean['Date'].dt.strftime('%Y-%m-%d %H:%M')
    df_clean['RA_str'] = df_clean['RA']
    df_clean['Dec_str'] = df_clean['Dec']
    df_clean['Magnitude'] = pd.to_numeric(df_clean['Magn'], errors='coerce')
    df_clean['Point_Size'] = 50 + (22 - df_clean['Magnitude']) * 10
    
    print(f"✅ 处理了 {len(df_clean)} 个观测数据")
    print(f"📅 日期范围: {df_clean['Date'].min()} 到 {df_clean['Date'].max()}")
    print(f"🌟 星等范围: {df_clean['Magnitude'].min():.2f} 到 {df_clean['Magnitude'].max():.2f}")
    
    return df_clean

def create_sky_map(filtered_df, title="天空图 - RA vs Dec"):
    """创建交互式RA vs Dec散点图"""
    
    if filtered_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="当前过滤条件下没有数据",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title=title,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    fig = px.scatter(
        filtered_df,
        x='RA_deg',
        y='Dec_deg',
        color='Magnitude',
        size='Point_Size',
        color_continuous_scale='Viridis_r',
        hover_data={
            'RA_str': True,
            'Dec_str': True, 
            'Magnitude': ':.2f',
            'Location': True,
            'Observatory_Name': True,
            'Date_str': True,
            'RA_deg': False,
            'Dec_deg': False,
            'Point_Size': False
        },
        labels={
            'RA_deg': '赤经 (度)',
            'Dec_deg': '赤纬 (度)',
            'Magnitude': '星等'
        },
        title=title
    )
    
    fig.update_traces(
        hovertemplate=
        "<b>%{customdata[4]}</b><br>" +
        "赤经: %{customdata[0]}<br>" +
        "赤纬: %{customdata[1]}<br>" +
        "星等: %{customdata[2]}<br>" +
        "观测站: %{customdata[3]}<br>" +
        "日期: %{customdata[5]}<br>" +
        "<extra></extra>"
    )
    
    fig.update_layout(
        xaxis_title="赤经 (度)",
        yaxis_title="赤纬 (度)",
        font=dict(size=12),
        height=500,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(10,10,20,0.9)',
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.2)',
            zerolinecolor='rgba(255,255,255,0.2)'
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.2)',
            zerolinecolor='rgba(255,255,255,0.2)'
        )
    )
    
    fig.update_xaxes(autorange="reversed")
    return fig

def create_magnitude_timeline(filtered_df, title="星等随时间变化"):
    """创建交互式时间序列图"""
    
    if filtered_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="当前过滤条件下没有数据",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title=title,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    df_sorted = filtered_df.sort_values('Date')
    fig = go.Figure()
    
    color_map = {
        'I41': '#FF6B6B',   # 红色
        'F52': '#4ECDC4',   # 青色
        'F51': '#45B7D1',   # 蓝色
        'M45': '#96CEB4',   # 绿色
        '807': '#FFEAA7',   # 黄色
        'H21': '#DDA0DD'    # 紫色
    }
    
    for location in df_sorted['Location'].unique():
        location_data = df_sorted[df_sorted['Location'] == location]
        
        fig.add_trace(go.Scatter(
            x=location_data['Date'],
            y=location_data['Magnitude'],
            mode='lines+markers',
            name=f"{location} ({location_data['Observatory_Name'].iloc[0]})",
            line=dict(color=color_map.get(location, '#666666'), width=2),
            marker=dict(
                size=8,
                color=color_map.get(location, '#666666'),
                line=dict(width=1, color='white')
            ),
            customdata=np.stack([
                location_data['RA_str'],
                location_data['Dec_str'],
                location_data['Location'],
                location_data['Observatory_Name'],
                location_data['Date_str']
            ], axis=-1),
            hovertemplate=
            "<b>%{customdata[3]}</b><br>" +
            "日期: %{customdata[4]}<br>" +
            "星等: %{y:.2f}<br>" +
            "赤经: %{customdata[0]}<br>" +
            "赤纬: %{customdata[1]}<br>" +
            "观测站: %{customdata[2]}<br>" +
            "<extra></extra>"
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="观测日期",
        yaxis_title="星等",
        font=dict(size=12),
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(10,10,20,0.9)',
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.2)',
            zerolinecolor='rgba(255,255,255,0.2)'
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.2)',
            zerolinecolor='rgba(255,255,255,0.2)',
            autorange='reversed'
        ),
        legend=dict(
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='rgba(255,255,255,0.2)',
            borderwidth=1
        )
    )
    
    return fig

def filter_data(df, start_date, end_date, selected_observatories, magnitude_range):
    """根据用户选择过滤数据"""
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date) + timedelta(days=1)
    
    filtered_df = df.copy()
    
    # 日期过滤
    filtered_df = filtered_df[
        (filtered_df['Date'] >= start_datetime) & 
        (filtered_df['Date'] <= end_datetime)
    ]
    
    # 观测站过滤
    if selected_observatories and 'ALL' not in selected_observatories:
        filtered_df = filtered_df[filtered_df['Location'].isin(selected_observatories)]
    
    # 星等过滤
    filtered_df = filtered_df[
        (filtered_df['Magnitude'] >= magnitude_range[0]) &
        (filtered_df['Magnitude'] <= magnitude_range[1])
    ]
    
    return filtered_df

def create_stats_display(filtered_df, total_observations):
    """创建统计信息显示"""
    if filtered_df.empty:
        return html.Div([
            html.H4("📊 当前过滤条件下没有数据", style={'color': '#FF6B6B'})
        ])
    
    stats = {
        'total_obs': len(filtered_df),
        'observatories': len(filtered_df['Location'].unique()),
        'date_range': f"{filtered_df['Date'].min().strftime('%Y-%m-%d')} 至 {filtered_df['Date'].max().strftime('%Y-%m-%d')}",
        'mag_range': f"{filtered_df['Magnitude'].min():.2f} - {filtered_df['Magnitude'].max():.2f}",
        'percentage': (len(filtered_df) / total_observations) * 100 if total_observations > 0 else 0
    }
    
    return html.Div([
        html.H4("📊 当前选择统计", style={'color': '#4ECDC4', 'marginBottom': '15px'}),
        html.Div([
            html.Div([
                html.H5(f"{stats['total_obs']}", style={'color': '#FFFFFF', 'margin': '0'}),
                html.P("观测次数", style={'color': '#CCCCCC', 'margin': '0', 'fontSize': '12px'})
            ], style={'textAlign': 'center', 'width': '20%', 'display': 'inline-block'}),
            
            html.Div([
                html.H5(f"{stats['observatories']}", style={'color': '#FFFFFF', 'margin': '0'}),
                html.P("观测站", style={'color': '#CCCCCC', 'margin': '0', 'fontSize': '12px'})
            ], style={'textAlign': 'center', 'width': '20%', 'display': 'inline-block'}),
            
            html.Div([
                html.H5(f"{stats['percentage']:.1f}%", style={'color': '#FFFFFF', 'margin': '0'}),
                html.P("数据比例", style={'color': '#CCCCCC', 'margin': '0', 'fontSize': '12px'})
            ], style={'textAlign': 'center', 'width': '20%', 'display': 'inline-block'}),
            
            html.Div([
                html.P(f"📅 {stats['date_range']}", style={'color': '#CCCCCC', 'margin': '5px 0', 'fontSize': '12px'}),
                html.P(f"🌟 星等: {stats['mag_range']}", style={'color': '#CCCCCC', 'margin': '5px 0', 'fontSize': '12px'})
            ], style={'width': '40%', 'display': 'inline-block', 'paddingLeft': '20px'})
        ])
    ])

def create_astronomy_dashboard():
    """创建完整的天文仪表板"""
    
    # 加载和预处理数据
    df_raw = load_astronomy_data()
    df = preprocess_astronomy_data(df_raw)
    
    # 初始化Dash应用
    app = dash.Dash(__name__)
    app.title = "天文数据仪表板"
    
    # 创建过滤器组件
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    
    date_picker = dcc.DatePickerRange(
        id='date-picker-range',
        start_date=min_date,
        end_date=max_date,
        display_format='YYYY-MM-DD',
        style={'width': '100%', 'color': '#000000'}
    )
    
    observatories = df[['Location', 'Observatory_Name']].drop_duplicates()
    observatory_options = [
        {'label': '所有观测站', 'value': 'ALL'}
    ] + [
        {'label': f"{row['Location']} - {row['Observatory_Name']}", 'value': row['Location']}
        for _, row in observatories.iterrows()
    ]
    
    observatory_dropdown = dcc.Dropdown(
        id='observatory-dropdown',
        options=observatory_options,
        value='ALL',
        multi=True,
        placeholder="选择观测站...",
        style={'width': '100%', 'color': '#000000'}
    )
    
    mag_min = df['Magnitude'].min()
    mag_max = df['Magnitude'].max()
    
    magnitude_slider = dcc.RangeSlider(
        id='magnitude-slider',
        min=mag_min,
        max=mag_max,
        step=0.1,
        value=[mag_min, mag_max],
        marks={
            mag_min: f'{mag_min:.1f}',
            mag_max: f'{mag_max:.1f}',
            (mag_min + mag_max) / 2: f'{(mag_min + mag_max) / 2:.1f}'
        },
        tooltip={"placement": "bottom", "always_visible": True}
    )
    
    # 定义布局
    app.layout = html.Div([
        # 标题
        html.Div([
            html.H1("🌌 交互式天文数据仪表板", 
                   style={
                       'textAlign': 'center',
                       'color': '#FFFFFF',
                       'marginBottom': '10px',
                       'fontFamily': 'Arial, sans-serif'
                   }),
            html.P(f"观测数据可视化 • {len(df)} 个观测 • {len(df['Location'].unique())} 个观测站",
                  style={
                      'textAlign': 'center',
                      'color': '#CCCCCC',
                      'marginBottom': '30px',
                      'fontFamily': 'Arial, sans-serif'
                  })
        ], style={'backgroundColor': '#1e1e2e', 'padding': '20px', 'marginBottom': '20px'}),
        
        # 过滤器部分
        html.Div([
            html.H3("🔧 过滤器", style={'color': '#FFFFFF', 'marginBottom': '15px'}),
            
            html.Div([
                html.Label("📅 日期范围:", style={'color': '#FFFFFF', 'fontWeight': 'bold'}),
                date_picker
            ], style={'marginBottom': '20px'}),
            
            html.Div([
                html.Label("🔭 观测站:", style={'color': '#FFFFFF', 'fontWeight': 'bold'}),
                observatory_dropdown
            ], style={'marginBottom': '20px'}),
            
            html.Div([
                html.Label("🌟 星等范围:", style={'color': '#FFFFFF', 'fontWeight': 'bold'}),
                magnitude_slider
            ], style={'marginBottom': '20px'}),
            
        ], style={
            'backgroundColor': '#2d2d44', 
            'padding': '20px', 
            'borderRadius': '10px',
            'marginBottom': '20px'
        }),
        
        # 图表部分
        html.Div([
            html.Div([
                dcc.Graph(id='sky-map-chart')
            ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%'}),
            
            html.Div([
                dcc.Graph(id='timeline-chart')
            ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '2%'}),
        ]),
        
        # 统计部分
        html.Div([
            html.Div(id='stats-display', style={'color': '#FFFFFF'})
        ], style={
            'backgroundColor': '#2d2d44',
            'padding': '20px',
            'borderRadius': '10px',
            'marginTop': '20px'
        }),
        
    ], style={
        'backgroundColor': '#0f0f1a',
        'minHeight': '100vh',
        'padding': '20px',
        'fontFamily': 'Arial, sans-serif'
    })
    
    # 定义回调函数
    @app.callback(
        [Output('sky-map-chart', 'figure'),
         Output('timeline-chart', 'figure'),
         Output('stats-display', 'children')],
        [Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('observatory-dropdown', 'value'),
         Input('magnitude-slider', 'value')]
    )
    def update_charts(start_date, end_date, selected_observatories, magnitude_range):
        """根据过滤器选择更新所有图表"""
        
        filtered_df = filter_data(df, start_date, end_date, selected_observatories, magnitude_range)
        
        sky_map = create_sky_map(filtered_df, f"天空图 - {len(filtered_df)} 个观测")
        sky_map.update_layout(
            transition_duration=500,
            transition_easing="cubic-in-out"
        )
        
        timeline = create_magnitude_timeline(filtered_df, f"星等时间线 - {len(filtered_df)} 个观测")
        timeline.update_layout(
            transition_duration=500,
            transition_easing="cubic-in-out"
        )
        
        stats = create_stats_display(filtered_df, len(df))
        
        return sky_map, timeline, stats
    
    return app

if __name__ == "__main__":
    print("=" * 80)
    print("🌌 交互式天文数据仪表板")
    print("=" * 80)
    print("正在启动仪表板...")
    
    app = create_astronomy_dashboard()
    
    print("✅ 仪表板创建成功!")
    print("🚀 启动中...")
    print("")
    print("📊 功能特点:")
    print("   • 交互式天空图 (RA vs Dec)")
    print("   • 星等时间线，按观测站分色")
    print("   • 按日期、位置和星等实时过滤")
    print("   • 平滑过渡和动画效果")
    print("   • 丰富的悬停提示信息")
    print("")
    print("🎯 在浏览器中打开: http://localhost:8050")
    print("🔧 使用 Ctrl+C 停止服务器")
    print("")
    
    # 启动服务器
    app.run_server(debug=False, host='0.0.0.0', port=8050)