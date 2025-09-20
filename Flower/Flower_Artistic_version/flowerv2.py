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
from datetime import datetime
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

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

def lighten(rgb, amount: float):
    """Lighten an RGB tuple toward white by amount (0-1)."""
    r,g,b = rgb
    return tuple(min(255, int(c + (255-c)*amount)) for c in (r,g,b))

# ------------------------------------------------------------------
# Global effect state
# ------------------------------------------------------------------
EFFECTS = {'trails': True, 'glow': True, 'background': True, 'morph': False, 'bubbles': True, 'mandala': False}
EFFECT_INTENSITY = 1.0
GLOBAL_ZOOM = 1.4
ZOOM_MIN, ZOOM_MAX = 0.5, 4.5
# exaggeration master scalar for size / petal count / noise amplitude
EXAGGERATION = 1.25

VARIANT_ID = 0
def random_variant():
    # wider range for more dramatic variety
    return {
        'length_mul': random.uniform(0.75, 1.75),
        'width_mul': random.uniform(0.60, 1.70),
        'petal_mul': random.uniform(0.70, 2.10),
        'jitter_mul': random.uniform(0.60, 2.40),
        'hue_shift': random.uniform(-0.28, 0.28),
        'pulse_mul': random.uniform(0.70, 1.60)
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

def draw_cycle_icon(surface, rect, active_species_color, hover=False):
    # simple circular arrows icon + central dot color-coded to current species
    bg = (35,35,55,180)
    icon_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(icon_surf, bg, icon_surf.get_rect(), border_radius=8)
    border_col = (150,150,210) if not hover else (200,200,255)
    pygame.draw.rect(icon_surf, border_col, icon_surf.get_rect(), width=2, border_radius=8)
    w,h = rect.size; cx,cy = w//2, h//2
    radius = min(w,h)//2 - 6
    # arrow circle
    pygame.draw.circle(icon_surf, (90,90,150), (cx,cy), radius, width=2)
    # two small arrow heads
    ah = 6
    pygame.draw.polygon(icon_surf, (90,90,150), [(cx+radius-4, cy-3), (cx+radius+ah-4, cy), (cx+radius-4, cy+3)])
    pygame.draw.polygon(icon_surf, (90,90,150), [(cx-radius+4, cy+3), (cx-radius-ah+4, cy), (cx-radius+4, cy-3)])
    # center dot with current species color
    pygame.draw.circle(icon_surf, active_species_color, (cx,cy), 5)
    surface.blit(icon_surf, rect.topleft)

def draw_compact_hud(surface, mode, variant_id, zoom, intensity, effects):
    # simplified bottom-left (remove effect toggles as requested)
    font_small = pygame.font.SysFont(None, 16)
    pad = 6
    lines = [f"{mode.upper()}  V{variant_id}", f"Z:{zoom:.2f} I:{intensity:.2f}"]
    rendered = [font_small.render(l, True, (230,230,235)) for l in lines]
    w = max(r.get_width() for r in rendered) + pad*2
    h = sum(r.get_height() for r in rendered) + pad*2 + (len(rendered)-1)*2
    box = pygame.Surface((w,h), pygame.SRCALPHA)
    pygame.draw.rect(box,(20,20,32,170), box.get_rect(), border_radius=8)
    pygame.draw.rect(box,(90,90,140), box.get_rect(), width=2, border_radius=8)
    cy = pad
    for r in rendered:
        box.blit(r,(pad,cy))
        cy += r.get_height()+2
    surface.blit(box,(10, HEIGHT - h - 10))

def draw_stats_panel(surface, stats_dict, current_mode, variant_id):
    # right side panel with PetalLengthCm & PetalWidthCm per species
    font_title = pygame.font.SysFont(None, 18)
    font_row = pygame.font.SysFont(None, 16)
    pad = 8
    species_names = list(stats_dict.keys())
    headers = ['Species','PetalL','PetalW']
    rows = []
    for sp in species_names:
        st = stats_dict[sp]
        rows.append((sp, f"{st['PetalLengthCm']:.2f}", f"{st['PetalWidthCm']:.2f}"))
    # measure widths
    col_widths = [0,0,0]
    all_rows = [headers] + rows
    font_measure = font_row
    for r in all_rows:
        for ci,val in enumerate(r):
            w = font_measure.render(val, True, (0,0,0)).get_width()
            if w > col_widths[ci]: col_widths[ci] = w
    table_w = sum(col_widths) + pad*2 + 12
    title = f"Mode:{current_mode} V{variant_id}"
    title_surf = font_title.render(title, True, (240,240,250))
    row_height = font_row.get_height()+2
    table_h = title_surf.get_height() + 6 + (row_height)*(len(rows)+1) + pad*2
    x = WIDTH - table_w - 15
    y = 20
    panel = pygame.Surface((table_w, table_h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (25,25,40,180), panel.get_rect(), border_radius=10)
    pygame.draw.rect(panel, (110,110,170), panel.get_rect(), width=2, border_radius=10)
    panel.blit(title_surf,(pad, pad))
    y_cursor = pad + title_surf.get_height() + 4
    # header
    header_color = (200,200,220)
    x_cursor = pad
    for ci,val in enumerate(headers):
        txt = font_row.render(val, True, header_color)
        panel.blit(txt,(x_cursor, y_cursor))
        x_cursor += col_widths[ci] + 6
    y_cursor += row_height
    # rows
    for (sp,pl,pw) in rows:
        x_cursor = pad
        active = (sp == current_mode)
        for ci,val in enumerate((sp,pl,pw)):
            col_col = (255,230,150) if active else (220,220,230)
            txt = font_row.render(val, True, col_col)
            panel.blit(txt,(x_cursor, y_cursor))
            x_cursor += col_widths[ci] + 6
        y_cursor += row_height
    surface.blit(panel,(x,y))

def draw_flower(surface, center, stats, color_rgb, time_t, petals_base=8, scale=1.0, jitter=0.0):
    v = CURRENT_VARIANT
    base_len = stats['PetalLengthCm'] * 15.0 * EXAGGERATION
    base_wid = stats['PetalWidthCm'] * 9.5 * EXAGGERATION
    noise_factor = 0.32 * EXAGGERATION
    petal_length = base_len * scale * (0.9 + 0.20*math.sin(time_t*0.7)) * v['length_mul']
    petal_width  = base_wid * scale * (0.9 + 0.15*math.cos(time_t*0.9)) * v['width_mul']
    # apply radial noise modulation
    sepal_factor = (stats['SepalLengthCm'] + stats['SepalWidthCm'])/2.0
    n_petals = min(300, int((petals_base + sepal_factor*1.6 + (math.sin(time_t*0.55)+1)*4) * v['petal_mul'] * (0.85 + EXAGGERATION*0.55)))
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
        jitter_angle = (random.random()-0.5) * jitter * 10.0 * v['jitter_mul'] * EXAGGERATION
        # noise distort length & width subtly per petal index and time
        nval = value_noise(i*0.6, angle*0.03, time_t*0.5)
        length_variation = petal_length * (0.70 + 0.30*math.sin(time_t*0.9 + i*0.8) + nval*noise_factor*0.2)
        width_variation  = petal_width  * (0.75 + 0.25*math.cos(time_t*1.0 + i*1.15) + nval*noise_factor*0.15)
        angle += (nval * 12 * noise_factor) + jitter_angle
        alpha = int(160 + 80*math.sin(time_t*1.4 + i*0.7 + nval*0.5))
        local_shift = (h_shift + 0.03*math.sin(i*0.9 + time_t*0.5) + nval*0.05) % 1.0
        lr,lg,lb = colorsys.hls_to_rgb(local_shift, l_mod, s_mod)
        local_color = (int(lr*255), int(lg*255), int(lb*255))
        draw_petal(surface, center, angle, length_variation*pulse, max(2,width_variation), local_color, alpha)
    # outer translucent halo petals for exaggeration
    halo_layers = 2
    halo_color = base_color
    for hl in range(halo_layers):
        spread = 1.15 + hl*0.18
        alpha_h = int(60 - hl*18)
        if alpha_h <= 0: continue
        for i in range(0, n_petals, 2):
            ang = i * (360.0 / n_petals) + rotation*0.8 + hl*7
            nval = value_noise(i*0.4, ang*0.02, time_t*0.35)
            lv = petal_length * (0.9 + 0.1*nval) * spread
            wv = petal_width * (0.9 + 0.08*nval) * spread
            draw_petal(surface, center, ang, lv, max(2,wv), halo_color, alpha_h)
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
    # species name buttons (left top)
    button_height = 30
    button_padding = 8
    species_buttons = []
    x_cursor = 15
    for sp in species_order:
        label_w = 90
        rect = pygame.Rect(x_cursor, 15, label_w, button_height)
        species_buttons.append((sp, rect))
        x_cursor += label_w + button_padding
    current_species_index = 0  # maintain for cycling logic if needed
    centers_all = [(WIDTH//4, HEIGHT//2), (WIDTH//2, HEIGHT//2), (3*WIDTH//4, HEIGHT//2)]
    morph_phase = 0.0
    morph_speed = 0.2
    morph_target_index = 0
    # GIF capture state
    capturing = False
    capture_frames = []
    capture_max = 180  # about 6 seconds at 30fps
    capture_scale = 0.6  # downscale to reduce size
    capture_every = 1    # frame stride
    frame_counter = 0
    gif_last_saved = None

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
                elif k == pygame.K_h:
                    if not PIL_AVAILABLE:
                        print("Pillow not installed; can't capture GIF.")
                    else:
                        capturing = not capturing
                        if capturing:
                            capture_frames.clear(); frame_counter = 0
                            print("[GIF] Capture started (H to stop, S to save early).")
                        else:
                            # auto save when stopping
                            if capture_frames:
                                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                                out_path = HERE / f"flower_capture_{ts}.gif"
                                try:
                                    capture_frames[0].save(out_path, save_all=True, append_images=capture_frames[1:], loop=0, duration=33, disposal=2)
                                    print(f"[GIF] Saved {out_path}")
                                    gif_last_saved = out_path
                                except Exception as e:
                                    print("[GIF] Save failed:", e)
                elif k == pygame.K_s:
                    # manual save without toggling capture
                    if capturing and capture_frames:
                        capturing = False
                        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                        out_path = HERE / f"flower_capture_{ts}.gif"
                        try:
                            capture_frames[0].save(out_path, save_all=True, append_images=capture_frames[1:], loop=0, duration=33, disposal=2)
                            print(f"[GIF] Saved {out_path}")
                            gif_last_saved = out_path
                        except Exception as e:
                            print("[GIF] Save failed:", e)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left
                    mx,my = event.pos
                    # species name buttons detection
                    clicked_button = False
                    for sp,rect in species_buttons:
                        if rect.collidepoint(mx,my):
                            if mode == sp:
                                # if already that species -> go back to all
                                mode = 'all'
                            else:
                                mode = sp
                            EFFECTS['morph'] = False
                            CURRENT_VARIANT = random_variant(); VARIANT_ID += 1
                            clicked_button = True
                            break
                    if clicked_button:
                        continue
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
            draw_flower(trail_surface if EFFECTS['trails'] else screen, (WIDTH//2, HEIGHT//2), current_stats, color, t, petals_base=14, scale=2.1*GLOBAL_ZOOM*EXAGGERATION, jitter=1.6*EFFECT_INTENSITY)

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
        # draw species buttons
        mouse_pos = pygame.mouse.get_pos()
        for sp,rect in species_buttons:
            is_active = (mode == sp)
            hovered = rect.collidepoint(mouse_pos)
            base_species_col = SPECIES_COLOR_RGB.get(sp, (80,80,110))
            if not is_active:
                # default black base, brighten on hover
                if hovered:
                    bg_col = lighten((0,0,0), 0.45)
                else:
                    bg_col = (0,0,0)
            else:
                # active uses species color lightened
                bg_col = lighten(base_species_col, 0.70)
                if hovered:
                    bg_col = lighten(base_species_col, 0.85)
            pygame.draw.rect(screen, bg_col, rect, border_radius=8)
            border_col = lighten(base_species_col, 0.9 if is_active else (0.65 if hovered else 0.5))
            pygame.draw.rect(screen, border_col, rect, width=2, border_radius=8)
            label_text = sp
            txt_color = (250,250,255) if hovered or is_active else (235,235,240)
            txt = font.render(label_text, True, txt_color)
            screen.blit(txt, (rect.x + (rect.width - txt.get_width())//2, rect.y + (rect.height - txt.get_height())//2))
        # small ALL toggle indicator (click species again returns to all so just display)
        all_status = 'ALL' if mode=='all' else ' ' 
        all_txt = font.render(all_status, True, (180,180,190))
        screen.blit(all_txt, (species_buttons[-1][1].right + 10, 20))
        # compact HUD bottom-left
        draw_compact_hud(screen, mode, VARIANT_ID, GLOBAL_ZOOM, EFFECT_INTENSITY, EFFECTS)
        # right side stats panel
        draw_stats_panel(screen, species_stats, mode, VARIANT_ID)

        # capture frame if enabled
        if capturing and PIL_AVAILABLE:
            frame_counter += 1
            if frame_counter % capture_every == 0:
                surf = screen.copy()
                if capture_scale != 1.0:
                    scaled = pygame.transform.smoothscale(surf, (int(WIDTH*capture_scale), int(HEIGHT*capture_scale)))
                else:
                    scaled = surf
                mode_str = mode
                # convert to PIL Image
                raw_str = pygame.image.tostring(scaled, 'RGB')
                img = Image.frombytes('RGB', scaled.get_size(), raw_str)
                capture_frames.append(img)
                if len(capture_frames) >= capture_max:
                    capturing = False
                    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                    out_path = HERE / f"flower_capture_{ts}.gif"
                    try:
                        capture_frames[0].save(out_path, save_all=True, append_images=capture_frames[1:], loop=0, duration=33, disposal=2)
                        print(f"[GIF] Auto-saved (max frames) {out_path}")
                        gif_last_saved = out_path
                    except Exception as e:
                        print("[GIF] Save failed:", e)
        # overlay capture status (small)
        if PIL_AVAILABLE:
            cap_font = pygame.font.SysFont(None, 16)
            status = "CAPTURE: ON" if capturing else "CAPTURE: OFF (H start)"
            if not PIL_AVAILABLE:
                status = "Pillow missing: pip install pillow"
            cap_txt = cap_font.render(status, True, (200,220,255))
            screen.blit(cap_txt, (10, 10 + 38))

        pygame.display.flip()

    pygame.quit(); sys.exit(0)

if __name__ == '__main__':
    main()