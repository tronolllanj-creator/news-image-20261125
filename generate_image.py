import os
import sys

from PIL import Image, ImageDraw, ImageFont

# ----- required local fonts ---------------------------------------------
BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# a tiny helper that never fails on size (deterministic local files)
_font_cache = {}


def _font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def load_bold(size):
    return _font(BOLD_PATH, size)


def load_reg(size):
    return _font(REG_PATH, size)


# ----- palette ------------------------------------------------------------
PAPER = (244, 239, 230)
INK = (26, 26, 26)
RED = (200, 16, 46)
BLUE = (43, 76, 126)
GREY = (138, 129, 120)
WHITE = (255, 255, 255)

SIZE = 1024


# ----- text helpers -------------------------------------------------------
def wrap_text(draw, text, font, max_width):
    if max_width is None or max_width <= 0:
        return [line for line in text.split("\n") if line.strip()] or [""]
    lines = []
    for para in text.split("\n"):
        para = para.strip()
        if not para:
            lines.append("")
            continue
        words = para.split(" ")
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if draw.textlength(trial, font=font) <= max_width or cur == "":
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines if lines else [""]


def draw_wrapped(draw, xy, lines, font, fill, leading=1):
    x, y = xy[0], xy[1]
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        bbox = font.getbbox(line)
        h = bbox[3] - bbox[1] if bbox else int(font.size)
        y = y + h * int(leading) + int(font.size * 0.18)
    return y


