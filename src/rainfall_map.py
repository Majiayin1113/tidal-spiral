# Enhanced Rainfall Map with Animation and Interactive City Selection
import requests
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Placeholder: Replace with actual data fetching from website
cities = [
    ('Hong Kong', 22.3193, 114.1694, 2400),
    ('London', 51.5074, -0.1278, 600),
    ('Sydney', -33.8688, 151.2093, 1200),
    ('New York', 40.7128, -74.0060, 1200),
]

# Simulate rainfall changes over 12 months
rainfall_series = {
    city[0]: np.abs(np.sin(np.linspace(0, 2*np.pi, 12)) * city[3] * np.random.uniform(0.8, 1.2, 12)) for city in cities
}

months = [f'{i+1}月' for i in range(12)]
colors = ['#1f77b4', '#2ca02c', '#d62728', '#9467bd']

fig = plt.figure(figsize=(12,8))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_global()
ax.coastlines(linewidth=1.2)
ax.add_feature(cfeature.BORDERS, linewidth=0.8)
ax.add_feature(cfeature.LAND, facecolor='#f7f7f7')
ax.add_feature(cfeature.OCEAN, facecolor='#a2cffe')

def animate(month):
    ax.clear()
    ax.set_global()
    ax.coastlines(linewidth=1.2)
    ax.add_feature(cfeature.BORDERS, linewidth=0.8)
    ax.add_feature(cfeature.LAND, facecolor='#f7f7f7')
    ax.add_feature(cfeature.OCEAN, facecolor='#a2cffe')
    handles = []
    for i, city in enumerate(cities):
        lat, lon = city[1], city[2]
        rainfall = rainfall_series[city[0]][month]
        sc = ax.scatter(lon, lat, s=rainfall/2, c=colors[i], alpha=0.7, edgecolors='black', linewidths=1.5,
                   label=f'{city[0]}: {int(rainfall)}mm', transform=ccrs.PlateCarree(), zorder=5)
        ax.text(lon, lat, city[0], fontsize=12, color=colors[i], transform=ccrs.PlateCarree(), zorder=6, ha='center', va='bottom')
        handles.append(sc)
    # 只显示有内容的图例
    ax.legend([h for h in handles if h.get_label() and not h.get_label().startswith('_')],
              [h.get_label() for h in handles if h.get_label() and not h.get_label().startswith('_')],
              loc='lower left', frameon=False)
    ax.set_title(f'🌏 世界城市月降雨量气泡图 - {months[month]}', fontsize=20, color='#22223B', pad=20)
    ax.text(0.5, -0.08, '气泡大小表示降雨量，数据为模拟，仅供展示', fontsize=13, color='#22223B', ha='center', va='center', transform=ax.transAxes)

ani = animation.FuncAnimation(fig, animate, frames=12, interval=800, repeat=True)
plt.tight_layout()
plt.show()
