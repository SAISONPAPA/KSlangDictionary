# -*- coding: utf-8 -*-
"""
Generates Instagram carousel/single-image PNG cards for @hellokslang from
the word data in build_kslang_db.py. Not part of the automated
GitHub Actions rebuild pipeline — this is a manual content tool.

Usage:
    python3 generate_instagram_cards.py --carousel "컴백"
    python3 generate_instagram_cards.py --new-word

See docs/superpowers/specs/2026-08-09-instagram-carousel-generator-design.md
for the full design.
"""
import argparse
import difflib
import os
import re
import sys
from datetime import date

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(SCRIPT_DIR, "..")
sys.path.insert(0, SCRIPT_DIR)
import build_kslang_db as db

# ---------------------------------------------------------------------------
# Canvas
# ---------------------------------------------------------------------------
W, H = 1080, 1350
INSET = 48
CONTENT_LEFT = INSET + 40
CONTENT_RIGHT = W - INSET - 40
CONTENT_WIDTH = CONTENT_RIGHT - CONTENT_LEFT

# ---------------------------------------------------------------------------
# Colors (verbatim from DESIGN.md)
# ---------------------------------------------------------------------------
CARDSTOCK = (242, 233, 216)
CARDSTOCK_HI = (248, 241, 227)
CARD_INK = (33, 27, 22)
CARD_INK_SOFT = (91, 82, 72)
GARNET = (178, 27, 62)
BRASS = (180, 146, 63)
BADGE_TEXT_BRASS = (122, 98, 36)
CAPTION_BLACK = (16, 14, 19)
CAPTION_INK = (253, 248, 238)
CAPTION_INK_SOFT = (184, 175, 159)
CHARCOAL_BACKDROP = (21, 18, 23)
CREAM_INK = (243, 236, 221)
CREAM_INK_SOFT = (167, 158, 146)
WHITE = (255, 255, 255)

FOIL_STOPS = [
    (110, 84, 25),   # #6E5419
    (201, 166, 76),  # #C9A64C
    (235, 208, 138), # #EBD08A
    (201, 166, 76),  # #C9A64C
    (122, 94, 30),   # #7A5E1E
]

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
FONT_DIR = os.path.join(REPO_ROOT, "assets", "fonts")
FONTS = {
    "black_han_sans": "BlackHanSans-Regular.ttf",
    "hanken_bold": "HankenGrotesk-Bold.ttf",
    "bricolage_bold": "BricolageGrotesque-Bold.ttf",
    "noto_kr_bold": "NotoSansKR-Bold.otf",
    "mono_bold": "JetBrainsMono-Bold.ttf",
    "mono_italic": "JetBrainsMono-Italic.ttf",
}


def load_font(name, size):
    filename = FONTS[name]
    path = os.path.join(FONT_DIR, filename)
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Missing font file: {path}\n"
            f"Download {filename} from Google Fonts and place it in "
            f"assets/fonts/ before running this script."
        )
    return ImageFont.truetype(path, size)


class WordNotFoundError(Exception):
    pass


def find_word(kr):
    for cat_kr, cat_en, terms in db.CATEGORIES:
        for row in terms:
            (w_kr, rom, en_short, meaning_en, meaning_es,
             ex_kr, ex_en, ex_es, where, status) = row
            if w_kr == kr:
                return {
                    "kr": w_kr, "rom": rom, "en_short": en_short,
                    "meaning_en": meaning_en, "meaning_es": meaning_es,
                    "ex_kr": ex_kr, "ex_en": ex_en, "ex_es": ex_es,
                    "where": where, "status": status,
                    "cat_kr": cat_kr, "cat_en": cat_en,
                }
    all_kr = [row[0] for _, _, terms in db.CATEGORIES for row in terms]
    close = difflib.get_close_matches(kr, all_kr, n=5)
    suggestion = f" Did you mean: {', '.join(close)}?" if close else ""
    raise WordNotFoundError(
        f'"{kr}" not found in build_kslang_db.py.{suggestion}'
    )


def slug_from_rom(rom):
    return re.sub(r"[^a-z0-9]+", "-", rom.lower()).strip("-")


def output_dir(word, date_str):
    dir_name = f"{date_str}-{slug_from_rom(word['rom'])}"
    path = os.path.join(REPO_ROOT, "assets", "instagram", dir_name)
    os.makedirs(path, exist_ok=True)
    return path


