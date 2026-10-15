# -*- coding: utf-8 -*-
"""
포카 (Poka) — HelloKSlang's mascot: a little cream photocard with a washi-tape
fringe, a brass inner frame and a heart lightstick. Original character, drawn
with plain shapes so it stays on-brand (pokku palette) and scales cleanly.

    from mascot import poka
    img = poka("happy")                       # RGBA, transparent background
    img = poka("excited", arm_l=-70, arm_r=-110, stick_tilt=20, size=0.6)

Expressions: happy, think, excited, wink, wow
Arms are angles in degrees (0 = pointing right, 90 = down, -90 = up).
The right hand always holds the heart lightstick.
"""
import math
import os
import sys

from PIL import Image, ImageDraw

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import generate_instagram_cards as g  # noqa: E402

INK = (31, 20, 24)
EDGE = (248, 241, 227)
CREAM = (242, 233, 216)
BLUSH = (255, 150, 196)
SS = 2           # supersampling
BASE = 520       # canvas size at size=1.0 (before supersampling)


def _limb(d, x0, y0, x1, y1, s):
    d.line([(x0, y0), (x1, y1)], fill=EDGE, width=int(17 * s))
    d.line([(x0, y0), (x1, y1)], fill=INK, width=int(9 * s))


def _hand(d, x, y, s):
    d.ellipse([x - 14 * s, y - 14 * s, x + 14 * s, y + 14 * s], fill=EDGE, outline=INK, width=int(4 * s))


def _heart(d, cx, cy, k, fill):
    pts = []
    for t in range(0, 360, 6):
        a = math.radians(t)
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((cx + x * k, cy - y * k))
    d.polygon(pts, fill=fill, outline=INK, width=max(1, int(k * 1.2)))


def _face(d, cx, cy, s, expr):
    blush_y = cy + 24 * s
    for dx in (-1, 1):
        bx = cx + dx * 84 * s
        d.ellipse([bx - 22 * s, blush_y - 10 * s, bx + 22 * s, blush_y + 10 * s], fill=BLUSH)

    def eye(ex, look_x=0, look_y=0):
        d.ellipse([ex - 14 * s, cy - 20 * s, ex + 14 * s, cy + 20 * s], fill=INK)
        d.ellipse([ex - 6 * s + look_x, cy - 14 * s + look_y, ex + 2 * s + look_x, cy - 4 * s + look_y],
                  fill=(255, 255, 255))

    def happy_arc(ex):  # ^ ^ closed eyes
        d.arc([ex - 18 * s, cy - 12 * s, ex + 18 * s, cy + 22 * s], 200, 340, fill=INK, width=int(7 * s))

    lx, rx = cx - 46 * s, cx + 46 * s
    if expr in ("happy", "wow"):
        eye(lx); eye(rx)
    elif expr == "think":
        eye(lx, 4 * s, -4 * s); eye(rx, 4 * s, -4 * s)
    elif expr == "excited":
        happy_arc(lx); happy_arc(rx)
    elif expr == "wink":
        eye(lx); happy_arc(rx)

    my = cy + 26 * s
    if expr == "excited":
        d.chord([cx - 22 * s, my - 10 * s, cx + 22 * s, my + 26 * s], 0, 180, fill=INK)
        d.chord([cx - 12 * s, my + 6 * s, cx + 12 * s, my + 22 * s], 0, 180, fill=g.POP_PINK)
    elif expr == "wow":
        d.ellipse([cx - 11 * s, my - 6 * s, cx + 11 * s, my + 20 * s], fill=INK)
    elif expr == "think":
        d.line([(cx - 14 * s, my + 6 * s), (cx + 14 * s, my + 2 * s)], fill=INK, width=int(5 * s))
    else:  # ω mouth
        m = [(cx - 18 * s, my - 4 * s), (cx - 9 * s, my + 6 * s), (cx, my - 2 * s),
             (cx + 9 * s, my + 6 * s), (cx + 18 * s, my - 4 * s)]
        d.line(m, fill=INK, width=int(5 * s), joint="curve")


