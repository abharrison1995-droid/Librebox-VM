import sys
import math
import random
from PIL import Image, ImageDraw
from generate_covers import (
    draw_bitmap_text,
    darken_lower_band,
    save_cover,
    dither_gradient_v,
    dither_lerp
)

# -------------------------------------------------------------
# 1. BENEATH A STEEL SKY (violet/magenta)
# -------------------------------------------------------------
def make_beneath_a_steel_sky():
    img = Image.new('RGB', (128, 128), (14, 6, 24))
    pixels = img.load()
    
    # 1. Atmospheric Sky: Deep cosmic indigo to intense neon violet / magenta horizon
    c_sky1 = (10, 4, 20)
    c_sky2 = (45, 12, 60)
    c_sky3 = (95, 20, 95)
    c_sky4 = (175, 45, 130)
    dither_gradient_v(img, 0, 30, c_sky1, c_sky2)
    dither_gradient_v(img, 30, 60, c_sky2, c_sky3)
    dither_gradient_v(img, 60, 85, c_sky3, c_sky4)
    
    # Giant dystopian corporation arcology moon / holo-dome
    cx, cy, rad = 95, 34, 22
    for y in range(cy - rad, cy + rad + 1):
        for x in range(cx - rad, cx + rad + 1):
            dist = math.hypot(x - cx, y - cy)
            if dist <= rad and 0 <= x < 128 and 0 <= y < 128:
                t = dist / rad
                c_orb = dither_lerp((255, 210, 245), (160, 40, 120), t * 1.1, x, y)
                pixels[x, y] = c_orb
                # Subtle planetary rings / grid overlay
                if abs(y - cy - (x - cx) * 0.25) < 1.5:
                    pixels[x, y] = (255, 240, 255)

    # Distant Megastructure Spires (layer 1)
    spires_far = [
        (8, 14, 80), (24, 18, 95), (44, 12, 70), (58, 20, 88),
        (80, 15, 75), (106, 22, 90)
    ]
    for bx, bw, bh in spires_far:
        for y in range(128 - bh, 128):
            for x in range(bx, bx + bw):
                if 0 <= x < 128:
                    pixels[x, y] = (35, 12, 45)
                    # Antenna spires on top
                    if y < 128 - bh + 6 and x == bx + bw // 2:
                        pixels[x, y] = (220, 80, 180)
                    # Windows
                    if (x % 3 == 0) and (y % 4 == 0) and ((x * 11 + y * 7) % 6 == 0):
                        pixels[x, y] = (230, 110, 210)

    # Midground Heavy Industrial Towers & Pipes (layer 2)
    spires_mid = [
        (0, 22, 105), (20, 26, 115), (50, 30, 110), (84, 28, 120), (110, 18, 100)
    ]
    for bx, bw, bh in spires_mid:
        for y in range(128 - bh, 128):
            for x in range(bx, bx + bw):
                if 0 <= x < 128:
                    # Shaded column
                    shade = 1.0 - abs(x - (bx + bw / 2.0)) / (bw / 2.0) * 0.4
                    pixels[x, y] = (int(25 * shade), int(8 * shade), int(35 * shade))
                    # Neon cyan / magenta corporate signage
                    if bx == 50 and 42 <= y <= 50 and 53 <= x <= 77:
                        if (x + y) % 2 == 0:
                            pixels[x, y] = (0, 240, 230)
                        else:
                            pixels[x, y] = (255, 60, 180)
                    elif (x % 4 == 1) and (y % 5 == 1) and ((x * 5 + y * 3) % 4 == 0):
                        pixels[x, y] = (255, 140, 230)

    # Steam / Smog clouds billowing across industrial canyon
    for sx, sy, srad in [(28, 62, 12), (68, 68, 16), (105, 60, 14)]:
        for dy in range(-srad, srad + 1):
            for dx in range(-srad * 2, srad * 2 + 1):
                px, py = sx + dx, sy + dy
                dist = math.hypot(dx * 0.6, dy * 1.2)
                if dist < srad and 0 <= px < 128 and 0 <= py < 128:
                    if (px + py + (px ^ py)) % 3 == 0:
                        pixels[px, py] = (130, 45, 115)

    # Foreground: Suspended High-Altitude Gantry & Handrail (y=66..76)
    for x in range(0, 128):
        # Steel walkway truss
        for y in range(68, 76):
            pixels[x, y] = (20, 6, 28)
        pixels[x, 68] = (80, 25, 95) # Top rim highlight
        pixels[x, 75] = (45, 15, 60) # Bottom rim
        # Handrail bar & vertical stanchions
        pixels[x, 62] = (80, 25, 95)
        if x % 8 == 0:
            for y in range(62, 68):
                pixels[x, y] = (95, 30, 110)
        # Diagonal truss lattice underneath
        if (x + y) % 6 == 0 and y >= 68:
            pixels[x, y] = (50, 15, 65)

    # Hero Figure: Cynical Trenchcoated Adventurer (x=40..50, y=48..70)
    # Hair & face silhouette
    for y in range(48, 54):
        for x in range(43, 49):
            pixels[x, y] = (15, 5, 20)
    pixels[47, 50] = (0, 255, 240) # Glowing cybernetic optic ocular implant!
    pixels[48, 50] = (0, 200, 200)
    # Long trenchcoat collar & shoulders
    for y in range(54, 69):
        span = int(3 + (y - 54) * 0.45)
        for x in range(45 - span, 46 + span):
            pixels[x, y] = (18, 6, 24)
    # Trenchcoat hem fluttering in atmospheric wind
    for y in range(60, 69):
        for x in range(36, 42):
            if x >= 42 - (y - 59):
                pixels[x, y] = (25, 8, 32)
                if x == 36 + (68 - y):
                    pixels[x, y] = (60, 20, 75)

    # Robotic Sidekick Droid (x=55..64, y=58..69)
    # Welded chassis box
    for y in range(60, 68):
        for x in range(56, 64):
            pixels[x, y] = (30, 10, 40)
            if x == 56 or y == 60:
                pixels[x, y] = (85, 35, 100) # metal edge highlight
    # Droid swivel optic eye
    pixels[58, 62] = (255, 220, 50) # bright yellow sensor
    pixels[59, 62] = (255, 160, 20)
    pixels[58, 63] = (255, 220, 50)
    # Antennas & tool arm
    pixels[57, 58] = (120, 45, 130)
    pixels[57, 59] = (120, 45, 130)
    pixels[64, 63] = (150, 55, 160) # weld torch tip

    # 2. Darken lower ~40% for title legibility (keeping lower cityscape visible)
    darken_lower_band(img, y_start=76, darken_factor=0.32, tint=(25, 8, 35))
    
    # 3. Title Typography: BENEATH A STEEL SKY
    draw_bitmap_text(img, "BENEATH A", 64, 88, fg_color=(255, 240, 250), bg_color=(12, 4, 18))
    draw_bitmap_text(img, "STEEL SKY", 64, 106, fg_color=(255, 215, 245), bg_color=(12, 4, 18))
    
    save_cover(img, "beneath-a-steel-sky.png")


