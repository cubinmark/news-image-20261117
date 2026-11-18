#!/usr/bin/env python3
"""Generator for the news-image-20261117 entry poster.

Draws a flat editorial front-page style poster (1024x1024) summing up the
world news of 17 November 2026 and saves it as entry.png next to this file.
This script is provenance/documentation only; the entry program (main.py)
simply copies the committed entry.png to the output directory.

Run:  python3 gen_poster.py
"""

import os
import textwrap  # noqa: F401  (kept for parity with brief; wrapping is measured, below)
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W = H = 1024
PAPER = "#f7f3ea"
INK = "#14202b"
RED = "#b3202a"
BLUEGREY = "#33566e"
SKY = "#dde6ea"
WATER_LINE = "#6f93a8"
SUN = "#e9d8a6"
CLOUD = "#f4f7f8"
STRIP_TEXT = "#f7f3ea"

DEJAVU_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
LIB_SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
LIB_SERIF_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
LIB_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
LIB_SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

MARGIN = 44
CONTENT_W = W - 2 * MARGIN  # 936


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap measured with draw.textlength."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_block(draw, text, path, start, minimum, max_w, max_h, lh_factor=1.26):
    """Largest font size (<= start) whose wrapped block fits max_w x max_h."""
    size = start
    while size > minimum:
        fnt = font(path, size)
        lines = wrap(draw, text, fnt, max_w)
        lh = round(size * lh_factor)
        if len(lines) * lh <= max_h:
            return fnt, lines, lh, size
        size -= 1
    fnt = font(path, minimum)
    lines = wrap(draw, text, fnt, max_w)
    return fnt, lines, round(minimum * lh_factor), minimum


