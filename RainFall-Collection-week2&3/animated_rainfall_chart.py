
# 动态地图动画和折线图结合
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.colors import Normalize

# 生成模拟降雨数据
np.random.seed(42)
months = np.arange(1, 13)
years = np.arange(1925, 2025)
cities = [
    ('Hong Kong', 22.3193, 114.1694),
    ('London', 51.5074, -0.1278),
    ('Sydney', -33.8688, 151.2093),
    ('New York', 40.7128, -74.0060),
]
rainfall_data = {
    city[0]: np.random.uniform(50, 300, size=(len(years), len(months))) for city in cities
}

# 热力图网格
lon_grid = np.linspace(-180, 180, 60)
lat_grid = np.linspace(-60, 80, 40)
heatmap = np.zeros((len(lat_grid), len(lon_grid)))

# 创建双子图：左地图，右折线
fig, (ax_map, ax_line) = plt.subplots(1, 2, figsize=(15, 7))
colors = ['#1f77b4', '#2ca02c', '#d62728', '#9467bd']
markers = ['o', 's', '^', 'D']

def animate(frame):
    year_idx = frame // 12
    month_idx = frame % 12
    # --- 地图动画 ---
    ax_map.clear()
    ax_map.set_xlim(-180, 180)
    ax_map.set_ylim(-60, 80)
    ax_map.set_xlabel('Longitude')
    ax_map.set_ylabel('Latitude')
    ax_map.set_title(f'Map: {years[year_idx]} Month {months[month_idx]}')
    heatmap.fill(0)
    for i, city in enumerate(cities):
        lat, lon = city[1], city[2]
        rainfall = rainfall_data[city[0]][year_idx, month_idx]
        lat_idx = np.abs(lat_grid - lat).argmin()
        lon_idx = np.abs(lon_grid - lon).argmin()
        heatmap[lat_idx, lon_idx] += rainfall
        ax_map.scatter(lon, lat, s=rainfall, c=colors[i], marker=markers[i], alpha=0.8, edgecolors='black', label=f'{city[0]}: {int(rainfall)}mm')
    norm = Normalize(vmin=0, vmax=300)
    ax_map.imshow(heatmap, extent=[-180,180,-60,80], origin='lower', cmap='YlGnBu', alpha=0.4, aspect='auto')
    ax_map.legend(loc='lower left')
    # --- 折线图 ---
    ax_line.clear()
    for i, city in enumerate(cities):
        # 取当前年份所有月份的降雨量
        ax_line.plot(months, rainfall_data[city[0]][year_idx], label=city[0], color=colors[i], marker=markers[i])
        # 当前月高亮点
        ax_line.scatter(months[month_idx], rainfall_data[city[0]][year_idx, month_idx], color=colors[i], s=100, edgecolors='black', zorder=5)
    ax_line.set_xticks(months)
    ax_line.set_xlabel('Month')
    ax_line.set_ylabel('Rainfall (mm)')
    ax_line.set_title(f'Rainfall Line Chart: {years[year_idx]}')
    ax_line.legend()
    ax_line.grid(True, linestyle='--', alpha=0.5)

ani = animation.FuncAnimation(fig, animate, frames=len(years)*len(months), interval=100, repeat=True)
plt.tight_layout()

# 保存为GIF
print("正在生成GIF动画...")
ani.save('rainfall_animation.gif', writer='pillow', fps=10, dpi=100)
print("GIF动画已保存为 'rainfall_animation.gif'")

# 如果想要显示动画，取消下面行的注释
# plt.show()
