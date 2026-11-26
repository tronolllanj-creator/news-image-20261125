import sys
import os
from PIL import Image, ImageDraw, ImageFont

# ─── Constants ───
W, H = 1024, 1024
BG = (0xF7, 0xF1, 0xE3)          # paper
INK = (0x14, 0x21, 0x3D)         # ink
RED = (0xC1, 0x27, 0x2D)         # accent red
NAVY = (0x1B, 0x2A, 0x4A)        # navy
TEAL = (0x0E, 0x7C, 0x7B)        # teal
GOLD = (0xD9, 0xA4, 0x41)        # gold
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ─── Font loading ───
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
FONT_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
FONT_REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")

def load_fonts():
    return {
        "masthead": ImageFont.truetype(FONT_BOLD, 36),
        "date": ImageFont.truetype(FONT_BOLD, 20),
        "lead_headline": ImageFont.truetype(FONT_BOLD, 28),
        "lead_summary": ImageFont.truetype(FONT_REG, 18),
        "chip": ImageFont.truetype(FONT_BOLD, 11),
        "story_headline": ImageFont.truetype(FONT_BOLD, 16),
        "story_body": ImageFont.truetype(FONT_REG, 13),
        "ticker": ImageFont.truetype(FONT_REG, 14),
        "footer": ImageFont.truetype(FONT_REG, 12),
        "icon_label": ImageFont.truetype(FONT_BOLD, 10),
    }

FONTS = load_fonts()

# ─── Text helpers ───
def wrap_text(draw, text, font, max_width):
    """Return list of lines wrapped to max_width."""
    words = text.split()
    lines = []
    cur = []
    for w in words:
        test = " ".join(cur + [w])
        if draw.textlength(test, font=font) <= max_width:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines

def draw_wrapped(draw, xy, lines, font, fill, leading=1.2):
    """Draw wrapped lines at xy, return (width, height) used."""
    x, y = xy
    line_h = int(font.size * leading)
    max_w = 0
    for line in lines:
        draw.text((int(x), int(y)), line, font=font, fill=fill)
        w = draw.textlength(line, font=font)
        if w > max_w:
            max_w = w
        y += line_h
    return int(max_w), int(y - xy[1])

# ─── Geometric icon helpers ───
def draw_chip(draw, xy, text, font, bg_color, padding=6, radius=4):
    """Draw a rounded-rect chip with white bold label."""
    x, y = xy
    tw = draw.textlength(text, font=font)
    th = font.size
    w = int(tw + 2 * padding)
    h = int(th + 2 * padding)
    # rounded rect via pieslices + rect
    r = radius
    draw.rounded_rectangle([int(x), int(y), int(x + w), int(y + h)], radius=r, fill=bg_color)
    draw.text((int(x + padding), int(y + padding)), text, font=font, fill=WHITE)
    return w, h