def draw_block(draw, x, y, lines, fnt, lh, fill):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def draw_tracked(draw, x, y, text, fnt, fill, tracking, centered_at=None):
    """Draw letterspaced text; if centered_at is given, x is ignored."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    if centered_at is not None:
        x = centered_at - total / 2
    for ch, wch in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += wch + tracking
    return total


# ---------------------------------------------------------------- masthead

def masthead(draw):
    small = font(LIB_SANS_BOLD, 27)
    draw_tracked(draw, 0, 28, "THE DAY IN ONE PICTURE", small, BLUEGREY,
                 tracking=5, centered_at=W / 2)

    # Date, auto-fit to the content width.
    size = 92
    while size > 40:
        fnt = font(DEJAVU_SERIF_BOLD, size)
        if draw.textlength("17 NOVEMBER 2026", font=fnt) <= CONTENT_W:
            break
        size -= 2
    draw.text((W / 2, 62), "17 NOVEMBER 2026", font=fnt, fill=INK, anchor="ma")

    draw.rectangle([MARGIN, 164, W - MARGIN, 168], fill=RED)

    italic = font(LIB_SERIF_ITALIC, 27)
    draw.text((W / 2, 178), "Tuesday \u2014 the world\u2019s news in a single image",
              font=italic, fill=INK, anchor="ma")


# ---------------------------------------------------------------- hero

def bridge_scene(draw, x0, y0, x1, y1):
    """Simple bridge over water with a broken span in the middle."""
    draw.rectangle([x0, y0, x1, y1], fill=SKY)
    # sun and clouds
    draw.ellipse([x1 - 118, y0 + 14, x1 - 66, y0 + 66], fill=SUN)
    for cx, cy, cw in ((x0 + 36, y0 + 18, 120), (x0 + 210, y0 + 34, 84)):
        draw.ellipse([cx, cy, cx + cw, cy + 22], fill=CLOUD)
        draw.ellipse([cx + 18, cy - 9, cx + cw - 26, cy + 16], fill=CLOUD)

    water_top = y1 - 46
    deck_y = water_top  # deck sits at the top of the water band
    mid = (x0 + x1) / 2
    gap0, gap1 = mid - 48, mid + 48
    t1 = x0 + (x1 - x0) * 0.32
    t2 = x0 + (x1 - x0) * 0.68
    tower_top = y0 + 26

    # water
    draw.rectangle([x0, water_top, x1, y1], fill=BLUEGREY)
    for i, wy in enumerate((water_top + 12, water_top + 24, water_top + 35)):
        off = 26 if i % 2 else 0
        for sx in range(int(x0) + 18 + off, int(x1) - 60, 130):
            draw.line([sx, wy, sx + 52, wy], fill=WATER_LINE, width=3)

    # piers under the towers
    for tx in (t1, t2):
        draw.rectangle([tx - 13, deck_y, tx + 13, y1], fill=INK)

    # main suspension cable (polyline through tower tops and mid dip)
    pts = [(x0 + 4, deck_y - 4), (t1, tower_top), (mid, deck_y - 34),
           (t2, tower_top), (x1 - 4, deck_y - 4)]
    draw.line(pts, fill=INK, width=3)
    # suspenders from cable down to deck
    def cable_y(x):
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            if ax <= x <= bx:
                return ay + (by - ay) * (x - ax) / (bx - ax)
        return deck_y
    sx = x0 + 44
    while sx < x1 - 30:
        if not (gap0 - 6 < sx < gap1 + 6):
            cy = cable_y(sx)
            if deck_y - cy > 14:
                draw.line([sx, cy, sx, deck_y - 8], fill=INK, width=2)
        sx += 62

    # towers
    for tx in (t1, t2):
        draw.rectangle([tx - 8, tower_top, tx + 8, deck_y], fill=INK)
        draw.rectangle([tx - 13, tower_top - 7, tx + 13, tower_top], fill=INK)

    # deck, in two spans with jagged broken ends
    draw.rectangle([x0, deck_y - 9, gap0, deck_y], fill=INK)
    draw.rectangle([gap1, deck_y - 9, x1, deck_y], fill=INK)
    draw.polygon([(gap0, deck_y - 9), (gap0 + 12, deck_y - 5), (gap0, deck_y)],
                 fill=INK)
    draw.polygon([(gap1, deck_y - 9), (gap1 - 12, deck_y - 4), (gap1, deck_y)],
                 fill=INK)
    # a deck fragment still hanging off the left break
    draw.polygon([(gap0 - 2, deck_y), (gap0 + 20, deck_y + 10),
                  (gap0 + 16, deck_y + 18), (gap0 - 4, deck_y + 8)], fill=INK)

    # falling fragments below the gap
    draw.polygon([(mid - 30, deck_y + 22), (mid - 2, deck_y + 30),
                  (mid - 6, deck_y + 40), (mid - 34, deck_y + 32)], fill=INK)
    draw.polygon([(mid + 12, deck_y + 44), (mid + 36, deck_y + 38),
                  (mid + 40, deck_y + 48), (mid + 16, deck_y + 54)], fill=INK)
    # splashes in the water under the gap
    for dx in (-26, 0, 26):
        draw.line([mid + dx, water_top + 6, mid + dx - 5, water_top - 4],
                  fill=CLOUD, width=3)
        draw.line([mid + dx, water_top + 6, mid + dx + 5, water_top - 4],
                  fill=CLOUD, width=3)


def hero(draw):
    x0, y0, x1, y1 = MARGIN, 216, W - MARGIN, 628
    draw.rectangle([x0, y0, x1, y1], outline=INK, width=2)
    bridge_scene(draw, x0 + 16, y0 + 14, x1 - 16, y0 + 164)

    inset = x0 + 24
    width = (x1 - x0) - 48
    kicker = font(LIB_SANS_BOLD, 24)
    draw_tracked(draw, inset, y0 + 178, "RUSSIA\u2013UKRAINE WAR", kicker, RED,
                 tracking=3)

    head = font(LIB_SERIF_BOLD, 50)
    y = draw_block(draw, inset, y0 + 208,
                   ["UKRAINE BREAKS THE", "CRIMEA BRIDGE"], head, 58, INK)

    body = ("Kyiv\u2019s \u2018unprecedented operation\u2019 severs the road-and-rail "
            "link to occupied Crimea. Moscow answers with strikes on "
            "Kyiv\u2019s bridges.")
    fnt, lines, lh, _ = fit_block(draw, body, LIB_SANS, 25, 20, width,
                                  y1 - y - 14)
    draw_block(draw, inset, y + 8, lines, fnt, lh, INK)


# ---------------------------------------------------------------- panels

def icon_flags(draw, x, y):
    for i, col in enumerate((RED, BLUEGREY, INK)):
        px = x + i * 30
        draw.line([px, y + 42, px, y + 2], fill=INK, width=3)
        draw.polygon([(px, y + 3), (px + 21, y + 8), (px, y + 14)], fill=col)


def icon_drone(draw, x, y):
    cx, cy = x + 27, y + 22
    corners = [(x + 5, y + 6), (x + 49, y + 6), (x + 5, y + 38), (x + 49, y + 38)]
    for (ex, ey) in corners:
        draw.line([cx, cy, ex, ey], fill=INK, width=3)
    draw.rectangle([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED)
    for (ex, ey) in corners:
        draw.ellipse([ex - 8, ey - 8, ex + 8, ey + 8], outline=INK, width=3)


def icon_jet(draw, x, y):
    pts = [(52, 22), (31, 20), (21, 5), (14, 5), (18, 19), (7, 13),
           (7, 31), (18, 25), (14, 39), (21, 39), (31, 24)]
    draw.polygon([(x + px, y + py) for px, py in pts], fill=INK)


PANELS = [
    (icon_flags, "THREE LEADERS, ONE TABLE",
     "Trump flies to APEC in Shenzhen for a trilateral with Xi and Putin "
     "on nuclear risk and Ukraine."),
    (icon_drone, "DRONES OVER BAHRAIN",
     "Iran fires drones at a U.S. radar base; Bahrain says all were "
     "intercepted. Washington weighs reports of a \u2018dirty bomb\u2019 plot."),
    (icon_jet, "JETS SCRAMBLED IN JAPAN",
     "Tokyo protests and scrambles fighters as Russian aircraft violate "
     "its airspace."),
]


def panels(draw):
    y0, y1 = 640, 912
    gap = 16
    pw = (CONTENT_W - 2 * gap) // 3
    head_f = font(LIB_SERIF_BOLD, 27)
    for i, (icon, headline, body) in enumerate(PANELS):
        x0 = MARGIN + i * (pw + gap)
        x1 = x0 + pw
        draw.rectangle([x0, y0, x1, y1], outline=INK, width=2)
        inset = x0 + 14
        width = pw - 28
        icon(draw, inset, y0 + 14)
        y = draw_block(draw, inset, y0 + 68,
                       wrap(draw, headline, head_f, width), head_f, 33, INK)
        fnt, lines, lh, _ = fit_block(draw, body, LIB_SANS, 20, 16, width,
                                      y1 - y - 16)
        draw_block(draw, inset, y + 6, lines, fnt, lh, INK)


# ---------------------------------------------------------------- strip + footer

def strip_and_footer(draw):
    y0, y1 = 924, 994
    draw.rectangle([0, y0, W, y1], fill=INK)
    text = ("ALSO THIS DAY \u2014 EUROPE: five nations unveil a joint migrant "
            "return hub in Rwanda \u2022 GENEVA: 128 states debate a treaty "
            "banning killer robots \u2022 GAZA: Western nations press Israel "
            "to open aid crossings \u2022 YEMEN: Houthi forces advance as "
            "government troops retreat")
    fnt, lines, lh, _ = fit_block(draw, text, LIB_SANS, 19, 15, CONTENT_W,
                                  y1 - y0 - 12, lh_factor=1.3)
    y = y0 + (y1 - y0 - len(lines) * lh) // 2
    for line in lines:
        draw.text((W / 2, y), line, font=fnt, fill=STRIP_TEXT, anchor="ma")
        y += lh

    foot = font(LIB_SANS, 18)
    draw.text((W / 2, 1000), "17 November 2026 \u2022 Compiled from the day\u2019s reporting",
              font=foot, fill=BLUEGREY, anchor="ma")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    masthead(draw)
    hero(draw)
    panels(draw)
    strip_and_footer(draw)
    img.save(OUT, format="PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
