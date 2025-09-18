
import matplotlib
matplotlib.use('TkAgg')  # 强制使用兼容弹窗的后端
import matplotlib.pyplot as plt
import requests
from lxml import html
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import time

# 获取世界主要城市天气数据
def fetch_city_weather():
    url = 'https://worldweather.wmo.int/en/home.html'
    resp = requests.get(url)
    tree = html.fromstring(resp.content)
    # 获取城市链接
    city_links = tree.xpath('//div[@id="myTabContent"]//a/@href')
    city_names = tree.xpath('//div[@id="myTabContent"]//a/text()')
    cities = []
    for name, link in zip(city_names, city_links):
        if not link.startswith('http'):
            link = 'https://worldweather.wmo.int' + link
        cities.append({'name': name.strip(), 'url': link})
    return cities

# 获取单个城市的气温和经纬度
def fetch_city_temp_and_location(city_url):
    resp = requests.get(city_url)
    tree = html.fromstring(resp.content)
    try:
        temp = tree.xpath('//span[@class="temp"]//text()')[0].replace('°C','').strip()
        temp = float(temp)
    except Exception:
        temp = None
    try:
        lat = float(tree.xpath('//meta[@name="latitude"]/@content')[0])
        lon = float(tree.xpath('//meta[@name="longitude"]/@content')[0])
    except Exception:
        lat, lon = None, None
    return temp, lat, lon

# 实时动画可视化
def animate_weather():
    import traceback
    import numpy as np
    import matplotlib.patheffects as pe
    try:
        plt.ion()
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(14, 7), facecolor='#181c24')
        ax = plt.axes(projection=ccrs.PlateCarree())
        fig.patch.set_facecolor('#181c24')
        ax.set_facecolor('#181c24')
        ax.add_feature(cfeature.COASTLINE, edgecolor='#00ffe7', linewidth=0.7)
        ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='#00ffe7', linewidth=0.5)
        ax.set_global()
        # 星空背景
        np.random.seed(42)
        star_x = np.random.uniform(-180, 180, 300)
        star_y = np.random.uniform(-90, 90, 150)
        ax.scatter(star_x, star_y, s=np.random.uniform(1, 8, 150), color='#ffffff22', alpha=0.5, zorder=0, transform=ccrs.PlateCarree())
        plt.show(block=False)
        # 强制窗口置顶
        try:
            fig_mgr = plt.get_current_fig_manager()
            if hasattr(fig_mgr.window, 'attributes'):
                fig_mgr.window.attributes('-topmost', 1)
        except Exception:
            pass
        # 动画参数
        anim_frames = 50  # 帧数更多
        anim_interval = 2  # 每帧秒数
        last_lats, last_lons, last_temps, last_names = None, None, None, None
        while True:
            print('Fetching data...')
            cities = fetch_city_weather()[:60]  # 展示更多城市
            lats, lons, temps, names = [], [], [], []
            for city in cities:
                temp, lat, lon = fetch_city_temp_and_location(city['url'])
                if temp is not None and lat is not None and lon is not None:
                    lats.append(lat)
                    lons.append(lon)
                    temps.append(temp)
                    names.append(city['name'])
            # 动画过渡
            if last_lats is not None and len(lats) == len(last_lats):
                for frame in range(anim_frames):
                    ax.clear()
                    ax.set_facecolor('#181c24')
                    ax.add_feature(cfeature.COASTLINE, edgecolor='#00ffe7', linewidth=0.7)
                    ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='#00ffe7', linewidth=0.5)
                    ax.set_global()
                    ax.scatter(star_x, star_y, s=np.random.uniform(1, 8, 150), color='#ffffff22', alpha=0.5, zorder=0, transform=ccrs.PlateCarree())
                    # 插值动画
                    interp_lats = np.array(last_lats) + (np.array(lats) - np.array(last_lats)) * (frame + 1) / anim_frames
                    interp_lons = np.array(last_lons) + (np.array(lons) - np.array(last_lons)) * (frame + 1) / anim_frames
                    interp_temps = np.array(last_temps) + (np.array(temps) - np.array(last_temps)) * (frame + 1) / anim_frames
                    # 闪烁/弹跳动画
                    bounce = 1 + 0.15 * np.sin(2 * np.pi * (frame / anim_frames) * 3)
                    scatter = ax.scatter(interp_lons, interp_lats, c=interp_temps, cmap='plasma', s=220*bounce, alpha=0.85, edgecolor='#fff', linewidth=1.5, zorder=3, transform=ccrs.PlateCarree())
                    for i, name in enumerate(names):
                        ax.text(interp_lons[i], interp_lats[i], name, fontsize=10*bounce, fontweight='bold', color='#fff',
                                path_effects=[pe.withStroke(linewidth=2, foreground='#181c24')],
                                ha='center', va='bottom', zorder=4, transform=ccrs.PlateCarree())
                    plt.title('🌏 World Cities Real-time Temperature', fontsize=18, color='#00ffe7', fontweight='bold', pad=20)
                    cbar = plt.colorbar(scatter, ax=ax, orientation='vertical', pad=0.02, aspect=30, shrink=0.7)
                    cbar.set_label('Temperature (°C)', color='#fff', fontsize=12)
                    cbar.ax.yaxis.set_tick_params(color='#fff')
                    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#fff', fontsize=10)
                    plt.draw()
                    plt.pause(anim_interval/anim_frames)
            # 静态展示新数据+闪烁
            for frame in range(anim_frames):
                ax.clear()
                ax.set_facecolor('#181c24')
                ax.add_feature(cfeature.COASTLINE, edgecolor='#00ffe7', linewidth=0.7)
                ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='#00ffe7', linewidth=0.5)
                ax.set_global()
                ax.scatter(star_x, star_y, s=np.random.uniform(1, 8, 150), color='#ffffff22', alpha=0.5, zorder=0, transform=ccrs.PlateCarree())
                bounce = 1 + 0.15 * np.sin(2 * np.pi * (frame / anim_frames) * 3)
                scatter = ax.scatter(lons, lats, c=temps, cmap='plasma', s=220*bounce, alpha=0.85, edgecolor='#fff', linewidth=1.5, zorder=3, transform=ccrs.PlateCarree())
                for i, name in enumerate(names):
                    ax.text(lons[i], lats[i], name, fontsize=10*bounce, fontweight='bold', color='#fff',
                            path_effects=[pe.withStroke(linewidth=2, foreground='#181c24')],
                            ha='center', va='bottom', zorder=4, transform=ccrs.PlateCarree())
                plt.title('🌏 World Cities Real-time Temperature', fontsize=18, color='#00ffe7', fontweight='bold', pad=20)
                cbar = plt.colorbar(scatter, ax=ax, orientation='vertical', pad=0.02, aspect=30, shrink=0.7)
                cbar.set_label('Temperature (°C)', color='#fff', fontsize=12)
                cbar.ax.yaxis.set_tick_params(color='#fff')
                plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#fff', fontsize=10)
                plt.draw()
                plt.pause(anim_interval/anim_frames)
            last_lats, last_lons, last_temps, last_names = lats, lons, temps, names
    except Exception as e:
        print('程序发生异常:', e)
        traceback.print_exc()
        input('按回车键退出...')

if __name__ == '__main__':
    animate_weather()