def draw_icon_fire(draw, cx, cy, size, fill):
    """Small flame icon."""
    s = size // 2
    pts = [
        (cx, cy - s),
        (cx - s//2, cy),
        (cx - s//3, cy),
        (cx, cy + s),
        (cx + s//3, cy),
        (cx + s//2, cy),
    ]
    draw.polygon(pts, fill=fill)
    # inner flame
    pts2 = [(cx, cy - s//2), (cx - s//4, cy), (cx, cy + s//2), (cx + s//4, cy)]
    draw.polygon(pts2, fill=(255, 200, 50))

def draw_icon_lightning(draw, cx, cy, size, fill):
    """Lightning bolt for energy/power."""
    s = size // 2
    pts = [
        (cx, cy - s),
        (cx + s//3, cy - s//4),
        (cx - s//6, cy - s//4),
        (cx, cy + s//2),
        (cx - s//3, cy + s//4),
        (cx + s//6, cy + s//4),
    ]
    draw.polygon(pts, fill=fill)

def draw_icon_drone(draw, cx, cy, size, fill):
    """Simple drone shape."""
    s = size // 2
    # body
    draw.ellipse([cx - s//3, cy - s//4, cx + s//3, cy + s//4], fill=fill)
    # four arms
    for dx, dy in [(-s, 0), (s, 0), (0, -s), (0, s)]:
        draw.rectangle([cx + dx - s//6, cy + dy - s//6, cx + dx + s//6, cy + dy + s//6], fill=fill)

def draw_icon_oil(draw, cx, cy, size, fill):
    """Oil drum / barrel."""
    s = size // 2
    draw.rectangle([cx - s//2, cy - s, cx + s//2, cy + s], fill=fill, outline=INK, width=1)
    draw.line([cx - s//2, cy - s//2, cx + s//2, cy - s//2], fill=INK, width=1)
    draw.line([cx - s//2, cy + s//2, cx + s//2, cy + s//2], fill=INK, width=1)

def draw_icon_tariff(draw, cx, cy, size, fill):
    """Up/down arrows for trade."""
    s = size // 2
    # up arrow
    draw.polygon([(cx - s//2, cy), (cx, cy - s), (cx + s//2, cy)], fill=fill)
    # down arrow
    draw.polygon([(cx - s//2, cy + 2), (cx, cy + s + 2), (cx + s//2, cy + 2)], fill=fill)

def draw_icon_rocket(draw, cx, cy, size, fill):
    """Rocket for space."""
    s = size // 2
    # body
    draw.rectangle([cx - s//4, cy - s, cx + s//4, cy + s//2], fill=fill)
    # nose
    draw.polygon([(cx - s//3, cy - s), (cx, cy - s - s//2), (cx + s//3, cy - s)], fill=fill)
    # fins
    draw.polygon([(cx - s//4, cy + s//2), (cx - s, cy + s), (cx - s//4, cy + s)], fill=fill)
    draw.polygon([(cx + s//4, cy + s//2), (cx + s, cy + s), (cx + s//4, cy + s)], fill=fill)
    # flame
    draw.polygon([(cx - s//6, cy + s//2), (cx, cy + s), (cx + s//6, cy + s//2)], fill=RED)

def draw_icon_nato(draw, cx, cy, size, fill):
    """Compass rose for NATO."""
    s = size // 2
    draw.ellipse([cx - s, cy - s, cx + s, cy + s], outline=fill, width=2)
    draw.line([cx, cy - s, cx, cy + s], fill=fill, width=2)
    draw.line([cx - s, cy, cx + s, cy], fill=fill, width=2)
    draw.line([cx - s, cy - s, cx + s, cy + s], fill=fill, width=1)
    draw.line([cx - s, cy + s, cx + s, cy - s], fill=fill, width=1)

def draw_icon_mine(draw, cx, cy, size, fill):
    """Mine shaft / pickaxe."""
    s = size // 2
    # shaft
    draw.rectangle([cx - s//3, cy - s, cx + s//3, cy + s], fill=fill)
    # pickaxe
    draw.line([cx - s, cy - s//2, cx + s, cy + s//2], fill=fill, width=2)
    draw.polygon([(cx + s, cy + s//2), (cx + s//2, cy), (cx + s//2, cy + s//2)], fill=fill)

def draw_icon_flag(draw, cx, cy, size, fill):
    """Flag for politics/diplomacy."""
    s = size // 2
    draw.line([cx, cy - s, cx, cy + s], fill=INK, width=2)
    draw.polygon([(cx, cy - s), (cx + s, cy - s//2), (cx, cy)], fill=fill)

def draw_icon_chip(draw, cx, cy, size, fill):
    """Microchip for markets/tech."""
    s = size // 2
    draw.rectangle([cx - s, cy - s, cx + s, cy + s], fill=fill, outline=INK, width=1)
    # pins
    for i in range(-1, 2):
        draw.line([cx - s, cy + i * s//2, cx - s - 3, cy + i * s//2], fill=INK, width=1)
        draw.line([cx + s, cy + i * s//2, cx + s + 3, cy + i * s//2], fill=INK, width=1)

def draw_icon_flood(draw, cx, cy, size, fill):
    """Water wave for floods."""
    s = size // 2
    draw.arc([cx - s, cy - s//2, cx + s, cy + s//2], 0, 180, fill=fill, width=3)
    draw.arc([cx - s//2, cy, cx + s//2, cy + s], 0, 180, fill=fill, width=2)

def draw_icon_handshake(draw, cx, cy, size, fill):
    """Handshake for alliances."""
    s = size // 2
    # two hands
    draw.ellipse([cx - s, cy - s//3, cx - s//3, cy + s//3], fill=fill)
    draw.ellipse([cx + s//3, cy - s//3, cx + s, cy + s//3], fill=fill)
    # wrists
    draw.rectangle([cx - s, cy + s//3, cx - s//3, cy + s], fill=fill)
    draw.rectangle([cx + s//3, cy + s//3, cx + s, cy + s], fill=fill)

def draw_icon_cop(draw, cx, cy, size, fill):
    """Globe for climate/COP."""
    s = size // 2
    draw.ellipse([cx - s, cy - s, cx + s, cy + s], outline=fill, width=2)
    draw.line([cx, cy - s, cx, cy + s], fill=fill, width=2)
    draw.arc([cx - s, cy - s, cx + s, cy + s], 30, 150, fill=fill, width=2)
    draw.arc([cx - s, cy - s, cx + s, cy + s], 210, 330, fill=fill, width=2)

def draw_icon_sport(draw, cx, cy, size, fill):
    """Cricket bat + ball."""
    s = size // 2
    draw.line([cx - s//2, cy + s, cx + s//2, cy - s], fill=INK, width=3)
    draw.ellipse([cx + s//2 - 4, cy - s - 4, cx + s//2 + 4, cy - s + 4], fill=RED)

ICON_FUNCS = {
    "fire": draw_icon_fire,
    "lightning": draw_icon_lightning,
    "drone": draw_icon_drone,
    "oil": draw_icon_oil,
    "tariff": draw_icon_tariff,
    "rocket": draw_icon_rocket,
    "nato": draw_icon_nato,
    "mine": draw_icon_mine,
    "flag": draw_icon_flag,
    "chip": draw_icon_chip,
    "flood": draw_icon_flood,
    "handshake": draw_icon_handshake,
    "cop": draw_icon_cop,
    "sport": draw_icon_sport,
}

def draw_story_icon(draw, cx, cy, size, icon_name, fill):
    fn = ICON_FUNCS.get(icon_name, draw_icon_fire)
    fn(draw, cx, cy, size, fill)

# ─── Lead story large scene (Cairo tanker fire) ───
def draw_cairo_scene(draw, x, y, w, h):
    """Draw large isometric scene: overturned tanker, flames, road, charred vehicles."""
    # Road surface (dark asphalt)
    road_y = y + int(h * 0.65)
    road_h = int(h * 0.35)
    draw.rectangle([int(x), int(road_y), int(x + w), int(road_y + road_h)], fill=(30, 30, 30))
    # Road markings
    for i in range(0, w, 60):
        draw.rectangle([int(x + i), int(road_y + road_h//2 - 4), int(x + i + 30), int(road_y + road_h//2 + 4)], fill=(200, 200, 200))
    
    # Cairo skyline silhouette in background
    sky_h = road_y - y
    for i in range(12):
        bx = x + i * (w // 12)
        bw = w // 12
        bh = int(sky_h * (0.3 + (i % 3) * 0.2))
        draw.rectangle([int(bx + 5), int(road_y - bh), int(bx + bw - 5), int(road_y)], fill=(60, 50, 45))
        # windows
        for wx in range(int(bx + 10), int(bx + bw - 10), 15):
            for wy in range(int(road_y - bh + 5), int(road_y - 5), 12):
                if (wx + wy) % 3 == 0:
                    draw.rectangle([wx, wy, wx + 3, wy + 3], fill=(120, 100, 80))
    
    # Overturned tanker (large cylinder on side)
    tx = x + int(w * 0.35)
    ty = road_y - int(h * 0.25)
    tr = int(h * 0.18)
    tl = int(w * 0.35)
    # Tanker body
    draw.ellipse([int(tx - tr), int(ty - tr), int(tx + tr), int(ty + tr)], fill=(40, 35, 35), outline=(80, 70, 60), width=2)
    draw.rectangle([int(tx - tr), int(ty - tr), int(tx - tr + tl), int(ty + tr)], fill=(40, 35, 35), outline=(80, 70, 60), width=2)
    draw.ellipse([int(tx - tr + tl), int(ty - tr), int(tx + tr + tl), int(ty + tr)], fill=(40, 35, 35), outline=(80, 70, 60), width=2)
    # Hazard markings
    for i in range(5):
        draw.rectangle([int(tx - tr + 5 + i * 15), int(ty - tr + 5), int(tx - tr + 15 + i * 15), int(ty + tr - 5)], fill=(255, 255, 0) if i % 2 == 0 else (30, 30, 30))
    
    # FLAMES rising from tanker
    flame_base_y = ty
    for layer in range(4):
        alpha = 1.0 - layer * 0.2
        fh = int(h * (0.25 - layer * 0.05))
        fw = int(tr * (1.5 - layer * 0.2))
        fx = tx + tl // 2
        # Main flame body
        pts = [
            (fx, flame_base_y),
            (fx - fw, flame_base_y - fh // 3),
            (fx - fw // 2, flame_base_y - fh // 2),
            (fx, flame_base_y - fh),
            (fx + fw // 2, flame_base_y - fh // 2),
            (fx + fw, flame_base_y - fh // 3),
        ]
        color = (int(255 * alpha), int(120 * alpha), int(20 * alpha))
        draw.polygon(pts, fill=color)
        # Inner flame
        pts2 = [
            (fx, flame_base_y - 5),
            (fx - fw // 3, flame_base_y - fh // 3),
            (fx, flame_base_y - int(fh * 0.7)),
            (fx + fw // 3, flame_base_y - fh // 3),
        ]
        color2 = (255, int(200 * alpha), int(50 * alpha))
        draw.polygon(pts2, fill=color2)
    
    # Smoke plume
    for i in range(6):
        sx = tx + tl // 2 + int((i - 2) * 12)
        sy = ty - int(h * 0.15) - i * 8
        sr = int(12 + i * 4)
        draw.ellipse([sx - sr, sy - sr//2, sx + sr, sy + sr//2], fill=(50, 50, 50, 180), outline=None)
    
    # Charred vehicles scattered on road
    vehicle_positions = [
        (x + int(w * 0.08), road_y + 10),
        (x + int(w * 0.22), road_y + 15),
        (x + int(w * 0.55), road_y + 5),
        (x + int(w * 0.7), road_y + 20),
        (x + int(w * 0.85), road_y + 10),
        (x + int(w * 0.92), road_y + 15),
    ]
    for vx, vy in vehicle_positions:
        # Car body (charred)
        draw.rectangle([int(vx), int(vy), int(vx + 40), int(vy + 18)], fill=(25, 20, 20), outline=(60, 50, 50), width=1)
        # Roof
        draw.rectangle([int(vx + 5), int(vy - 8), int(vx + 35), int(vy)], fill=(30, 25, 25), outline=(60, 50, 50), width=1)
        # Wheels
        draw.ellipse([int(vx + 5), int(vy + 15), int(vx + 15), int(vy + 25)], fill=(15, 15, 15))
        draw.ellipse([int(vx + 25), int(vy + 15), int(vx + 35), int(vy + 25)], fill=(15, 15, 15))
        # Fire on some
        if (vx + vy) % 3 == 0:
            draw.polygon([(vx + 15, vy), (vx + 10, vy - 15), (vx + 20, vy - 10), (vx + 30, vy - 15), (vx + 25, vy)], fill=(255, 100, 20))
    
    # Emergency lights (blue/red) on sides
    for ex in [x + 30, x + w - 30]:
        for ey in range(int(road_y), int(road_y + road_h), 30):
            draw.ellipse([ex - 8, ey - 8, ex + 8, ey + 8], fill=RED if (ey // 30) % 2 == 0 else (0, 100, 255))
    
    # Silhouettes for casualties (31 dead, 21 injured) - small figures along roadside
    for i in range(31):
        fx = x + 40 + (i % 10) * 45
        fy = road_y - 40 - (i // 10) * 25
        draw.line([fx, fy, fx, fy + 12], fill=(100, 80, 70), width=2)
        draw.line([fx - 4, fy + 3, fx + 4, fy + 3], fill=(100, 80, 70), width=1)
        draw.line([fx, fy + 12, fx - 4, fy + 20], fill=(100, 80, 70), width=1)
        draw.line([fx, fy + 12, fx + 4, fy + 20], fill=(100, 80, 70), width=1)
    for i in range(21):
        fx = x + 40 + (i % 7) * 45
        fy = road_y - 120 - (i // 7) * 20
        draw.line([fx, fy, fx, fy + 10], fill=(150, 120, 100), width=2)
        draw.line([fx - 3, fy + 2, fx + 3, fy + 2], fill=(150, 120, 100), width=1)
        draw.line([fx, fy + 10, fx - 3, fy + 17], fill=(150, 120, 100), width=1)
        draw.line([fx, fy + 10, fx + 3, fy + 17], fill=(150, 120, 100), width=1)

def draw_variant1(img, draw):
    """DENSE FRONT PAGE layout."""
    # ─── Background ───
    draw.rectangle([0, 0, W, H], fill=BG)
    
    # ─── Navy masthead band ───
    mast_h = 90
    draw.rectangle([0, 0, W, mast_h], fill=NAVY)
    draw.text((int(W * 0.04), 12), "THE WORLD IN ONE IMAGE", font=FONTS["masthead"], fill=WHITE)
    draw.text((int(W * 0.04), 52), "WEDNESDAY 25 NOVEMBER 2026", font=FONTS["date"], fill=GOLD)
    
    # ─── Lead story area ───
    lead_y = mast_h + 10
    lead_h = 300
    lead_x = 20
    lead_w = W - 40
    
    # Lead background panel
    draw.rounded_rectangle([lead_x, lead_y, lead_x + lead_w, lead_y + lead_h], radius=8, fill=(255, 252, 245), outline=NAVY, width=2)
    
    # Large Cairo scene on right half
    scene_x = lead_x + int(lead_w * 0.52)
    scene_w = lead_w - (scene_x - lead_x) - 15
    scene_h = lead_h - 20
    draw.rectangle([scene_x, lead_y + 10, scene_x + scene_w, lead_y + 10 + scene_h], fill=(255, 252, 245))
    draw.polygon([(scene_x, lead_y + 10), (scene_x + scene_w, lead_y + 10), (scene_x + scene_w, lead_y + 10 + scene_h), (scene_x, lead_y + 10 + scene_h)], fill=(255, 252, 245))
    draw_cairo_scene(draw, scene_x, lead_y + 10, scene_w, scene_h)
    draw.rectangle([lead_x, lead_y, lead_x + lead_w, lead_y + lead_h], outline=NAVY, width=2)
    
    # Lead text on left half
    text_x = lead_x + 20
    text_w = int(lead_w * 0.48) - 30
    text_y = lead_y + 20
    
    # Category chip
    draw_chip(draw, (text_x, text_y), "CAIRO", FONTS["chip"], RED)
    
    # Headline
    hl_y = text_y + 28
    headline = "Fuel tanker overturns and burns on Ring Road — 31 dead, 21 hurt"
    lines = wrap_text(draw, headline, FONTS["lead_headline"], text_w)
    draw_wrapped(draw, (text_x, hl_y), lines[:2], FONTS["lead_headline"], INK)
    
    # Summary (2 lines)
    sum_y = hl_y + 60
    summary = "Al-Warraq, Giza: tanker catches fire Wednesday evening; more than two dozen vehicles charred. Deadliest road blaze in years."
    lines = wrap_text(draw, summary, FONTS["lead_summary"], text_w)
    draw_wrapped(draw, (text_x, sum_y), lines[:2], FONTS["lead_summary"], (60, 60, 60))
    
    # ─── Row of 3 stories (2, 3, 4) ───
    row1_y = lead_y + lead_h + 15
    row_h = 132
    col_w = (W - 60) // 3
    
    stories_row1 = [
        ("UK ENERGY", GOLD, "Ofgem raises price cap 26% to £2,166; 20M hit as gas surges.", "lightning"),
        ("GULF", RED, "Houthi drone strikes Riyadh PIF Tower, wounding 11 in second hit.", "drone"),
        ("ENERGY", RED, "Tankers hit mines in Hormuz; 400 ships waiting, oil traffic down 40%.", "oil"),
    ]
    
    for i, (cat, chip_color, body, icon) in enumerate(stories_row1):
        cx = 20 + i * (col_w + 10)
        cy = row1_y
        draw.rounded_rectangle([cx, cy, cx + col_w, cy + row_h], radius=6, fill=(255, 252, 245), outline=(200, 195, 185), width=1)
        draw_chip(draw, (cx + 10, cy + 8), cat, FONTS["chip"], chip_color)
        icon_zone_w = 65
        text_w = col_w - icon_zone_w - 16
        draw_story_icon(draw, cx + col_w - 35, cy + 45, 36, icon, chip_color)
        hl = cat.split()[0] + " " + ("Price cap up 26%" if i == 0 else "PIF Tower hit again" if i == 1 else "Tankers mined in Hormuz")
        lines = wrap_text(draw, hl, FONTS["story_headline"], text_w)
        draw_wrapped(draw, (cx + 10, cy + 34), lines[:2], FONTS["story_headline"], INK)
        lines = wrap_text(draw, body, FONTS["story_body"], text_w)
        draw_wrapped(draw, (cx + 10, cy + 74), lines[:2], FONTS["story_body"], (50, 50, 50))
    
    # ─── Row of 4 briefs (5, 6, 7, 8) ───
    row2_y = row1_y + row_h + 8
    row2_h = 112
    col4_w = (W - 70) // 4
    
    stories_row2 = [
        ("TRADE", RED, "US proposes tariffs on 14 economies.", "tariff"),
        (
            "SPACE",
            TEAL,
            "Shenzhou-24 launches with new crew.",
            "rocket",
        ),
        ("POLITICS", NAVY, "NATO deploys planes in Poland; EU acts.", "nato"),
        ("MARKETS", RED, "AI doubts sink chip stocks.", "chip"),
    ]
    
    for i, (cat, chip_color, body, icon) in enumerate(stories_row2):
        cx = 20 + i * (col4_w + 10)
        cy = row2_y
        draw.rounded_rectangle([cx, cy, cx + col4_w, cy + row2_h], radius=6, fill=(255, 252, 245), outline=(200, 195, 185), width=1)
        draw_chip(draw, (cx + 8, cy + 6), cat, FONTS["chip"], chip_color)
        icon_zone_w = 60
        text_w = col4_w - icon_zone_w - 14
        draw_story_icon(draw, cx + col4_w - 30, cy + 40, 30, icon, chip_color)
        hl = ("US tariffs on 14" if i == 0 else "Shenzhou-24 flight" if i == 1 else "NATO planes to Poland" if i == 2 else "AI doubts sink chips")
        lines = wrap_text(draw, hl, FONTS["story_headline"], text_w)
        draw_wrapped(draw, (cx + 8, cy + 30), lines[:2], FONTS["story_headline"], INK)
        lines = wrap_text(draw, body, FONTS["story_body"], text_w)
        draw_wrapped(draw, (cx + 8, cy + 64), lines[:2], FONTS["story_body"], (50, 50, 50))
    
    # ─── Row of 4 briefs (9, 10, 11, 12) ───
    row3_y = row2_y + row2_h + 8
    row3_h = 112
    
    stories_row3 = [
        ("INDONESIA", TEAL, "Heavy rain floods gold mine; 9 dead.", "flood"),
        ("INDIA", GOLD, "BJP and Akali Dal ally for polls.", "handshake"),
        (
            "CLIMATE",
            NAVY,
            "COP31 climate summit collapses.",
            "cop",
        ),
        ("SPORT", TEAL, "England beat Australia in T20.", "sport"),
    ]
    
    for i, (cat, chip_color, body, icon) in enumerate(stories_row3):
        cx = 20 + i * (col4_w + 10)
        cy = row3_y
        draw.rounded_rectangle([cx, cy, cx + col4_w, cy + row3_h], radius=6, fill=(255, 252, 245), outline=(200, 195, 185), width=1)
        draw_chip(draw, (cx + 8, cy + 6), cat, FONTS["chip"], chip_color)
        icon_zone_w = 60
        text_w = col4_w - icon_zone_w - 14
        draw_story_icon(draw, cx + col4_w - 30, cy + 40, 30, icon, chip_color)
        hl = ("West Java flood: 9 dead" if i == 0 else "BJP-Akali Dal alliance" if i == 1 else "COP31 climate summit fails" if i == 2 else "England win T20 match")
        lines = wrap_text(draw, hl, FONTS["story_headline"], text_w)
        draw_wrapped(draw, (cx + 8, cy + 30), lines[:2], FONTS["story_headline"], INK)
        lines = wrap_text(draw, body, FONTS["story_body"], text_w)
        draw_wrapped(draw, (cx + 8, cy + 64), lines[:2], FONTS["story_body"], (50, 50, 50))
    
    # ─── Bottom ticker strip & footer moved up to avoid clipping ───
    footer_y = H - 56
    footer_text = "All stories first reported 25 November 2026"
    fw = draw.textlength(footer_text, font=FONTS["footer"])
    draw.text((int((W - fw) // 2), int(footer_y)), footer_text, font=FONTS["footer"], fill=(100, 100, 100))
    
    ticker_y = H - 40
    draw.rectangle([0, ticker_y, W, H], fill=INK)
    ticker_text = "THANKSGIVING: 81.5M US TRIPS  •  UKRAINE HIT RUSSIAN SHIP IN GULF OF FINLAND  •  SARKOZY CASE TO TRIAL  •  GAZA TOLL 74,746"
    tw = draw.textlength(ticker_text, font=FONTS["ticker"])
    tx = (W - tw) // 2
    draw.text((int(tx), int(ticker_y + 8)), ticker_text, font=FONTS["ticker"], fill=WHITE)

# ─── Main entry ───
def main():
    variant = sys.argv[1] if len(sys.argv) > 1 else "1"
    draw_fn = globals().get("draw_variant" + variant)
    if not draw_fn:
        print(f"Unknown variant: {variant}", file=sys.stderr)
        sys.exit(1)
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_fn(img, draw)
    out_name = f"variant_r2_{variant}.png"
    img.save(out_name, "PNG")
    size = os.path.getsize(out_name)
    print(f"wrote {out_name} 1024x1024 bytes {size}")

def draw_variant2(img, draw):
    """SIX PANELS WITH SCENES: date banner + 2x3 grid for stories 1-6."""
    draw.rectangle([0, 0, W, H], fill=BG)
    
    # Date banner
    banner_h = 56
    draw.rectangle([0, 0, W, banner_h], fill=NAVY)
    draw.text((40, 16), "WEDNESDAY 25 NOVEMBER 2026", font=FONTS["masthead"], fill=WHITE)
    
    # Grid layout
    margin = 24
    gap = 16
    grid_x = margin
    grid_y = banner_h + 20
    grid_w = W - 2 * margin
    panel_w = (grid_w - 2 * gap) // 3
    panel_h = (H - grid_y - margin - gap) // 2
    
    stories = [
        ("CAIRO", RED, "Fuel tanker overturns and burns on Ring Road — 31 dead, 21 hurt",
         "Al-Warraq, Giza: tanker catches fire Wednesday evening; more than two dozen vehicles charred. Deadliest road blaze in years.",
         "fire", draw_cairo_scene),
        ("UK ENERGY", GOLD, "Ofgem raises price cap 26% to £2,166 from Jan; 20M households hit",
         "Wholesale gas surges on Mideast conflict; highest cap in almost four years.",
         "lightning", lambda d, x, y, w, h: draw_story_icon(d, x + w//2, y + h//2, min(w, h)//2, "lightning", GOLD)),
        ("GULF", RED, "Houthi drone strikes Riyadh's PIF Tower again, wounding 11",
         "Second hit in a week on King Abdullah Financial District tower; 2 Saudis, 2 Indians, 3 Nepalis, 4 Egyptians hurt.",
         "drone", lambda d, x, y, w, h: draw_story_icon(d, x + w//2, y + h//2, min(w, h)//2, "drone", RED)),
        ("ENERGY", RED, "Iran says more tankers hit mines in Strait of Hormuz; ~400 ships waiting",
         "Oil traffic down 40%, rial hits record low 2.83M/$ after new US sanctions.",
         "oil", lambda d, x, y, w, h: draw_story_icon(d, x + w//2, y + h//2, min(w, h)//2, "oil", RED)),
        ("TRADE", RED, "US proposes tariffs on 14 economies: India 25%/17%, China up to 40%, Japan 15%",
         "Aim: counter excess industrial capacity across steel, aluminium, EVs, solar.",
         "tariff", lambda d, x, y, w, h: draw_story_icon(d, x + w//2, y + h//2, min(w, h)//2, "tariff", RED)),
        ("SPACE", TEAL, "China launches Shenzhou-24 to Tiangong with Pakistani pilot Muhammad Zeeshan Ali",
         "First foreign astronaut in China's manned space program.",
         "rocket", lambda d, x, y, w, h: draw_story_icon(d, x + w//2, y + h//2, min(w, h)//2, "rocket", TEAL)),
    ]
    
    for idx, (cat, chip_color, headline, summary, icon_name, scene_fn) in enumerate(stories):
        row = idx // 3
        col = idx % 3
        px = grid_x + col * (panel_w + gap)
        py = grid_y + row * (panel_h + gap)
        
        # Panel background
        draw.rounded_rectangle([px, py, px + panel_w, py + panel_h], radius=8, fill=WHITE, outline=(200, 195, 185), width=1)
        
        # Header chip
        chip_w, chip_h = draw_chip(draw, (px + 12, py + 10), cat, FONTS["chip"], chip_color)
        
        # Headline (up to 2 lines)
        hl_x = px + 12
        hl_y = py + chip_h + 20
        hl_w = panel_w - 24
        lines = wrap_text(draw, headline, FONTS["story_headline"], hl_w)
        draw_wrapped(draw, (hl_x, hl_y), lines[:2], FONTS["story_headline"], INK)
        
        # Summary (1 line)
        sum_y = hl_y + 48
        sum_lines = wrap_text(draw, summary, FONTS["story_body"], hl_w)
        draw_wrapped(draw, (hl_x, sum_y), sum_lines[:1], FONTS["story_body"], (60, 60, 60))
        
        # Large geometric scene in lower half
        scene_y = py + panel_h // 2 + 10
        scene_h = panel_h - (scene_y - py) - 15
        scene_w = panel_w - 20
        scene_x = px + 10
        scene_fn(draw, scene_x, scene_y, scene_w, scene_h)
    
    # Footer
    footer_y = H - 30
    footer_text = "All stories first reported 25 November 2026"
    fw = draw.textlength(footer_text, font=FONTS["footer"])
    draw.text(((W - fw) // 2, footer_y), footer_text, font=FONTS["footer"], fill=(100, 100, 100))


def draw_variant3(img, draw):
    """LEAD + BRIEFS: huge story-1 headline, red rule, large scene, 8 brief rows, bottom strip."""
    draw.rectangle([0, 0, W, H], fill=BG)
    
    # Date line
    date_y = 18
    draw.text((40, date_y), "WEDNESDAY 25 NOVEMBER 2026", font=FONTS["masthead"], fill=NAVY)
    
    # Huge headline for story 1
    hl_y = date_y + 48
    headline = "Fuel tanker overturns and burns on Cairo Ring Road — 31 dead, 21 hurt"
    lines = wrap_text(draw, headline, FONTS["lead_headline"], W - 80)
    draw_wrapped(draw, (40, hl_y), lines[:2], FONTS["lead_headline"], INK)
    
    # Red rule
    rule_y = hl_y + 68
    draw.rectangle([40, rule_y, W - 40, rule_y + 4], fill=RED)
    
    # Large Cairo scene
    scene_y = rule_y + 20
    scene_h = 340
    draw_cairo_scene(draw, 40, scene_y, W - 80, scene_h)
    
    # Eight horizontal brief rows for stories 2-9
    brief_y = scene_y + scene_h + 20
    brief_h = 52
    brief_gap = 8
    
    briefs = [
        ("UK ENERGY", GOLD, "Ofgem raises price cap 26% to £2,166; 20M households hit as wholesale gas surges on Mideast conflict.", "lightning"),
        ("GULF", RED, "Houthi drone strikes Riyadh's PIF Tower again, wounding 11 (2 Saudis, 2 Indians, 3 Nepalis, 4 Egyptians); second hit in a week.", "drone"),
        ("ENERGY", RED, "Iran says more tankers hit mines in Strait of Hormuz; ~400 ships waiting, oil traffic down 40%, rial at 2.83M/$. ", "oil"),
        ("TRADE", RED, "US proposes tariffs on 14 economies: India 25%/17%, China up to 40%, Japan 15% to counter excess capacity.", "tariff"),
        ("SPACE", TEAL, "China launches Shenzhou-24 to Tiangong with Pakistani pilot Muhammad Zeeshan Ali — first foreign astronaut in program.", "rocket"),
        ("POLITICS", NAVY, "NATO to deploy early-warning planes in Poland after missile strikes; UN: Russia/Ukraine trade accusations; EU adds sanctions.", "nato"),
        ("MARKETS", RED, "AI doubts sink chips: Kospi -6.2%, Nasdaq near bear; S&P may cut Nvidia credit rating.", "chip"),
        ("INDONESIA", TEAL, "Heavy rain floods illegal gold mine in West Java; 9 dead, 17 trapped.", "flood"),
    ]
    
    for i, (cat, chip_color, body, icon) in enumerate(briefs):
        by = brief_y + i * (brief_h + brief_gap)
        # Row background
        draw.rounded_rectangle([30, by, W - 30, by + brief_h], radius=6, fill=WHITE, outline=(220, 215, 205), width=1)
        # Chip
        draw_chip(draw, (40, by + 10), cat, FONTS["chip"], chip_color)
        # Icon
        draw_story_icon(draw, W - 60, by + brief_h // 2, 28, icon, chip_color)
        # Headline + body combined as one-liner
        text_x = 40 + 100
        text_w = W - text_x - 80
        lines = wrap_text(draw, body, FONTS["story_headline"], text_w)
        draw_wrapped(draw, (text_x, by + 12), lines[:1], FONTS["story_headline"], INK)
    
    # Bottom strip: stories 10-12 + 2 ticker items
    strip_y = brief_y + 8 * (brief_h + brief_gap) + 10
    strip_h = H - strip_y - 10
    
    # Three story items side by side
    item_w = (W - 80) // 3
    bottom_stories = [
        ("INDIA", GOLD, "BJP and Shiromani Akali Dal ally for 2027 Punjab polls after 6-year split; Nepal PM Balendra Shah visits Modi.", "handshake"),
        ("CLIMATE", NAVY, "COP31 collapses in Antalya — first failure since Copenhagen 2009; Tuvalu/Ireland to host fossil-fuel exit summit 2027.", "cop"),
        ("SPORT", TEAL, "England beat Australia by 8 wickets in 2nd T20, chase 185 to level series; India women face China in Asian Champions Trophy.", "sport"),
    ]
    
    for i, (cat, chip_color, body, icon) in enumerate(bottom_stories):
        ix = 40 + i * (item_w + 10)
        draw.rounded_rectangle([ix, strip_y, ix + item_w, strip_y + strip_h], radius=6, fill=WHITE, outline=(200, 195, 185), width=1)
        draw_chip(draw, (ix + 10, strip_y + 8), cat, FONTS["chip"], chip_color)
        draw_story_icon(draw, ix + item_w // 2, strip_y + 40, 30, icon, chip_color)
        lines = wrap_text(draw, body, FONTS["story_body"], item_w - 20)
        draw_wrapped(draw, (ix + 10, strip_y + 65), lines[:3], FONTS["story_body"], (50, 50, 50))
    
    # Ticker strip at very bottom
    ticker_y = H - 36
    draw.rectangle([0, ticker_y, W, H], fill=INK)
    ticker_text = "THANKSGIVING TRAVEL PEAKS: 81.5M US TRIPS  •  ZELENSKIY CONFIRMS UKRAINE STRUCK RUSSIAN SHIP IN GULF OF FINLAND  •  FRANCE ORDERS SARKOZY CORRUPTION CASE TO TRIAL  •  GAZA DEATH TOLL REACHES 74,746"
    tw = draw.textlength(ticker_text, font=FONTS["ticker"])
    tx = (W - tw) // 2
    draw.text((int(tx), int(ticker_y + 8)), ticker_text, font=FONTS["ticker"], fill=WHITE)

if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
