import pandas as pd
import plotly.express as px
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
csv = ROOT / 'Flower' / 'Iris.csv'
df = pd.read_csv(csv)
df['Species'] = df['Species'].str.replace('Iris-', '')

# group mean
df_mean = df.groupby('Species').mean().reset_index()
df_melt = df_mean.melt(id_vars='Species', value_vars=['SepalLengthCm','SepalWidthCm','PetalLengthCm','PetalWidthCm'], var_name='Feature', value_name='Value')

custom_colors = ["#E0D7C7", "#BE9F89", "#98C3C7", "#5399A0", "#1B2A31"]
fig = px.line_polar(df_melt, r='Value', theta='Feature', color='Species', line_close=True, color_discrete_sequence=custom_colors)
fig.update_traces(fill='toself', opacity=0.7)
fig.update_layout(
    polar=dict(
        bgcolor='black',
        radialaxis=dict(showgrid=True, gridcolor='gray', gridwidth=0.5),
        angularaxis=dict(showgrid=True, gridcolor='gray', gridwidth=0.5)
    ),
    paper_bgcolor='black',
    plot_bgcolor='black',
    font=dict(color='white'),
    title=dict(text='Iris Flower - Artistic Radar Chart', font=dict(size=22, color='white'))
)
fig.update_layout(
    updatemenus=[
        dict(
            type='dropdown',
            showactive=True,
            x=1.2, y=1,
            buttons=list([
                dict(label='All Species', method='update', args=[{'visible':[True,True,True]}]),
                dict(label='Iris-setosa', method='update', args=[{'visible':[True,False,False]}]),
                dict(label='Iris-versicolor', method='update', args=[{'visible':[False,True,False]}]),
                dict(label='Iris-virginica', method='update', args=[{'visible':[False,False,True]}]),
            ])
        )
    ]
)
out_html = Path(__file__).parent / 'iris_radar.html'
out_png = Path(__file__).parent / 'iris_radar.png'
fig.write_html(out_html, include_plotlyjs='cdn')
print('Wrote', out_html)
try:
    fig.write_image(out_png, scale=2)
    print('Wrote', out_png)
except Exception as e:
    print('PNG export failed:', e)
