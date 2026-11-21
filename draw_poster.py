#!/usr/bin/env python3
"""KORVATH — The City That Sails on a Whale.

Draws a 1024x1024 travel poster with PIL only. Deterministic, no
randomness, no network. Writes entry.png next to this script.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1024, 1024
HORIZON = 640
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vgrad(width, height, stops):
    """Vertical gradient through (position, colour) stops."""
    arr = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        t = y / max(height - 1, 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = 0.0 if p1 == p0 else (t - p0) / (p1 - p0)
                arr[y, :, :] = lerp(c0, c1, f)
                break
        else:
            arr[y, :, :] = stops[-1][1]
    return Image.fromarray(arr, "RGB")


def catmull_rom(points, samples=24):
    """Smooth curve through points -> list of (x, y)."""
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(len(pts) - 3):
        p0, p1, p2, p3 = pts[i], pts[i + 1], pts[i + 2], pts[i + 3]
        for s in range(samples):
            t = s / samples
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(points[-1])
    return out


def back_y_at(x, curve):
    """Interpolate the whale back curve at a given x."""
    for i in range(len(curve) - 1):
        x0, y0 = curve[i]
        x1, y1 = curve[i + 1]
        if x0 <= x <= x1 and x1 != x0:
            f = (x - x0) / (x1 - x0)
            return y0 + (y1 - y0) * f
    return curve[-1][1]


def letter_spaced(draw, cx, y, text, font, fill, spacing):
    """Draw text centred on cx, with extra space between letters."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + spacing
    return total