def poka(expr="happy", arm_l=135, arm_r=-40, stick_tilt=0, size=1.0, lean=0.0):
    s = SS * size
    W = H = int(BASE * s)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, H / 2 + 10 * s
    bw, bh = 200 * s, 260 * s
    top, bottom = cy - bh / 2, cy + bh / 2

    # legs
    for dx in (-44, 44):
        x = cx + dx * s
        _limb(d, x, bottom - 10 * s, x, bottom + 38 * s, s)
        d.ellipse([x - 28 * s, bottom + 24 * s, x + 24 * s, bottom + 54 * s], fill=EDGE)
        d.ellipse([x - 24 * s, bottom + 28 * s, x + 20 * s, bottom + 50 * s], fill=INK)

    # arms
    arm_len = 70 * s
    shoulder_y = cy + 30 * s
    lsx, rsx = cx - bw / 2 + 4 * s, cx + bw / 2 - 4 * s
    la, ra = math.radians(arm_l), math.radians(arm_r)
    lhx, lhy = lsx + math.cos(la) * arm_len, shoulder_y + math.sin(la) * arm_len
    rhx, rhy = rsx + math.cos(ra) * arm_len, shoulder_y + math.sin(ra) * arm_len
    _limb(d, lsx, shoulder_y, lhx, lhy, s)
    _limb(d, rsx, shoulder_y, rhx, rhy, s)

    # lightstick in right hand
    t = math.radians(-90 + stick_tilt)
    sx2, sy2 = rhx + math.cos(t) * 62 * s, rhy + math.sin(t) * 62 * s
    d.line([(rhx - math.cos(t) * 14 * s, rhy - math.sin(t) * 14 * s), (sx2, sy2)], fill=EDGE, width=int(22 * s))
    d.line([(rhx - math.cos(t) * 14 * s, rhy - math.sin(t) * 14 * s), (sx2, sy2)], fill=g.GARNET, width=int(14 * s))
    _heart(d, sx2 + math.cos(t) * 26 * s, sy2 + math.sin(t) * 26 * s, 3.2 * s, g.POP_PINK)
    _hand(d, rhx, rhy, s)
    _hand(d, lhx, lhy, s)

    # body (photocard)
    d.rounded_rectangle([cx - bw / 2 - 7 * s, top - 7 * s, cx + bw / 2 + 7 * s, bottom + 7 * s],
                        radius=36 * s, fill=EDGE)
    d.rounded_rectangle([cx - bw / 2, top, cx + bw / 2, bottom], radius=30 * s, fill=CREAM,
                        outline=INK, width=int(5 * s))
    d.rounded_rectangle([cx - bw / 2 + 15 * s, top + 15 * s, cx + bw / 2 - 15 * s, bottom - 15 * s],
                        radius=20 * s, outline=g.BRASS, width=int(4 * s))
    _face(d, cx, cy - 6 * s, s, expr)

    # washi-tape fringe
    tp = g.tape(int(140 * size * SS), int(42 * size * SS), "lilac").rotate(-8, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(tp, (int(cx - tp.width / 2 + 6 * s), int(top - tp.height / 2 + 4 * s)))

    if expr == "think":
        d = ImageDraw.Draw(img)
        d.text((cx - bw / 2 - 10 * s, top - 18 * s), "?", font=g.load_font("bricolage_bold", int(78 * s)),
               fill=g.POP_LEMON, anchor="mm", stroke_width=int(4 * s), stroke_fill=INK)

    if lean:
        img = img.rotate(lean, resample=Image.BICUBIC)
    return img.resize((int(W / SS), int(H / SS)), Image.LANCZOS)


if __name__ == "__main__":
    # character sheet
    poses = [
        ("happy", dict()),
        ("think", dict(arm_l=-120, arm_r=-30, stick_tilt=-15)),
        ("excited", dict(arm_l=-130, arm_r=-60, stick_tilt=25, lean=-4)),
        ("wink", dict(arm_l=-150, arm_r=-35)),
        ("wow", dict(arm_l=170, arm_r=10, stick_tilt=-10)),
    ]
    sheet = Image.new("RGB", (len(poses) * 420, 540), g.CHARCOAL_BACKDROP)
    dd = ImageDraw.Draw(sheet)
    for i, (e, kw) in enumerate(poses):
        im = poka(e, size=0.8, **kw)
        sheet.paste(im, (i * 420 + (420 - im.width) // 2, 20), im)
        dd.text((i * 420 + 210, 510), e, font=g.load_font("mono_bold", 30), fill=g.CREAM_INK, anchor="ms")
    out = sys.argv[1] if len(sys.argv) > 1 else "poka_sheet.png"
    sheet.save(out)
    print(out)
