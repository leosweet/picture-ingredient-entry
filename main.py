#!/usr/bin/env python3
"""Melted-cheese burger, drawn from scratch with Pillow only.

One 1024x1024 food picture: a cheeseburger on a wooden board, warm dark
background, no text, no network, no external files. Rendered at 2x and
downscaled with LANCZOS. Deterministic: fixed coordinates, no randomness,
no timestamps.
"""

import math

from PIL import Image, ImageDraw, ImageFilter

S = 2            # supersampling factor
W = 1024 * S     # working canvas
OUT = "/output/entry.png"


def sc(v):
    """Scale a 1024-space coordinate to working space."""
    return int(round(v * S))


def bbox(x0, y0, x1, y1):
    return (sc(x0), sc(y0), sc(x1), sc(y1))


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vertical_gradient(size, top, bottom):
    """A tall RGB gradient image, top colour to bottom colour."""
    grad = Image.new("RGB", (1, size[1]))
    px = [lerp(top, bottom, y / max(1, size[1] - 1)) for y in range(size[1])]
    grad.putdata(px)
    return grad.resize(size)


def radial_glow(base, centre, radius, colour, peak_alpha, steps=48):
    """Warm light: nested ellipses, faintest outside, strongest inside."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = sc(centre[0]), sc(centre[1])
    r = sc(radius)
    for i in range(steps, 0, -1):
        t = i / steps
        a = int(peak_alpha * (1.0 - t) ** 2)
        d.ellipse([cx - r * t, cy - r * t * 0.62, cx + r * t, cy + r * t * 0.62],
                  fill=colour + (a,))
    return Image.alpha_composite(base, layer)


def shade(base, draw_fn, blur=0):
    """Draw semi-transparent shading on its own layer, then composite.

    Drawing translucent fills straight onto an RGBA layer replaces pixels
    (including their alpha), which punches holes through opaque paint.
    A separate overlay avoids that.
    """
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(sc(blur)))
    return Image.alpha_composite(base, layer)


def wavy_band_points(x0, x1, y_base, amp, waves, step=8, phase=0.0):
    """Points along a sine-waved horizontal edge, left to right."""
    pts = []
    x = x0
    while x <= x1:
        t = (x - x0) / max(1, x1 - x0)
        y = y_base + amp * math.sin(2 * math.pi * waves * t + phase)
        pts.append((sc(x), sc(y)))
        x += step
    pts.append((sc(x1), sc(y_base)))
    return pts


def leaf(draw, cx, cy, length, width, angle_deg, colour):
    """A pointed oval leaf, rotated by angle, centred at (cx, cy)."""
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for i in range(25):
        t = i / 24.0
        # lens shape: two arcs meeting at the tips
        along = (t - 0.5) * length
        across = width * math.sin(math.pi * t) * 0.5
        # taper the lens so both ends come to a point
        pts.append((cx + along * ca - across * sa,
                    cy + along * sa + across * ca))
    draw.polygon([(sc(px), sc(py)) for px, py in pts], fill=colour)


def main():
    img = vertical_gradient((W, W), (74, 43, 26), (34, 19, 12)).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # ---- warm light from the top ----
    img = radial_glow(img, (512, 150), 620, (255, 196, 110), 72)
    draw = ImageDraw.Draw(img)

    # ---- wooden board: wide flat ellipse ----
    board_cx, board_cy, board_rx, board_ry = 512, 800, 430, 128
    draw.ellipse(bbox(board_cx - board_rx, board_cy - board_ry,
                      board_cx + board_rx, board_cy + board_ry),
                 fill=(122, 76, 40, 255))
    draw.ellipse(bbox(board_cx - board_rx + 14, board_cy - board_ry + 12,
                      board_cx + board_rx - 14, board_cy + board_ry - 10),
                 fill=(146, 94, 50, 255))
    # plank seams across the board
    for fy in (756, 800, 844):
        draw.arc(bbox(board_cx - board_rx + 30, fy - 46,
                      board_cx + board_rx - 30, fy + 46),
                 start=18, end=162, fill=(96, 58, 30, 255), width=sc(3))

    # ---- bottom bun ----
    draw.rounded_rectangle(bbox(268, 668, 756, 742), radius=sc(34),
                           fill=(214, 148, 52, 255))
    img = shade(img, lambda d: d.rounded_rectangle(
        bbox(268, 700, 756, 742), radius=sc(30), fill=(150, 88, 26, 110)))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(bbox(268, 668, 756, 692), radius=sc(16),
                           fill=(238, 178, 84, 255))

    # ---- beef patty: dark, grilled ----
    draw.rounded_rectangle(bbox(248, 606, 776, 690), radius=sc(30),
                           fill=(84, 48, 26, 255))
    img = shade(img, lambda d: (
        d.rounded_rectangle(bbox(248, 606, 776, 640), radius=sc(26),
                            fill=(122, 74, 38, 120)),
        d.rounded_rectangle(bbox(248, 656, 776, 690), radius=sc(26),
                            fill=(40, 20, 10, 130)),
    ))
    draw = ImageDraw.Draw(img)
    # char marks
    for x0 in (330, 430, 540, 640):
        draw.line([sc(x0), sc(624), sc(x0 + 24), sc(656)],
                  fill=(52, 28, 14, 255), width=sc(6))

    # ---- melted cheese: one sheet, wavy lower edge, three soft bumps ----
    top = wavy_band_points(258, 766, 560, 4, 3, phase=0.4)
    bottom = []
    x = 766
    while x >= 258:
        t = (x - 258) / 508.0
        # three broad lobes + fine ripple, never separate drips
        y = 606 + 10 * math.sin(2 * math.pi * 1.5 * t + 0.6) \
            + 16 * math.exp(-((t - 0.28) ** 2) / 0.012) \
            + 20 * math.exp(-((t - 0.55) ** 2) / 0.010) \
            + 16 * math.exp(-((t - 0.80) ** 2) / 0.012)
        bottom.append((sc(x), sc(y)))
        x -= 8
    cheese = [(sc(258), sc(560))] + top + [(sc(766), sc(560))] + bottom
    draw.polygon(cheese, fill=(244, 140, 24, 255))
    img = shade(img, lambda d: d.polygon(
        [(sc(258), sc(596))] + wavy_band_points(258, 766, 596, 4, 3, phase=0.4)
        + [(sc(766), sc(596))] + bottom, fill=(196, 96, 8, 90)))
    draw = ImageDraw.Draw(img)
    draw.line([sc(258), sc(560)] + [p for p in top],
              fill=(255, 186, 92, 255), width=sc(4))

    # ---- tomato slice: red band peeking out at the sides ----
    draw.rounded_rectangle(bbox(262, 522, 762, 568), radius=sc(20),
                           fill=(198, 44, 32, 255))
    draw.rounded_rectangle(bbox(262, 522, 762, 542), radius=sc(14),
                           fill=(226, 74, 52, 255))
    img = shade(img, lambda d: d.rounded_rectangle(
        bbox(262, 550, 762, 568), radius=sc(12), fill=(140, 24, 18, 110)))
    draw = ImageDraw.Draw(img)

    # ---- lettuce: wavy band plus overlapping leaves of varied sizes ----
    lettuce_top = wavy_band_points(252, 772, 474, 9, 5, phase=1.1)
    lettuce_bot = wavy_band_points(772, 252, 516, 11, 5, phase=0.2)
    draw.polygon([(sc(252), sc(474))] + lettuce_top + [(sc(772), sc(474))]
                 + lettuce_bot, fill=(74, 138, 44, 255))
    for (lx, ly, ll, lw, la) in (
            (330, 516, 92, 46, -24), (430, 522, 110, 54, 8),
            (540, 518, 96, 48, -8), (650, 520, 104, 50, 18),
            (716, 510, 78, 40, -32)):
        leaf(draw, lx, ly, ll, lw, la, (96, 168, 58, 255))
    img = shade(img, lambda d: d.polygon(
        [(sc(252), sc(504))] + wavy_band_points(252, 772, 504, 9, 5, phase=1.1)
        + [(sc(772), sc(504))] + wavy_band_points(772, 252, 516, 11, 5, phase=0.2),
        fill=(40, 92, 24, 90)))
    draw = ImageDraw.Draw(img)

    # ---- top bun: tall dome with a flat bottom (pieslice, not a disc) ----
    draw.pieslice(bbox(252, 296, 772, 624), start=180, end=360,
                  fill=(222, 158, 58, 255))
    draw.rounded_rectangle(bbox(252, 438, 772, 482), radius=sc(18),
                           fill=(222, 158, 58, 255))
    img = shade(img, lambda d: (
        d.ellipse(bbox(340, 296, 684, 436), fill=(246, 196, 104, 70)),
        d.rounded_rectangle(bbox(252, 440, 772, 482), radius=sc(18),
                            fill=(146, 86, 24, 110)),
    ), blur=14)
    draw = ImageDraw.Draw(img)
    # crust edge along the dome's curve
    draw.arc(bbox(252, 296, 772, 624), start=195, end=345,
             fill=(238, 184, 92, 255), width=sc(5))

    # ---- sesame seeds on the dome (~15), hand-placed ----
    seeds = [
        (380, 350, -18), (460, 332, 12), (540, 326, -6), (620, 340, 20),
        (350, 388, 8), (440, 372, -14), (520, 362, 4), (600, 372, -20),
        (680, 392, 10), (400, 420, 16), (480, 408, -10), (560, 404, 14),
        (640, 418, -6), (450, 442, 6), (590, 440, -12),
    ]
    for (sx, sy, ang) in seeds:
        a = math.radians(ang)
        ca, sa = math.cos(a), math.sin(a)
        pts = []
        for k in range(17):
            th = 2 * math.pi * k / 16
            px = sx + 11 * math.cos(th) * ca - 7 * math.sin(th) * sa
            py = sy + 11 * math.cos(th) * sa + 7 * math.sin(th) * ca
            pts.append((sc(px), sc(py)))
        draw.polygon(pts, fill=(250, 226, 168, 255))
        draw.ellipse(bbox(sx - 3, sy - 4, sx + 3, sy + 1),
                     fill=(255, 244, 208, 255))

    # ---- board garnish: stray sesame + two herb leaves ----
    for (gx, gy, ga) in ((330, 872, 20), (700, 868, -14), (742, 836, 30)):
        a = math.radians(ga)
        ca, sa = math.cos(a), math.sin(a)
        pts = []
        for k in range(17):
            th = 2 * math.pi * k / 16
            px = gx + 9 * math.cos(th) * ca - 5.5 * math.sin(th) * sa
            py = gy + 9 * math.cos(th) * sa + 5.5 * math.sin(th) * ca
            pts.append((sc(px), sc(py)))
        draw.polygon(pts, fill=(240, 210, 150, 255))
    leaf(draw, 268, 836, 62, 26, -38, (52, 116, 44, 255))
    leaf(draw, 760, 884, 56, 24, 24, (60, 128, 48, 255))

    # ---- vignette: per-pixel distance mask, centre clear, corners dim ----
    small = 256
    mask = Image.new("L", (small, small))
    vals = []
    for yy in range(small):
        for xx in range(small):
            dx = (xx - small / 2) / (small / 2)
            dy = (yy - small / 2) / (small / 2)
            dist = math.sqrt(dx * dx + dy * dy)
            t = max(0.0, min(1.0, (dist - 0.62) / 0.55))
            vals.append(int(96 * t ** 1.6))
    mask.putdata(vals)
    mask = mask.resize((W, W), Image.LANCZOS)
    dark = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    dark.putalpha(mask)
    img = Image.alpha_composite(img, dark)

    # ---- downscale and save ----
    final = img.convert("RGB").resize((1024, 1024), Image.LANCZOS)
    final.save(OUT, "PNG")


if __name__ == "__main__":
    main()
