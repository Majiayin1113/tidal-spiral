# Rainfall Map 2: Generative Art & Data Visualization Suite
# 1. Moving Spiral Visualization using Tidal Data (Pygame)
# 2. Rainfall Chart by City on a Map (Matplotlib, fetch from web)
# 3. Animated Chart: Monthly Average Rainfall as Colored Dots on Map (Matplotlib)

import pygame
import math
import random
import sys
import requests
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# --- 1. Moving Spiral Visualization using Tidal Data (Pygame) ---
WIDTH, HEIGHT = 800, 800
FPS = 60
TIDAL_DATA = [math.sin(i/20.0)*100+200 for i in range(2000)]

def spiral_visualization():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    angle = 0
    step = 0
    speed = 1
    thickness = 2
    running = True
    def get_color(i, total):
        t = i / total
        r = int(100 + 155 * t)
        g = int(100 + 155 * (1-t))
        b = int(200 + 55 * math.sin(t * math.pi))
        return (r, g, b)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    speed += 1
                elif event.key == pygame.K_DOWN:
                    speed = max(1, speed-1)
                elif event.key == pygame.K_RIGHT:
                    thickness += 1
                elif event.key == pygame.K_LEFT:
                    thickness = max(1, thickness-1)
        screen.fill((10, 10, 30))
        center = (WIDTH//2, HEIGHT//2)
        points = []
        total = 400
        for i, tide in enumerate(TIDAL_DATA[step:step+total]):
            a = angle + i * 0.12
            r = 120 + tide + 30*math.sin(i/15.0 + angle)
            x = int(center[0] + r * math.cos(a))
            y = int(center[1] + r * math.sin(a))
            color = get_color(i, total)
            if i > 0:
                pygame.draw.line(screen, color, points[-1], (x, y), thickness)
            points.append((x, y))
        angle += 0.01 * speed
        step = (step + speed) % len(TIDAL_DATA)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

# --- 2. Rainfall Chart by City on a Map (Matplotlib, fetch from web) ---
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

def rainfall_map():
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
        for i, city in enumerate(cities):
            lat, lon = city[1], city[2]
            rainfall = rainfall_series[city[0]][month]
            ax.scatter(lon, lat, s=rainfall/2, c=colors[i], alpha=0.7, edgecolors='black', linewidths=1.5,
                       label=f'{city[0]}: {int(rainfall)}mm', transform=ccrs.PlateCarree(), zorder=5)
            ax.text(lon, lat, city[0], fontsize=12, color=colors[i], transform=ccrs.PlateCarree(), zorder=6, ha='center', va='bottom')
        ax.legend(loc='lower left')
        ax.set_title(f'🌏 世界城市月降雨量气泡图 - {months[month]}', fontsize=20, color='#22223B', pad=20)
        ax.text(0.5, -0.08, '气泡大小表示降雨量，数据为模拟，仅供展示', fontsize=13, color='#22223B', ha='center', va='center', transform=ax.transAxes)
    ani = animation.FuncAnimation(fig, animate, frames=12, interval=800, repeat=True)
    plt.tight_layout()
    plt.show()

# --- 3. Animated Chart: Monthly Average Rainfall as Colored Dots on Map (Matplotlib) ---
years = np.arange(1925, 2025)
city_coords = [(22.3193, 114.1694), (51.5074, -0.1278), (-33.8688, 151.2093), (40.7128, -74.0060)]
city_names = [city[0] for city in cities]

rainfall_data = {
    city: np.random.uniform(50, 300, size=(len(years), len(months))) for city in city_names
}

def animated_rainfall_chart():
    fig, ax = plt.subplots(figsize=(12,8))
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 80)
    ax.set_title('Monthly Average Rainfall (Animated)')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    def animate(frame):
        ax.clear()
        ax.set_xlim(-180, 180)
        ax.set_ylim(-60, 80)
        year_idx = frame // 12
        month_idx = frame % 12
        for i, city in enumerate(city_names):
            lat, lon = city_coords[i]
            rainfall = rainfall_data[city][year_idx, month_idx]
            ax.scatter(lon, lat, s=rainfall, c=colors[i], alpha=0.8, edgecolors='black', label=f'{city}: {int(rainfall)}mm')
            ax.text(lon, lat, city, fontsize=12, color=colors[i], ha='center', va='bottom')
        ax.legend(loc='lower left')
        ax.set_title(f'Monthly Average Rainfall: {years[year_idx]} Month {months[month_idx]}')
    ani = animation.FuncAnimation(fig, animate, frames=len(years)*len(months), interval=100, repeat=True)
    plt.tight_layout()
    plt.show()

# --- Main Entrypoint ---
if __name__ == '__main__':
    # spiral_visualization()  # 运行潮汐螺旋艺术
    rainfall_map()          # 运行城市降雨气泡地图动画
    # animated_rainfall_chart() # Uncomment to run animated rainfall chart
