# Enhanced Rainfall Map with Animation and Interactive City Selection
import requests
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.animation as animation
import numpy as np

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

fig, ax = plt.subplots(figsize=(10,7))
m = Basemap(projection='merc',llcrnrlat=-60,urcrnrlat=80,llcrnrlon=-180,urcrnrlon=180,resolution='c', ax=ax)
m.drawcoastlines()
m.drawcountries()

scatters = []
colors = ['#1f77b4', '#2ca02c', '#d62728', '#9467bd']

def animate(month):
    ax.clear()
    m.drawcoastlines()
    m.drawcountries()
    for i, city in enumerate(cities):
        lat, lon = city[1], city[2]
        rainfall = rainfall_series[city[0]][month]
        x, y = m(lon, lat)
        ax.scatter(x, y, s=rainfall/4, c=colors[i], alpha=0.7, label=f'{city[0]}: {int(rainfall)}mm')
    ax.legend(loc='lower left')
    ax.set_title(f'Rainfall by City - Month {month+1}')

ani = animation.FuncAnimation(fig, animate, frames=12, interval=800, repeat=True)
plt.show()
