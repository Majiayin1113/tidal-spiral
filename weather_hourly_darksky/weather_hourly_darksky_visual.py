
# 单指标折线图+下拉菜单切换
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio

df = pd.read_csv('weather_hourly_darksky.csv')
df['time'] = pd.to_datetime(df['time'])

# 处理降水概率
if 'precipProbability' in df.columns:
    df['precip'] = df['precipProbability']
else:
    df['precip'] = df['precipType'].apply(lambda x: 1 if str(x).strip().lower() in ['rain','snow','sleet','hail'] else 0)

indicators = [
    {'col': 'temperature', 'name': '温度 (°C)', 'color': 'orange'},
    {'col': 'humidity', 'name': '湿度', 'color': 'blue'},
    {'col': 'windSpeed', 'name': '风速 (m/s)', 'color': 'green'},
    {'col': 'precip', 'name': '降水概率', 'color': 'purple'}
]

traces = []
for i, ind in enumerate(indicators):
    traces.append(go.Scatter(
        x=df['time'],
        y=df[ind['col']],
        mode='markers',
        name=ind['name'],
        line=dict(color=ind['color']),
        visible=True if i==0 else False
    ))

# 下拉菜单
updatemenus = [
    dict(
        active=0,
        buttons=[
            dict(label=ind['name'],
                 method='update',
                 args=[{'visible': [i==j for j in range(len(indicators))]},
                       {'yaxis': {'title': ind['name']}, 'title': f"{ind['name']}趋势"}])
            for i, ind in enumerate(indicators)
        ],
        direction='down',
        showactive=True,
        x=0.5,
        y=1.15,
        xanchor='center',
        yanchor='top',
    )
]

layout = go.Layout(
    title=f"{indicators[0]['name']}趋势",
    xaxis=dict(title="时间"),
    yaxis=dict(title=indicators[0]['name']),
    updatemenus=updatemenus
)

fig = go.Figure(data=traces, layout=layout)
pio.write_html(fig, file="weather_trend_interactive.html", auto_open=True)