# ---------------------------------------------------------------------------
# Pokku (photocard-decorating) layer — mirrors assets/pokku.css.
# Pop colors are for stickers / tape / sparkles ONLY, never for body text.
# ---------------------------------------------------------------------------
POP_PINK = (255, 111, 174)
POP_LILAC = (185, 162, 255)
POP_MINT = (116, 227, 196)
POP_LEMON = (255, 225, 107)
STICKER_INK = (31, 20, 24)
STICKER_EDGE = (248, 241, 227)
TAPES = {
    "lilac": ((185, 162, 255, 199), (205, 188, 255, 199)),
    "pink": ((255, 111, 174, 184), (255, 150, 196, 184)),
    "mint": ((116, 227, 196, 191), (150, 236, 212, 191)),
}

# Photocard placed on the charcoal backdrop
CARD_X, CARD_Y = 70, 140
CARD_W, CARD_H = W - CARD_X * 2, 1110
PAD = 72  # inner text padding of the card
TEXT_W = CARD_W - PAD * 2


def is_hangul(ch):
    o = ord(ch)
    return 0xAC00 <= o <= 0xD7A3 or 0x3130 <= o <= 0x318F or 0x1100 <= o <= 0x11FF


def text_w(draw, text, font):
    b = draw.textbbox((0, 0), text, font=font)
    return b[2] - b[0]


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if text_w(draw, candidate, font) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _runs(text):
    """Split text into (is_hangul, chunk) runs. Pillow has no font fallback,
    so Hangul must be drawn in Noto Sans KR (CLAUDE.md bug #3)."""
    runs = []
    for ch in text:
        k = is_hangul(ch) if not ch.isspace() and ch not in "\"“”'.,()!?" else None
        if runs and (k is None or runs[-1][0] == k):
            runs[-1][1] += ch
        else:
            runs.append([k if k is not None else False, ch])
    return runs


def rich_width(draw, text, latin, korean):
    return sum(text_w(draw, c, korean if k else latin) for k, c in _runs(text))


def wrap_rich(draw, text, latin, korean, max_width):
    lines, current = [], ""
    for word in text.split():
        cand = f"{current} {word}".strip()
        if rich_width(draw, cand, latin, korean) <= max_width or not current:
            current = cand
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_rich(draw, xy, text, latin, korean, fill):
    x, y = xy
    for k, chunk in _runs(text):
        f = korean if k else latin
        draw.text((x, y), chunk, font=f, fill=fill, anchor="ls")
        x += text_w(draw, chunk, f)


def draw_foil_gradient_text(text, font):
    probe = Image.new("L", (10, 10), 0)
    probe_draw = ImageDraw.Draw(probe)
    bbox = probe_draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    pad = 6
    size = (tw + pad * 2, th + pad * 2)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).text((pad - bbox[0], pad - bbox[1]), text, font=font, fill=255)

    gradient = Image.new("RGB", size)
    grad_draw = ImageDraw.Draw(gradient)
    stops = FOIL_STOPS
    for x in range(size[0]):
        t = x / max(size[0] - 1, 1)
        seg = t * (len(stops) - 1)
        i = min(int(seg), len(stops) - 2)
        lt = seg - i
        c0, c1 = stops[i], stops[i + 1]
        grad_draw.line([(x, 0), (x, size[1])],
                       fill=tuple(int(c0[k] + (c1[k] - c0[k]) * lt) for k in range(3)))

    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(gradient, (0, 0), mask)
    return out


def backdrop(page=None):
    """Charcoal backdrop + tiny header line, like the binder page behind a card."""
    img = Image.new("RGBA", (W, H), CHARCOAL_BACKDROP + (255,))
    d = ImageDraw.Draw(img)
    f = load_font("mono_bold", 22)
    d.text((CARD_X + 6, 70), "@HELLOKSLANG", font=f, fill=CREAM_INK_SOFT, anchor="ls")
    if page:
        d.text((W - CARD_X - 6, 70), page, font=f, fill=CREAM_INK_SOFT, anchor="rs")
    return img


