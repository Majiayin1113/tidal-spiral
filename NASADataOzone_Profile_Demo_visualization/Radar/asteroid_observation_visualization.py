#!/usr/bin/env python3
"""
小行星2025RZ4观测数据可视化
包含天体坐标图、地面观测站地图、星等变化图和动画GIF生成
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 读取观测数据
data_file = '2025RZ4_observations.csv'
df = pd.read_csv(data_file)

# 观测站信息 (MPC代码到地理坐标的映射)
observatory_info = {
    'I41': {'name': 'Palomar Mountain-ZTF', 'lat': 33.3563, 'lon': -116.8648, 'country': 'USA'},
    'F52': {'name': 'Gaia-ESA Space Observatory', 'lat': 0, 'lon': 0, 'country': 'Space'},  # L2点
    'F51': {'name': 'Pan-STARRS 1, Haleakala', 'lat': 20.7084, 'lon': -156.2571, 'country': 'USA'},
    'M45': {'name': 'Mauna Kea-UH/Tholen NEO Follow-Up', 'lat': 19.8283, 'lon': -155.4783, 'country': 'USA'},
    '807': {'name': 'Cerro Tololo-DECam', 'lat': -30.1674, 'lon': -70.8151, 'country': 'Chile'},
    'H21': {'name': 'NEOWISE', 'lat': 0, 'lon': 0, 'country': 'Space'}  # 太空观测站
}

def parse_coordinates(ra_str, dec_str):
    """解析RA和Dec坐标字符串转换为度"""
    # RA格式: "HH MM SS.sss"
    ra_parts = ra_str.split()
    ra_hours = float(ra_parts[0])
    ra_minutes = float(ra_parts[1])
    ra_seconds = float(ra_parts[2])
    ra_degrees = (ra_hours + ra_minutes/60.0 + ra_seconds/3600.0) * 15.0  # 转换为度
    
    # Dec格式: "+/-DD MM SS.ss"
    dec_parts = dec_str.split()
    dec_sign = 1 if dec_str.startswith('+') or not dec_str.startswith('-') else -1
    dec_degrees_part = abs(float(dec_parts[0]))
    dec_minutes = float(dec_parts[1])
    dec_seconds = float(dec_parts[2])
    dec_degrees = dec_sign * (dec_degrees_part + dec_minutes/60.0 + dec_seconds/3600.0)
    
    return ra_degrees, dec_degrees

# 处理坐标数据
df['RA_deg'] = 0.0
df['Dec_deg'] = 0.0

for i, row in df.iterrows():
    ra_deg, dec_deg = parse_coordinates(row['RA'], row['Dec'])
    df.loc[i, 'RA_deg'] = ra_deg
    df.loc[i, 'Dec_deg'] = dec_deg

# 转换日期格式
df['Date'] = pd.to_datetime(df['Date_UT'], format='%Y-%m-%d.%f')

# 创建综合可视化
fig = plt.figure(figsize=(20, 12))
plt.style.use('dark_background')

# 设置子图
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
ax_sky = fig.add_subplot(gs[0:2, 0:2])  # 天体坐标图
ax_map = fig.add_subplot(gs[0, 2])      # 观测站地图
ax_mag = fig.add_subplot(gs[1, 2])      # 星等变化
ax_info = fig.add_subplot(gs[2, :])     # 信息面板

# 颜色方案
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
observatory_colors = {obs: colors[i] for i, obs in enumerate(observatory_info.keys())}

def plot_sky_chart(ax, frame_idx=None):
    """绘制天体坐标图"""
    ax.clear()
    ax.set_facecolor('#0a0a1a')
    
    # 如果是动画，只显示到当前帧
    if frame_idx is not None:
        current_data = df.iloc[:frame_idx+1]
    else:
        current_data = df
    
    # 按观测站分组绘制轨迹
    for obs_code in observatory_info.keys():
        obs_data = current_data[current_data['Location'] == obs_code]
        if len(obs_data) > 0:
            # 绘制轨迹线
            ax.plot(obs_data['RA_deg'], obs_data['Dec_deg'], 
                   color=observatory_colors[obs_code], alpha=0.7, linewidth=2,
                   label=f"{obs_code} ({observatory_info[obs_code]['name'][:15]}...)")
            
            # 绘制观测点
            scatter = ax.scatter(obs_data['RA_deg'], obs_data['Dec_deg'], 
                               c=obs_data['Magn'], cmap='plasma_r', 
                               s=60, edgecolors=observatory_colors[obs_code], 
                               linewidth=2, alpha=0.8)
    
    # 如果是动画模式，高亮当前点
    if frame_idx is not None and frame_idx < len(df):
        current_point = df.iloc[frame_idx]
        ax.scatter([current_point['RA_deg']], [current_point['Dec_deg']], 
                  s=200, c='yellow', marker='*', edgecolors='white', linewidth=2,
                  label='当前位置')
    
    ax.set_xlabel('赤经 (度)', fontsize=12, color='white')
    ax.set_ylabel('赤纬 (度)', fontsize=12, color='white')
    ax.set_title('小行星2025RZ4天体坐标轨迹\nPan-STARRS 2初始发现观测', 
                fontsize=14, color='white', weight='bold')
    ax.grid(True, alpha=0.3, color='gray')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    
    # 添加颜色条
    if not current_data.empty:
        cbar = plt.colorbar(scatter, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('星等 (Magnitude)', rotation=270, labelpad=15, color='white')
        cbar.ax.yaxis.label.set_color('white')
        cbar.ax.tick_params(colors='white')

def plot_observatory_map(ax):
    """绘制观测站地图"""
    ax.clear()
    ax.set_facecolor('#0a0a1a')
    
    # 绘制世界地图轮廓（简化版）
    world_lats = np.linspace(-60, 80, 100)
    world_lons = np.linspace(-180, 180, 200)
    
    # 地面观测站
    ground_obs = {k: v for k, v in observatory_info.items() 
                  if v['country'] != 'Space'}
    
    for obs_code, info in ground_obs.items():
        obs_count = len(df[df['Location'] == obs_code])
        ax.scatter(info['lon'], info['lat'], 
                  s=obs_count*30, c=observatory_colors[obs_code], 
                  alpha=0.8, edgecolors='white', linewidth=2,
                  label=f"{obs_code}: {obs_count}次观测")
        
        # 添加标签
        ax.annotate(obs_code, (info['lon'], info['lat']), 
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=10, color='white', weight='bold')
    
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 80)
    ax.set_xlabel('经度', fontsize=12, color='white')
    ax.set_ylabel('纬度', fontsize=12, color='white')
    ax.set_title('地面观测站分布', fontsize=14, color='white', weight='bold')
    ax.grid(True, alpha=0.3, color='gray')
    ax.legend(fontsize=8, loc='lower left')

def plot_magnitude_timeline(ax, frame_idx=None):
    """绘制星等时间变化图"""
    ax.clear()
    ax.set_facecolor('#0a0a1a')
    
    if frame_idx is not None:
        current_data = df.iloc[:frame_idx+1]
    else:
        current_data = df
    
    # 按观测站分组
    for obs_code in observatory_info.keys():
        obs_data = current_data[current_data['Location'] == obs_code]
        if len(obs_data) > 0:
            ax.plot(obs_data['Date'], obs_data['Magn'], 
                   'o-', color=observatory_colors[obs_code], 
                   alpha=0.8, linewidth=2, markersize=6,
                   label=obs_code)
    
    ax.set_xlabel('观测日期', fontsize=12, color='white')
    ax.set_ylabel('星等', fontsize=12, color='white')
    ax.set_title('星等随时间变化', fontsize=14, color='white', weight='bold')
    ax.grid(True, alpha=0.3, color='gray')
    ax.legend(fontsize=8)
    ax.tick_params(axis='x', rotation=45, colors='white')
    ax.tick_params(axis='y', colors='white')
    
    # 反转y轴（星等越小越亮）
    ax.invert_yaxis()

def plot_info_panel(ax, frame_idx=None):
    """信息面板"""
    ax.clear()
    ax.set_facecolor('#0a0a1a')
    ax.axis('off')
    
    # 基本信息
    info_text = """
