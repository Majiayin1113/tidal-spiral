
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)
alt = np.linspace(0, 30, 100)  # 0-30km
o3 = 30 + 80 * np.exp(-((alt-20)/7)**2) + np.random.normal(0, 5, size=alt.shape)

plt.figure(figsize=(6,8))
plt.plot(o3, alt)
plt.xlabel('Ozone (ppbv)')
plt.ylabel('Altitude (km)')
plt.title('Ozone Profile (Demo)')
plt.gca().invert_yaxis()
plt.grid(True)
plt.show()
