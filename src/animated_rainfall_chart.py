# Enhanced Animated Rainfall Chart with Smooth Transitions, Heatmap, and Custom Markers
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.colors import Normalize

# Generate synthetic rainfall data for 100 years
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

# Create a heatmap grid
lon_grid = np.linspace(-180, 180, 60)
lat_grid = np.linspace(-60, 80, 40)
heatmap = np.zeros((len(lat_grid), len(lon_grid)))

fig, ax = plt.subplots(figsize=(10,7))
ax.set_xlim(-180, 180)
ax.set_ylim(-60, 80)
ax.set_title('Monthly Average Rainfall (Animated)')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

colors = ['#1f77b4', '#2ca02c', '#d62728', '#9467bd']
markers = ['o', 's', '^', 'D']

def animate(frame):
    ax.clear()
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 80)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    year_idx = frame // 12
    month_idx = frame % 12
    # Update heatmap
    heatmap.fill(0)
    for i, city in enumerate(cities):
        lat, lon = city[1], city[2]
        rainfall = rainfall_data[city[0]][year_idx, month_idx]
        # Find nearest grid cell
        lat_idx = np.abs(lat_grid - lat).argmin()
        lon_idx = np.abs(lon_grid - lon).argmin()
        heatmap[lat_idx, lon_idx] += rainfall
        ax.scatter(lon, lat, s=rainfall, c=colors[i], marker=markers[i], alpha=0.8, edgecolors='black', label=f'{city[0]}: {int(rainfall)}mm')
    # Show heatmap
    norm = Normalize(vmin=0, vmax=300)
    ax.imshow(heatmap, extent=[-180,180,-60,80], origin='lower', cmap='YlGnBu', alpha=0.4, aspect='auto')
    ax.legend(loc='lower left')
    ax.set_title(f'Monthly Average Rainfall: {years[year_idx]} Month {months[month_idx]}')

ani = animation.FuncAnimation(fig, animate, frames=len(years)*len(months), interval=100, repeat=True)
plt.show()
