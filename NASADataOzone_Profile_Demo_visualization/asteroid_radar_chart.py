
# 动态多小行星雷达图（Plotly实现，支持交互和动画）
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# 读取数据
file = os.path.join(os.path.dirname(__file__), 'asteroid_orbital_elements.csv')
df = pd.read_csv(file)

# 维度标签
labels = ['inclination', 'eccentricity', 'semimajor_axis', 'delta_v', 'H']
num_vars = len(labels)

# 颜色列表
color_list = [
	'#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A',
	'#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52'
]

# 闭合雷达图
def close_vals(vals):
	return np.concatenate([vals, [vals[0]]])

# 动画帧生成
frames = []
max_steps = 30  # 动画步数
for step in range(1, max_steps+1):
	frame_data = []
	for idx, row in df.iterrows():
		vals = row[labels].values.astype(float)
		vals = close_vals(vals)
		# 动态步进
		vals_anim = vals[0] + (vals - vals[0]) * step / max_steps
		frame_data.append(go.Scatterpolar(
			r=vals_anim,
			theta=labels + [labels[0]],
			mode='lines+markers',
			name=row['name'],
			line=dict(color=color_list[idx % len(color_list)], width=3),
			marker=dict(size=8),
			hovertemplate='<b>%{text}</b><br>%{theta}: %{r:.2f}',
			text=[row['name']] * (num_vars+1)
		))
	frames.append(go.Frame(data=frame_data, name=str(step)))

# 静态初始帧
data = []
for idx, row in df.iterrows():
	vals = row[labels].values.astype(float)
	vals = close_vals(vals)
	vals_anim = vals[0] + (vals - vals[0]) * 1 / max_steps
	data.append(go.Scatterpolar(
		r=vals_anim,
		theta=labels + [labels[0]],
		mode='lines+markers',
		name=row['name'],
		line=dict(color=color_list[idx % len(color_list)], width=3),
		marker=dict(size=8),
		hovertemplate='<b>%{text}</b><br>%{theta}: %{r:.2f}',
		text=[row['name']] * (num_vars+1)
	))

# 布局
layout = go.Layout(
	title='小行星轨道参数动态雷达图',
	polar=dict(
		radialaxis=dict(visible=True, showticklabels=True, ticks='outside', linewidth=2)
	),
	showlegend=True,
	legend=dict(x=1.05, y=1),
	updatemenus=[dict(
		type='buttons',
		showactive=False,
		buttons=[dict(label='播放动画', method='animate', args=[None, {'frame': {'duration': 60, 'redraw': True}, 'fromcurrent': True}])]
	)]
)

fig = go.Figure(data=data, layout=layout, frames=frames)
# 保存为HTML并自动打开
import plotly.io as pio
import webbrowser
html_path = os.path.join(os.path.dirname(__file__), 'asteroid_radar_chart.html')
pio.write_html(fig, file=html_path, auto_open=True)
