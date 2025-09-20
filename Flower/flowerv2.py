#!/usr/bin/env python3
"""
FlowerV2 (Enhanced) – Generative Iris Flower Art (Pygame)

Controls:
    0/1/2/3  : All / setosa / versicolor / virginica
    Click (all mode)   : Select that species
    Click (single)     : New random stylistic variant
    Shift+Click        : Cycle species (single mode)
    Right Click        : New variant (always)
    Mouse Wheel        : Zoom in/out (global)
    T / G / B / M      : Trails / Glow / Background / Morph toggle (morph only in single mode)
    + / -              : Adjust effect intensity (0.5 – 2.0)
    Esc                : Quit

Features: dynamic hue shifts, layered petals, glow, trails, morphing between species, stylistic variants, zoom.
"""

import sys, math, random, colorsys
from pathlib import Path
import pygame
import pandas as pd
import functools

# ------------------------------------------------------------------
# Data loading
# ------------------------------------------------------------------
HERE = Path(__file__).parent
CSV_PATH = HERE / "Iris.csv"
if not CSV_PATH.exists():
        print("Iris.csv not found – please place it beside flowerv2.py")
        sys.exit(1)
df = pd.read_csv(CSV_PATH)
df['Species'] = df['Species'].str.replace('Iris-', '', regex=False)
mean_df = df.groupby('Species')[['SepalLengthCm','SepalWidthCm','PetalLengthCm','PetalWidthCm']].mean()
species_stats = {s: mean_df.loc[s].to_dict() for s in mean_df.index}

# ------------------------------------------------------------------
# Colors & palettes
# ------------------------------------------------------------------
PALETTE = {
    'WISTERIA': '#BAACEB',
    'ULTRA_VIOLET': '#5F5AA5',
    'YELLOW_GREEN': '#B8D062',
    'AVOCADO': '#5E891B',
    'PAKISTAN_GREEN': '#283B0A'
}
SPECIES_COLOR = {
    'setosa': PALETTE['WISTERIA'],
    'versicolor': PALETTE['ULTRA_VIOLET'],
    'virginica': PALETTE['YELLOW_GREEN']
}
ACCENTS = [PALETTE['AVOCADO'], PALETTE['PAKISTAN_GREEN']]

def hex_to_rgb(h: str):
    h = h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
SPECIES_COLOR_RGB = {k: hex_to_rgb(v) for k,v in SPECIES_COLOR.items()}
ACCENTS_RGB = [hex_to_rgb(c) for c in ACCENTS]

# ------------------------------------------------------------------
# Global effect state
# ------------------------------------------------------------------
EFFECTS = {'trails': True, 'glow': True, 'background': True, 'morph': False, 'bubbles': True, 'mandala': False}
EFFECT_INTENSITY = 1.0
GLOBAL_ZOOM = 1.3
ZOOM_MIN, ZOOM_MAX = 0.5, 3.2

VARIANT_ID = 0
def random_variant():
    return {
        'length_mul': random.uniform(0.85, 1.45),
        'width_mul': random.uniform(0.75, 1.40),
        'petal_mul': random.uniform(0.80, 1.60),
        'jitter_mul': random.uniform(0.70, 1.90),
        'hue_shift': random.uniform(-0.18, 0.18),
        'pulse_mul': random.uniform(0.85, 1.35)
    }
CURRENT_VARIANT = random_variant()

species_list = ['setosa','versicolor','virginica']

# Trail / glow helpers
trail_surface = None
fade_rect_cache = None

# simple value noise (defined early so draw_flower can use it)
NOISE_SEED = random.randint(0, 1_000_000)
@functools.lru_cache(maxsize=50000)
def value_noise(ix, iy, iz):
    h = hash((int(ix), int(iy), int(iz), NOISE_SEED)) & 0xffffffff
    return (h / 0xffffffff) * 2 - 1

# ------------------------------------------------------------------
# Init Pygame
# ------------------------------------------------------------------
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FlowerV2 — Iris Generative Art")
clock = pygame.time.Clock()

# ------------------------------------------------------------------
# Utility interpolation
# ------------------------------------------------------------------
def lerp(a,b,t): return a + (b-a)*t
def lerp_dict(d1,d2,t): return {k: lerp(d1[k], d2[k], t) for k in d1}

