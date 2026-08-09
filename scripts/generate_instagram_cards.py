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


if __name__ == "__main__":
    pass
