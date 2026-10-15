# -*- coding: utf-8 -*-
"""
Instagram Reel (9:16 MP4) for one word, built from the same pokku photocards
as generate_instagram_cards.py. Silent by design — trending audio is added by
hand in the Instagram app (API music needs a FB-Page-linked business account).

Usage:
    python3 generate_instagram_reel.py "입덕"
Output: assets/instagram/<date>-<slug>/reel.mp4

Needs ffmpeg on PATH. Manual tool, not part of the site build.
"""
import argparse
import math
import os
import subprocess
import sys
from datetime import date

from PIL import Image, ImageDraw

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import generate_instagram_cards as g  # noqa: E402

RW, RH = 1080, 1920
FPS = 30
CX, CY = RW // 2, 930          # card center — keeps the card clear of Reels UI (top ~220px, bottom ~380px)
DY = CY - (g.CARD_Y + g.CARD_H // 2)   # shift from carousel coords to reel coords


def ease_out_cubic(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def ease_out_back(t, s=1.9):
    t = max(0.0, min(1.0, t))
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def progress(f, start, length):
    return (f - start) / float(length)


def pop_scale(f, start, length=8):
    """0 → overshoot → 1, like the site's --ease-pop sticker entrance."""
    if f < start:
        return 0.0
    return max(0.01, ease_out_back(progress(f, start, length), 2.6))


def scaled(layer, sx, sy=None):
    sy = sx if sy is None else sy
    w, h = max(1, int(layer.width * sx)), max(1, int(layer.height * sy))
    return layer.resize((w, h), Image.BICUBIC)


def backdrop(f):
    img = Image.new("RGBA", (RW, RH), g.CHARCOAL_BACKDROP + (255,))
    d = ImageDraw.Draw(img)
    d.text((CX, 300), "K-SLANG OF THE DAY", font=g.load_font("mono_bold", 30),
           fill=g.CREAM_INK_SOFT, anchor="ms")
    # twinkling sparkles on the backdrop only (never over the card text)
    for i, (x, y, size, color) in enumerate([
        (110, 330, 46, g.POP_LEMON), (980, 320, 34, g.POP_MINT),
        (90, 1560, 38, g.POP_PINK), (990, 1580, 48, g.POP_LEMON),
    ]):
        k = 0.75 + 0.25 * math.sin((f / FPS) * 3.2 + i * 1.7)
        g.sparkle(img, x, y, size * k, color)
    return img


def deco_layers(word):
    """Pre-render tapes/stickers once (rotation baked in)."""
    rot = lambda im, a: im.rotate(a, expand=True, resample=Image.BICUBIC)  # noqa: E731
    return {
        "tape_lilac": rot(g.tape(240, 60, "lilac"), -8),
        "tape_pink": rot(g.tape(200, 54, "pink"), 30),
        "tape_mint": rot(g.tape(230, 58, "mint"), -4),
        "heart": rot(g.sticker("♥", g.POP_PINK, "noto_kr_bold", 54, circle=True), 12),
        "what": rot(g.sticker("WHAT?!", g.POP_LEMON, "bricolage_bold", 42), -6),
        "star": rot(g.sticker("✦", g.POP_LILAC, "noto_kr_bold", 50, circle=True), -10),
        "kk": rot(g.sticker("ㅋㅋ", g.POP_MINT, "black_han_sans", 46, circle=True), 9),
        "follow": rot(g.sticker("Follow ♥", g.POP_PINK, "noto_kr_bold", 40), -3),
    }


def put(canvas, layer, x, y, scale=1.0, shadow=False):
    if scale <= 0.02:
        return
    g.place(canvas, scaled(layer, scale) if scale != 1 else layer, x, y, 0, shadow)


def render_frames(word):
    hook = [g.build_hook_card(word, stage=s) for s in (1, 2, 3)]
    meaning = g.build_meaning_card(word)
    usage = g.build_usage_card(word)
    cta = g.build_cta_card()
    deco = deco_layers(word)

    # card-relative anchor points (carousel coords shifted by DY)
    L, T, R, B = g.CARD_X, g.CARD_Y + DY, g.CARD_X + g.CARD_W, g.CARD_Y + g.CARD_H + DY

    # timeline (frames)
    S2, S3, S4, END = 105, 200, 330, 400
    FLIP = 6  # frames per half-flip

    for f in range(END):
        canvas = backdrop(f)

        if f < S2 + FLIP:
            # ---- scene 1: hook card drops in, word stamps, question appears
            card = hook[0] if f < 24 else hook[1] if f < 54 else hook[2]
            t = ease_out_back(progress(f, 0, 16), 1.4)
            angle = 8 + (-1.6 - 8) * t
            yoff = (1 - ease_out_cubic(progress(f, 0, 16))) * 700
            sc = 0.88 + 0.12 * t
            if 24 <= f < 30:   # stamp bump when the word lands
                sc *= 1 + 0.035 * (1 - progress(f, 24, 6))
            sx = 1.0
            if f >= S2:        # first half of flip
                sx = 1 - ease_out_cubic(progress(f, S2, FLIP))
            layer = scaled(card.rotate(angle, resample=Image.BICUBIC, expand=True), sc * max(sx, 0.02), sc)
            g.place(canvas, layer, CX, CY + yoff, 0, shadow=True)
            if f < S2:
                if f >= 10:
                    put(canvas, deco["tape_lilac"], CX, T + 4, pop_scale(f, 10, 6))
                put(canvas, deco["heart"], R - 40, T + 150, pop_scale(f, 30))
                put(canvas, deco["what"], R - 150, B - 20, pop_scale(f, 60))

        elif f < S3 + FLIP:
            # ---- scene 2: meaning
            sx = ease_out_cubic(progress(f, S2 + FLIP, FLIP))
            if f >= S3:
                sx = 1 - ease_out_cubic(progress(f, S3, FLIP))
            g.place(canvas, scaled(meaning, max(sx, 0.02), 1), CX, CY, 0, shadow=True)
            if S2 + 2 * FLIP <= f < S3:
                put(canvas, deco["tape_pink"], L + 30, T + 20)
                put(canvas, deco["tape_pink"], R - 30, B - 20)
                put(canvas, deco["star"], R - 50, T + 40, pop_scale(f, S2 + 2 * FLIP + 4))

        elif f < S4 + FLIP:
            # ---- scene 3: real usage
            sx = ease_out_cubic(progress(f, S3 + FLIP, FLIP))
            if f >= S4:
                sx = 1 - ease_out_cubic(progress(f, S4, FLIP))
            g.place(canvas, scaled(usage, max(sx, 0.02), 1), CX, CY, 0, shadow=True)
            if S3 + 2 * FLIP <= f < S4:
                put(canvas, deco["tape_mint"], CX, T + 2)
                put(canvas, deco["kk"], R - 46, B - 50, pop_scale(f, S3 + 2 * FLIP + 4))

        else:
            # ---- scene 4: save / follow
            sx = ease_out_cubic(progress(f, S4 + FLIP, FLIP))
            layer = cta.rotate(2.2, resample=Image.BICUBIC, expand=True)
            g.place(canvas, scaled(layer, max(sx, 0.02), 1), CX, 860, 0, shadow=True)
            if f >= S4 + 2 * FLIP:
                d = ImageDraw.Draw(canvas)
                a = int(255 * ease_out_cubic(progress(f, S4 + 2 * FLIP, 10)))
                over = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
                od = ImageDraw.Draw(over)
                od.text((CX, 1360), "hellokslang.com", font=g.load_font("bricolage_bold", 56),
                        fill=g.CREAM_INK + (a,), anchor="ms")
                od.text((CX, 1420), "NEW SLANG EVERY WEEK · EN / ES / 中文 / 日本語",
                        font=g.load_font("noto_kr_bold", 26), fill=g.CREAM_INK_SOFT + (a,), anchor="ms")
                canvas.alpha_composite(over)
                put(canvas, deco["follow"], CX, 1510, pop_scale(f, S4 + 2 * FLIP + 8))

        yield canvas.convert("RGB")


def make_reel(kr, date_str=None):
    word = g.find_word(kr)
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
    for frame in render_frames(word):
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("ffmpeg failed")
    return out


def main():
    p = argparse.ArgumentParser(description="Generate a 9:16 Instagram Reel MP4 for one word.")
    p.add_argument("word", help='Korean word exactly as in build_kslang_db.py, e.g. "입덕"')
    args = p.parse_args()
    try:
        print(make_reel(args.word))
    except g.WordNotFoundError as e:
        sys.exit(f"Error: {e}")


if __name__ == "__main__":
    main()
