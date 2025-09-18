data = [
    ["2025-09-15.378449", "02 48 26.656", "-04 14 06.78", 20.74],
    ["2025-09-15.422793", "02 48 45.069", "-04 20 17.52", 21.00],
    ["2025-09-15.541162", "02 49 37.002", "-04 36 32.92", 20.54],
    ["2025-09-15.553495", "02 49 42.032", "-04 38 15.53", 20.36],
    ["2025-09-15.565869", "02 49 47.114", "-04 39 59.09", 20.39],
    ["2025-09-15.578236", "02 49 52.149", "-04 41 41.98", 20.50],
    ["2025-09-15.629894", "02 50 13.262", "-04 48 51.82", 20.25],
    ["2025-09-15.630711", "02 50 13.599", "-04 48 58.67", 20.31],
    ["2025-09-15.98560", "02 52 51.66", "-05 38 22.9", 20.2],
    ["2025-09-15.99094", "02 52 53.84", "-05 39 06.5", 20.4],
    ["2025-09-15.99610", "02 52 56.01", "-05 39 48.5", 20.2],
    ["2025-09-16.223720", "02 54 35.300", "-06 09 23.00", 20.8],
    ["2025-09-16.234160", "02 54 39.590", "-06 10 48.60", 20.4],
    ["2025-09-16.244610", "02 54 43.840", "-06 12 14.30", 20.5],
    ["2025-09-16.326648", "02 55 17.97", "-06 24 49.2", 20.4],
    ["2025-09-16.335037", "02 55 21.33", "-06 25 57.6", 20.7],
    ["2025-09-17.205840", "03 01 29.920", "-08 20 50.40", 20.4],
    ["2025-09-17.213679", "03 01 33.020", "-08 21 52.50", 20.9],
    ["2025-09-17.221510", "03 01 36.090", "-08 22 54.30", 20.7],
]
def hms_to_deg(hms):
    h, m, s = [float(x) for x in hms.split()]
    return 15 * (h + m/60 + s/3600)
def dms_to_deg(dms):
    sign = -1 if dms.strip().startswith('-') else 1
    dms = dms.replace('-', '').replace('+', '')
    d, m, s = [float(x) for x in dms.split()]
    return sign * (d + m/60 + s/3600)
dec = [dms_to_deg(row[2]) for row in data]
mag = [row[3] for row in data]
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

def hms_to_deg(hms):
    h, m, s = [float(x) for x in hms.split()]
    return 15 * (h + m/60 + s/3600)

def dms_to_deg(dms):
    sign = -1 if dms.strip().startswith('-') else 1
    dms = dms.replace('-', '').replace('+', '')
    d, m, s = [float(x) for x in dms.split()]
    return sign * (d + m/60 + s/3600)

ra = [hms_to_deg(row[1]) for row in data]
dec = [dms_to_deg(row[2]) for row in data]
mag = [row[3] for row in data]

fig, ax = plt.subplots(figsize=(8,6))
sc = ax.scatter([], [], c=[], cmap='viridis_r', s=60, edgecolor='k')
cb = plt.colorbar(sc, label='Magnitude')
ax.invert_xaxis()
ax.set_xlabel('RA (deg)')
ax.set_ylabel('Dec (deg)')
ax.set_title('2025 RZ4 Observed Sky Path (Animated)')
ax.grid(True, linestyle='--', alpha=0.5)
ax.set_xlim(max(ra)+1, min(ra)-1)
ax.set_ylim(min(dec)-1, max(dec)+1)

def animate(i):
    ax.clear()
    ax.scatter(ra[:i+1], dec[:i+1], c=mag[:i+1], cmap='viridis_r', s=60, edgecolor='k')
    ax.invert_xaxis()
    ax.set_xlabel('RA (deg)')
    ax.set_ylabel('Dec (deg)')
    ax.set_title(f'2025 RZ4 Observed Sky Path (Frame {i+1})')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_xlim(max(ra)+1, min(ra)-1)
    ax.set_ylim(min(dec)-1, max(dec)+1)
    return ax.collections

ani = animation.FuncAnimation(fig, animate, frames=len(ra), interval=500, blit=False)
ani.save('minor_planet_2025RZ4_sky_path.gif', writer='pillow')
print('动画已保存为 minor_planet_2025RZ4_sky_path.gif')
input("Press Enter to exit...")