# ----- tiny geometric pictogram helper ------------------------------------
def draw_icon(draw, cx, cy, kind, color, s=28):
    s = int(s)
    cx = int(cx)
    cy = int(cy)
    hw = s // 2
    if kind == "tower":
        # two stacked blocks offset to suggest a high-rise
        top = (cx - hw // 2, cy - hw, cx + hw // 2, cy + hw // 3)
        bot = (cx - hw // 3, cy - hw // 3, cx + hw, cy + hw)
        draw.rectangle(top, fill=color)
        draw.rectangle(bot, fill=color)
        draw.line((cx + hw // 2, cy - hw // 2, cx + hw, cy - hw // 2), fill=color, width=2)
    elif kind == "gauge":
        # barrel + dial
        draw.ellipse((cx - hw, cy - 6, cx - 6, cy + 6), fill=color)
        draw.rectangle((cx - 6, cy - hw // 2, cx + hw, cy + hw // 2), fill=color)
        draw.line((cx + hw // 2, cy + hw // 4, cx + hw - 2, cy - hw // 2), fill=PAPER, width=2)
    elif kind == "plane":
        p1 = (cx - hw, cy)
        p2 = (cx + hw, cy)
        p3 = (cx, cy - hw // 2)
        draw.polygon((p1, p2, p3), fill=color)
        draw.line((cx - hw // 2, cy, cx + hw // 2, cy), fill=color, width=2)
    elif kind == "broken":
        # two bricks not touching, a gap + diagonal slash = link broken
        draw.rectangle((cx - hw, cy - hw // 3, cx - 2, cy + hw // 3), fill=color)
        draw.rectangle((cx + 2, cy - hw // 3, cx + hw, cy + hw // 3), fill=color)
        draw.line((cx - hw, cy + hw, cx + hw, cy - hw), fill=color, width=2)
    elif kind == "bats":
        draw.ellipse((cx - hw, cy - hw, cx - 2, cy + hw), fill=color)
        draw.line((cx - 4, cy, cx + hw, cy), fill=color, width=3)
    elif kind == "bolt":
        pts = [(cx + hw // 3, cy - hw), (cx - hw // 2, cy + 2), (cx, cy + 2),
               (cx - hw // 3, cy + hw), (cx + hw // 2, cy - 2), (cx, cy - 2)]
        draw.polygon(pts, fill=color)
    else:
        draw.ellipse((cx - hw // 2, cy - hw // 2, cx + hw // 2, cy + hw // 2), fill=color)


def chip(draw, left, top, text, ffont, color, pad_x=12, pad_y=6):
    w = int(draw.textlength(text, font=ffont))
    bb = ffont.getbbox(text)
    h = bb[3] - bb[1]
    left = int(left)
    top = int(top)
    draw.rounded_rectangle([left, top, left + w + 2 * pad_x, top + h + 2 * pad_y],
                           radius=6, fill=color)
    draw.text((left + pad_x, top + pad_y), text, font=ffont, fill=WHITE)
    return left + w + 2 * pad_x


# ----- variant 1 : FRONT PAGE --------------------------------------------
def draw_variant1():
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    d = ImageDraw.Draw(img)

    f_mast = load_bold(46)
    f_date = load_bold(26)
    f_lead = load_bold(52)
    f_dek = load_reg(24)
    f_blk = load_bold(22)
    f_sm = load_reg(17)
    f_stat = load_bold(30)
    f_chip = load_bold(15)
    f_tick = load_bold(15)

    M = 34
    right = SIZE - M

    # masthead
    d.rectangle([M, M, right, M + 58], fill=INK)
    d.text((M + 18, M + 7), "THE DAILY SIGNAL", font=f_mast, fill=PAPER)
    d.text((right - 18, M + 56 - 30), "WEDNESDAY 25 NOVEMBER 2026",
           font=f_date, fill=RED)
    d.line([M, M + 60, right, M + 60], fill=RED, width=4)

    top = M + 76

    # LEAD story (story 1, GULF) full width
    lead_head = "DRONE HITS RIYADH'S TALLEST TOWER; COALITION VOWS BLOWBACK"
    lead_sum = ("Houthi strike on the PIF Tower in the King Abdullah Financial "
                "District wounds 11 people. It is the second strike on the tower "
                "in under a week; the US urges heightened vigilance.")
    d.text((M, top), "GULF", font=f_blk, fill=RED)
    hh = top + 32
    for ln in wrap_text(d, lead_head, f_lead, right - M - 70):
        d.text((M, hh), ln, font=f_lead, fill=INK)
        bb = f_lead.getbbox(ln)
        hh += (bb[3] - bb[1]) + 8
    hh += 6
    chips = [("11 WOUNDED", RED), ("2ND STRIKE IN 7 DAYS", BLUE)]
    cx = M
    for txt, col in chips:
        cx = chip(d, cx, hh, txt, f_chip, col) + 12
    hh += 42
    for ln in wrap_text(d, lead_sum, f_dek, right - M):
        d.text((M, hh), ln, font=f_dek, fill=INK)
        bb = f_dek.getbbox(ln)
        hh += (bb[3] - bb[1]) + 6
    lead_bottom = hh + 8
    d.line([M, lead_bottom - 2, right, lead_bottom - 2], fill=GREY, width=1)

    # STRONG SECONDARY (story 2, ENERGY) full width with gauge
    top = lead_bottom + 10
    d.text((M, top), "ENERGY", font=f_blk, fill=INK)
    d.line([M, top + 28, M + 90, top + 28], fill=RED, width=3)
    gy = top + 44
    gx = right - 60
    draw_icon(d, gx, gy + 18, "gauge", RED, s=44)
    gtxt = ("Iran: more tankers mined and ablaze in the Strait of Hormuz. "
            "The strait is near-paralysed. Oil rebounds from three-month lows "
            "and the rial dips to a record 2.83M per dollar.")
    ok = True
    for ln in wrap_text(d, gtxt, f_dek, right - M - 90):
        d.text((M, gy + 18), ln, font=f_dek, fill=INK)
        bb = f_dek.getbbox(ln)
        gy += (bb[3] - bb[1]) + 6
    # stat chips
    stat_y = gy + 6
    sx = M
    for txt, col in [("-40% OIL TRAFFIC", RED), ("400 SHIPS HELD", BLUE),
                     ("RIAL 2.83M/$", RED)]:
        sx = chip(d, sx, stat_y, txt, f_stat, col) + 16
    sec_bottom = stat_y + 54
    d.line([M, sec_bottom, right, sec_bottom], fill=GREY, width=1)

    # THREE-COLUMN news band : politics(2.3), india(2.4), climate(2.5)
    col_top = sec_bottom + 12
    col_gap = 18
    colw = (right - M - 2 * col_gap) // 3
    cols = [
        ("POLITICS", "plane", BLUE,
         "NATO to fly early-warning jets over Poland; Russia, Ukraine trade "
         "accusations over Black Sea strikes."),
        ("INDIA", "tower", BLUE,
         "BJP and SAD re-bond for 2027 Punjab vote; Nepal PM closes first "
         "state visit to India."),
        ("CLIMATE", "broken", RED,
         "COP31 ends a no-deal in Antalya; Thailand banks 800M baht; Tuvalu "
         "plans 2027 fossil-fuel exit summit."),
    ]
    for i, (blk, ico, ccol, body) in enumerate(cols):
        x0 = M + i * (colw + col_gap)
        x1 = x0 + colw
        d.text((x0, col_top), blk, font=f_blk, fill=ccol)
        ico_y = col_top + 40
        draw_icon(d, x0 + 18, ico_y, ico, ccol, s=34)
        bx = x0 + 56
        # headline shortened to fit width
        title = wrap_text(d, (body.split(".")[0] + "."), f_dek, x1 - bx)
        ty = ico_y
        for ln in title:
            d.text((bx, ty), ln, font=f_dek, fill=INK)
            bb = f_dek.getbbox(ln)
            ty += (bb[3] - bb[1]) + 5
        ty += 4
        for ln in wrap_text(d, "", f_sm, x1 - x0):
            pass
        # body text
        by = ty
        full = body
        for ln in wrap_text(d, full, f_sm, x1 - x0):
            d.text((x0, by), ln, font=f_sm, fill=INK)
            bb = f_sm.getbbox(ln)
            by += (bb[3] - bb[1]) + 4
        d.line([x0, col_top + 8, x0, by], fill=GREY, width=2)
    band_bottom = col_top + 150

    # SPORT strip (2.6) full width
    sp_top = band_bottom + 16
    d.rectangle([M, sp_top, right, sp_top + 56], fill=BLUE)
    draw_icon(d, M + 26, sp_top + 28, "bats", PAPER, s=34)
    d.text((M + 60, sp_top + 14),
           "SPORT  |  England down Australia by 8 wickets to level the T20s.",
           font=f_blk, fill=PAPER)
    d.text((right - 18 - int(d.textlength(
        "Women's hockey: India face China, Asian Champions Trophy", font=f_blk)),
           sp_top + 14),
           "Women's hockey: India face China, Asian Champions Trophy",
           font=f_blk, fill=PAPER)
    sport_bottom = sp_top + 56

    # TICKER strip (story 6 / extras)
    tk_top = sport_bottom + 14
    d.rectangle([M, tk_top, right, tk_top + 54], fill=INK)
    d.text((M + 14, tk_top + 15), "TICKER", font=f_blk, fill=RED)
    d.line([M + 92, tk_top + 13, M + 92, tk_top + 41], fill=RED, width=2)
    tick_items = [
        "Thanksgiving: 81.5M travellers, 417K flights (AAA/FAA)",
        "Ukraine says it struck a Russian ship, Gulf of Finland",
        "Sarkozy corruption case to trial (France)",
        "Gaza death toll: 74,746",
    ]
    tx = M + 104
    for t in tick_items:
        tw = d.textlength(t, font=f_sm)
        if tx + tw + 30 > right:
            break
        d.text((tx, tk_top + 16), t, font=f_sm, fill=PAPER)
        tx += tw + 24
        d.line((tx - 12, tk_top + 18, tx - 12, tk_top + 38), fill=GREY, width=2)
    ticker_bottom = tk_top + 54

    # footer line
    d.text((M, SIZE - 30), "All stories first reported 25 November 2026.",
           font=f_sm, fill=GREY)
    d.line([M, SIZE - 44, right, SIZE - 44], fill=GREY, width=1)

    return img


def draw_variant2():
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    d = ImageDraw.Draw(img)

    f_ban = load_bold(34)
    f_head = load_bold(22)
    f_sum = load_reg(16)
    f_chip = load_bold(14)

    M = 28
    right = SIZE - M
    ban_h = 56
    top_y = M + ban_h + 14

    # date banner
    d.rectangle([M - 10, M - 10, right + 10, M - 10 + ban_h], fill=INK)
    d.text((M + 14, M + 4), "WEDNESDAY 25 NOVEMBER 2026", font=f_ban, fill=PAPER)
    d.line([M - 10, M - 10 + ban_h, right + 10, M - 10 + ban_h], fill=RED, width=4)

    # 2x3 grid: six equal panels
    gap = 18
    pad = 14
    grid_top = top_y
    grid_bottom = SIZE - M
    cols, rows = 2, 3
    cell_w = (SIZE - 2 * M - (cols - 1) * gap) // cols
    cell_h = (grid_bottom - grid_top - (rows - 1) * gap) // rows

    stories = [
        ("GULF", RED,
         "DRONE HITS RIYADH TALLEST TOWER",
         "Houthi strike on PIF Tower wounds 11; the second hit in under a week; US urges vigilance.",
         "tower"),
        ("ENERGY", BLUE,
         "TANKERS MINE-HIT IN HORMUZ",
         "Strait near-paralysed, \u2248400 ships waiting, oil traffic -40%; rial at 2.83M a low.",
         "gauge"),
        ("POLITICS", (110, 40, 160),
         "NATO EARLY-WARN AIRCRAFT TO POLAND",
         "After missiles landed there during an attack on Ukraine; EU adds sanctions; Russia-Ukraine shipping feud.",
         "plane"),
        ("INDIA", (20, 140, 90),
         "BJP + SAD ALLY FOR 2027 PUNJAB",
         "Parties reunite after a six-year split; PM Shah wraps his first state visit to India.",
         "broken"),
        ("SPORT", (30, 120, 200),
         "ENGLAND BEATS AUSTRALIA 8 WCKTS",
         "Chase 185 to level the T20 series; India's women's hockey face China in Asia.",
         "bats"),
        ("CLIMATE", (200, 110, 20),
         "COP31 FALLOUT: BOWEN RESIGN CALL",
         "Opposition wants minister out; first no-deal since 2009; Tuvalu/Ireland 2027 exit summit.",
         "bolt"),
    ]

    for i, (tag, col, head, summ, icon) in enumerate(stories):
        r, c = divmod(i, cols)
        x0 = M + c * (cell_w + gap)
        y0 = grid_top + r * (cell_h + gap)
        x1 = x0 + cell_w
        y1 = y0 + cell_h

        # panel card
        d.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=WHITE, outline=col, width=3)
        # top accent bar
        d.rectangle([x0, y0, x1, y0 + 8], fill=col)

        # header chip
        chip(d, x0 + pad, y0 + 20, tag, f_chip, col, pad_x=10, pad_y=5)

        # headline (up to 2 lines)
        hy = y0 + 20 + 30
        hh = hy
        for ln in wrap_text(d, head, f_head, cell_w - 2 * pad):
            if hh >= y1 - 96:
                break
            d.text((x0 + pad, hh), ln, font=f_head, fill=INK)
            bb = f_head.getbbox(ln)
            hh += (bb[3] - bb[1]) + 6
            hy = hh
        hy = hh + 4

        # divider
        d.line([x0 + pad, hy, x1 - pad, hy], fill=GREY, width=1)
        hy += 10

        # summary (one-line wrap, keep inside)
        for ln in wrap_text(d, summ, f_sum, cell_w - 2 * pad - 54):
            if hy >= y1 - pad - 4:
                break
            d.text((x0 + pad, hy), ln, font=f_sum, fill=INK)
            bb = f_sum.getbbox(ln)
            hy += (bb[3] - bb[1]) + 4

        # icon bottom-right
        icon_s = 30
        ico_cx = x1 - pad - icon_s // 2
        ico_cy = y1 - pad - icon_s // 2
        draw_icon(d, ico_cx, ico_cy, icon, col, s=icon_s)

    return img



def draw_variant3():
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    draw = ImageDraw.Draw(img)

    # fonts
    f_date = load_bold(28)
    f_headline = load_bold(52)
    f_subhead = load_bold(26)
    f_summary = load_reg(22)
    f_chip = load_bold(18)
    f_ticker = load_reg(20)

    left = 60
    right = SIZE - 60
    content_w = right - left
    y = 40

    # DATE LINE
    date_text = "WEDNESDAY 25 NOVEMBER 2026"
    date_lines = wrap_text(draw, date_text, f_date, content_w)
    y = draw_wrapped(draw, (left, y), date_lines, f_date, INK, leading=1.2)
    y += 20

    # STORY 1 HUGE HEADLINE
    s1_headline = "Houthi drone strike hits Riyadh\'s tallest tower, PIF Tower, 11 wounded"
    s1_lines = wrap_text(draw, s1_headline, f_headline, content_w)
    y = draw_wrapped(draw, (left, y), s1_lines, f_headline, INK, leading=1.15)
    y += 12

    # RED RULE
    rule_y = int(y)
    draw.line((left, rule_y, right, rule_y), fill=RED, width=4)
    y = rule_y + 20

    # STORIES 2-6: FIVE HORIZONTAL BRIEF ROWS
    stories = [
        {
            "chip": "ENERGY",
            "color": BLUE,
            "headline": "Iran says more oil tankers hit mines in Strait of Hormuz, ~400 ships waiting, traffic down 40%",
            "summary": "Oil prices rebound from three-month lows; rial falls to record 2.83 million per US dollar after new US sanctions.",
            "icon": "gauge",
        },
        {
            "chip": "POLITICS",
            "color": RED,
            "headline": "NATO to deploy early-warning aircraft in Poland after missiles land during attack on Ukraine",
            "summary": "At UN, Russia and Ukraine trade accusations over Black Sea shipping and energy attacks; EU announces further sanctions.",
            "icon": "plane",
        },
        {
            "chip": "INDIA",
            "color": (180, 100, 30),
            "headline": "BJP and Shiromani Akali Dal announce alliance for 2027 Punjab elections, reuniting after six-year split",
            "summary": "Nepal PM Balendra Shah wraps first state visit to India after talks with PM Modi.",
            "icon": "broken",
        },
        {
            "chip": "SPORT",
            "color": (30, 140, 80),
            "headline": "England beat Australia by eight wickets in 2nd T20I, chase 185 to level five-match series",
            "summary": "In India, women\'s hockey team faces China in Asian Champions Trophy.",
            "icon": "bats",
        },
        {
            "chip": "CLIMATE",
            "color": (140, 60, 140),
            "headline": "COP31 fallout: Australia opposition demands Climate Minister Bowen resign over Antalya collapse",
            "summary": "First failure to reach deal since Copenhagen 2009; Thailand secures 800M baht climate support; Tuvalu to co-host fossil-fuel exit summit with Ireland in 2027.",
            "icon": "bolt",
        },
    ]

    row_h = 130
    icon_size = 28
    chip_top_offset = 8
    for i, s in enumerate(stories):
        row_y = int(y)
        # chip
        chip_x = left
        chip_y = row_y + chip_top_offset
        chip_right = chip(draw, chip_x, chip_y, s["chip"], f_chip, s["color"])
        # icon
        icon_cx = left + 30
        icon_cy = row_y + row_h // 2
        draw_icon(draw, icon_cx, icon_cy, s["icon"], s["color"], s=icon_size)
        # headline
        hl_x = chip_right + 20
        hl_w = right - hl_x
        hl_lines = wrap_text(draw, s["headline"], f_subhead, hl_w)
        draw_wrapped(draw, (hl_x, row_y + 4), hl_lines, f_subhead, INK, leading=1.2)
        # summary
        sum_y = row_y + 50
        sum_lines = wrap_text(draw, s["summary"], f_summary, hl_w)
        draw_wrapped(draw, (hl_x, sum_y), sum_lines, f_summary, GREY, leading=1.25)
        y = row_y + row_h + 6

    # BOTTOM TICKER STRIP
    ticker_y = SIZE - 70
    draw.rectangle((0, ticker_y - 10, SIZE, SIZE), fill=INK)
    ticker_items = [
        "THANKSGIVING TRAVEL: AAA expects 81.5 million US travellers; FAA forecasts 417,000 flights over nine days",
        "Zelenskiy confirms Ukraine struck a Russian ship in the Gulf of Finland",
    ]
    ticker_text = "  •  ".join(ticker_items)
    ticker_lines = wrap_text(draw, ticker_text, f_ticker, SIZE - 120)
    tx = 60
    ty = ticker_y + 6
    for line in ticker_lines:
        draw.text((tx, ty), line, font=f_ticker, fill=WHITE)
        bbox = f_ticker.getbbox(line)
        h = bbox[3] - bbox[1] if bbox else int(f_ticker.size)
        ty += h + 2

    return img



def main():
    variant = sys.argv[1] if len(sys.argv) > 1 else "1"
    fn = globals().get("draw_variant" + variant)
    if fn is None:
        sys.stderr.write("unknown variant: %s\n" % variant)
        sys.exit(1)
    img = fn()
    out = "variant_%s.png" % variant
    img.save(out)
    with open(out, "rb") as f:
        n = len(f.read())
    print("wrote %s %dx%d bytes %d" % (out, img.size[0], img.size[1], n))


if __name__ == "__main__":
    main()
