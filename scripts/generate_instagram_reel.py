# -*- coding: utf-8 -*-
"""
Instagram Reel (9:16 MP4) — "Guess the meaning" quiz format.

  0.0s  giant foil word + "GUESS THE MEANING" headline (no empty first frame)
  0.3s  three answer stickers pop in (A/B/C)
  1.0s  3-2-1 countdown
  4.0s  reveal: wrong answers fade, right one turns garnet
  5.5s  the dictionary card (EN + ES meaning)
  8.3s  "Got it right? Comment!" + follow

Wrong answers are the short English titles of REAL related words from the DB
(DETAILS["similar"], Verified only), so the quiz never invents meanings.
Silent by design — trending audio is added by hand in the Instagram app.

Usage:
    python3 generate_instagram_reel.py "입덕"
    python3 generate_instagram_reel.py "입덕" --distractors 탈덕 휴덕
Output: assets/instagram/<date>-<slug>/reel.mp4   (needs ffmpeg)
"""
import argparse
import math
import os
import random
import subprocess
import sys
from datetime import date

from PIL import Image, ImageDraw

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import generate_instagram_cards as g  # noqa: E402
from mascot import poka  # noqa: E402

db = g.db
RW, RH = 1080, 1920
FPS = 30
CX = RW // 2

# timeline (frames)
T_OPTS = 9          # first answer sticker
T_COUNT = 30        # countdown starts
T_REVEAL = 120
T_CARD = 165
T_CTA = 250
T_END = 300

LETTER_COLORS = [g.POP_LEMON, g.POP_LILAC, g.POP_MINT]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def clamp(t):
    return max(0.0, min(1.0, t))


def ease_out_cubic(t):
    return 1 - (1 - clamp(t)) ** 3


def ease_in_cubic(t):
    return clamp(t) ** 3


def ease_out_back(t, s=1.9):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def prog(f, start, length):
    return (f - start) / float(length)


def pop(f, start, length=8):
    return 0.0 if f < start else max(0.01, ease_out_back(prog(f, start, length), 2.6))


def scaled(layer, s):
    if abs(s - 1) < 1e-3:
        return layer
    return layer.resize((max(1, int(layer.width * s)), max(1, int(layer.height * s))), Image.BICUBIC)


def with_alpha(layer, a):
    if a >= 0.999:
        return layer
    out = layer.copy()
    out.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
    return out


def put(canvas, layer, x, y, scale=1.0, alpha=1.0, shadow=False):
    if scale <= 0.02 or alpha <= 0.01:
        return
    g.place(canvas, with_alpha(scaled(layer, scale), alpha), x, y, 0, shadow)