# ------------------------------------------------------------------
# Drawing helpers
# ------------------------------------------------------------------
def draw_petal(surface, center, angle_deg, length, width, color, alpha=200):
    layers = 3
    base_surf_size = int(max(6, length*1.8))
    petal_surf = pygame.Surface((base_surf_size, base_surf_size), pygame.SRCALPHA)
    cx = cy = base_surf_size//2
    r,g,b = color
    for i in range(layers):
        k = i/(layers-1) if layers>1 else 0
        layer_alpha = int(alpha * (0.4 + 0.6*(1-k)))
        shrink = 1.0 - 0.25*k
        rect = pygame.Rect(0,0,max(2,int(length*shrink)), max(2,int(width*shrink)))
        rect.center = (cx,cy)
        pygame.draw.ellipse(petal_surf,(r,g,b,layer_alpha),rect)
    outline_rect = pygame.Rect(0,0,max(2,int(length)), max(2,int(width)))
    outline_rect.center=(cx,cy)
    pygame.draw.ellipse(petal_surf,(255,255,255,60), outline_rect, width=1)
    rotated = pygame.transform.rotate(petal_surf, -angle_deg)
    w,h = rotated.get_size(); ang = math.radians(angle_deg); offset = 0.18*length
    pos = (center[0] + math.cos(ang)*offset - w/2, center[1] - math.sin(ang)*offset - h/2)
    surface.blit(rotated,pos)

def draw_flower(surface, center, stats, color_rgb, time_t, petals_base=8, scale=1.0, jitter=0.0):
    v = CURRENT_VARIANT
    base_len = stats['PetalLengthCm'] * 13.5
    base_wid = stats['PetalWidthCm'] * 8.5
    noise_factor = 0.25
    petal_length = base_len * scale * (0.9 + 0.15*math.sin(time_t*0.7)) * v['length_mul']
    petal_width  = base_wid * scale * (0.9 + 0.10*math.cos(time_t*0.9)) * v['width_mul']
    # apply radial noise modulation
    sepal_factor = (stats['SepalLengthCm'] + stats['SepalWidthCm'])/2.0
    n_petals = min(220, int((petals_base + sepal_factor*1.2 + (math.sin(time_t*0.6)+1)*3) * v['petal_mul']))
    core_r = int(7 + sepal_factor*3.3*scale)
    rotation = (time_t * 22) % 360
    pulse = (1.0 + 0.08*math.sin(time_t*2.3)) * v['pulse_mul']
    r,g,b = color_rgb
    h,l,s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    h_shift = (h + 0.08*math.sin(time_t*0.4) + v['hue_shift']) % 1.0
    l_mod = min(1.0, l*(0.9 + 0.25*math.sin(time_t*1.1)))
    s_mod = min(1.0, s*(0.85 + 0.30*math.sin(time_t*0.6 + 1.2)))
    base_color = tuple(int(c*255) for c in colorsys.hls_to_rgb(h_shift, l_mod, s_mod))
    for i in range(max(1,n_petals)):
        angle = i * (360.0 / n_petals) + rotation
        jitter_angle = (random.random()-0.5) * jitter * 8.0 * v['jitter_mul']
        # noise distort length & width subtly per petal index and time
        # noise: feed scaled indices (no scale kw in value_noise)
        nval = value_noise(i*0.6, angle*0.03, time_t*0.5)
        length_variation = petal_length * (0.70 + 0.30*math.sin(time_t*0.9 + i*0.8) + nval*noise_factor*0.2)
        width_variation  = petal_width  * (0.75 + 0.25*math.cos(time_t*1.0 + i*1.15) + nval*noise_factor*0.15)
        angle += nval * 10 * noise_factor
        alpha = int(160 + 80*math.sin(time_t*1.4 + i*0.7 + nval*0.5))
        local_shift = (h_shift + 0.03*math.sin(i*0.9 + time_t*0.5) + nval*0.05) % 1.0
        lr,lg,lb = colorsys.hls_to_rgb(local_shift, l_mod, s_mod)
        local_color = (int(lr*255), int(lg*255), int(lb*255))
        draw_petal(surface, center, angle, length_variation*pulse, max(2,width_variation), local_color, alpha)
    # Removed inner concentric circles per user request (中心的两层圆圈不要)
    # (Previously drew accent outer, darker inner, and pulsing ring.)
    # bubble aura
    if EFFECTS.get('bubbles', True):
        # reintroduce an accent color solely for bubbles (central circles removed)
        accent = ACCENTS_RGB[int(time_t*0.8) % len(ACCENTS_RGB)]
        bubble_count = int(6 + math.sqrt(n_petals)*0.8)
        for bi in range(bubble_count):
            phi = (bi / bubble_count) * math.tau + time_t*0.3 + i*0.01
            radius_orbit = core_r*2.2 + 15*math.sin(time_t*0.7 + bi)
            bx = center[0] + math.cos(phi)*radius_orbit
            by = center[1] + math.sin(phi)*radius_orbit
            br = int(4 + 3*math.sin(time_t*1.3 + bi) + random.random()*2)
            bubble_alpha = int(60 + 40*math.sin(time_t*2 + bi*0.5))
            bubble_color = (*accent, max(10,min(180,bubble_alpha)))
            pygame.draw.circle(surface, bubble_color, (int(bx), int(by)), max(1,br), width=0)