# -------------------------------------------------------------
# 2. BIO MENACE (amber/orange)
# -------------------------------------------------------------
def make_bio_menace():
    img = Image.new('RGB', (128, 128), (22, 10, 4))
    pixels = img.load()
    
    # 1. Sky: Fiery apocalypse sunset (deep mahogany -> glowing amber-red -> bright flame orange)
    c_sky1 = (35, 10, 4)
    c_sky2 = (130, 45, 8)
    c_sky3 = (210, 95, 15)
    c_sky4 = (255, 175, 30)
    dither_gradient_v(img, 0, 25, c_sky1, c_sky2)
    dither_gradient_v(img, 25, 55, c_sky2, c_sky3)
    dither_gradient_v(img, 55, 80, c_sky3, c_sky4)
    
    # Billowing volcanic smoke plumes & ember storm
    for cx, cy, rad in [(25, 20, 16), (62, 15, 20), (105, 22, 18)]:
        for y in range(cy - rad, cy + rad + 1):
            for x in range(cx - rad * 2, cx + rad * 2 + 1):
                dist = math.hypot((x - cx) * 0.7, y - cy)
                if dist <= rad and 0 <= x < 128 and 0 <= y < 128:
                    if (x * 3 + y * 7 + (x ^ y)) % 3 == 0:
                        pixels[x, y] = (95, 35, 8)
                        
    # Floating fire embers
    for ex, ey in [(15, 32), (38, 25), (75, 28), (92, 18), (118, 35), (55, 42), (85, 48)]:
        pixels[ex, ey] = (255, 240, 120)
        pixels[ex + 1, ey] = (255, 140, 20)

    # Ruined Metro City Skyline (crumbling skyscrapers, exposed girders, fire pockets)
    skyscrapers = [
        (6, 18, 65), (28, 24, 80), (56, 16, 60), (76, 22, 75), (102, 20, 85)
    ]
    for bx, bw, bh in skyscrapers:
        for y in range(128 - bh, 128):
            for x in range(bx, bx + bw):
                if 0 <= x < 128:
                    # Jagged collapsed tops
                    if y == 128 - bh and (x % 3 == 0 or x % 4 == 0):
                        continue
                    pixels[x, y] = (45, 18, 6)
                    # Building edge lighting
                    if x == bx or x == bx + bw - 1:
                        pixels[x, y] = (90, 40, 12)
                    # Burning structural fires in windows
                    if (y % 6 == 0) and (x % 4 == 1) and ((x * 7 + y) % 5 == 0) and y < 85:
                        pixels[x, y] = (255, 190, 40)
                        if (x + y) % 2 == 0:
                            pixels[x, y] = (255, 100, 10)

    # Shattered concrete roadway / hazardous platform (y=66..76)
    for y in range(66, 78):
        for x in range(0, 128):
            # Broken asphalt texture
            if y >= 68 + ((x * 13) % 3):
                pixels[x, y] = (40, 20, 10)
                if y == 68 + ((x * 13) % 3):
                    pixels[x, y] = (120, 65, 25)
                # Cracked fissures glowing with orange bio-slime
                if (x % 17 == 0 or (x + y) % 23 == 0) and y > 70:
                    pixels[x, y] = (255, 140, 20)

    # Hero Commando (Snake Logan archetype, x=30..46, y=42..70)
    # Head & iconic red bandana
    for y in range(42, 45):
        for x in range(33, 41):
            pixels[x, y] = (220, 30, 20) # Red headband
    pixels[30, 43] = (220, 30, 20) # Bandana tail flowing in wind
    pixels[29, 44] = (180, 20, 15)
    for y in range(45, 50):
        for x in range(34, 40):
            pixels[x, y] = (235, 175, 125) # Commando face
    pixels[38, 46] = (40, 20, 10) # Eye / grim expression
    
    # Muscular torso & tactical combat vest
    for y in range(50, 68):
        for x in range(32, 43):
            pixels[x, y] = (75, 55, 25) # Olive-drab combat vest
            if 54 <= y <= 62 and 34 <= x <= 40:
                pixels[x, y] = (160, 110, 45) # Tactical pockets / ammo pouches
    # Holster & belt
    for x in range(32, 43):
        pixels[x, 62] = (140, 85, 30)

    # Assault Rifle & Blazing Muzzle Flash (firing toward right mutant)
    # Gun receiver & barrel (x=41..60, y=52..56)
    for x in range(41, 58):
        for y in range(53, 56):
            pixels[x, y] = (30, 30, 35)
    pixels[46, 56] = (20, 20, 25) # Curved magazine
    pixels[46, 57] = (20, 20, 25)
    pixels[46, 58] = (20, 20, 25)
    
    # Blazing explosive muzzle flare!
    for fx, fy, frad in [(60, 54, 7), (64, 54, 4), (67, 54, 2)]:
        for y in range(fy - frad, fy + frad + 1):
            for x in range(fx - frad, fx + frad + 1):
                if math.hypot(x - fx, (y - fy) * 1.2) <= frad:
                    pixels[x, y] = (255, 245, 140)
    pixels[59, 54] = (255, 255, 255)
    
    # High-velocity tracer fire bullet line
    for x in range(68, 92):
        pixels[x, 54] = (255, 230, 90)
        pixels[x, 55] = (255, 130, 20)

    # Horrific Bio-Mutant Abomination (x=90..124, y=38..74)
    # Giant grotesque multi-segmented mutant body
    for y in range(40, 74):
        for x in range(92, 126):
            dist = math.hypot((x - 108) * 0.85, (y - 56) * 0.9)
            if dist <= 17:
                pixels[x, y] = (45, 125, 40) # toxic bio-slime green
                # Shading / texture scales
                if (x + y) % 3 == 0:
                    pixels[x, y] = (75, 175, 55)
                if (x * y) % 7 == 0:
                    pixels[x, y] = (175, 45, 130) # grotesque mutagen pustule
    # Cluster of malevolent glowing mutant eyes
    for mx, my in [(98, 48), (103, 45), (108, 49), (96, 54), (104, 55)]:
        pixels[mx, my] = (255, 240, 40)
        pixels[mx + 1, my] = (255, 40, 20)
    # Razor fangs dripping toxic sludge
    for fx, fy in [(94, 58), (98, 59), (102, 58)]:
        pixels[fx, fy] = (255, 255, 240)
        pixels[fx, fy + 1] = (90, 240, 70) # dripping green acid
    # Grasping mutant tentacle lunging forward
    for tx, ty in [(92, 63), (88, 65), (84, 68), (80, 72)]:
        pixels[tx, ty] = (60, 160, 50)
        pixels[tx, ty + 1] = (35, 95, 30)

    # 2. Darken lower ~40%
    darken_lower_band(img, y_start=76, darken_factor=0.34, tint=(35, 16, 8))
    
    # 3. Title typography: BIO MENACE
    draw_bitmap_text(img, "BIO MENACE", 64, 98, fg_color=(255, 220, 70), bg_color=(25, 8, 4))
    
    save_cover(img, "bio-menace.png")


