"""
Abstract bio-visualization animation generator
- Synthesizes a heartbeat (sine with beats) and a slow growth signal
- Renders a dark, glowing animated GIF showing concentric rings and growing stems

Run:
    & <venv>/Scripts/python.exe Flower/biovis_abstract_animation.py

Output: Flower/biovis_abstract_animation.gif
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageEnhance
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

OUT = Path(__file__).parent
OUTGIF = OUT / 'biovis_abstract_animation.gif'

# parameters
FRAMES = 120
WIDTH, HEIGHT = 800, 600
DPI = 100

# synthesize signals
t = np.linspace(0, 8 * np.pi, FRAMES)
# heartbeat: base sine + short sharp beats
heartbeat = 0.6 * np.sin(2 * t) + 0.4 * np.sin(20 * t) * (np.abs(np.sin(2*t))>0.9)
# growth: slow rising curve
growth = np.clip(np.linspace(0, 1, FRAMES)**1.2, 0, 1)
# randomness for organic motion
np.random.seed(1)
jitter = 0.03 * np.random.randn(FRAMES)

frames = []
for i in range(FRAMES):
    fig = plt.figure(figsize=(WIDTH/DPI, HEIGHT/DPI), dpi=DPI, facecolor='black')
    ax = fig.add_axes([0,0,1,1], facecolor='black')
    ax.set_xlim(0, WIDTH)
    ax.set_ylim(0, HEIGHT)
    ax.axis('off')

    # draw concentric glowing rings whose radius pulses with heartbeat
    center_x, center_y = WIDTH*0.5, HEIGHT*0.45
    base_r = 40 + 60 * growth[i]
    for k in range(6):
        r = base_r + k*30 + 6 * heartbeat[i]
        alpha = max(0.02, 0.15 - k*0.02)
        color = (0.18 + 0.12*k, 0.6 - 0.08*k, 0.95 - 0.12*k)
        circ = plt.Circle((center_x, center_y), r, color=color, fill=False, lw=8, alpha=alpha, zorder=1)
        ax.add_patch(circ)

    # draw growing stems (plant-like) on the left
    stems = 4
    for s in range(stems):
        x0 = WIDTH*0.2 + s*30
        y0 = HEIGHT*0.1
        height = 200 * growth[i] + 10 * s
        xs = [x0, x0 + 10*np.sin(0.3*i + s), x0 + 5*np.sin(0.1*i + s*1.2), x0]
        ys = [y0, y0 + 0.4*height, y0 + 0.9*height, y0 + height]
        ax.plot(xs, ys, color=(0.2,0.7,0.3), linewidth=3 + s*0.8, alpha=0.95, zorder=3)
        # leaves
        lx = x0 + 5*np.sin(0.1*i + s)
        ly = y0 + 0.6*height
        ax.scatter([lx],[ly], s=60*(0.5+growth[i]), color=(0.5,0.9,0.6), edgecolors='white', linewidth=0.6, zorder=4)

    # draw a faint grid of points with heartbeat-driven glow
    for p in range(80):
        px = (p*37 % WIDTH) + 10*np.sin(0.11*p + 0.05*i)
        py = (p*67 % HEIGHT) + 6*np.cos(0.09*p + 0.03*i)
        s = 4 + 6*(0.5+0.5*heartbeat[i])
        ax.scatter(px, py, s=s, color=(0.3,0.65,0.95), alpha=0.08, zorder=0)

    # vignette / glow enhancement by drawing with an Agg canvas and getting RGB buffer
    canvas = FigureCanvas(fig)
    canvas.draw()
    w, h = canvas.get_width_height()
    # get RGBA buffer and convert to RGB
    buf = canvas.buffer_rgba()
    img = Image.frombuffer('RGBA', (w, h), buf, 'raw', 'RGBA', 0, 1).convert('RGB')
    plt.close(fig)

    # enhance glow by increasing brightness of bright areas
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.05 + 0.05*growth[i])
    # optional slight blur could be added here if pillow had more filters available

    frames.append(img)

# save as GIF
frames[0].save(OUTGIF, save_all=True, append_images=frames[1:], duration=60, loop=0)
print('Saved', OUTGIF)
