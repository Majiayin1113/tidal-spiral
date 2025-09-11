# Moving Spiral Visualization using Tidal Data (Pygame)

# Enhanced Spiral Visualization with Color Gradients, Dynamic Thickness, and Interactive Controls
import pygame
import math
import random
import sys

WIDTH, HEIGHT = 900, 900
FPS = 60

# Placeholder for tidal data
TIDAL_DATA = [math.sin(i/20.0)*100+200 for i in range(2000)]

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

angle = 0
step = 0
speed = 1
thickness = 2
running = True

def get_color(i, total):
    # Gradient from blue to cyan to magenta
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
    # Animated background stars
    for _ in range(30):
        sx = random.randint(0, WIDTH)
        sy = random.randint(0, HEIGHT)
        pygame.draw.circle(screen, (255,255,255), (sx, sy), random.randint(1,2))
    angle += 0.01 * speed
    step = (step + speed) % len(TIDAL_DATA)
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
sys.exit()
