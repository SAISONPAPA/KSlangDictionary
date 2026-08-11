from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import math

W, H = 1080, 1350

# assets/Instagram/Word Introduction/Templates/ -> assets/fonts
_TEMPLATES_DIR = Path(__file__).resolve().parent
FONT_DIR = _TEMPLATES_DIR.parent.parent.parent / "fonts"
# output goes directly under assets/Instagram/Word Introduction/
OUT_BASE_DIR = _TEMPLATES_DIR.parent

# ---- palette sampled from the live site's photocard ----
OUTER_BG = (14, 11, 12)          # near-black outer margin
CARD_BG = (232, 222, 199)        # warm cream cardstock
CARD_BG_DARK = (222, 210, 184)   # slightly deeper cream for shadow blend
GOLD = (161, 122, 33)            # foil gold for the word title
GOLD_HI = (196, 158, 66)
CRIMSON = (196, 30, 58)
CRIMSON_LIGHT = (230, 70, 95)
INK = (35, 28, 24)               # near-black warm ink for body text on cream
INK_SOFT = (92, 80, 68)
BADGE_BG = (183, 154, 90)
BADGE_TEXT = (40, 30, 18)
BOX_BLACK = (24, 19, 17)
BOX_TEXT = (238, 231, 216)

MARGIN_OUT = 46
CARD_RADIUS = 34

def font(path, size, weight=None):
    f = ImageFont.truetype(f"{FONT_DIR}/{path}", size)
    if weight:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f

def blackhan(size):
    return font("BlackHanSans-Regular.ttf", size)

def manrope(size, weight=500):
    return font("Manrope-Variable.ttf", size, weight)

def mono(size, weight=700):
    return font("JetBrainsMono-Bold.ttf", size, weight)

def noise_layer(w, h, seed_scale=26):
    n = Image.effect_noise((w, h), seed_scale).convert("L")
    return n

def grain(img, strength=0.05):
    w, h = img.size
    n = noise_layer(w, h)
    n_rgb = Image.merge("RGB", (n, n, n))
    return Image.blend(img, n_rgb, strength)

def rounded_rect(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)

def outer_canvas():
    img = Image.new("RGB", (W, H), OUTER_BG)
    img = grain(img, 0.035)
    return img

def cream_card(card_box):
    x0, y0, x1, y1 = card_box
    cw, ch = x1 - x0, y1 - y0
    card = Image.new("RGB", (cw, ch), CARD_BG)
    card = grain(card, 0.045)
    mask = Image.new("L", (cw, ch), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle([0, 0, cw, ch], radius=CARD_RADIUS, fill=255)
    return card, mask

def paste_card(base, card_box):
    card, mask = cream_card(card_box)
    base.paste(card, (card_box[0], card_box[1]), mask)
    return ImageDraw.Draw(base)

def notch_cuts(base, card_box, y_frac):
    # emulate the ticket-style side notches on the divider line
    x0, y0, x1, y1 = card_box
    y = int(y0 + (y1 - y0) * y_frac)
    r = 20
    d = ImageDraw.Draw(base)
    d.ellipse([x0 - r, y - r, x0 + r, y + r], fill=OUTER_BG)
    d.ellipse([x1 - r, y - r, x1 + r, y + r], fill=OUTER_BG)
    # dashed line across
    dash_w, gap = 14, 10
    xx = x0 + 30
    while xx < x1 - 30:
        d.line([(xx, y), (xx + dash_w, y)], fill=(198, 186, 160), width=3)
        xx += dash_w + gap
    return d

def wrap_text(draw, text, fnt, max_width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=fnt) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_wrapped(draw, xy, text, fnt, max_width, fill, line_spacing=1.28, align="left"):
    x, y = xy
    lines = wrap_text(draw, text, fnt, max_width)
    ascent, descent = fnt.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    for line in lines:
        lw = draw.textlength(line, font=fnt)
        lx = x
        if align == "center":
            lx = x + (max_width - lw) / 2
        draw.text((lx, y), line, font=fnt, fill=fill)
        y += line_h
    return y

def badge(draw, text, x, y):
    f = mono(24, 700)
    pad_x, pad_y = 24, 14
    tw = draw.textlength(text.upper(), font=f)
    box = [x, y, x + tw + pad_x * 2, y + 24 + pad_y * 2 - 8]
    draw.rounded_rectangle(box, radius=8, fill=BADGE_BG)
    draw.text((x + pad_x, y + pad_y - 4), text.upper(), font=f, fill=BADGE_TEXT)
    return box

def gold_text(draw, xy, text, size, base_img):
    f = blackhan(size)
    x, y = xy
    # fake foil shimmer: base gold fill + lighter overlay offset
    draw.text((x, y), text, font=f, fill=GOLD)
    draw.text((x - 2, y - 2), text, font=f, fill=GOLD_HI)
    draw.text((x, y), text, font=f, fill=GOLD)

def play_button(draw, cx, cy, r=34):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CRIMSON)
    # triangle
    tri = [(cx - 10, cy - 16), (cx - 10, cy + 16), (cx + 16, cy)]
    draw.polygon(tri, fill=(255, 250, 246))