def text_layer(text, font, fill, stroke=0, stroke_fill=None):
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    b = probe.textbbox((0, 0), text, font=font, stroke_width=stroke)
    img = Image.new("RGBA", (b[2] - b[0] + 8, b[3] - b[1] + 8), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((4 - b[0], 4 - b[1]), text, font=font, fill=fill,
                             stroke_width=stroke, stroke_fill=stroke_fill)
    return img


def check_mark(d, cx, cy, r, fill, width=10):
    d.line([(cx - r * 0.55, cy), (cx - r * 0.12, cy + r * 0.42), (cx + r * 0.6, cy - r * 0.45)],
           fill=fill, width=width, joint="curve")


# ---------------------------------------------------------------------------
# quiz data
# ---------------------------------------------------------------------------
def pick_distractors(word, override=None):
    if override:
        return [g.find_word(k) for k in override]
    verified = []
    for kr in (db.DETAILS.get(word["kr"], {}).get("similar") or []):
        try:
            w = g.find_word(kr)
        except g.WordNotFoundError:
            continue
        if w["status"].startswith("Verified") and w["en_short"].lower() != word["en_short"].lower():
            verified.append(w)
    if len(verified) < 2:  # fall back to same category
        for cat_kr, cat_en, terms in db.CATEGORIES:
            if cat_en != word["cat_en"]:
                continue
            for t in terms:
                if t[0] != word["kr"] and t[-1].startswith("Verified"):
                    verified.append(g.find_word(t[0]))
    rng = random.Random(word["kr"])
    rng.shuffle(verified)
    return verified[:2]


# ---------------------------------------------------------------------------
# static layers
# ---------------------------------------------------------------------------
def option_pill(letter, text, color, state="normal"):
    """state: normal | right | wrong"""
    w, h = 880, 150
    img = Image.new("RGBA", (w + 14, h + 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    face = g.GARNET if state == "right" else g.CARDSTOCK
    ink = g.CAPTION_INK if state == "right" else g.CARD_INK
    d.rounded_rectangle([0, 0, w + 13, h + 13], radius=40, fill=g.STICKER_EDGE)
    d.rounded_rectangle([7, 7, w + 6, h + 6], radius=34, fill=face)
    # letter badge
    bx, by, br = 7 + 82, 7 + h // 2, 50
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=color, outline=g.STICKER_INK, width=3)
    if state == "right":
        check_mark(d, bx, by, br, g.STICKER_INK, 11)
    else:
        d.text((bx, by + 2), letter, font=g.load_font("black_han_sans", 54), fill=g.STICKER_INK, anchor="mm")
    font = g.load_font("hanken_bold", 50)
    tw = g.text_w(d, text, font)
    if tw > w - 200:
        font = g.load_font("hanken_bold", int(50 * (w - 200) / tw))
    d.text((7 + 170, by + 2), text, font=font, fill=ink, anchor="lm")
    return img


def countdown_sticker(n):
    return g.sticker(str(n), g.POP_PINK, "black_han_sans", 96, pad=(46, 0), circle=True)


def build_layers(word, distractors):
    L = {}
    L["headline"] = text_layer("GUESS THE MEANING", g.load_font("bricolage_bold", 78), g.CREAM_INK)
    L["sub"] = text_layer("3 seconds. Go!", g.load_font("mono_bold", 34), g.CREAM_INK_SOFT)
    L["it_means"] = text_layer("IT MEANS…", g.load_font("bricolage_bold", 78), g.CREAM_INK)
    L["got_it"] = text_layer("Got it right?", g.load_font("bricolage_bold", 92), g.CREAM_INK)

    term_font = g.load_font("black_han_sans", 270 if len(word["kr"]) <= 3 else 200)
    foil = g.draw_foil_gradient_text(word["kr"], term_font)
    if foil.width > RW - 560:  # leave room for 포카 on the left and the countdown on the right
        foil = foil.resize((RW - 560, int(foil.height * (RW - 560) / foil.width)), Image.LANCZOS)
    L["term"] = foil
    L["rom"] = text_layer(f"/{word['rom']}/", g.load_font("mono_italic", 42), g.CREAM_INK_SOFT)

    answers = [(word["en_short"], True)] + [(w["en_short"], False) for w in distractors]
    random.Random(word["kr"] + "pos").shuffle(answers)
    L["answers"] = answers
    L["opt"] = []
    for i, (text, right) in enumerate(answers):
        letter = "ABC"[i]
        L["opt"].append({
            "normal": option_pill(letter, text, LETTER_COLORS[i]),
            "right": option_pill(letter, text, g.POP_LEMON, "right"),
            "right_flag": right,
            "angle": (-1.2, 0.9, -0.7)[i],
        })
    for k in ("normal", "right"):
        for o in L["opt"]:
            o[k] = o[k].rotate(o["angle"], expand=True, resample=Image.BICUBIC)
    L["count"] = {n: countdown_sticker(n) for n in (3, 2, 1)}
    L["card"] = scaled(g.build_meaning_card(word), 0.9)
    L["tape"] = g.tape(240, 60, "pink").rotate(-6, expand=True, resample=Image.BICUBIC)
    L["follow"] = g.sticker("Follow for a new word every week", g.POP_LEMON, "bricolage_bold", 38).rotate(
        -2, expand=True, resample=Image.BICUBIC)
    L["comment"] = text_layer("Tell us in the comments", g.load_font("bricolage_bold", 52), g.POP_PINK)
    L["site"] = text_layer("hellokslang.com", g.load_font("bricolage_bold", 56), g.CREAM_INK)
    return L


def backdrop(f):
    img = Image.new("RGBA", (RW, RH), g.CHARCOAL_BACKDROP + (255,))
    for i, (x, y, size, color) in enumerate([
        (90, 250, 46, g.POP_LEMON), (995, 270, 34, g.POP_MINT),
        (80, 1610, 38, g.POP_PINK), (1000, 1620, 50, g.POP_LEMON),
    ]):
        k = 0.75 + 0.25 * math.sin((f / FPS) * 3.4 + i * 1.7)
        g.sparkle(img, x, y, size * k, color)
    d = ImageDraw.Draw(img)
    d.text((CX, 1700), "@HELLOKSLANG", font=g.load_font("mono_bold", 26), fill=g.CREAM_INK_SOFT, anchor="ms")
    return img


def mascot(c, f):
    """포카's acting: happy hello → thinking during countdown → cheering at reveal."""
    t = f / FPS
    if f < T_COUNT:
        img = poka("happy", arm_l=-150 + 25 * math.sin(t * 14), arm_r=-40, size=0.68)
        y = 650 + 6 * math.sin(t * 6)
        sc = pop(f, 4, 9)
    elif f < T_REVEAL:
        img = poka("think", arm_l=-120, arm_r=-30, stick_tilt=-15 + 8 * math.sin(t * 5), size=0.68,
                   lean=4 * math.sin(t * 2.5))
        y, sc = 650, 1
    else:
        k = (f - T_REVEAL) / FPS
        up = abs(math.sin(k * 9)) * 50 * max(0.0, 1 - k / 1.4)
        img = poka("excited", arm_l=-130 + 20 * math.sin(k * 18), arm_r=-60, stick_tilt=25 * math.sin(k * 14),
                   size=0.68, lean=-4)
        y, sc = 650 - up, 1
    return img, y, sc


# ---------------------------------------------------------------------------
# frames
# ---------------------------------------------------------------------------
OPT_Y = [1010, 1185, 1360]


def render_frames(word, distractors):
    L = build_layers(word, distractors)

    for f in range(T_END):
        c = backdrop(f)

        # ---- quiz part (slides up & out when the card arrives)
        if f < T_CARD + 12:
            out = ease_in_cubic(prog(f, T_CARD, 12)) if f >= T_CARD else 0.0
            dy = -out * 1200

            # headline
            put(c, L["headline"], CX, 330 + dy - (1 - ease_out_cubic(prog(f, 0, 8))) * 40)
            if f < T_REVEAL:
                put(c, L["sub"], CX, 410 + dy, alpha=ease_out_cubic(prog(f, 4, 8)))

            # giant word: starts oversized (fills the first frame), settles
            s = 1.45 - 0.45 * ease_out_back(prog(f, 0, 12), 1.6)
            if T_REVEAL <= f < T_REVEAL + 8:
                s *= 1 + 0.06 * (1 - prog(f, T_REVEAL, 8))
            put(c, L["term"], CX + 95, 640 + dy, s)
            put(c, L["rom"], CX + 95, 820 + dy, alpha=ease_out_cubic(prog(f, 6, 8)))

            # 포카
            m, my, msc = mascot(c, f)
            put(c, m, 170, my + dy, msc)

            # countdown
            if T_COUNT <= f < T_REVEAL:
                n = 3 - (f - T_COUNT) // 30
                put(c, L["count"][n], 985, 470 + dy, pop(f, T_COUNT + (3 - n) * 30, 7))

            # answers
            for i, o in enumerate(L["opt"]):
                y = OPT_Y[i] + dy
                sc = pop(f, T_OPTS + i * 5, 8)
                if f < T_REVEAL:
                    put(c, o["normal"], CX, y, sc, shadow=True)
                elif o["right_flag"]:
                    bump = 1 + 0.08 * (1 - ease_out_cubic(prog(f, T_REVEAL, 10)))
                    put(c, o["right"], CX, y, bump, shadow=True)
                else:
                    a = 1 - 0.7 * ease_out_cubic(prog(f, T_REVEAL, 8))
                    put(c, o["normal"], CX, y, 0.97, alpha=a)
                    if f >= T_REVEAL + 4:  # strike-through
                        d = ImageDraw.Draw(c)
                        k = ease_out_cubic(prog(f, T_REVEAL + 4, 6))
                        x0 = CX - 300
                        d.line([(x0, y), (x0 + 600 * k, y)], fill=g.CREAM_INK_SOFT, width=6)

            # sparkle burst around the right answer
            if T_REVEAL <= f < T_CARD:
                ri = [o["right_flag"] for o in L["opt"]].index(True)
                k = ease_out_cubic(prog(f, T_REVEAL, 14))
                for j in range(6):
                    ang = j * math.pi / 3 + 0.3
                    r = 120 + 360 * k
                    g.sparkle(c, CX + math.cos(ang) * r * 1.3, OPT_Y[ri] + dy + math.sin(ang) * r * 0.4,
                              44 * (1 - 0.6 * k), (g.POP_LEMON, g.POP_PINK, g.POP_MINT)[j % 3])

        # ---- dictionary card
        if T_CARD <= f < T_CTA + 10:
            inn = ease_out_cubic(prog(f, T_CARD + 4, 14))
            leave = ease_in_cubic(prog(f, T_CTA, 10)) if f >= T_CTA else 0.0
            y = 1020 + (1 - inn) * 1100 - leave * 1300
            put(c, L["it_means"], CX, 300 - leave * 1300, alpha=inn)
            put(c, L["card"], CX, y, shadow=True)
            if f >= T_CARD + 18:
                put(c, L["tape"], CX, y - L["card"].height / 2 + 6 - 0, pop(f, T_CARD + 18, 6))
                peek = poka("wink", arm_l=-150 + 20 * math.sin(f / FPS * 10), arm_r=-35, size=0.5)
                put(c, peek, 905, y + L["card"].height / 2 - 40, pop(f, T_CARD + 22, 9))

        # ---- CTA
        if f >= T_CTA:
            put(c, L["got_it"], CX, 470, pop(f, T_CTA + 6, 9))
            put(c, L["comment"], CX, 590, alpha=ease_out_cubic(prog(f, T_CTA + 12, 8)))
            t = f / FPS
            hi = poka("happy" if (f // 12) % 4 else "wink", arm_l=-150 + 30 * math.sin(t * 12), arm_r=-50,
                      stick_tilt=15 * math.sin(t * 8), size=0.9)
            put(c, hi, CX, 900 + 8 * math.sin(t * 6), pop(f, T_CTA + 2, 10))
            put(c, L["follow"], CX, 1210, pop(f, T_CTA + 18, 9))
            put(c, L["site"], CX, 1330, alpha=ease_out_cubic(prog(f, T_CTA + 22, 8)))

        yield c.convert("RGB")


def make_reel(kr, distractors=None, date_str=None):
    word = g.find_word(kr)
    dis = pick_distractors(word, distractors)
    if len(dis) < 2:
        sys.exit(f"Not enough Verified distractors for {kr}; pass --distractors")
    out_dir = g.output_dir(word, date_str or date.today().isoformat())
    out = os.path.join(out_dir, "reel.mp4")
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{RW}x{RH}", "-r", str(FPS), "-i", "-",
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", out,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for frame in render_frames(word, dis):
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("ffmpeg failed")
    return out, [w["kr"] for w in dis]


def main():
    p = argparse.ArgumentParser(description="Generate a 'guess the meaning' Instagram Reel MP4.")
    p.add_argument("word", help='Korean word exactly as in build_kslang_db.py, e.g. "입덕"')
    p.add_argument("--distractors", nargs=2, metavar="KR", help="two Verified words to use as wrong answers")
    args = p.parse_args()
    try:
        out, dis = make_reel(args.word, args.distractors)
    except g.WordNotFoundError as e:
        sys.exit(f"Error: {e}")
    print(out)
    print("wrong answers:", ", ".join(dis))


if __name__ == "__main__":
    main()