def new_card(cat_en=None):
    """Cream cardstock photocard (RGBA, rounded) with grain + brass frame."""
    card = Image.new("RGBA", (CARD_W, CARD_H), CARDSTOCK + (255,))
    hi = Image.new("RGBA", (CARD_W, CARD_H), CARDSTOCK_HI + (255,))
    m = Image.new("L", (CARD_W, CARD_H))
    md = ImageDraw.Draw(m)
    for y in range(CARD_H):
        t = 1 - abs((y / CARD_H) - 0.3)
        md.line([(0, y), (CARD_W, y)], fill=max(0, int(255 * t * 0.55)))
    card = Image.composite(hi, card, m)
    # cardstock grain
    noise = Image.effect_noise((CARD_W, CARD_H), 40).point(lambda v: max(0, v - 128) // 6)
    grain = Image.new("RGBA", (CARD_W, CARD_H), (120, 100, 70, 255))
    card = Image.composite(grain, card, noise)

    d = ImageDraw.Draw(card)
    d.rounded_rectangle([22, 22, CARD_W - 22, CARD_H - 22], radius=22, outline=BRASS, width=3)
    if cat_en:
        f = load_font("mono_bold", 24)
        label = cat_en.upper()
        b = d.textbbox((0, 0), label, font=f)
        tw, th = b[2] - b[0], b[3] - b[1]
        bx, by = PAD, 66
        d.rounded_rectangle([bx, by, bx + tw + 40, by + th + 24], radius=(th + 24) // 2, fill=GARNET)
        d.text((bx + 20 - b[0], by + 12 - b[1]), label, font=f, fill=WHITE)

    mask = Image.new("L", (CARD_W, CARD_H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, CARD_W - 1, CARD_H - 1], radius=36, fill=255)
    card.putalpha(mask)
    return card


def place(canvas, layer, cx, cy, angle=0, shadow=True):
    """Paste an RGBA layer centered at (cx, cy), rotated `angle` degrees (CCW)."""
    if angle:
        layer = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    x, y = int(cx - layer.width / 2), int(cy - layer.height / 2)
    if shadow:
        a = layer.getchannel("A").point(lambda v: v * 0.55)
        sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        sh.putalpha(a)
        big = Image.new("RGBA", (layer.width + 80, layer.height + 80), (0, 0, 0, 0))
        big.paste(sh, (40, 40))
        big = big.filter(ImageFilter.GaussianBlur(18))
        canvas.alpha_composite(big, (x - 40 + 6, y - 40 + 14))
    canvas.alpha_composite(layer, (x, y))


def place_card(canvas, card, angle=0):
    place(canvas, card, CARD_X + CARD_W / 2, CARD_Y + CARD_H / 2, angle)


def tape(width=230, height=58, color="lilac"):
    a, b = TAPES[color]
    t = Image.new("RGBA", (width, height), a)
    d = ImageDraw.Draw(t)
    step = 16
    for x in range(-height, width + height, step * 2):
        d.polygon([(x, height), (x + step, height), (x + step + height, 0), (x + height, 0)], fill=b)
    # torn-ish short edges
    m = Image.new("L", (width, height), 255)
    md = ImageDraw.Draw(m)
    for y in range(0, height, 6):
        md.polygon([(0, y), (4, y + 3), (0, y + 6)], fill=0)
        md.polygon([(width, y), (width - 4, y + 3), (width, y + 6)], fill=0)
    t.putalpha(Image.composite(t.getchannel("A"), Image.new("L", t.size, 0), m))
    return t


def sticker(text, color, font_name="black_han_sans", size=44, pad=(26, 14), circle=False):
    """Die-cut sticker: pop-color pill with a cream edge (3px CSS -> 6px here)."""
    f = load_font(font_name, size)
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    b = probe.textbbox((0, 0), text, font=f)
    tw, th = b[2] - b[0], b[3] - b[1]
    edge = 7
    if circle:
        side = max(tw, th) + pad[0] * 2
        w = h = side
    else:
        w, h = tw + pad[0] * 2, th + pad[1] * 2
    img = Image.new("RGBA", (w + edge * 2, h + edge * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = (h + edge * 2) // 2 if circle else 20
    d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=r + edge, fill=STICKER_EDGE)
    d.rounded_rectangle([edge, edge, edge + w - 1, edge + h - 1], radius=r, fill=color)
    if text == "✦":
        d.polygon(star_points(img.width / 2, img.height / 2, size * 0.55), fill=STICKER_INK)
    else:
        d.text((edge + (w - tw) / 2 - b[0], edge + (h - th) / 2 - b[1]), text, font=f, fill=STICKER_INK)
    return img


def star_points(cx, cy, r, pinch=0.28):
    """4-point sparkle (✦) as a polygon — no bundled font has a real ✦ glyph."""
    import math
    pts = []
    for i in range(8):
        a = math.pi / 4 * i - math.pi / 2
        rr = r if i % 2 == 0 else r * pinch
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def sparkle(canvas, x, y, size=40, color=POP_LEMON):
    ImageDraw.Draw(canvas).polygon(star_points(x, y, size / 2), fill=color)


def center_text(d, y, text, font, fill, cx=CARD_W // 2):
    d.text((cx, y), text, font=font, fill=fill, anchor="ms")


def finish(canvas):
    return canvas.convert("RGB")


# ---------------------------------------------------------------------------
# Slides
# ---------------------------------------------------------------------------
def build_hook_card(word, new_word=False, stage=3):
    """stage < 3 is only used by the reel to reveal the hook step by step."""
    card = new_card(word["cat_en"])
    d = ImageDraw.Draw(card)
    cx = CARD_W // 2

    q_font = load_font("bricolage_bold", 54)
    center_text(d, 300, "NEW WORD ALERT" if new_word else "Your bias just said…", q_font, CARD_INK)

    if stage < 2:
        return card
    term_font = load_font("black_han_sans", 230 if len(word["kr"]) <= 3 else 170)
    foil = draw_foil_gradient_text(word["kr"], term_font)
    if foil.width > TEXT_W:
        foil = foil.resize((TEXT_W, int(foil.height * TEXT_W / foil.width)), Image.LANCZOS)
    card.alpha_composite(foil, (cx - foil.width // 2, 520 - foil.height // 2))

    rom_font = load_font("mono_italic", 40)
    center_text(d, 520 + foil.height // 2 + 90, f"/{word['rom']}/", rom_font, CARD_INK_SOFT)

    if stage < 3:
        return card
    y = 520 + foil.height // 2 + 220
    if new_word:
        f = load_font("hanken_bold", 44)
        for line in wrap_text(d, word["meaning_en"], f, TEXT_W):
            center_text(d, y, line, f, CARD_INK)
            y += 60
    else:
        f = load_font("bricolage_bold", 50)
        center_text(d, y, "…wait, what does it mean?", f, GARNET)
    return card


def build_meaning_card(word):
    card = new_card(word["cat_en"])
    d = ImageDraw.Draw(card)
    x = PAD

    term_font = load_font("black_han_sans", 120)
    title_font = load_font("bricolage_bold", 46)
    label_font = load_font("mono_bold", 24)
    en_font = load_font("hanken_bold", 46)
    es_font = load_font("hanken_bold", 36)

    en_lines = wrap_text(d, word["meaning_en"], en_font, TEXT_W)
    es_lines = wrap_text(d, word["meaning_es"], es_font, TEXT_W)
    block = 120 + 70 + 90 + len(en_lines) * 62 + 70 + 34 + len(es_lines) * 50
    y = max(200, 120 + (CARD_H - 160 - block) // 2) + 80

    d.text((x, y), word["kr"], font=term_font, fill=CARD_INK, anchor="ls")
    y += 70
    d.text((x, y), word["en_short"], font=title_font, fill=GARNET, anchor="ls")
    y += 90
    d.text((x, y), "MEANING", font=label_font, fill=GARNET, anchor="ls")
    y += 62
    for line in en_lines:
        d.text((x, y), line, font=en_font, fill=CARD_INK, anchor="ls")
        y += 62
    y += 30
    d.line([(x, y - 20), (x + TEXT_W, y - 20)], fill=BRASS, width=2)
    y += 34
    d.text((x, y), "EN ESPAÑOL", font=label_font, fill=BADGE_TEXT_BRASS, anchor="ls")
    y += 54
    for line in es_lines:
        d.text((x, y), line, font=es_font, fill=CARD_INK_SOFT, anchor="ls")
        y += 50
    return card


def build_usage_card(word):
    card = new_card(word["cat_en"])
    d = ImageDraw.Draw(card)
    x = PAD

    label_font = load_font("mono_bold", 24)
    kr_font = load_font("noto_kr_bold", 50)
    en_font = load_font("hanken_bold", 34)
    es_font = load_font("hanken_bold", 30)
    tip_font = load_font("hanken_bold", 34)
    tip_kr = load_font("noto_kr_bold", 32)

    bar_inner = TEXT_W - 80
    kr_lines = wrap_text(d, f"“{word['ex_kr']}”", kr_font, bar_inner)
    en_lines = wrap_text(d, f"→ {word['ex_en']}", en_font, bar_inner)
    es_lines = wrap_text(d, f"→ {word['ex_es']}", es_font, bar_inner)

    tip = (db.DETAILS.get(word["kr"], {}).get("usage") or {}).get("en", "")
    tip_lines = wrap_rich(d, tip, tip_font, tip_kr, TEXT_W) if tip else []
    if len(tip_lines) > 5:
        tip_lines = []  # too long for a card — leave it out rather than cram

    bar_h = 44 * 2 + len(kr_lines) * 66 + 20 + len(en_lines) * 46 + 8 + len(es_lines) * 42
    tip_h = (70 + len(tip_lines) * 48) if tip_lines else 0
    total = 60 + bar_h + tip_h
    y = 170 + (CARD_H - 170 - 120 - total) // 2

    d.text((x, y), "REAL USAGE", font=label_font, fill=GARNET, anchor="ls")
    y += 36
    d.rounded_rectangle([x, y, x + TEXT_W, y + bar_h], radius=18, fill=CAPTION_BLACK)
    ty = y + 44 + 48
    for line in kr_lines:
        d.text((x + 40, ty), line, font=kr_font, fill=CAPTION_INK, anchor="ls")
        ty += 66
    ty += 20 - 66 + 46
    for line in en_lines:
        d.text((x + 40, ty), line, font=en_font, fill=CAPTION_INK_SOFT, anchor="ls")
        ty += 46
    ty += 8 - 46 + 42
    for line in es_lines:
        d.text((x + 40, ty), line, font=es_font, fill=CAPTION_INK_SOFT, anchor="ls")
        ty += 42
    y += bar_h

    if tip_lines:
        y += 70
        d.text((x, y), "HOW FANS USE IT", font=label_font, fill=GARNET, anchor="ls")
        y += 52
        for line in tip_lines:
            draw_rich(d, (x, y), line, tip_font, tip_kr, CARD_INK)
            y += 48
    return card


def build_cta_card():
    cw, ch = 760, 760
    card = Image.new("RGBA", (cw, ch), CARDSTOCK + (255,))
    noise = Image.effect_noise((cw, ch), 40).point(lambda v: max(0, v - 128) // 6)
    card = Image.composite(Image.new("RGBA", (cw, ch), (120, 100, 70, 255)), card, noise)
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([20, 20, cw - 20, ch - 20], radius=20, outline=BRASS, width=3)
    cx = cw // 2

    # bookmark icon
    iw, ih, top = 64, 82, 150
    pts = [(cx - iw // 2, top), (cx + iw // 2, top), (cx + iw // 2, top + ih),
           (cx, top + ih - 26), (cx - iw // 2, top + ih)]
    d.polygon(pts, fill=GARNET)

    d.text((cx, 360), "Save this card —", font=load_font("bricolage_bold", 58), fill=CARD_INK, anchor="ms")
    d.text((cx, 440), "see you next time", font=load_font("bricolage_bold", 58), fill=CARD_INK, anchor="ms")
    d.text((cx, 590), "HelloKSlang", font=load_font("black_han_sans", 64), fill=GARNET, anchor="ms")

    m = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=32, fill=255)
    card.putalpha(m)
    return card


def render_hook_slide(word, new_word=False):
    canvas = backdrop(None if new_word else "1/4")
    card = build_hook_card(word, new_word)

    angle = -1.6
    place_card(canvas, card, angle)
    # decorations sit on the card edges, never over the text block
    place(canvas, tape(240, 60, "lilac").rotate(-8, expand=True, resample=Image.BICUBIC), W / 2, CARD_Y + 4, shadow=False)
    place(canvas, sticker("♥", POP_PINK, "noto_kr_bold", 54, circle=True), CARD_X + CARD_W - 40, CARD_Y + 150, 12)
    if new_word:
        place(canvas, sticker("NEW", POP_LEMON, "black_han_sans", 46), CARD_X + 110, CARD_Y + CARD_H - 24, 7)
    else:
        place(canvas, sticker("SWIPE →", POP_LEMON, "bricolage_bold", 40), CARD_X + CARD_W - 140, CARD_Y + CARD_H - 20, -6)
    sparkle(canvas, 70, 1300, 46)
    sparkle(canvas, 1030, 175, 34, POP_MINT)
    sparkle(canvas, 1000, 1310, 28, POP_PINK)
    return finish(canvas)


def render_meaning_slide(word):
    canvas = backdrop("2/4")
    card = build_meaning_card(word)
    place_card(canvas, card)  # long text → card stays level
    place(canvas, tape(200, 54, "pink").rotate(30, expand=True, resample=Image.BICUBIC), CARD_X + 30, CARD_Y + 20, shadow=False)
    place(canvas, tape(200, 54, "pink").rotate(30, expand=True, resample=Image.BICUBIC), CARD_X + CARD_W - 30, CARD_Y + CARD_H - 20, shadow=False)
    place(canvas, sticker("✦", POP_LILAC, "noto_kr_bold", 50, circle=True), CARD_X + CARD_W - 50, CARD_Y + 40, -10)
    sparkle(canvas, 50, 1310, 34, POP_LEMON)
    return finish(canvas)


def render_usage_slide(word):
    canvas = backdrop("3/4")
    card = build_usage_card(word)
    place_card(canvas, card)
    place(canvas, tape(230, 58, "mint").rotate(-4, expand=True, resample=Image.BICUBIC), W / 2, CARD_Y + 2, shadow=False)
    place(canvas, sticker("ㅋㅋ", POP_MINT, "black_han_sans", 46, circle=True), CARD_X + CARD_W - 46, CARD_Y + CARD_H - 50, 9)
    sparkle(canvas, 1030, 1300, 40)
    sparkle(canvas, 46, 160, 30, POP_PINK)
    return finish(canvas)


def render_cta_slide():
    canvas = backdrop("4/4")
    card = build_cta_card()
    place(canvas, card, W / 2, 560, 2.2)
    place(canvas, tape(220, 56, "lilac").rotate(-12, expand=True, resample=Image.BICUBIC), W / 2 - 230, 200, shadow=False)
    place(canvas, tape(220, 56, "pink").rotate(14, expand=True, resample=Image.BICUBIC), W / 2 + 240, 925, shadow=False)
    place(canvas, sticker("ㅋㅋ", POP_MINT, "black_han_sans", 50, circle=True), W / 2 + 360, 230, -12)

    d = ImageDraw.Draw(canvas)
    d.text((W / 2, 1100), "hellokslang.com", font=load_font("bricolage_bold", 52), fill=CREAM_INK, anchor="ms")
    d.text((W / 2, 1160), "NEW SLANG EVERY WEEK · EN / ES / 中文 / 日本語", font=load_font("noto_kr_bold", 24), fill=CREAM_INK_SOFT, anchor="ms")
    place(canvas, sticker("Follow ♥", POP_PINK, "noto_kr_bold", 38), W / 2, 1245, -3)
    sparkle(canvas, 120, 1050, 44)
    sparkle(canvas, 970, 1060, 32, POP_LILAC)
    sparkle(canvas, 140, 130, 30, POP_MINT)
    return finish(canvas)


def generate_carousel(kr, date_str=None):
    word = find_word(kr)
    if date_str is None:
        date_str = date.today().isoformat()
    out_dir = output_dir(word, date_str)

    slides = [
        render_hook_slide(word),
        render_meaning_slide(word),
        render_usage_slide(word),
        render_cta_slide(),
    ]

    paths = []
    for i, slide_img in enumerate(slides, start=1):
        path = os.path.join(out_dir, f"slide-{i}.png")
        slide_img.save(path, "PNG")
        paths.append(path)
    return paths


def generate_new_word_cards():
    latest_date, latest_words = db.NEW_WORDS_LOG[0]
    paths = []
    for kr in latest_words:
        word = find_word(kr)
        out_dir = output_dir(word, latest_date)
        path = os.path.join(out_dir, "slide-1.png")
        render_hook_slide(word, new_word=True).save(path, "PNG")
        paths.append(path)
    return paths


def main():
    parser = argparse.ArgumentParser(
        description="Generate Instagram carousel/single-image cards for @hellokslang."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--carousel", metavar="KR_WORD",
        help='Generate a 4-slide carousel for one word, e.g. --carousel "컴백"',
    )
    group.add_argument(
        "--new-word", action="store_true",
        help="Generate single-slide announcement cards for the latest NEW_WORDS_LOG entry.",
    )
    args = parser.parse_args()

    try:
        if args.carousel:
            paths = generate_carousel(args.carousel)
        else:
            paths = generate_new_word_cards()
    except WordNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