# ------------------------------------------------------------------
# Main loop
# ------------------------------------------------------------------
def main():
    global trail_surface, fade_rect_cache, EFFECT_INTENSITY, GLOBAL_ZOOM, CURRENT_VARIANT, VARIANT_ID
    running = True
    t = 0.0
    fps = 30
    mode = 'all'
    species_order = ['setosa','versicolor','virginica']
    # button to cycle single-species mode
    button_rect = pygame.Rect(15,15,130,32)
    current_species_index = 0  # used when in button-controlled single mode
    centers_all = [(WIDTH//4, HEIGHT//2), (WIDTH//2, HEIGHT//2), (3*WIDTH//4, HEIGHT//2)]
    morph_phase = 0.0
    morph_speed = 0.2
    morph_target_index = 0

    while running:
        dt = clock.tick(fps)/1000.0
        if EFFECT_INTENSITY > 1.7 and fps != 24: fps = 24
        elif EFFECT_INTENSITY <= 1.7 and fps != 30: fps = 30
        t += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_ESCAPE: running = False
                elif k == pygame.K_1: mode='setosa'; EFFECTS['morph']=False
                elif k == pygame.K_2: mode='versicolor'; EFFECTS['morph']=False
                elif k == pygame.K_3: mode='virginica'; EFFECTS['morph']=False
                elif k == pygame.K_0: mode='all'; EFFECTS['morph']=False
                elif k == pygame.K_t: EFFECTS['trails']=not EFFECTS['trails']
                elif k == pygame.K_g: EFFECTS['glow']=not EFFECTS['glow']
                elif k == pygame.K_b: EFFECTS['background']=not EFFECTS['background']
                elif k == pygame.K_p: EFFECTS['bubbles']=not EFFECTS['bubbles']
                elif k == pygame.K_f: EFFECTS['mandala']=not EFFECTS['mandala']
                elif k in (pygame.K_PLUS, pygame.K_EQUALS): EFFECT_INTENSITY = min(2.0, EFFECT_INTENSITY+0.1)
                elif k == pygame.K_MINUS: EFFECT_INTENSITY = max(0.5, EFFECT_INTENSITY-0.1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left
                    mx,my = event.pos
                    # button click detection (always active)
                    if button_rect.collidepoint(mx,my):
                        # switch to single-species mode and advance
                        current_species_index = (current_species_index + 1) % len(species_order)
                        mode = species_order[current_species_index]
                        EFFECTS['morph'] = False
                        CURRENT_VARIANT = random_variant(); VARIANT_ID += 1
                        continue  # skip other left-click logic
                    if mode == 'all':
                        for i,c in enumerate(centers_all):
                            if abs(mx-c[0]) < WIDTH//8:
                                mode = species_order[i]; EFFECTS['morph']=False; break
                    else:
                        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                            idx = species_list.index(mode)
                            mode = species_list[(idx+1)%len(species_list)]
                            EFFECTS['morph']=False
                        else:
                            CURRENT_VARIANT = random_variant(); VARIANT_ID += 1
                elif event.button == 3:  # right
                    CURRENT_VARIANT = random_variant(); VARIANT_ID += 1
                elif event.button == 4: GLOBAL_ZOOM = min(ZOOM_MAX, GLOBAL_ZOOM*1.08)
                elif event.button == 5: GLOBAL_ZOOM = max(ZOOM_MIN, GLOBAL_ZOOM/1.08)

        if trail_surface is None:
            trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            trail_surface.fill((0,0,0,0))

        # Background
        if EFFECTS['background']:
            screen.fill((0,0,0))
            cx,cy = WIDTH//2, HEIGHT//2
            max_r = math.hypot(WIDTH, HEIGHT)
            steps = 20
            for i in range(steps):
                k = i/steps
                pulse = 0.5 + 0.5*math.sin(t*0.7 + k*6)
                radius = int(k*max_r)
                shade = int(8 + 75*(1-k)*pulse)
                pygame.draw.circle(screen,(shade,shade,shade),(cx,cy),radius,width=2)
        else:
            screen.fill((0,0,0))

        # Trails fade
        if EFFECTS['trails']:
            fade_alpha = int(40*(2.0 - EFFECT_INTENSITY))
            if fade_alpha < 1: fade_alpha = 1
            if fade_rect_cache is None or fade_rect_cache.get_alpha() != fade_alpha:
                fade_rect_cache = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                fade_rect_cache.fill((0,0,0,fade_alpha))
            trail_surface.blit(fade_rect_cache,(0,0))
        else:
            trail_surface.fill((0,0,0,0))

        # Drawing
        if EFFECTS.get('mandala') and mode != 'all':
            # mandala: multiple rings of the current (or morphing) stats / species cycle colors
            center = (WIDTH//2, HEIGHT//2)
            rings = 4
            petals_per_ring = 6
            base_stats = species_stats[mode]
            # optional morph influence
            working_stats = base_stats
            if EFFECTS['morph']:
                # simple morph sample target for ring variety
                target_stats = species_stats[species_list[(species_list.index(mode)+1)%len(species_list)]]
                working_stats = lerp_dict(base_stats, target_stats, (math.sin(t*0.5)+1)/2)
            for r_i in range(rings):
                radius = (80 + r_i*70) * GLOBAL_ZOOM
                scale = 0.55 + r_i*0.25
                for p_i in range(petals_per_ring + r_i):
                    ang = (p_i / (petals_per_ring + r_i)) * math.tau + t*0.1 * (1 + 0.15*r_i)
                    fx = center[0] + math.cos(ang)*radius
                    fy = center[1] + math.sin(ang)*radius
                    # cycle species color for ring
                    color_species = species_list[(r_i + p_i) % len(species_list)]
                    color = SPECIES_COLOR_RGB[color_species]
                    draw_flower(trail_surface if EFFECTS['trails'] else screen, (int(fx), int(fy)), working_stats, color, t + r_i*0.3 + p_i*0.05, petals_base=8 + r_i, scale=scale*GLOBAL_ZOOM, jitter=0.6*EFFECT_INTENSITY)
        elif mode == 'all':
            for i,sp in enumerate(species_order):
                stats = species_stats[sp]; color = SPECIES_COLOR_RGB[sp]
                s = (1.0 + 0.05*i) * GLOBAL_ZOOM
                draw_flower(trail_surface if EFFECTS['trails'] else screen, centers_all[i], stats, color, t+i*0.7, petals_base=10, scale=s, jitter=0.8*EFFECT_INTENSITY)
        else:
            base_stats = species_stats[mode]; current_stats = base_stats
            if EFFECTS['morph']:
                morph_phase += dt * morph_speed
                if morph_phase >= 1.0:
                    mode = species_list[morph_target_index]
                    base_stats = species_stats[mode]
                    morph_target_index = (morph_target_index+1)%len(species_list)
                    morph_phase = 0.0
                target_stats = species_stats[species_list[morph_target_index]]
                current_stats = lerp_dict(base_stats, target_stats, morph_phase)
            color = SPECIES_COLOR_RGB[mode]
            draw_flower(trail_surface if EFFECTS['trails'] else screen, (WIDTH//2, HEIGHT//2), current_stats, color, t, petals_base=12, scale=1.6*GLOBAL_ZOOM, jitter=1.4*EFFECT_INTENSITY)

        # Glow composite
        if EFFECTS['trails']:
            if EFFECTS['glow']:
                glow = pygame.transform.smoothscale(trail_surface, (int(WIDTH*0.55), int(HEIGHT*0.55)))
                glow = pygame.transform.smoothscale(glow,(WIDTH,HEIGHT))
                glow.set_alpha(int(85*EFFECT_INTENSITY))
                screen.blit(glow,(0,0),special_flags=pygame.BLEND_ADD)
            screen.blit(trail_surface,(0,0))

        # HUD
        font = pygame.font.SysFont(None, 20)
        # draw species cycle button
        btn_color_bg = (40,40,60)
        pygame.draw.rect(screen, btn_color_bg, button_rect, border_radius=6)
        pygame.draw.rect(screen, (120,120,180), button_rect, width=2, border_radius=6)
        btn_label = '切换花朵'  # Chinese: switch flower
        # show current species short label
        if mode == 'all':
            show_sp = 'All'
        else:
            show_sp = mode
        btn_text = font.render(f"{btn_label}:{show_sp}", True, (235,235,240))
        screen.blit(btn_text, (button_rect.x+8, button_rect.y+7))
        hud_lines = [
            f"Mode:{mode}  Click(all)=select  Click(single)=variant  Shift+Click=cycle  Mandala(F):{EFFECTS['mandala']}",
            f"T:{EFFECTS['trails']} G:{EFFECTS['glow']} Bk:{EFFECTS['background']} M:{EFFECTS['morph']} Bub(P):{EFFECTS['bubbles']} Int:{EFFECT_INTENSITY:.2f}",
            f"Zoom:{GLOBAL_ZOOM:.2f} Variant:{VARIANT_ID} RightClick=new variant"
        ]
        for i,line in enumerate(hud_lines):
            txt = font.render(line, True, (235,235,235))
            screen.blit(txt,(10, HEIGHT-20*(len(hud_lines)-i)))

        pygame.display.flip()

    pygame.quit(); sys.exit(0)

if __name__ == '__main__':
    main()