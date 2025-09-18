
# 动态多小行星雷达图（Plotly实现，支持交互和动画）
import pandas as pd
import numpy as np

import plotly.graph_objects as go
import plotly.io as pio
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

# HEX转RGBA
def hex_to_rgba(hex_color, alpha=0.3):
	import matplotlib.colors as mcolors
	rgb = mcolors.to_rgb(hex_color)
	return f'rgba({int(rgb[0]*255)},{int(rgb[1]*255)},{int(rgb[2]*255)},{alpha})'

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
			line=dict(color=color_list[idx % len(color_list)], width=5),
			marker=dict(size=12, color=color_list[idx % len(color_list)], line=dict(width=2, color='#fff')),
		fill='toself',
		fillcolor=hex_to_rgba(color_list[idx % len(color_list)], 0.3),  # 半透明填充
		opacity=0.85,
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
		line=dict(color=color_list[idx % len(color_list)], width=5),
		marker=dict(size=12, color=color_list[idx % len(color_list)], line=dict(width=2, color='#fff')),
	fill='toself',
	fillcolor=hex_to_rgba(color_list[idx % len(color_list)], 0.3),  # 半透明填充
	opacity=0.85,
		hovertemplate='<b>%{text}</b><br>%{theta}: %{r:.2f}',
		text=[row['name']] * (num_vars+1)
	))

# 布局
layout = go.Layout(
	title='小行星轨道参数动态雷达图',
	paper_bgcolor='#181c25',
	plot_bgcolor='#222',
	font=dict(color='#fff', size=18),
	polar=dict(
		bgcolor='#222',
		radialaxis=dict(
			visible=True,
			showticklabels=True,
			ticks='outside',
			linewidth=2,
			gridcolor='#444',
			gridwidth=2,
			linecolor='#888',
			tickfont=dict(color='#FECB52', size=14)
		),
		angularaxis=dict(
			linewidth=2,
			gridcolor='#444',
			gridwidth=2,
			linecolor='#888',
			tickfont=dict(color='#19D3F3', size=14)
		)
	),
	showlegend=True,
	legend=dict(x=1.05, y=1, bgcolor='#181c25', bordercolor='#444', borderwidth=1),
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

# 读取观测数据并生成表格
html_path = os.path.join(os.path.dirname(__file__), 'asteroid_radar_chart.html')
obs_file = os.path.join(os.path.dirname(__file__), '2025RZ4_observations.csv')
if os.path.exists(obs_file):
	obs_df = pd.read_csv(obs_file)
	obs_df['date'] = obs_df['Date_UT'].str.extract(r'2025\-(09-\d+)')[0]
	day_map = {'09-15': '9.15', '09-16': '9.16', '09-17': '9.17'}
	obs_df['day'] = obs_df['date'].map(day_map)
	tables = {}
	# 全部数据表
	all_df = obs_df.copy()
	tables['全部'] = go.Table(
		header=dict(values=list(all_df.columns[:-2]), fill_color='#222', font=dict(color='gold', size=14), align='center'),
		cells=dict(values=[all_df[c] for c in all_df.columns[:-2]], fill_color='#181c25', font=dict(color='white', size=12), align='center')
	)
	for day in ['9.15', '9.16', '9.17']:
		day_df = obs_df[obs_df['day'] == day]
		tables[day] = go.Table(
			header=dict(values=list(day_df.columns[:-2]), fill_color='#222', font=dict(color='gold', size=14), align='center'),
			cells=dict(values=[day_df[c] for c in day_df.columns[:-2]], fill_color='#181c25', font=dict(color='white', size=12), align='center')
		)
	# 生成切换按钮的JS
	html = '''<html><head><meta charset="utf-8"><title>小行星可视化</title>
	<script src="https://cdn.plot.ly/plotly-2.30.0.min.js"></script></head>
	<body style="background:#181c25; color:#fff;">
	<h2 style="color:gold;">小行星轨道参数动态雷达图</h2>''' + pio.to_html(fig, include_plotlyjs=False, full_html=False) + '''
		<h2 style="color:gold;">2025 RZ4 观测数据表</h2>
		<div style="text-align:center; margin:24px 0 12px 0;">
			<button style="background:#636EFA;color:#fff;border:none;padding:8px 18px;margin:0 8px;border-radius:6px;font-size:16px;cursor:pointer;" onclick="showTable('全部')">全部</button>
			<button style="background:#EF553B;color:#fff;border:none;padding:8px 18px;margin:0 8px;border-radius:6px;font-size:16px;cursor:pointer;" onclick="showTable('9.15')">9.15</button>
			<button style="background:#00CC96;color:#fff;border:none;padding:8px 18px;margin:0 8px;border-radius:6px;font-size:16px;cursor:pointer;" onclick="showTable('9.16')">9.16</button>
			<button style="background:#FFA15A;color:#fff;border:none;padding:8px 18px;margin:0 8px;border-radius:6px;font-size:16px;cursor:pointer;" onclick="showTable('9.17')">9.17</button>
		</div>
		<div id="table-container"></div>
	<script>
	var tables = {};
	'''
	for day in ['全部', '9.15', '9.16', '9.17']:
		html += f"tables['{day}'] = `{pio.to_html(go.Figure(data=[tables[day]]), include_plotlyjs=False, full_html=False)}`;\n"
	html += '''
	function showTable(day) {
	  document.getElementById('table-container').innerHTML = tables[day];
	  Plotly.Plots.resize('table-container');
	}
	showTable('全部');
	</script></body></html>'''
	with open(html_path, 'w', encoding='utf-8') as f:
		f.write(html)
	webbrowser.open('file://' + html_path)
else:
	pio.write_html(fig, file=html_path, auto_open=True)