小行星2025RZ4观测数据分析
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 观测统计:
   • 观测总数: {} 次
   • 观测时间跨度: {} 至 {}
   • 参与观测站: {} 个
   • 星等范围: {:.2f} - {:.2f}

🔭 主要观测站:
   • F51 (Pan-STARRS 1, Haleakala): 初始发现者
   • 807 (Cerro Tololo-DECam): 南半球主要观测
   • I41 (Palomar Mountain-ZTF): 北半球跟踪
   • M45 (Mauna Kea): 夏威夷观测

📈 发现意义:
   • Pan-STARRS 2首次报告的近地小行星
   • 为轨道确定提供了关键的初始观测数据
   • 展示了全球观测网络的协作能力
    """.format(
        len(df),
        df['Date'].min().strftime('%Y-%m-%d'),
        df['Date'].max().strftime('%Y-%m-%d'),
        df['Location'].nunique(),
        df['Magn'].min(),
        df['Magn'].max()
    )
    
    if frame_idx is not None and frame_idx < len(df):
        current_obs = df.iloc[frame_idx]
        current_info = f"""
🎯 当前观测 (第{frame_idx+1}/{len(df)}次):
   • 日期: {current_obs['Date'].strftime('%Y-%m-%d %H:%M')}
   • 观测站: {current_obs['Location']} ({observatory_info.get(current_obs['Location'], {}).get('name', '未知')})
   • 坐标: RA {current_obs['RA']}, Dec {current_obs['Dec']}
   • 星等: {current_obs['Magn']}
        """
        info_text += current_info
    
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
            fontsize=11, color='white', verticalalignment='top',
            fontfamily='monospace')

# 静态图表
def create_static_visualization():
    """创建静态可视化"""
    plot_sky_chart(ax_sky)
    plot_observatory_map(ax_map)
    plot_magnitude_timeline(ax_mag)
    plot_info_panel(ax_info)
    
    plt.suptitle('小行星2025RZ4观测数据可视化 - Pan-STARRS 2初始发现', 
                fontsize=16, color='white', weight='bold', y=0.98)
    
    plt.tight_layout()
    plt.savefig('asteroid_2025RZ4_static_analysis.png', dpi=150, bbox_inches='tight',
                facecolor='#0a0a1a', edgecolor='none')
    print("静态图表已保存为: asteroid_2025RZ4_static_analysis.png")

# 动画函数
def animate_frame(frame):
    """动画帧更新函数"""
    plot_sky_chart(ax_sky, frame)
    plot_magnitude_timeline(ax_mag, frame)
    plot_info_panel(ax_info, frame)
    
    # 观测站地图保持静态
    if frame == 0:  # 只在第一帧绘制一次
        plot_observatory_map(ax_map)

def create_animation():
    """创建动画GIF"""
    print("正在生成动画...")
    
    # 重新绘制观测站地图
    plot_observatory_map(ax_map)
    
    # 创建动画
    anim = animation.FuncAnimation(fig, animate_frame, frames=len(df), 
                                 interval=800, repeat=True, blit=False)
    
    plt.suptitle('小行星2025RZ4观测数据动画 - Pan-STARRS 2初始发现', 
                fontsize=16, color='white', weight='bold', y=0.98)
    
    # 保存为GIF
    anim.save('asteroid_2025RZ4_observation_animation.gif', 
              writer='pillow', fps=1.25, dpi=100)
    print("动画GIF已保存为: asteroid_2025RZ4_observation_animation.gif")
    
    return anim

if __name__ == "__main__":
    print("=" * 60)
    print("小行星2025RZ4观测数据可视化")
    print("=" * 60)
    
    # 创建静态可视化
    print("\n1. 创建静态分析图表...")
    create_static_visualization()
    
    # 创建动画
    print("\n2. 创建动画GIF...")
    anim = create_animation()
    
    print("\n✅ 可视化完成!")
    print("生成的文件:")
    print("  - asteroid_2025RZ4_static_analysis.png (静态分析图)")
    print("  - asteroid_2025RZ4_observation_animation.gif (动态观测动画)")
    
    # 显示图表（可选）
    # plt.show()