# -------------------------------------------------------------
# 3. BLAKE STONE: ALIENS OF GOLD (amber/orange)
# -------------------------------------------------------------
def make_blake_stone():
    img = Image.new('RGB', (128, 128), (20, 12, 6))
    pixels = img.load()
    
    # 1. Sci-Fi Underground Fortress Interior (Amber / Gold lighting)
    # Metallic bulkhead wall with hexagonal panels & hazard trims
    c_wall_dark = (32, 20, 10)
    c_wall_mid = (75, 45, 20)
    c_wall_hi = (145, 95, 40)
    
    dither_gradient_v(img, 0, 75, c_wall_dark, c_wall_mid)
    
    # Isometric ceiling conduit / fluorescent amber light bars (y=4..10)
    for x in range(0, 128):
        for y in range(4, 9):
            if (x // 8) % 2 == 0:
                pixels[x, y] = (255, 185, 30) # Bright amber security lamp
            else:
                pixels[x, y] = (90, 50, 15)
                
    # Modular bulkhead wall seams & vents
    for y in range(9, 75):
        for x in range(0, 128):
            if x % 22 == 0 or y == 22 or y == 48:
                pixels[x, y] = c_wall_dark
            elif (x % 22 == 1 or y == 23 or y == 49) and y < 70:
                pixels[x, y] = c_wall_hi
            # Ventilation grating texture
            if (28 <= x <= 40 or 88 <= x <= 100) and (28 <= y <= 42):
                if y % 2 == 0:
                    pixels[x, y] = (25, 15, 8)
                else:
                    pixels[x, y] = (110, 70, 30)

    # Reinforced Blast Door / Elevator Airlock in Center (x=46..82, y=16..75)
    for y in range(16, 75):
        for x in range(46, 83):
            pixels[x, y] = (50, 32, 16)
            if x == 46 or x == 82 or x == 64:
                pixels[x, y] = (100, 65, 30)
            # Diagonal warning hazard stripes (yellow/black) along frame
            if (x <= 50 or x >= 78) and (x + y) % 6 < 3:
                pixels[x, y] = (240, 170, 20)

    # High-Tech Keycard Terminal & Informant Console (x=84..95, y=34..54)
    for y in range(34, 54):
        for x in range(84, 95):
            pixels[x, y] = (28, 18, 12)
    # Console screen with gold tactical wireframe radar
    for y in range(38, 48):
        for x in range(86, 93):
            pixels[x, y] = (245, 180, 30)
            if (x == 89 or y == 43) or (x + y) % 3 == 0:
                pixels[x, y] = (80, 45, 10)
    # LED status indicators
    pixels[86, 50] = (255, 40, 30) # Red LED
    pixels[89, 50] = (255, 200, 30) # Amber LED
    pixels[92, 50] = (50, 255, 60) # Green LED

    # Covert Space Agent (Blake archetype, x=22..40, y=34..72)
    # Agent visor & haircut
    for y in range(34, 38):
        for x in range(26, 33):
            pixels[x, y] = (70, 40, 15) # Brown hair
    for y in range(38, 43):
        for x in range(27, 33):
            pixels[x, y] = (235, 175, 125) # Face
    pixels[30, 39] = (40, 200, 255) # High-tech blue tactical scanner eyepiece
    pixels[31, 39] = (0, 240, 255)
    
    # Body: Royal blue space agent field uniform with gold epaulets
    for y in range(43, 66):
        for x in range(24, 36):
            pixels[x, y] = (25, 50, 110) # Blue combat suit
            if y == 43 and 25 <= x <= 35:
                pixels[x, y] = (255, 205, 40) # Gold shoulder epaulets
            if y == 46 and 28 <= x <= 32:
                pixels[x, y] = (255, 215, 50) # Star federation gold badge
            if 53 <= y <= 56 and 25 <= x <= 35:
                pixels[x, y] = (100, 65, 25) # Utility belt & holster
                
    # High-Tech Particle Blaster firing forward (x=34..52, y=47..51)
    for x in range(34, 48):
        for y in range(47, 50):
            pixels[x, y] = (70, 75, 85)
    # Plasma beam discharging!
    for x in range(48, 70):
        pixels[x, 48] = (255, 240, 150)
        if x % 2 == 0:
            pixels[x, 47] = (255, 160, 30)
            pixels[x, 49] = (255, 160, 30)

    # Alien Bio-Specimen Containment Chamber on right (x=98..124, y=24..74)
    # Brass/Gold reinforced cryogenic chamber
    for y in range(24, 72):
        for x in range(98, 124):
            if x == 98 or x == 123 or y == 24 or y == 71:
                pixels[x, y] = (175, 125, 45) # Gold metal frame
                if (x + y) % 2 == 0:
                    pixels[x, y] = (245, 195, 80) # Gold sheen
            else:
                # Bubbling golden mutagen liquid
                t = math.sin(x * 0.5 + y * 0.4)
                pixels[x, y] = (195, 120, 25) if t > 0 else (135, 75, 15)
                if (x * 11 + y * 7) % 9 == 0:
                    pixels[x, y] = (255, 230, 100) # Rising bio-bubble
    # Terrifying gold/shadow alien entity inside pod with glowing red eyes
    for y in range(36, 54):
        for x in range(104, 118):
            pixels[x, y] = (80, 40, 12)
    pixels[107, 42] = (255, 30, 20) # Glowing red alien eyes
    pixels[108, 42] = (255, 200, 40)
    pixels[113, 42] = (255, 30, 20)
    pixels[114, 42] = (255, 200, 40)

    # 2. Darken lower ~40%
    darken_lower_band(img, y_start=76, darken_factor=0.34, tint=(35, 20, 8))
    
    # 3. Title typography: BLAKE STONE / ALIENS OF GOLD (2 lines)
    draw_bitmap_text(img, "BLAKE STONE", 64, 88, fg_color=(255, 225, 90), bg_color=(25, 12, 4))
    draw_bitmap_text(img, "ALIENS OF GOLD", 64, 106, fg_color=(255, 185, 55), bg_color=(25, 12, 4))
    
    save_cover(img, "blake-stone-shareware.png")


# -------------------------------------------------------------
# 4. CAVE STORY (blue/cyan)
# -------------------------------------------------------------
def make_cave_story():
    img = Image.new('RGB', (128, 128), (8, 16, 32))
    pixels = img.load()
    
    # 1. Background: Deep mystical subterranean cavern glowing with blue & cyan bioluminescence
    c_cave1 = (6, 12, 28)
    c_cave2 = (14, 35, 68)
    c_cave3 = (20, 80, 120)
    c_cave4 = (35, 135, 175)
    dither_gradient_v(img, 0, 30, c_cave1, c_cave2)
    dither_gradient_v(img, 30, 60, c_cave2, c_cave3)
    dither_gradient_v(img, 60, 85, c_cave3, c_cave4)
    
    # Cavern Stalactites hanging from roof with dripping crystal water
    stalactites = [
        (6, 26, 12), (24, 18, 10), (45, 32, 16), (68, 20, 12), (90, 28, 14), (114, 22, 12)
    ]
    for sx, sh, sw in stalactites:
        for y in range(0, sh):
            w = int(sw * (1.0 - y / float(sh)))
            for x in range(sx - w, sx + w + 1):
                if 0 <= x < 128:
                    pixels[x, y] = (12, 28, 52)
                    if x == sx:
                        pixels[x, y] = (30, 75, 110)
                    # Luminous water droplet at tip
                    if y == sh - 1:
                        pixels[x, y] = (150, 245, 255)

    # Giant Bioluminescent Cyan Mushrooms & Flora (left background, x=10..26, y=42..72)
    # Mushroom Cap (cyan glow with spore spots)
    for y in range(44, 54):
        w = int(12 * math.cos((y - 49) / 4.5))
        for x in range(18 - w, 18 + w + 1):
            if 0 <= x < 128:
                pixels[x, y] = (0, 215, 235)
                if (x + y) % 2 == 0:
                    pixels[x, y] = (180, 255, 255) # Spore glow
                if y == 53:
                    pixels[x, y] = (0, 140, 160) # Cap rim shadow
    # Stalk
    for y in range(54, 76):
        for x in range(16, 21):
            pixels[x, y] = (25, 75, 105)
            if x == 18:
                pixels[x, y] = (50, 125, 160)

    # Floating Ruin Platforms with Lush Glowing Cyan Moss
    platforms = [(8, 72, 30), (48, 65, 34), (94, 70, 28)]
    for px, py, pw in platforms:
        for x in range(px, px + pw):
            for y in range(py, py + 10):
                if 0 <= x < 128:
                    # Glowing moss top
                    if y == py:
                        pixels[x, y] = (0, 235, 190)
                    elif y == py + 1:
                        pixels[x, y] = (0, 160, 130)
                    else:
                        # Ancient brickwork
                        pixels[x, y] = (18, 40, 68)
                        if (x % 6 == 0 and y % 3 == 0):
                            pixels[x, y] = (35, 70, 110)

    # Hero: Scout Robot in Mid-Air Leap (Quote archetype, x=54..68, y=40..66)
    # Iconic green cap & robotic antennas
    pixels[56, 38] = (0, 255, 225) # Left antenna tip
    pixels[56, 39] = (30, 180, 150)
    pixels[63, 38] = (0, 255, 225) # Right antenna tip
    pixels[63, 39] = (30, 180, 150)
    # Cap (green/emerald)
    for y in range(40, 45):
        for x in range(56, 65):
            pixels[x, y] = (20, 165, 105)
    pixels[65, 44] = (40, 215, 140) # Cap visor brim
    pixels[66, 44] = (40, 215, 140)
    
    # Face (pale android face & expressive eyes)
    for y in range(45, 50):
        for x in range(57, 65):
            pixels[x, y] = (240, 235, 225)
    pixels[62, 47] = (20, 30, 65) # Eye
    pixels[62, 46] = (0, 210, 255) # Eye gleam
    
    # Flowing Red Scarf blowing dynamically behind
    scarf_pts = [(54, 48), (51, 47), (48, 46), (45, 47), (42, 49), (39, 48)]
    for sx, sy in scarf_pts:
        pixels[sx, sy] = (235, 45, 55)
        pixels[sx, sy + 1] = (185, 25, 35)

    # Torso & Combat Trousers (mid-leap pose)
    for y in range(50, 60):
        for x in range(57, 65):
            pixels[x, y] = (32, 38, 52) # Dark combat vest
    # Leaping boots
    pixels[56, 60] = (210, 40, 40)
    pixels[57, 60] = (210, 40, 40)
    pixels[63, 61] = (210, 40, 40)
    pixels[64, 61] = (210, 40, 40)

    # Polar Star Energy Blaster & Pulsing Star Projectiles
    # Handgun (x=65..74, y=51..54)
    for x in range(65, 73):
        pixels[x, 52] = (230, 230, 240)
        pixels[x, 53] = (130, 135, 150)
    # Pulsing energy star projectiles flying right
    for bx, by in [(78, 51), (92, 49), (108, 48)]:
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if abs(dx) + abs(dy) <= 2:
                    pixels[bx + dx, by + dy] = (0, 255, 240)
        pixels[bx, by] = (255, 255, 255) # Core brightness

    # Flying Cavern Critters / Bats in high darkness (x=90..118, y=20..32)
    for bx, by in [(94, 28), (112, 20), (32, 26)]:
        pixels[bx, by] = (15, 25, 48)
        pixels[bx - 1, by - 1] = (25, 45, 75)
        pixels[bx + 1, by - 1] = (25, 45, 75)
        pixels[bx - 2, by - 2] = (35, 65, 100)
        pixels[bx + 2, by - 2] = (35, 65, 100)
        pixels[bx, by] = (255, 60, 90) # Red glowing eye

    # 2. Darken lower ~40%
    darken_lower_band(img, y_start=76, darken_factor=0.34, tint=(10, 22, 48))
    
    # 3. Title typography: CAVE STORY
    draw_bitmap_text(img, "CAVE STORY", 64, 98, fg_color=(210, 245, 255), bg_color=(8, 14, 28))
    
    save_cover(img, "cave-story.png")


if __name__ == "__main__":
    make_beneath_a_steel_sky()
    make_bio_menace()
    make_blake_stone()
    make_cave_story()
    print("Batch 1 completed successfully.")
