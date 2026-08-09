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

from PIL import Image, ImageDraw, ImageFont

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


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_foil_gradient_text(text, font):
    probe = Image.new("L", (10, 10), 0)
    probe_draw = ImageDraw.Draw(probe)
    bbox = probe_draw.textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    pad = 6
    size = (text_w + pad * 2, text_h + pad * 2)
    mask = Image.new("L", size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.text((pad - bbox[0], pad - bbox[1]), text, font=font, fill=255)

    gradient = Image.new("RGB", size)
    grad_draw = ImageDraw.Draw(gradient)
    stops = FOIL_STOPS
    for x in range(size[0]):
        t = x / max(size[0] - 1, 1)
        seg = t * (len(stops) - 1)
        i = min(int(seg), len(stops) - 2)
        local_t = seg - i
        c0, c1 = stops[i], stops[i + 1]
        color = tuple(
            int(c0[k] + (c1[k] - c0[k]) * local_t) for k in range(3)
        )
        grad_draw.line([(x, 0), (x, size[1])], fill=color)

    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(gradient, (0, 0), mask)
    return out


def draw_card_base(cat_en):
    img = Image.new("RGB", (W, H), CARDSTOCK)
    highlight = Image.new("RGB", (W, H), CARDSTOCK_HI)
    blend_mask = Image.new("L", (W, H))
    mask_draw = ImageDraw.Draw(blend_mask)
    for y in range(H):
        t = 1 - abs((y / H) - 0.32)
        mask_draw.line([(0, y), (W, y)], fill=max(0, int(255 * t * 0.5)))
    img = Image.composite(highlight, img, blend_mask)

    draw = ImageDraw.Draw(img)
    draw.rectangle(
        [INSET, INSET, W - INSET, H - INSET], outline=BRASS, width=3
    )

    badge_font = load_font("mono_bold", 24)
    label = cat_en.upper()
    bbox = draw.textbbox((0, 0), label, font=badge_font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 20, 12
    bx, by = CONTENT_LEFT, INSET + 40
    draw.rounded_rectangle(
        [bx, by, bx + text_w + pad_x * 2, by + text_h + pad_y * 2],
        radius=(text_h + pad_y * 2) // 2,
        fill=GARNET,
    )
    draw.text(
        (bx + pad_x - bbox[0], by + pad_y - bbox[1]),
        label, font=badge_font, fill=WHITE,
    )
    return img


def render_hook_slide(word):
    img = draw_card_base(word["cat_en"])
    draw = ImageDraw.Draw(img)

    term_font = load_font("black_han_sans", 220)
    foil_term = draw_foil_gradient_text(word["kr"], term_font)
    term_x = (W - foil_term.width) // 2
    term_y = int(H * 0.32) - foil_term.height // 2
    img.paste(foil_term, (term_x, term_y), foil_term)

    tag_font = load_font("mono_bold", 28)
    rom_font = load_font("mono_italic", 34)
    tag_text = word["en_short"].upper()
    rom_text = f"/{word['rom']}/"

    tag_lines = wrap_text(draw, tag_text, tag_font, CONTENT_WIDTH)
    rom_bbox = draw.textbbox((0, 0), rom_text, font=rom_font)
    rom_h = rom_bbox[3] - rom_bbox[1]

    line_gap = 8
    tag_line_h = tag_font.size + 6
    block_gap = 20

    # anchor the tag/romanization block just under the term itself, rather
    # than pinning it to the card's bottom edge — keeps the two halves of
    # the composition close together instead of leaving a large dead gap
    y = term_y + foil_term.height + 64
    for line in tag_lines:
        draw.text((CONTENT_LEFT, y), line, font=tag_font, fill=BADGE_TEXT_BRASS)
        y += tag_line_h + line_gap
    y += block_gap - line_gap
    draw.text((CONTENT_LEFT, y - rom_bbox[1]), rom_text, font=rom_font, fill=CARD_INK_SOFT)

    return img


def render_meaning_slide(word):
    img = draw_card_base(word["cat_en"])
    draw = ImageDraw.Draw(img)

    term_font = load_font("black_han_sans", 90)
    eyelabel_font = load_font("mono_bold", 22)
    def_font = load_font("hanken_bold", 44)

    term_bbox = draw.textbbox((0, 0), word["kr"], font=term_font)
    term_h = term_bbox[3] - term_bbox[1]
    eyelabel = "MEANING"
    eyelabel_bbox = draw.textbbox((0, 0), eyelabel, font=eyelabel_font)
    eyelabel_h = eyelabel_bbox[3] - eyelabel_bbox[1]
    def_lines = wrap_text(draw, word["meaning_en"], def_font, CONTENT_WIDTH)
    line_h = def_font.size + 16

    # measure the whole block up front so it can be vertically centered,
    # instead of anchoring to a fixed top offset and leaving a dead gap
    # below whatever happens to be the shortest definition
    total_h = term_h + 36 + eyelabel_h + 24 + len(def_lines) * line_h
    y = (H - total_h) // 2

    draw.text((CONTENT_LEFT, y - term_bbox[1]), word["kr"], font=term_font, fill=CARD_INK)
    y += term_h + 36

    draw.text((CONTENT_LEFT, y - eyelabel_bbox[1]), eyelabel, font=eyelabel_font, fill=GARNET)
    y += eyelabel_h + 24

    for line in def_lines:
        line_bbox = draw.textbbox((0, 0), line, font=def_font)
        draw.text((CONTENT_LEFT, y - line_bbox[1]), line, font=def_font, fill=CARD_INK)
        y += line_h

    return img


def render_usage_slide(word):
    img = draw_card_base(word["cat_en"])
    draw = ImageDraw.Draw(img)

    eyelabel_font = load_font("mono_bold", 22)
    eyelabel = "REAL USAGE"
    eyelabel_y = INSET + 40 + 70  # clear of the category badge drawn by draw_card_base
    eyelabel_bbox = draw.textbbox((0, 0), eyelabel, font=eyelabel_font)
    draw.text(
        (CONTENT_LEFT, eyelabel_y - eyelabel_bbox[1]),
        eyelabel, font=eyelabel_font, fill=GARNET,
    )

    kr_font = load_font("noto_kr_bold", 46)
    en_font = load_font("hanken_bold", 32)
    bar_left, bar_right = CONTENT_LEFT, CONTENT_RIGHT
    bar_inner_w = bar_right - bar_left - 80

    kr_text = f"“{word['ex_kr']}”"
    en_text = f"→ “{word['ex_en']}”"
    kr_lines = wrap_text(draw, kr_text, kr_font, bar_inner_w)
    en_lines = wrap_text(draw, en_text, en_font, bar_inner_w)

    kr_line_h = kr_font.size + 14
    en_line_h = en_font.size + 12
    pad_y = 40
    gap = 24
    bar_h = pad_y * 2 + len(kr_lines) * kr_line_h + gap + len(en_lines) * en_line_h
    bar_top = (H - bar_h) // 2
    bar_bottom = bar_top + bar_h

    draw.rounded_rectangle(
        [bar_left, bar_top, bar_right, bar_bottom], radius=16, fill=CAPTION_BLACK
    )

    y = bar_top + pad_y
    for line in kr_lines:
        line_bbox = draw.textbbox((0, 0), line, font=kr_font)
        draw.text((bar_left + 40, y - line_bbox[1]), line, font=kr_font, fill=CAPTION_INK)
        y += kr_line_h
    y += gap - kr_line_h + kr_font.size
    for line in en_lines:
        line_bbox = draw.textbbox((0, 0), line, font=en_font)
        draw.text((bar_left + 40, y - line_bbox[1]), line, font=en_font, fill=CAPTION_INK_SOFT)
        y += en_line_h

    return img


def render_cta_slide():
    img = Image.new("RGB", (W, H), CHARCOAL_BACKDROP)
    draw = ImageDraw.Draw(img)
    cx = W // 2

    icon_w, icon_h = 60, 76
    icon_top = int(H * 0.30)
    icon_pts = [
        (cx - icon_w // 2, icon_top),
        (cx + icon_w // 2, icon_top),
        (cx + icon_w // 2, icon_top + icon_h),
        (cx, icon_top + icon_h - 26),
        (cx - icon_w // 2, icon_top + icon_h),
    ]
    draw.line(icon_pts + [icon_pts[0]], fill=GARNET, width=4, joint="curve")

    y = icon_top + icon_h + 40

    wordmark_font = load_font("black_han_sans", 48)
    wordmark = "HelloKSlang"
    wm_bbox = draw.textbbox((0, 0), wordmark, font=wordmark_font)
    draw.text(
        (cx - (wm_bbox[2] - wm_bbox[0]) // 2, y - wm_bbox[1]),
        wordmark, font=wordmark_font, fill=CREAM_INK,
    )
    y += (wm_bbox[3] - wm_bbox[1]) + 44

    line_font = load_font("bricolage_bold", 44)
    for line in ("Save this card —", "see you next time"):
        line_bbox = draw.textbbox((0, 0), line, font=line_font)
        draw.text(
            (cx - (line_bbox[2] - line_bbox[0]) // 2, y - line_bbox[1]),
            line, font=line_font, fill=CREAM_INK,
        )
        y += (line_bbox[3] - line_bbox[1]) + 20

    y += 40
    sub_font = load_font("mono_bold", 22)
    for line in ("hellokslang.com", "New slang daily"):
        sub_bbox = draw.textbbox((0, 0), line, font=sub_font)
        draw.text(
            (cx - (sub_bbox[2] - sub_bbox[0]) // 2, y - sub_bbox[1]),
            line, font=sub_font, fill=CREAM_INK_SOFT,
        )
        y += (sub_bbox[3] - sub_bbox[1]) + 14

    return img


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
        render_hook_slide(word).save(path, "PNG")
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