def main():
    # ---- sky -------------------------------------------------------
    sky = vgrad(W, HORIZON, [
        (0.00, (22, 26, 58)),
        (0.35, (52, 48, 96)),
        (0.62, (122, 74, 116)),
        (0.85, (214, 122, 92)),
        (1.00, (244, 178, 110)),
    ])
    sea = vgrad(W, H - HORIZON, [
        (0.00, (64, 84, 110)),
        (1.00, (14, 28, 52)),
    ])
    img = Image.new("RGB", (W, H))
    img.paste(sky, (0, 0))
    img.paste(sea, (0, HORIZON))
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- stars high up ---------------------------------------------
    stars = [(70, 60), (150, 110), (230, 55), (330, 90), (430, 45),
             (560, 70), (640, 40), (900, 70), (960, 130), (60, 170),
             (350, 150), (700, 110), (830, 60), (480, 120)]
    for sx, sy in stars:
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 244, 222, 235))
    for sx, sy in [(200, 90), (600, 130), (920, 100), (120, 130)]:
        draw.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 244, 222, 170))

    # ---- soft pink clouds ------------------------------------------
    cloud = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cloud)
    for cx, cy, rx, ry, alpha in [
            (230, 300, 190, 26, 46), (250, 318, 130, 18, 38),
            (800, 290, 170, 24, 42), (820, 306, 110, 16, 34),
            (520, 340, 150, 18, 30)]:
        cd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry],
                   fill=(255, 170, 150, alpha))
    img = Image.alpha_composite(
        img.convert("RGBA"), cloud.filter(ImageFilter.GaussianBlur(14)))

    # ---- low sun + glow --------------------------------------------
    sun_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun_layer)
    sd.ellipse([800 - 150, 430 - 150, 800 + 150, 430 + 150],
               fill=(255, 205, 130, 60))
    sd.ellipse([800 - 95, 430 - 95, 800 + 95, 430 + 95],
               fill=(255, 220, 160, 90))
    img = Image.alpha_composite(img.convert("RGBA"),
                                sun_layer.filter(ImageFilter.GaussianBlur(18)))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.ellipse([800 - 60, 430 - 60, 800 + 60, 430 + 60],
                 fill=(255, 236, 190, 255))
    draw.ellipse([800 - 44, 430 - 44, 800 + 44, 430 + 44],
                 fill=(255, 246, 214, 255))

    # ---- horizon line ----------------------------------------------
    draw.line([(0, HORIZON), (W, HORIZON)], fill=(255, 220, 170, 110), width=2)

    # ---- golden reflection column under the whale ------------------
    refl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(refl)
    for i, (ry, half, alpha) in enumerate([
            (665, 150, 90), (700, 120, 80), (735, 95, 70),
            (775, 75, 60), (820, 60, 50), (870, 48, 42),
            (925, 38, 34), (975, 30, 26)]):
        rd.line([(512 - half, ry), (512 + half, ry)],
                fill=(255, 200, 120, alpha), width=4)
    img = Image.alpha_composite(img, refl.filter(ImageFilter.GaussianBlur(3)))
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- sun reflection streaks on the right -----------------------
    for i, (ry, x0, x1, a) in enumerate([
            (655, 700, 880, 150), (680, 730, 900, 120), (705, 760, 870, 100),
            (735, 780, 860, 85), (770, 800, 850, 70)]):
        draw.line([(x0, ry), (x1, ry)], fill=(255, 205, 130, a), width=3)

    # ---- THE WHALE --------------------------------------------------
    back_ctrl = [(58, 606), (150, 528), (300, 498), (520, 478),
                 (700, 492), (850, 536), (952, 592)]
    back = catmull_rom(back_ctrl)
    belly_ctrl = [(58, 606), (180, 668), (380, 700), (560, 706),
                  (740, 692), (880, 652), (952, 592)]
    belly = catmull_rom(belly_ctrl)

    whale = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(whale)
    # tail flukes, lifted on the left: two lobes rising above the back
    wd.polygon([(70, 606), (18, 478), (78, 548), (138, 458),
                (152, 560), (118, 600)], fill=(38, 56, 88, 255))
    # body
    body = back + list(reversed(belly))
    wd.polygon(body, fill=(38, 56, 88, 255))
    # paler belly crescent
    belly_top = [(x, y - 26 - 14 * math.sin(math.pi * (x - 60) / 890))
                 for x, y in belly]
    wd.polygon(belly_top + list(reversed(belly)), fill=(94, 122, 158, 255))
    # pectoral fin under the belly
    wd.polygon([(600, 690), (640, 758), (676, 700), (648, 682)],
               fill=(30, 46, 74, 255))
    img = Image.alpha_composite(img, whale)
    draw = ImageDraw.Draw(img, "RGBA")

    # eye + glint (head on the right)
    draw.ellipse([878, 556, 898, 576], fill=(16, 22, 38, 255))
    draw.ellipse([883, 560, 890, 567], fill=(255, 244, 222, 255))
    # mouth hint
    draw.arc([860, 600, 950, 640], start=20, end=110,
             fill=(20, 30, 54, 255), width=3)

    # foam dashes at the waterline
    for fx, fy, fl in [(120, 668, 46), (240, 690, 60), (400, 702, 70),
                       (700, 700, 64), (850, 668, 50), (60, 640, 40),
                       (930, 630, 36)]:
        draw.line([(fx, fy), (fx + fl, fy)], fill=(220, 235, 245, 170), width=3)

    # ---- spout ------------------------------------------------------
    spout = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    spd = ImageDraw.Draw(spout)
    bx, by = 165, back_y_at(165, back) - 2
    for dx, top, wdt in [(-10, 412, 4), (0, 398, 5), (10, 414, 4)]:
        spd.line([(bx + dx, by), (bx + int(dx * 1.6), top)],
                 fill=(245, 250, 252, 235), width=wdt)
    spd.ellipse([bx - 56, 376, bx + 56, 440], fill=(255, 255, 255, 200))
    spd.ellipse([bx - 38, 358, bx + 34, 414], fill=(255, 255, 255, 215))
    spd.ellipse([bx - 20, 348, bx + 18, 388], fill=(255, 255, 255, 225))
    img = Image.alpha_composite(
        img, spout.filter(ImageFilter.GaussianBlur(12)))
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- THE CITY on the whale's back -------------------------------
    WINDOW = (255, 205, 110, 255)
    DARK = (24, 30, 52, 255)
    ROOF = (18, 22, 40, 255)

    def house(cx, wdt=46, hgt=42):
        by = back_y_at(cx, back)
        x0, x1 = cx - wdt // 2, cx + wdt // 2
        draw.polygon([(x0, by - hgt + 12), (cx, by - hgt - 12),
                      (x1, by - hgt + 12)], fill=ROOF)
        draw.rectangle([x0, by - hgt + 12, x1, by], fill=DARK)
        draw.rectangle([x0 + 8, by - hgt + 22, x0 + 16, by - hgt + 32],
                       fill=WINDOW)
        draw.rectangle([x1 - 16, by - hgt + 22, x1 - 8, by - hgt + 32],
                       fill=WINDOW)

    def dome(cx, r=22):
        by = back_y_at(cx, back)
        draw.pieslice([cx - r, by - r, cx + r, by], start=180, end=360,
                      fill=(196, 120, 58, 255))
        draw.rectangle([cx - 1, by - r - 26, cx + 1, by - r], fill=(40, 40, 50, 255))
        draw.polygon([(cx + 1, by - r - 26), (cx + 20, by - r - 20),
                      (cx + 1, by - r - 14)], fill=(214, 64, 54, 255))

    for hx in [150, 205, 262, 320, 378, 560, 620, 682, 742, 800, 858]:
        house(hx)
    for dx in [292, 652, 772]:
        dome(dx)

    # lighthouse at x=470
    lx = 470
    ly = int(back_y_at(lx, back))
    tower_top = ly - 158
    draw.rectangle([lx - 15, tower_top, lx + 15, ly], fill=(240, 238, 230, 255))
    for i, band_y in enumerate(range(tower_top + 8, ly - 10, 26)):
        if i % 2 == 0:
            draw.rectangle([lx - 15, band_y, lx + 15, band_y + 13],
                           fill=(198, 52, 46, 255))
    draw.rectangle([lx - 19, tower_top - 12, lx + 19, tower_top],
                   fill=(30, 34, 52, 255))
    # lamp glow + lamp
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([lx - 46, tower_top - 58, lx + 46, tower_top + 34],
               fill=(255, 214, 120, 110))
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(10)))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.ellipse([lx - 13, tower_top - 32, lx + 13, tower_top - 6],
                 fill=(255, 226, 150, 255))
    # faint beam sweeping left, slightly downward
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon([(lx - 12, tower_top - 18), (290, tower_top - 34),
                (290, tower_top - 6), (lx - 12, tower_top - 6)],
               fill=(255, 226, 150, 30))
    img = Image.alpha_composite(img, beam.filter(ImageFilter.GaussianBlur(6)))
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- sailboat, foreground bottom left --------------------------
    boat = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bdd = ImageDraw.Draw(boat)
    # wake
    bdd.line([(120, 952), (330, 952)], fill=(200, 220, 235, 150), width=3)
    bdd.line([(150, 966), (300, 966)], fill=(200, 220, 235, 110), width=2)
    # hull
    bdd.polygon([(150, 912), (292, 912), (272, 944), (172, 944)],
                fill=(26, 32, 56, 255))
    bdd.line([(150, 912), (292, 912)], fill=(120, 140, 170, 255), width=2)
    # mast + one warm triangular sail
    bdd.line([(221, 912), (221, 838)], fill=(40, 44, 66, 255), width=4)
    bdd.polygon([(221, 842), (221, 908), (290, 908)],
                fill=(255, 196, 110, 255))
    bdd.polygon([(221, 856), (221, 908), (176, 908)],
                fill=(226, 158, 84, 255))
    # lantern glow + lantern
    bdd.ellipse([212, 828, 232, 848], fill=(255, 214, 120, 255))
    img = Image.alpha_composite(img, boat)
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- pale wave shimmer strokes ---------------------------------
    for wx, wy, wl, a in [(90, 720, 60, 120), (300, 760, 80, 100),
                          (620, 740, 90, 110), (820, 720, 70, 120),
                          (180, 800, 70, 90), (760, 830, 80, 90),
                          (420, 860, 60, 80), (880, 860, 60, 90),
                          (520, 960, 90, 70), (80, 900, 60, 80)]:
        draw.line([(wx, wy), (wx + wl, wy)], fill=(190, 215, 235, a), width=3)

    # ---- title ------------------------------------------------------
    title_font = ImageFont.truetype(BOLD, 118)
    sub_font = ImageFont.truetype(BOLD, 30)
    letter_spaced(draw, 512, 58, "KORVATH", title_font,
                  (255, 244, 222, 255), 26)
    sub_w = letter_spaced(draw, 512, 210, "THE CITY THAT SAILS ON A WHALE",
                          sub_font, (255, 214, 140, 255), 5)
    rule_y = 224
    draw.line([(512 - sub_w / 2 - 84, rule_y), (512 - sub_w / 2 - 16, rule_y)],
              fill=(255, 214, 140, 255), width=3)
    draw.line([(512 + sub_w / 2 + 16, rule_y), (512 + sub_w / 2 + 84, rule_y)],
              fill=(255, 214, 140, 255), width=3)

    # ---- soft dark vignette ----------------------------------------
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    vd.rectangle([0, 0, W, H], fill=0)
    vd.ellipse([-140, -140, W + 140, H + 140], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    dark = Image.new("RGBA", (W, H), (10, 10, 26, 255))
    img = Image.composite(img, Image.alpha_composite(img, dark),
                          vig.point(lambda p: 255 - int((255 - p) * 0.55)))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.convert("RGB").save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