def pill_button(draw, box, text, fill, text_color, fnt):
    draw.rounded_rectangle(box, radius=(box[3] - box[1]) // 2, fill=fill)
    tw = draw.textlength(text, font=fnt)
    th = fnt.getmetrics()
    cx = (box[0] + box[2]) / 2
    cy = (box[1] + box[3]) / 2
    draw.text((cx - tw / 2, cy - (th[0] + th[1]) / 2 + 4), text, font=fnt, fill=text_color)

def pill_outline(draw, box, text, outline, text_color, fnt):
    draw.rounded_rectangle(box, radius=(box[3] - box[1]) // 2, outline=outline, width=2)
    tw = draw.textlength(text, font=fnt)
    th = fnt.getmetrics()
    cx = (box[0] + box[2]) / 2
    cy = (box[1] + box[3]) / 2
    draw.text((cx - tw / 2, cy - (th[0] + th[1]) / 2 + 4), text, font=fnt, fill=text_color)

def page_tag(draw, current, total):
    draw.text((MARGIN_OUT + 6, H - 74), "HELLOKSLANG", font=mono(24, 700), fill=(150, 138, 130))

CARD_BOX = (MARGIN_OUT, 150, W - MARGIN_OUT, H - 150)

# ------------- WORD DATA (swap this block for each new post) -------------
WORD = {
    "category": "ONLINE MEMES",
    "hangul": "\uc601\ud06c\ud06c",
    "roman": "yeong-keu-keu",
    "meaning": "\u201cYoung creator crew.\u201d From a CORTIS song title \u2014 now used to jokingly praise someone for being completely on top of every trend and meme. The positive opposite of being called out of touch (neuk-keu-keu).",
    "quote_kr": "\uc774 \ubc08 \ubc8c\uc368 \uc54c\uc544? \uc644\uc804 \uc601\ud06c\ud06c\ub124.",
    "quote_en": "You already know this meme? You're totally in the loop.",
    "meta": "Commonly seen on: Comment sections, K-pop fandom, 2026 slang",
    "tip": "Tip: use it to hype up a friend who's always first to know the trend.",
}

# caption text saved alongside the images as "<hangul>_캡션.txt"
CAPTION = """Today's word: 영크크 (yeong-keu-keu)

"Young creator crew" — from the title of a CORTIS song, now used to jokingly praise someone for being completely on top of every trend and meme. It's the positive opposite of 늙크크.

You'll see it in comment sections and K-pop fandom chats when someone flexes on knowing a meme before everyone else.

Swipe through for the meaning and a real example →

500+ words like this one, romanized and explained in English, Spanish, Chinese, and Japanese — free at hellokslang.com.

#hellokslang #kpopslang #koreanslang #kdrama #learnkorean"""

# ---------------- PAGES ----------------

def ghost_watermark(img, card_box, text, size, x_off=40):
    x0, y0, x1, y1 = card_box
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    f = blackhan(size)
    tw = ld.textlength(text, font=f)
    tx = x1 - tw - x_off
    ty = y1 - size * 1.05
    ld.text((tx, ty), text, font=f, fill=(*GOLD, 26))
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"), (0, 0))

def measure_wrapped_height(draw, text, fnt, max_width, line_spacing=1.28):
    lines = wrap_text(draw, text, fnt, max_width)
    ascent, descent = fnt.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    return line_h * len(lines)

def page1_intro():
    img = outer_canvas()
    d = paste_card(img, CARD_BOX)
    x0, y0, x1, y1 = CARD_BOX
    pad = 64
    bx = badge(d, WORD["category"], x0 + pad, y0 + 56)

    title_y = y0 + 170
    gold_text(d, (x0 + pad - 4, title_y), WORD["hangul"], 190, img)

    pron_y = title_y + 250
    d.text((x0 + pad, pron_y), f"/ {WORD['roman']} /", font=manrope(40, 600), fill=INK_SOFT)

    div_y = pron_y + 90
    notch_cuts(img, CARD_BOX, (div_y - y0) / (y1 - y0))

    below_y = div_y + 40
    draw_wrapped(d, (x0 + pad, below_y), "Swipe to see what it means \u2192", manrope(32, 600), (x1 - x0) - 2 * pad, INK_SOFT)

    ghost_watermark(img, CARD_BOX, WORD["hangul"], 340)
    d = ImageDraw.Draw(img)

    page_tag(d, 1, 4)
    return img

def page2_meaning():
    img = outer_canvas()
    d = paste_card(img, CARD_BOX)
    x0, y0, x1, y1 = CARD_BOX
    pad = 64

    f_label = mono(28, 700)
    d.text((x0 + pad, y0 + 56), "MEANING", font=f_label, fill=CRIMSON)

    hy = y0 + 120
    d.text((x0 + pad, hy), WORD["hangul"], font=blackhan(72), fill=GOLD)
    d.text((x0 + pad + d.textlength(WORD["hangul"], font=blackhan(72)) + 24, hy + 18), WORD["roman"], font=manrope(30, 600), fill=INK_SOFT)

    my = hy + 130
    end_y = draw_wrapped(d, (x0 + pad, my), WORD["meaning"], manrope(46, 600), (x1 - x0) - 2 * pad, INK, line_spacing=1.34)

    div_y = end_y + 50
    d.line([(x0 + pad, div_y), (x1 - pad, div_y)], fill=(206, 193, 165), width=2)
    draw_wrapped(d, (x0 + pad, div_y + 36), WORD["tip"], manrope(30, 500), (x1 - x0) - 2 * pad, INK_SOFT, line_spacing=1.3)

    ghost_watermark(img, CARD_BOX, WORD["hangul"], 340)
    d = ImageDraw.Draw(img)

    page_tag(d, 2, 4)
    return img

def page3_usage():
    img = outer_canvas()
    d = paste_card(img, CARD_BOX)
    x0, y0, x1, y1 = CARD_BOX
    pad = 64

    d.text((x0 + pad, y0 + 56), "REAL USAGE", font=mono(28, 700), fill=CRIMSON)

    box_y = y0 + 120
    box_bottom = y1 - pad
    box_h = box_bottom - box_y
    box = [x0 + pad, box_y, x1 - pad, box_bottom]
    d.rounded_rectangle(box, radius=22, fill=BOX_BLACK)

    ip = 48
    inner_w = (box[2] - box[0]) - 2 * ip
    kr_font = blackhan(56)
    en_font = manrope(38, 500)
    meta_font = manrope(26, 500)

    kr_h = measure_wrapped_height(d, WORD["quote_kr"], kr_font, inner_w, 1.22)
    en_h = measure_wrapped_height(d, "\u2192 " + WORD["quote_en"], en_font, inner_w, 1.3)
    gap = 34
    meta_h = measure_wrapped_height(d, WORD["meta"], meta_font, inner_w, 1.2)
    meta_gap = 50

    content_h = kr_h + gap + en_h
    avail_h = box_h - 2 * ip - meta_h - meta_gap
    start_y = box_y + ip + max(0, (avail_h - content_h) / 2)

    ty = draw_wrapped(d, (box[0] + ip, start_y), WORD["quote_kr"], kr_font, inner_w, BOX_TEXT, line_spacing=1.22)
    ty += gap
    draw_wrapped(d, (box[0] + ip, ty), "\u2192 " + WORD["quote_en"], en_font, inner_w, (216, 204, 190), line_spacing=1.3)

    draw_wrapped(d, (box[0] + ip, box_bottom - ip - meta_h), WORD["meta"], meta_font, inner_w, (150, 138, 126), line_spacing=1.2)

    page_tag(d, 3, 4)
    return img


def page4_cta():
    img = outer_canvas()
    d = paste_card(img, CARD_BOX)
    x0, y0, x1, y1 = CARD_BOX
    pad = 64

    badge(d, "Full Dictionary", x0 + pad, y0 + 56)

    title_y = y0 + 150
    end_y = draw_wrapped(d, (x0 + pad, title_y), "500+ words. Way more than just K-pop.", blackhan(64), (x1 - x0) - 2 * pad, GOLD, line_spacing=1.12)

    body_y = end_y + 40
    body_y = draw_wrapped(d, (x0 + pad, body_y), "HelloKSlang covers idol fandom slang, drama lines, viral memes, and everyday Korean pop culture \u2014 explained in English, plus 4 more languages (ES/CN/JP).", manrope(36, 500), (x1 - x0) - 2 * pad, INK, line_spacing=1.35)

    div_y = body_y + 40
    notch_cuts(img, CARD_BOX, (div_y - y0) / (y1 - y0))
    d = ImageDraw.Draw(img)

    url_y = div_y + 60
    url_box = [x0 + pad, url_y, x1 - pad, url_y + 120]
    d.rounded_rectangle(url_box, radius=60, fill=CRIMSON)
    txt = "hellokslang.com"
    tf = manrope(46, 800)
    tw = d.textlength(txt, font=tf)
    d.text(((W - tw) / 2, url_y + 38), txt, font=tf, fill=(255, 248, 244))

    tag_y = url_y + 160
    draw_wrapped(d, (x0 + pad, tag_y), "Free. No sign-up. Just search and learn.", manrope(30, 500), (x1 - x0) - 2 * pad, INK_SOFT, align="center")

    ghost_watermark(img, CARD_BOX, WORD["hangul"], 340)
    d = ImageDraw.Draw(img)

    page_tag(d, 4, 4)
    return img

import re

def find_existing_post_dir(base_dir, hangul):
    base_dir.mkdir(parents=True, exist_ok=True)
    for p in base_dir.iterdir():
        if p.is_dir():
            m = re.match(r"^\d+\.\s*(.+)$", p.name)
            if m and m.group(1) == hangul:
                return p
    return None

def next_post_dir(base_dir, hangul):
    existing = find_existing_post_dir(base_dir, hangul)
    if existing:
        if any(existing.iterdir()):
            raise SystemExit(f"'{hangul}' 폴더가 이미 있고 내용도 있음: {existing} (중복 생성 방지 — 새 단어인지 확인할 것)")
        return existing  # empty placeholder folder -> reuse it
    nums = [int(m.group(1)) for p in base_dir.iterdir() if p.is_dir()
            for m in [re.match(r"^(\d+)\.", p.name)] if m]
    next_n = max(nums, default=0) + 1
    out_dir = base_dir / f"{next_n}. {hangul}"
    out_dir.mkdir(parents=True, exist_ok=False)
    return out_dir

HANGUL_RE = re.compile(r"[가-힣]")

def check_no_stray_hangul():
    # meaning/tip/meta/quote_en render in Manrope/JetBrains Mono, which have no
    # Hangul glyphs -> PIL doesn't font-fallback, so any Hangul here silently
    # renders as tofu boxes. Only "hangul" and "quote_kr" (Black Han Sans) may contain it.
    for field in ("meaning", "tip", "meta", "quote_en"):
        if HANGUL_RE.search(WORD[field]):
            raise SystemExit(f"WORD['{field}']에 한글이 섞여있음 (Manrope/Mono 폰트라 tofu로 깨짐): {WORD[field]!r}")

check_no_stray_hangul()

OUT_DIR = next_post_dir(OUT_BASE_DIR, WORD["hangul"])
pages = [page1_intro(), page2_meaning(), page3_usage(), page4_cta()]
for i, im in enumerate(pages, start=1):
    im.save(OUT_DIR / f"{WORD['hangul']}_page_{i}.png")
(OUT_DIR / f"{WORD['hangul']}_캡션.txt").write_text(CAPTION, encoding="utf-8")
print(f"done -> {OUT_DIR}")
