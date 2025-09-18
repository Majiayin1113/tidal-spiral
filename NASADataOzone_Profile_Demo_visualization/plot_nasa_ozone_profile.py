
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

np.random.seed(42)
alt = np.linspace(0, 30, 100)  # 0-30km
frames = 60
o3_profiles = []
for t in range(frames):
	# 随时间变化的剖面，模拟大气扰动
	o3 = 30 + 80 * np.exp(-((alt-20-t*0.1)/7)**2) + np.random.normal(0, 5, size=alt.shape)
	o3_profiles.append(o3)
o3_profiles = np.array(o3_profiles)

fig, ax = plt.subplots(figsize=(6,8))
line, = ax.plot([], [], lw=2)
ax.set_xlabel('Ozone (ppbv)')
ax.set_ylabel('Altitude (km)')
ax.set_title('Ozone Profile (Demo, Animated)')
ax.set_xlim(0, 120)
ax.set_ylim(30, 0)
ax.grid(True)

def animate(i):
	line.set_data(o3_profiles[i], alt)
	ax.set_title(f'Ozone Profile (Demo, Frame {i+1})')
	return line,

ani = animation.FuncAnimation(fig, animate, frames=frames, interval=100, blit=True)
plt.show()
