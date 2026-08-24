import os
import math
from pixel_art_engine import PixelCanvas

# =============================================================
# BATCH A: 14 to 22
# =============================================================

def make_epic_pinball():
    c = PixelCanvas((25, 10, 5))
    c.dither_gradient_v(0, 50, (45, 15, 5), (145, 60, 12))
    c.dither_gradient_v(50, 128, (145, 60, 12), (70, 25, 8))
    
    for y in range(0, 128):
        c.pixels[8, y] = (255, 190, 45)
        c.pixels[9, y] = (90, 40, 10)
        c.pixels[118, y] = (90, 40, 10)
        c.pixels[119, y] = (255, 190, 45)
        if 12 <= y <= 72:
            rx1 = int(22 + 14 * math.sin((y - 12) * 0.08))
            c.pixels[rx1, y] = (255, 220, 80)
            c.pixels[rx1 + 1, y] = (255, 130, 20)
            rx2 = int(105 - 14 * math.sin((y - 12) * 0.08))
            c.pixels[rx2, y] = (255, 220, 80)
            c.pixels[rx2 - 1, y] = (255, 130, 20)

    for bx, by in [(38, 28), (88, 28), (64, 48)]:
        c.draw_dithered_radial(bx, by, 14, (255, 240, 160), (180, 70, 15))
        for dy in range(-5, 6):
            for dx in range(-5, 6):
                if math.hypot(dx, dy) <= 5:
                    c.pixels[bx + dx, by + dy] = (255, 255, 230)
                    
    px, py = 52, 34
    for dy in range(-7, 8):
        for dx in range(-7, 8):
            if math.hypot(dx, dy) <= 7.2:
                shade = (dx - dy) / 9.0
                col = max(40, min(255, int(195 + shade * 65)))
                c.pixels[px + dx, py + dy] = (col, col, int(col * 0.9))
    c.pixels[px - 3, py - 3] = (255, 255, 255)
    c.pixels[px - 2, py - 3] = (255, 255, 255)

    for sx, sy in [(60, 32), (66, 28), (62, 22), (48, 20), (44, 42), (64, 42)]:
        c.pixels[sx, sy] = (255, 255, 200)

    for y in range(66, 76):
        fx1 = int(32 + (y - 66) * 1.8)
        fx2 = int(96 - (y - 66) * 1.8)
        for w in range(4):
            c.pixels[fx1 + w, y] = (255, 50, 30)
            c.pixels[fx2 - w, y] = (255, 50, 30)

    c.finalize_cover("epic-pinball-shareware.png", ["EPIC PINBALL"], (255, 225, 75), (25, 8, 4), (35, 18, 8))

def make_flight_amazon_queen():
    c = PixelCanvas((18, 8, 28))
    c.dither_gradient_v(0, 35, (20, 6, 32), (90, 22, 95))
    c.dither_gradient_v(35, 75, (90, 22, 95), (180, 50, 140))
    
    for y in range(30, 75):
        step = (y - 30) // 5
        pw = int(12 + step * 6)
        for x in range(48 - pw, 48 + pw):
            if 0 <= x < 128:
                c.pixels[x, y] = (50, 15, 60)
                if (x + y) % 4 == 0:
                    c.pixels[x, y] = (85, 28, 95)
    c.pixels[48, 28] = (255, 200, 120)
    c.pixels[48, 29] = (255, 80, 140)

    for bx, by, brad in [(10, 56, 20), (118, 52, 24), (92, 64, 20), (26, 68, 18)]:
        for y in range(by - brad, by + brad + 1):
            for x in range(bx - brad, bx + brad + 1):
                if math.hypot(x - bx, (y - by) * 1.2) <= brad and 0 <= x < 128 and 0 <= y < 128:
                    c.pixels[x, y] = (30, 10, 45)
                    if (x * 5 + y * 11) % 4 == 0:
                        c.pixels[x, y] = (65, 22, 85)

    plane_lines = [
        "........rrrrrrrr....................",
        ".....bbbbwwwwwwwwss.................",
        "..bbbbwwwwwwwwwwwwwwssss............",
        "bbbbwwwwwwwwwwwwwwwwwwwwssss........",
        "ppppGGGGppppGGGGppppGGGGpppp........",
        "..wwwwwwwwwwwwwwwwwwwwwwssss........",
        "....wwwwwwwwwwwwwwssss..............",
        "........rrrrrrrr...................."
    ]
    pal = {
        'w': (235, 225, 245),
        's': (160, 140, 180),
        'b': (80, 220, 255),
        'r': (255, 50, 90),
        'G': (70, 25, 80),
        'p': (240, 230, 255)
    }
    c.draw_sprite(45, 30, plane_lines, pal)

    for y in range(65, 128):
        rx = int(64 + 20 * math.sin(y * 0.08))
        for x in range(rx - 16, rx + 16):
            if 0 <= x < 128:
                c.pixels[x, y] = (45, 18, 70)
                if (x + y) % 3 == 0:
                    c.pixels[x, y] = (150, 55, 130)

    c.finalize_cover("flight-of-the-amazon-queen.png", ["FLIGHT OF THE", "AMAZON QUEEN"], (255, 235, 250), (15, 4, 20), (25, 8, 35))

def make_freedoom():
    c = PixelCanvas((8, 16, 28))
    c.dither_gradient_v(0, 75, (6, 12, 25), (15, 65, 105))
    
    for bx, bw, bh in [(8, 26, 68), (38, 30, 78), (74, 28, 70), (106, 20, 60)]:
        for y in range(128 - bh, 128):
            for x in range(bx, bx + bw):
                if 0 <= x < 128:
                    c.pixels[x, y] = (14, 32, 54)
                    if x == bx or x == bx + bw - 1:
                        c.pixels[x, y] = (30, 85, 125)
                    if (y % 8 == 0) and (x % 3 == 0) and y < 75:
                        c.pixels[x, y] = (0, 240, 230)

    for y in range(64, 128):
        for x in range(0, 128):
            if y >= 68:
                c.pixels[x, y] = (0, 190, 180)
                if (x + y) % 3 == 0:
                    c.pixels[x, y] = (140, 255, 245)

    marine = [
        "......HHHHHHHH......",
        ".....HVVVVVVVVH.....",
        "....HBBBBBBBBBBH....",
        "....HBBBBBBBBBBH....",
        ".....HBBBBBBBBH.....",
        ".....AAAAAAAAAA.....",
        "....AGGGAAAAAGGA....",
        "...AGGGGGGGGGGGGA...",
        "...AGPGPPPPPPPPA....",
        "....AAPPPAAAAAA.....",
        "....LLLL....LLLL....",
        "....LLLL....LLLL....",
        "....FFFF....FFFF...."
    ]
    pal_marine = {
        'H': (20, 50, 75),
        'V': (0, 255, 240),
        'B': (35, 80, 115),
        'A': (30, 70, 100),
        'G': (50, 110, 150),
        'P': (180, 190, 210),
        'L': (25, 55, 80),
        'F': (15, 35, 55)
    }
    c.draw_sprite(18, 32, marine, pal_marine)

    for x in range(40, 88):
        c.pixels[x, 44] = (255, 255, 255)
        c.pixels[x, 43] = (0, 230, 255)
        c.pixels[x, 45] = (0, 230, 255)

    demon = [
        "....DDDDDDDDDDDD....",
        "..DDEEEEEEEEEEEEDD..",
        ".DEEYYYEEEEEYYYEED.",
        "DEEYRYYYEEEEYRYYYEED",
        "DEEEEEEEEEEEEEEEEEED",
        "DDEEFFFFFFFFFFFFEEDD",
        ".DDEFFFFFFFFFFFFEDD.",
        "..TT..TT....TT..TT.."
    ]
    pal_demon = {
        'D': (10, 35, 50),
        'E': (20, 65, 90),
        'Y': (0, 255, 230),
        'R': (255, 50, 80),
        'F': (240, 245, 255),
        'T': (15, 50, 70)
    }
    c.draw_sprite(86, 32, demon, pal_demon)

    c.finalize_cover("freedoom.png", ["FREEDOOM", "PHASE 1 & 2"], (210, 245, 255), (8, 14, 28), (10, 22, 45))

def make_heretic():
    c = PixelCanvas((22, 8, 4))
    c.dither_gradient_v(0, 35, (38, 10, 4), (160, 55, 10))
    c.dither_gradient_v(35, 75, (160, 55, 10), (245, 140, 25))
    
    for bx, bw, bh in [(6, 24, 75), (32, 30, 90), (66, 26, 72), (96, 28, 85)]:
        for y in range(128 - bh, 128):
            for x in range(bx, bx + bw):
                if 0 <= x < 128:
                    if y < 128 - bh + 12:
                        w = int((y - (128 - bh)) * (bw / 24.0))
                        if abs(x - (bx + bw // 2)) > w:
                            continue
                    c.pixels[x, y] = (40, 16, 6)
                    if x == bx or x == bx + bw - 1:
                        c.pixels[x, y] = (85, 35, 12)
                    if (y % 12 in [4, 5]) and (x in [bx + bw // 2 - 1, bx + bw // 2]):
                        c.pixels[x, y] = (255, 200, 40)

    for cx in [20, 54, 88, 114]:
        for y in range(62, 66):
            c.pixels[cx, y] = (20, 8, 4)
        c.pixels[cx, 60] = (255, 140, 20)
        c.pixels[cx, 59] = (255, 240, 150)

    wizard = [
        "....HHHHHHHH....",
        "...HEEEEEEEEH...",
        "..HHEEEEEEEEHH..",
        "..HRRRRRRRRRRH..",
        "..HRRRRRRRRRRH..",
        ".HGRRRRRRRRRRG..",
        ".HGRRRRRRRRRRGH.",
        "HHRRRRRRRRRRRRHH",
        "HHRRRRRRRRRRRRHH",
        "HHRRRRRRRRRRRRHH"
    ]
    pal_wiz = {
        'H': (20, 6, 4),
        'E': (255, 235, 120),
        'R': (45, 15, 6),
        'G': (180, 110, 30)
    }
    c.draw_sprite(24, 36, wizard, pal_wiz)

    for y in range(28, 72):
        c.pixels[44, y] = (110, 65, 25)
    c.pixels[44, 27] = (255, 240, 160)
    
    for fbx, fby in [(58, 38), (76, 34), (96, 30)]:
        c.draw_dithered_radial(fbx, fby, 8, (255, 255, 220), (255, 80, 10))

    garg = [
        "WW..HHHHHHHH..WW",
        "WW.HEEEEEEEEH.WW",
        "WWWHRRRRRRRRHHWW",
        ".WWHRRRRRRRRHW.W",
        "..RRRRRRRRRR....",
        "..FFFF....FFFF.."
    ]
    pal_garg = {
        'W': (65, 22, 8),
        'H': (35, 12, 5),
        'E': (255, 40, 20),
        'R': (45, 16, 6),
        'F': (25, 8, 3)
    }
    c.draw_sprite(94, 22, garg, pal_garg)

    c.finalize_cover("heretic-shareware.png", ["HERETIC"], (255, 225, 75), (25, 8, 2), (35, 15, 6))

def make_hocus_pocus():
    c = PixelCanvas((22, 12, 6))
    c.dither_gradient_v(0, 75, (40, 16, 6), (230, 125, 25))
    
    for bx, bw, bh in [(8, 22, 68), (32, 28, 80), (64, 24, 65), (92, 30, 85)]:
        for y in range(128 - bh, 128):
            for x in range(bx, bx + bw):
                if 0 <= x < 128:
                    c.pixels[x, y] = (60, 28, 12)
                    if x == bx or x == bx + bw - 1:
                        c.pixels[x, y] = (120, 60, 25)
                    if y < 128 - bh + 12:
                        w = (y - (128 - bh))
                        if abs(x - (bx + bw // 2)) <= w:
                            c.pixels[x, y] = (150, 45, 120)

    hocus = [
        "......PPPP......",
        ".....PPPPPP.....",
        "....PPSSSSPP....",
        "...PPPPPPPPPP...",
        "..PPPPPPPPPPPP..",
        "....FFFFFFFEE...",
        "....FFFFFFFFF...",
        "...RRRRRRRRRRR..",
        "..RRRRRRRRRRRRR.",
        "..RRRRRRRRRRRRR.",
        "...RRRR...RRRR.."
    ]
    pal_hocus = {
        'P': (160, 45, 130),
        'S': (255, 220, 40),
        'F': (245, 185, 135),
        'E': (20, 10, 5),
        'R': (65, 35, 105)
    }
    c.draw_sprite(24, 32, hocus, pal_hocus)

    for ox, oy in [(48, 44), (64, 38), (82, 34), (102, 30)]:
        c.draw_dithered_radial(ox, oy, 7, (255, 255, 220), (255, 180, 20))

    book = [
        "WW..BBBBBBBB..WW",
        "WW.BGGGGGGGGB.WW",
        "WW.BGGGGGGGGB.WW",
        ".WWBBBBBBBBBB.WW",
        "..WWW......WWW.."
    ]
    pal_book = {
        'W': (240, 240, 255),
        'B': (190, 40, 30),
        'G': (255, 230, 120)
    }
    c.draw_sprite(92, 26, book, pal_book)

    c.finalize_cover("hocus-pocus.png", ["HOCUS POCUS"], (255, 225, 75), (25, 10, 4), (35, 18, 8))

def make_jazz_jackrabbit():
    c = PixelCanvas((22, 12, 5))
    c.dither_gradient_v(0, 75, (45, 15, 5), (235, 130, 20))
    
    for x in range(0, 128):
        hill_y = int(56 + 12 * math.sin(x * 0.05))
        for y in range(hill_y, 128):
            c.pixels[x, y] = (50, 100, 25)
            if y == hill_y:
                c.pixels[x, y] = (100, 190, 45)

    for cx, ch in [(16, 36), (86, 44), (114, 30)]:
        for y in range(60 - ch, 60):
            w = int(8 * (1.0 - (60 - y) / float(ch)))
            for x in range(cx - w, cx + w + 1):
                if 0 <= x < 128:
                    c.pixels[x, y] = (225, 95, 15)
        for lx in range(cx - 5, cx + 6):
            c.pixels[lx, 60 - ch - 1] = (60, 165, 35)

    jazz = [
        "...EEEE......EEEE...",
        "...EEEE......EEEE...",
        "...EPPP......EPPP...",
        "...GGGGGGGGGGGGGG...",
        "..RRRRRRRRRRRRRRRR..",
        "..GGFFFFFFEEGGGGGG..",
        "..GGFFFFFFFFGGGGGG..",
        "...GGGGGGGGGBBBBB...",
        "..GGGGGGGGGGGBBBBB..",
        "...SSSSSS...SSSSSS.."
    ]
    pal_jazz = {
        'E': (45, 170, 55),
        'P': (255, 140, 160),
        'G': (55, 190, 65),
        'R': (235, 30, 20),
        'F': (240, 230, 200),
        'B': (35, 95, 230),
        'S': (225, 30, 20)
    }
    c.draw_sprite(34, 32, jazz, pal_jazz)

    for x in range(62, 98):
        c.pixels[x, 46] = (255, 240, 80)
    for dx in range(-18, 0):
        c.pixels[38 + dx, 62] = (220, 160, 80)

    c.finalize_cover("jazz-jackrabbit-shareware.png", ["JAZZ JACKRABBIT"], (255, 225, 75), (25, 8, 4), (35, 18, 8))

def make_keen_dreams():
    c = PixelCanvas((20, 12, 5))
    c.dither_gradient_v(0, 75, (40, 14, 5), (230, 130, 25))
    
    for x in range(0, 128):
        if x % 10 == 0:
            for y in range(48, 75):
                c.pixels[x, y] = (145, 95, 45)

    billy = [
        "....YYYYYYYY....",
        "...YYYYYYYYYY...",
        "...YYYYEEYYYY...",
        "....FFFFFFFF....",
        "...SPPSPPSPP....",
        "...SPPSPPSPP....",
        "...SPPSPPSPP....",
        "...PPPP..PPPP...",
        "...SSSS..SSSS..."
    ]
    pal_billy = {
        'Y': (245, 195, 30),
        'E': (20, 10, 5),
        'F': (240, 180, 130),
        'S': (170, 45, 150),
        'P': (240, 235, 240)
    }
    c.draw_sprite(22, 32, billy, pal_billy)

    for x in range(38, 54):
        c.pixels[x, 46] = (100, 60, 25)
    c.pixels[55, 46] = (255, 100, 180)
    for px, py in [(62, 44), (72, 42), (82, 40)]:
        c.pixels[px, py] = (255, 255, 160)

    tomato = [
        ".......GGGG.......",
        "....RRRRRRRRRR....",
        "...RRRRRRRRRRRR...",
        "..RRWEERRRRWEERR..",
        "..RRRRRRRRRRRRRR..",
        "..RRFFFFFFFFFFRR..",
        "...RRRRRRRRRRRR...",
        "....LLLL..LLLL...."
    ]
    pal_tomato = {
        'G': (40, 160, 45),
        'R': (220, 35, 25),
        'W': (255, 255, 255),
        'E': (20, 10, 5),
        'F': (255, 255, 240),
        'L': (180, 25, 20)
    }
    c.draw_sprite(86, 32, tomato, pal_tomato)

    c.finalize_cover("keen-dreams.png", ["KEEN DREAMS"], (255, 220, 70), (25, 8, 4), (35, 18, 8))

def make_lure_of_the_temptress():
    c = PixelCanvas((18, 6, 26))
    c.dither_gradient_v(0, 75, (20, 6, 32), (150, 38, 115))
    
    for bx, bw, bh in [(6, 26, 75), (34, 32, 90), (70, 28, 70), (100, 26, 80)]:
        for y in range(128 - bh, 128):
            for x in range(bx, bx + bw):
                if 0 <= x < 128:
                    c.pixels[x, y] = (42, 14, 52)
                    if x == bx or x == bx + bw - 1:
                        c.pixels[x, y] = (80, 26, 90)
                    if (y % 12 == 0) and (x % 6 == 0) and y < 75:
                        c.pixels[x, y] = (255, 120, 220)

    for x in range(76, 98):
        c.pixels[x, 48] = (95, 32, 105)
    for y in range(36, 48):
        for x in range(84, 90):
            c.pixels[x, y] = (20, 5, 25)
    c.pixels[87, 38] = (255, 60, 180)

    hero = [
        "....FFFF....",
        "...FFFFFF...",
        "...FEEFFF...",
        "...TTTTTT...",
        "..TTTTTTTT..",
        "..TTTTTTTT..",
        "...PPP..PPP.",
        "...BBB..BBB."
    ]
    pal_hero = {
        'F': (225, 165, 125),
        'E': (30, 15, 10),
        'T': (85, 55, 35),
        'P': (45, 30, 20),
        'B': (25, 15, 10)
    }
    c.draw_sprite(24, 42, hero, pal_hero)

    skorl = [
        "....AAAAAA....",
        "...AAGGGGAA...",
        "...AGRRREEA...",
        "...AAAAAAAA...",
        "..AAAAAAAAAA..",
        "..AAAAAAAAAA..",
        "...AAA..AAA..."
    ]
    pal_skorl = {
        'A': (40, 35, 50),
        'G': (55, 130, 50),
        'R': (255, 40, 30),
        'E': (20, 10, 5)
    }
    c.draw_sprite(54, 40, skorl, pal_skorl)
    for y in range(28, 68):
        c.pixels[68, y] = (95, 70, 45)
    c.pixels[68, 27] = (210, 210, 230)

    c.finalize_cover("lure-of-the-temptress.png", ["LURE OF THE", "TEMPTRESS"], (255, 235, 250), (15, 4, 20), (25, 8, 35))

def make_major_stryker():
    c = PixelCanvas((20, 10, 4))
    c.dither_gradient_v(0, 75, (25, 8, 4), (185, 75, 14))
    
    for sx, sy in [(14, 12), (36, 24), (72, 8), (96, 18), (116, 30), (54, 38)]:
        c.pixels[sx, sy] = (255, 235, 170)

    for x in range(0, 128):
        planet_y = int(60 + 10 * math.sin(x * 0.04))
        for y in range(planet_y, 128):
            c.pixels[x, y] = (95, 38, 12)
            if (x + y) % 4 == 0:
                c.pixels[x, y] = (160, 65, 18)

    jet = [
        "........WW........",
        ".......WCCW.......",
        "......WWCCWW......",
        ".....WWWCCWWW.....",
        "....WWWWSSWWWW....",
        "...LLWWSSSSWWLL...",
        "..LLLWSSSSSSWLLL..",
        ".LLLLWSSSSSSWLLLL.",
        "LLLLLWSSSSSSWLLLLL",
        ".....WEEEEEEW.....",
        "......FF..FF......"
    ]
    pal_jet = {
        'W': (225, 220, 235),
        'C': (80, 190, 255),
        'S': (160, 150, 175),
        'L': (120, 120, 140),
        'E': (50, 50, 65),
        'F': (255, 140, 20)
    }
    c.draw_sprite(54, 34, jet, pal_jet)

    for y in range(6, 34):
        c.pixels[54, y] = (255, 230, 50)
        c.pixels[73, y] = (255, 230, 50)
        c.pixels[64, y] = (255, 130, 20)

    for ex, ey, erad in [(104, 22, 12), (96, 18, 7), (112, 26, 8)]:
        c.draw_dithered_radial(ex, ey, erad, (255, 255, 220), (220, 70, 15))

    c.finalize_cover("major-stryker.png", ["MAJOR STRYKER"], (255, 225, 75), (25, 8, 4), (35, 18, 8))

# =============================================================
# BATCH B: 23 to 31
# =============================================================

def make_monster_bash():
    c = PixelCanvas((25, 12, 5))
    c.dither_gradient_v(0, 75, (35, 12, 5), (220, 110, 20))
    
    c.draw_dithered_radial(96, 28, 18, (255, 245, 180), (220, 130, 30))
    for bx, bw, bh in [(15, 28, 65), (45, 24, 55)]:
        for y in range(128 - bh, 128):
            for x in range(bx, bx + bw):
                if 0 <= x < 128:
                    c.pixels[x, y] = (40, 16, 6)

    for gx, gy in [(12, 60), (74, 58), (110, 62)]:
        for dy in range(0, 14):
            for dx in range(-4, 5):
                c.pixels[gx + dx, gy + dy] = (80, 45, 20)

    johnny = [
        "....CCCC....",
        "...CCCCCC...",
        "...CCFEFF...",
        "...FFFFFF...",
        "..VVVVVVVV..",
        ".VVVVVVVVVV.",
        "..JJJ..JJJ..",
        "..JJJ..JJJ..",
        "..SSS..SSS.."
    ]
    pal_j = {
        'C': (220, 35, 25),
        'F': (240, 180, 130),
        'E': (20, 10, 5),
        'V': (45, 90, 180),
        'J': (40, 40, 60),
        'S': (240, 230, 220)
    }
    c.draw_sprite(28, 38, johnny, pal_j)

    for y in range(44, 52):
        c.pixels[42, y] = (140, 85, 30)
    for x in range(44, 78):
        c.pixels[x, 46] = (255, 240, 120)

    frank = [
        "...GGGGGGGG...",
        "..GGGGGGGGGG..",
        "..GGGGEEGGGG..",
        "..GGGGGGGGGG..",
        "..BBBBBBBBBB..",
        ".BBBBBBBBBBBB.",
        ".BBBBBBBBBBBB.",
        "..TTT....TTT..",
        "..TTT....TTT.."
    ]
    pal_f = {
        'G': (60, 140, 65),
        'E': (255, 220, 40),
        'B': (60, 35, 20),
        'T': (30, 20, 15)
    }
    c.draw_sprite(82, 36, frank, pal_f)

    c.finalize_cover("monster-bash.png", ["MONSTER BASH"], (255, 225, 75), (25, 8, 4), (35, 18, 8))

def make_one_must_fall():
    c = PixelCanvas((24, 10, 4))
    c.dither_gradient_v(0, 75, (40, 12, 4), (230, 110, 15))
    
    for x in range(0, 128):
        if (x // 8) % 2 == 0:
            c.pixels[x, 14] = (255, 200, 40)
            c.pixels[x, 15] = (255, 120, 20)

    mech_left = [
        "......BBBB......",
        ".....BVVVVB.....",
        "....BBBBBBBB....",
        "...BBAAAABBA....",
        "..BBAAAAAAAABB..",
        ".BBAAAAAAAAAABBA",
        ".BBAAAAAAAAAABBA",
        "..BBAAAABBAA....",
        "...LL......LL...",
        "...LL......LL...",
        "...FF......FF..."
    ]
    pal_l = {
        'B': (25, 70, 150),
        'V': (0, 240, 255),
        'A': (60, 120, 205),
        'L': (20, 50, 110),
        'F': (15, 35, 80)
    }
    c.draw_sprite(20, 34, mech_left, pal_l)

    c.draw_dithered_radial(64, 44, 16, (255, 255, 240), (255, 70, 10))

    mech_right = [
        "......RRRR......",
        ".....RVVVVR.....",
        "....RRRRRRRR....",
        "...RRAAAARRA....",
        "..RRAAAAAAAARR..",
        ".RRAAAAAAAAAARRA",
        ".RRAAAAAAAAAARRA",
        "..RRAAAARRAA....",
        "...LL......LL...",
        "...LL......LL...",
        "...FF......FF..."
    ]
    pal_r = {
        'R': (180, 40, 20),
        'V': (255, 220, 40),
        'A': (230, 95, 30),
        'L': (130, 30, 15),
        'F': (80, 20, 10)
    }
    c.draw_sprite(76, 34, mech_right, pal_r)

    c.finalize_cover("one-must-fall-2097.png", ["ONE MUST FALL", "2097"], (255, 225, 75), (25, 8, 4), (35, 18, 8))

def make_openra():
    c = PixelCanvas((8, 18, 32))
    c.dither_gradient_v(0, 75, (6, 14, 28), (18, 75, 120))
    
    for y in range(60, 128):
        for x in range(0, 128):
            c.pixels[x, y] = (30, 65, 95)
            if (x + y) % 3 == 0:
                c.pixels[x, y] = (160, 220, 245)

    for y in range(28, 65):
        c.pixels[96, y] = (80, 90, 110)
        c.pixels[97, y] = (140, 150, 170)
    c.draw_dithered_radial(96, 24, 10, (200, 255, 255), (0, 160, 240))
    for lx, ly in [(86, 32), (76, 38), (64, 42), (52, 46)]:
        c.pixels[lx, ly] = (255, 255, 255)
        c.pixels[lx, ly - 1] = (0, 230, 255)

    tank = [
        "......GGGGGGGGGG......",
        ".....GGCCCCCCCCGG.....",
        "....GGGGGGGGGGGGGG....",
        "...GGGGGGGGGGGGGGGG...",
        "..TTTTTTTTTTTTTTTTTT..",
        "..TWWWTWWWTWWWTWWWTW..",
        "..TTTTTTTTTTTTTTTTTT.."
    ]
    pal_tank = {
        'G': (30, 75, 105),
        'C': (0, 240, 255),
        'T': (15, 40, 60),
        'W': (80, 120, 150)
    }
    c.draw_sprite(16, 42, tank, pal_tank)
    for x in range(36, 68):
        c.pixels[x, 44] = (140, 160, 180)
        c.pixels[x, 46] = (140, 160, 180)

    c.finalize_cover("openra.png", ["OPENRA"], (210, 245, 255), (8, 14, 28), (10, 22, 45))

def make_openttd():
    c = PixelCanvas((10, 22, 38))
    c.dither_gradient_v(0, 75, (12, 28, 55), (45, 125, 180))
    
    for x in range(0, 128):
        hy = int(54 + 8 * math.sin(x * 0.06))
        for y in range(hy, 128):
            c.pixels[x, y] = (25, 95, 45)
            if (x + y) % 3 == 0:
                c.pixels[x, y] = (45, 150, 70)

    for x in range(12, 116):
        c.pixels[x, 46] = (130, 135, 150)
        c.pixels[x, 47] = (70, 75, 85)
        if x % 20 in [0, 1, 2]:
            for y in range(48, 68):
                c.pixels[x, y] = (110, 115, 130)

    train = [
        "....RRRRRRRRRRRRRRRRRR....",
        "...RRWWWWWWWWWWWWWWWWRR...",
        "..RRRRRRRRRRRRRRRRRRRRRR..",
        "...WW..WW..WW..WW..WW..WW."
    ]
    pal_train = {
        'R': (220, 45, 35),
        'W': (240, 240, 250)
    }
    c.draw_sprite(38, 38, train, pal_train)
    for sx, sy in [(34, 30), (28, 24), (20, 20)]:
        c.draw_dithered_radial(sx, sy, 5, (255, 255, 255), (180, 210, 235))

    c.finalize_cover("openttd.png", ["OPENTTD"], (210, 245, 255), (8, 14, 28), (10, 22, 45))

def make_raptor():
    c = PixelCanvas((22, 10, 4))
    c.dither_gradient_v(0, 75, (35, 10, 4), (195, 80, 15))
    
    for bx, bw, bh in [(10, 26, 50), (45, 30, 65), (88, 28, 55)]:
        for y in range(128 - bh, 128):
            for x in range(bx, bx + bw):
                if 0 <= x < 128:
                    c.pixels[x, y] = (45, 20, 8)
                    if (x + y) % 5 == 0:
                        c.pixels[x, y] = (85, 35, 12)

    for ex, ey in [(28, 48), (98, 44)]:
        c.draw_dithered_radial(ex, ey, 14, (255, 255, 200), (220, 70, 10))

    raptor_jet = [
        "..............GG..............",
        ".............GGGG.............",
        "............GGCCGG............",
        "...........GGGGCGGG...........",
        "..........GGGGGGGGGG..........",
        ".........GGGGSSSSGGGG.........",
        "........WWGGSSSSSSGGWW........",
        ".......WWWGGSSSSSSGGWWW.......",
        "......WWWWGGSSSSSSGGWWWW......",
        ".....WWWWWGGSSSSSSGGWWWWW.....",
        "....WWWWWWGGSSSSSSGGWWWWWW....",
        "...WWWWWWWGGSSSSSSGGWWWWWWW...",
        "..WWWWWWWWGGSSSSSSGGWWWWWWWW..",
        ".WWWWWWWWWGGSSSSSSGGWWWWWWWWW.",
        "WWWWWWWWWWGGSSSSSSGGWWWWWWWWWW",
        "..........GGFFFFFFGG.........."
    ]
    pal_rap = {
        'G': (80, 85, 100),
        'C': (0, 240, 255),
        'S': (45, 50, 60),
        'W': (125, 130, 145),
        'F': (255, 140, 20)
    }
    c.draw_sprite(42, 26, raptor_jet, pal_rap)

    for y in range(6, 26):
        c.pixels[42, y] = (255, 230, 40)
        c.pixels[85, y] = (255, 230, 40)

    c.finalize_cover("raptor-call-of-the-shadows.png", ["RAPTOR", "CALL OF SHADOWS"], (255, 225, 75), (25, 8, 4), (35, 18, 8))

def make_rise_of_the_triad():
    c = PixelCanvas((25, 10, 4))
    c.dither_gradient_v(0, 75, (40, 12, 4), (235, 115, 18))
    
    for x in range(0, 128):
        c.pixels[x, 66] = (90, 40, 15)
        for y in range(67, 128):
            c.pixels[x, y] = (45, 18, 6)

    # Large operative
    op = [
        "........HHHH........",
        ".......HVVVVH.......",
        ".......HVVVVH.......",
        ".......HBBBBH.......",
        "......HBAAAABH......",
        "......HBAAAABH......",
        ".....HHBAAAABHH.....",
        ".....HHBAAAABHH.....",
        "......HBAAAABH......",
        ".......BAAAAB.......",
        ".......LL..LL.......",
        ".......LL..LL.......",
        ".......LL..LL.......",
        ".......FF..FF.......",
        ".......FF..FF......."
    ]
    pal_op = {
        'H': (20, 20, 25),
        'V': (255, 40, 30),
        'B': (40, 40, 50),
        'A': (70, 75, 90),
        'L': (30, 30, 40),
        'F': (15, 15, 20)
    }
    c.draw_sprite(30, 24, op, pal_op)

    for x in range(48, 68):
        c.pixels[x, 32] = (90, 95, 110)
    for x in range(68, 105):
        c.pixels[x, 32] = (255, 240, 80)
        c.pixels[x, 31] = (255, 120, 20)
        c.pixels[x, 33] = (255, 120, 20)
    c.draw_dithered_radial(106, 32, 14, (255, 255, 220), (220, 60, 10))
    c.draw_dithered_radial(40, 66, 12, (255, 240, 100), (180, 60, 15))

    c.finalize_cover("rise-of-the-triad-shareware.png", ["RISE OF THE", "TRIAD"], (255, 225, 75), (25, 8, 4), (35, 18, 8))

def make_secret_agent():
    c = PixelCanvas((22, 12, 5))
    c.dither_gradient_v(0, 75, (35, 14, 5), (225, 120, 20))
    
    for bx, bw, bh in [(12, 28, 65), (78, 32, 70)]:
        for y in range(128 - bh, 128):
            for x in range(bx, bx + bw):
                if 0 <= x < 128:
                    c.pixels[x, y] = (40, 18, 8)
                    if (y % 10 == 0) and (x % 4 == 0) and y < 75:
                        c.pixels[x, y] = (255, 200, 40)

    c.draw_dithered_radial(94, 24, 12, (140, 145, 160), (60, 65, 75))

    # Large Secret Agent
    agent = [
        "........HHHH........",
        ".......HHHHHH.......",
        ".......HFFEEH.......",
        ".......HFFEEH.......",
        "........FFFF........",
        ".......TWTWTT.......",
        "......TTWTWTTT......",
        ".....TTTWTWTTTT.....",
        ".....TTTTTTTTTT.....",
        "......TTTTTTTT......",
        ".......PP..PP.......",
        ".......PP..PP.......",
        ".......PP..PP.......",
        ".......SS..SS.......",
        ".......SS..SS......."
    ]
    pal_ag = {
        'H': (50, 30, 15),
        'F': (240, 180, 130),
        'E': (20, 10, 5),
        'T': (20, 20, 25),
        'W': (245, 245, 255),
        'P': (20, 20, 25),
        'S': (10, 10, 15)
    }
    c.draw_sprite(28, 28, agent, pal_ag)

    for x in range(46, 62):
        c.pixels[x, 38] = (80, 85, 95)
    for x in range(62, 108):
        c.pixels[x, 38] = (255, 40, 30)

    c.finalize_cover("secret-agent.png", ["SECRET AGENT"], (255, 225, 75), (25, 8, 4), (35, 18, 8))

def make_soltys():
    c = PixelCanvas((18, 6, 28))
    c.dither_gradient_v(0, 75, (20, 6, 32), (150, 35, 115))
    
    for y in range(25, 75):
        w = int(8 + (y - 25) * 0.3)
        for x in range(88 - w, 89 + w):
            c.pixels[x, y] = (45, 15, 55)
    for i in range(-18, 19):
        c.pixels[88 + i, 25 + i] = (220, 80, 180)
        c.pixels[88 + i, 25 - i] = (220, 80, 180)

    soltys = [
        "........CCCC........",
        ".......CCCCCC.......",
        ".......CFFFFC.......",
        ".......CFEEFC.......",
        ".......CFMMFC.......",
        ".......CFMMFC.......",
        ".......VVWWVV.......",
        "......VVVWWVVV......",
        ".....VVVVWWVVVV.....",
        ".....VVVVWWVVVV.....",
        "......VVVVVVVV......",
        ".......TT..TT.......",
        ".......TT..TT.......",
        ".......TT..TT.......",
        ".......TT..TT......."
    ]
    pal_s = {
        'C': (60, 20, 70),
        'F': (240, 175, 130),
        'E': (20, 10, 5),
        'M': (50, 25, 10),
        'V': (140, 45, 110),
        'W': (230, 220, 240),
        'T': (40, 15, 45)
    }
    c.draw_sprite(28, 28, soltys, pal_s)
    c.draw_dithered_radial(52, 44, 10, (255, 240, 150), (180, 50, 120))

    c.finalize_cover("soltys.png", ["SOLTYS"], (255, 235, 250), (15, 4, 20), (25, 8, 35))

def make_supertux():
    c = PixelCanvas((8, 20, 38))
    c.dither_gradient_v(0, 75, (10, 25, 55), (35, 130, 190))
    
    for x in range(0, 128):
        ice_y = int(58 + 6 * math.sin(x * 0.08))
        for y in range(ice_y, 128):
            c.pixels[x, y] = (0, 180, 220)
            if y == ice_y:
                c.pixels[x, y] = (200, 250, 255)

    # Large Tux
    tux = [
        "........RRRR........",
        ".......RRRRRR.......",
        "......RRRRRRRR......",
        "......BBEEEEBB......",
        "......BBEEEEBB......",
        "......BBFFFFBB......",
        ".....BBWWWWWWBB.....",
        "....BBBWWWWWWBBB....",
        "....BBBWWWWWWBBB....",
        ".....BBWWWWWWBB.....",
        "......BBBBBBBB......",
        ".......YY..YY.......",
        ".......YY..YY......."
    ]
    pal_tux = {
        'R': (225, 35, 30),
        'B': (15, 25, 45),
        'E': (255, 255, 255),
        'F': (255, 170, 20),
        'W': (245, 250, 255),
        'Y': (255, 170, 20)
    }
    c.draw_sprite(38, 28, tux, pal_tux)

    for fx, fy in [(72, 30), (92, 26)]:
        c.draw_dithered_radial(fx, fy, 6, (255, 240, 120), (255, 160, 20))

    c.finalize_cover("supertux.png", ["SUPERTUX"], (210, 245, 255), (8, 14, 28), (10, 22, 45))

# =============================================================
# BATCH C: 32 to 40
# =============================================================

def make_supertuxkart():
    c = PixelCanvas((10, 24, 45))
    c.dither_gradient_v(0, 75, (12, 28, 60), (40, 140, 210))
    
    for y in range(55, 128):
        for x in range(0, 128):
            c.pixels[x, y] = (50, 55, 65)
            if (x + y) % 8 < 4:
                c.pixels[x, y] = (70, 75, 85)

    kart = [
        "........TTTT........",
        ".......TEEEET.......",
        "......KKKKKKKK......",
        ".....KKRRRRRRKK.....",
        "....KKRRRRRRRRKK....",
        "...KKKRRRRRRRRKKK...",
        "..WWKKKKKKKKKKKKWW..",
        "..WW..FFFFFFFF..WW.."
    ]
    pal_k = {
        'T': (20, 30, 50),
        'E': (255, 255, 255),
        'K': (220, 40, 30),
        'R': (255, 220, 40),
        'W': (15, 15, 20),
        'F': (0, 220, 255)
    }
    c.draw_sprite(40, 34, kart, pal_k)

    for bx in range(12, 40):
        c.pixels[bx, 44] = (0, 240, 255)

    c.finalize_cover("supertuxkart.png", ["SUPERTUXKART"], (210, 245, 255), (8, 14, 28), (10, 22, 45))

def make_terminal_velocity():
    c = PixelCanvas((24, 10, 4))
    c.dither_gradient_v(0, 75, (40, 12, 4), (240, 120, 15))
    
    for y in range(20, 128):
        w1 = int(28 - (y - 20) * 0.15)
        for x in range(0, max(0, w1)):
            c.pixels[x, y] = (80, 35, 10)
        w2 = int(100 + (y - 20) * 0.15)
        for x in range(min(127, w2), 128):
            c.pixels[x, y] = (80, 35, 10)

    tv_ship = [
        "..............WW..............",
        ".............WCCW.............",
        "............WWCCWW............",
        "...........WWWCCWWW...........",
        "..........WWWWSSWWWW..........",
        ".........WWWWWSSWWWWW.........",
        "........WWWWWWSSWWWWWW........",
        ".......WWWWWWSSSSWWWWWW.......",
        "......WWWWWWSSSSSSWWWWWW......",
        ".....WWWWWWSSSSSSSSWWWWWW.....",
        "....WWWWWWSSSSSSSSSSWWWWWW....",
        "...WWWWWWSSSSSSSSSSSSWWWWWW...",
        "..WWWWWWSSSSSSSSSSSSSSWWWWWW..",
        ".WWWWWWSSSSSSSSSSSSSSSSWWWWWW.",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        ".......FF............FF......."
    ]
    pal_tv = {
        'W': (225, 220, 235),
        'C': (255, 170, 20),
        'S': (145, 135, 160),
        'F': (255, 110, 20)
    }
    c.draw_sprite(44, 28, tv_ship, pal_tv)

    for y in range(6, 28):
        c.pixels[44, y] = (255, 240, 60)
        c.pixels[75, y] = (255, 240, 60)

    c.finalize_cover("terminal-velocity-shareware.png", ["TERMINAL", "VELOCITY"], (255, 225, 75), (25, 8, 4), (35, 18, 8))

def make_the_battle_for_wesnoth():
    c = PixelCanvas((8, 18, 35))
    c.dither_gradient_v(0, 75, (8, 16, 32), (25, 80, 130))
    
    for bx, bw, bh in [(8, 30, 70), (88, 32, 75)]:
        for y in range(128 - bh, 128):
            for x in range(bx, bx + bw):
                if 0 <= x < 128:
                    c.pixels[x, y] = (20, 45, 75)

    knight = [
        "........HHHH........",
        ".......HVVVVH.......",
        ".......HVVVVH.......",
        ".......HAAAAH.......",
        "......HAAAAAAH......",
        ".....HHAAAAAAHH.....",
        ".....HHAAAAAAHH.....",
        ".....HHAAAAAAHH.....",
        "......HAAAAAAH......",
        ".......AAAAAA.......",
        ".......LL..LL.......",
        ".......LL..LL.......",
        ".......LL..LL.......",
        ".......FF..FF.......",
        ".......FF..FF......."
    ]
    pal_k = {
        'H': (180, 190, 210),
        'V': (0, 240, 255),
        'A': (140, 150, 170),
        'L': (90, 100, 120),
        'F': (60, 70, 90)
    }
    c.draw_sprite(34, 24, knight, pal_k)

    for y in range(14, 46):
        c.pixels[56, y] = (240, 250, 255)
        c.pixels[57, y] = (160, 210, 240)

    for hx, hy in [(25, 55), (45, 58), (68, 56), (92, 54)]:
        c.draw_dithered_radial(hx, hy, 6, (0, 230, 220), (15, 45, 75))

    c.finalize_cover("the-battle-for-wesnoth.png", ["BATTLE FOR", "WESNOTH"], (210, 245, 255), (8, 14, 28), (10, 22, 45))

def make_the_ur_quan_masters():
    c = PixelCanvas((6, 12, 28))
    c.dither_gradient_v(0, 75, (4, 8, 22), (18, 55, 105))
    
    c.draw_dithered_radial(28, 30, 24, (0, 220, 255), (10, 40, 85))

    cruiser = [
        ".......WW.......",
        "......WWWW......",
        ".....WWCCWW.....",
        "....WWCCCCWW....",
        "...WWSSSSSSWW...",
        "..WWSSSSSSSSWW..",
        ".WWSSSSSSSSSSWW.",
        "WWWWWWWWWWWWWWWW",
        "....FF....FF...."
    ]
    pal_cr = {
        'W': (235, 235, 250),
        'C': (0, 240, 255),
        'S': (155, 155, 180),
        'F': (0, 200, 255)
    }
    c.draw_sprite(68, 34, cruiser, pal_cr)

    dread = [
        "...GGGGGG...",
        "..GGPPEEGG..",
        ".GGPPPEEEGG.",
        "GGGPPPPEEGGG",
        ".GGPPPPPEGG.",
        "..GGGGGGGG.."
    ]
    pal_dr = {
        'G': (30, 115, 65),
        'P': (170, 45, 145),
        'E': (255, 40, 40)
    }
    c.draw_sprite(82, 16, dread, pal_dr)

    c.finalize_cover("the-ur-quan-masters.png", ["THE UR-QUAN", "MASTERS"], (210, 245, 255), (8, 14, 28), (10, 22, 45))

def make_tyrian_2000():
    c = PixelCanvas((24, 10, 4))
    c.dither_gradient_v(0, 75, (38, 10, 4), (225, 110, 15))
    
    for y in range(60, 128):
        for x in range(0, 128):
            c.pixels[x, y] = (140, 50, 10)
            if (x + y) % 3 == 0:
                c.pixels[x, y] = (255, 160, 20)

    talon = [
        "..............GG..............",
        ".............GGGG.............",
        "............GGCCGG............",
        "...........GGGCCGGG...........",
        "..........GGGGGGGGGG..........",
        ".........GGGGSSSSGGGG.........",
        "........WWGGSSSSSSGGWW........",
        ".......WWWGGSSSSSSGGWWW.......",
        "......WWWWGGSSSSSSGGWWWW......",
        ".....WWWWWGGSSSSSSGGWWWWW.....",
        "....WWWWWWGGSSSSSSGGWWWWWW....",
        "...WWWWWWWGGSSSSSSGGWWWWWWW...",
        "..WWWWWWWWGGSSSSSSGGWWWWWWWW..",
        ".WWWWWWWWWGGSSSSSSGGWWWWWWWWW.",
        "WWWWWWWWWWGGSSSSSSGGWWWWWWWWWW",
        "..........FF......FF.........."
    ]
    pal_talon = {
        'G': (250, 200, 40),
        'C': (0, 240, 255),
        'S': (185, 135, 20),
        'W': (255, 235, 130),
        'F': (255, 120, 20)
    }
    c.draw_sprite(42, 26, talon, pal_talon)

    for y in range(6, 26):
        c.pixels[38, y] = (255, 230, 50)
        c.pixels[89, y] = (255, 230, 50)
        c.pixels[64, y] = (255, 100, 20)

    c.finalize_cover("tyrian-2000.png", ["TYRIAN 2000"], (255, 225, 75), (25, 8, 4), (35, 18, 8))

def make_warzone_2100():
    c = PixelCanvas((8, 18, 32))
    c.dither_gradient_v(0, 75, (8, 16, 30), (25, 75, 120))
    
    for y in range(22, 65):
        c.pixels[95, y] = (80, 95, 115)
    c.draw_dithered_radial(95, 18, 8, (0, 255, 240), (20, 60, 90))

    tank = [
        "......LLLLLLLLLL......",
        ".....LLLLCCCCLLLL.....",
        "....LLLLLLLLLLLLLL....",
        "...LLLLLLLLLLLLLLLL...",
        "..TTTTTTTTTTTTTTTTTT..",
        "..TWWWTWWWTWWWTWWWTW..",
        "..TTTTTTTTTTTTTTTTTT.."
    ]
    pal_wtank = {
        'L': (40, 90, 130),
        'C': (0, 240, 255),
        'T': (18, 45, 65),
        'W': (90, 135, 170)
    }
    c.draw_sprite(22, 42, tank, pal_wtank)
    for x in range(42, 78):
        c.pixels[x, 44] = (150, 165, 185)

    c.finalize_cover("warzone-2100.png", ["WARZONE 2100"], (210, 245, 255), (8, 14, 28), (10, 22, 45))

def make_widelands():
    c = PixelCanvas((10, 25, 45))
    c.dither_gradient_v(0, 75, (12, 30, 65), (45, 140, 200))
    
    for x in range(0, 128):
        hy = int(52 + 10 * math.sin(x * 0.05))
        for y in range(hy, 128):
            c.pixels[x, y] = (30, 110, 50)
            if (x + y) % 3 == 0:
                c.pixels[x, y] = (60, 170, 80)

    for bx, bw, bh in [(12, 28, 65), (82, 30, 70)]:
        for y in range(128 - bh, 128):
            for x in range(bx, bx + bw):
                if 0 <= x < 128:
                    c.pixels[x, y] = (110, 115, 130)
                    if (y % 8 == 0) or (x == bx or x == bx + bw - 1):
                        c.pixels[x, y] = (60, 65, 75)

    for x in range(25, 105):
        c.pixels[x, 62] = (160, 165, 175)
        if x % 16 == 0:
            c.pixels[x, 56] = (255, 40, 30)
            c.pixels[x, 57] = (255, 40, 30)
            c.pixels[x, 58] = (20, 20, 20)

    c.finalize_cover("widelands.png", ["WIDELANDS"], (210, 245, 255), (8, 14, 28), (10, 22, 45))

def make_wolfenstein_3d():
    c = PixelCanvas((24, 10, 4))
    c.dither_gradient_v(0, 75, (38, 12, 4), (170, 65, 12))
    
    # Castle Wolfenstein Stone Corridors lit by Torches
    for bx, bw, bh in [(6, 26, 75), (96, 26, 75)]:
        for y in range(128 - bh, 128):
            for x in range(bx, bx + bw):
                if 0 <= x < 128:
                    c.pixels[x, y] = (50, 22, 10)
                    if (y % 10 == 0) or (x == bx or x == bx + bw - 1):
                        c.pixels[x, y] = (25, 10, 4)

    for y in range(16, 75):
        for x in range(44, 85):
            c.pixels[x, y] = (70, 35, 15)
            if (x == 44 or x == 84 or x == 64):
                c.pixels[x, y] = (30, 15, 6)

    for tx in [22, 106]:
        c.draw_dithered_radial(tx, 36, 10, (255, 240, 140), (200, 70, 15))

    # Large Allied Commando
    bj = [
        "........HHHH........",
        ".......HHHHHH.......",
        ".......HFFEEH.......",
        ".......HFFEEH.......",
        "........FFFF........",
        ".......JJJJJJ.......",
        "......JJJJJJJJ......",
        ".....JJJJJJJJJJ.....",
        ".....JJJWWWWJJJ.....",
        ".....JJJJJJJJJJ.....",
        "......JJJJJJJJ......",
        ".......TT..TT.......",
        ".......TT..TT.......",
        ".......TT..TT.......",
        ".......BB..BB.......",
        ".......BB..BB......."
    ]
    pal_bj = {
        'H': (75, 45, 20),
        'F': (240, 180, 130),
        'E': (20, 10, 5),
        'J': (115, 70, 28),
        'W': (230, 225, 220),
        'T': (60, 65, 80),
        'B': (25, 15, 10)
    }
    c.draw_sprite(30, 26, bj, pal_bj)

    # Submachine gun & muzzle flash
    for x in range(46, 68):
        c.pixels[x, 38] = (60, 65, 75)
    c.draw_dithered_radial(72, 38, 9, (255, 255, 220), (255, 120, 20))

    c.finalize_cover("wolfenstein-3d-shareware.png", ["WOLFENSTEIN 3D"], (255, 225, 75), (25, 8, 4), (35, 18, 8))

def make_xonotic():
    c = PixelCanvas((8, 18, 35))
    c.dither_gradient_v(0, 75, (6, 12, 28), (20, 75, 130))
    
    for bx, bw, bh in [(12, 32, 65), (84, 32, 65)]:
        for y in range(128 - bh, 128):
            for x in range(bx, bx + bw):
                if 0 <= x < 128:
                    c.pixels[x, y] = (15, 40, 70)
                    if (y % 8 == 0) and x % 3 == 0:
                        c.pixels[x, y] = (0, 240, 255)

    # Large Cyber-Warrior
    warrior = [
        "........CCCC........",
        ".......CVVVVC.......",
        ".......CVVVVC.......",
        ".......CAAAAC.......",
        "......CAAAAAAC......",
        ".....CCAAAAAACC.....",
        ".....CCAAAAAACC.....",
        ".....CCAAAAAACC.....",
        "......CAAAAAAC......",
        ".......AAAAAA.......",
        ".......LL..LL.......",
        ".......LL..LL.......",
        ".......LL..LL.......",
        ".......FF..FF.......",
        ".......FF..FF......."
    ]
    pal_w = {
        'C': (20, 60, 95),
        'V': (0, 255, 240),
        'A': (45, 110, 160),
        'L': (25, 70, 110),
        'F': (0, 220, 255)
    }
    c.draw_sprite(34, 20, warrior, pal_w)

    for x in range(50, 76):
        c.pixels[x, 30] = (180, 190, 210)
    for x in range(76, 115):
        c.pixels[x, 30] = (255, 255, 255)
        c.pixels[x, 29] = (0, 240, 255)
        c.pixels[x, 31] = (0, 240, 255)

    c.draw_dithered_radial(44, 48, 12, (255, 255, 240), (0, 180, 255))

    c.finalize_cover("xonotic.png", ["XONOTIC"], (210, 245, 255), (8, 14, 28), (10, 22, 45))

def generate_all_remaining():
    print("--- GENERATING BATCH A ---")
    make_epic_pinball()
    make_flight_amazon_queen()
    make_freedoom()
    make_heretic()
    make_hocus_pocus()
    make_jazz_jackrabbit()
    make_keen_dreams()
    make_lure_of_the_temptress()
    make_major_stryker()

    print("--- GENERATING BATCH B ---")
    make_monster_bash()
    make_one_must_fall()
    make_openra()
    make_openttd()
    make_raptor()
    make_rise_of_the_triad()
    make_secret_agent()
    make_soltys()
    make_supertux()

    print("--- GENERATING BATCH C ---")
    make_supertuxkart()
    make_terminal_velocity()
    make_the_battle_for_wesnoth()
    make_the_ur_quan_masters()
    make_tyrian_2000()
    make_warzone_2100()
    make_widelands()
    make_wolfenstein_3d()
    make_xonotic()

    print("All remaining covers generated successfully!")

if __name__ == "__main__":
    generate_all_remaining()
