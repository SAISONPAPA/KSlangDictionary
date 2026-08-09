# Instagram Carousel Card Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `scripts/generate_instagram_cards.py`, a Pillow-based CLI tool that renders 4-slide Instagram carousel decks and single-slide new-word announcement cards from `scripts/build_kslang_db.py` data.

**Architecture:** One flat script (matching the existing `scripts/*.py` convention — no new package/module layout), built bottom-up: data lookup → output-path helpers → text-wrapping and foil-gradient-text primitives → a shared card-base renderer → four slide renderers → two CLI orchestration modes → argparse entrypoint. Every function is unit-tested with pytest as it's built; image-producing functions get dimension/pixel-sample smoke tests, and the final task is a real end-to-end run that's visually inspected by hand (Pillow output can't be meaningfully asserted pixel-perfect in CI).

**Tech Stack:** Python 3.12, Pillow (image rendering), pytest (tests). No new runtime dependency beyond what's already in the repo (`openpyxl`, used indirectly via `build_kslang_db`).

## Global Constraints

- Python 3.12 (matches `.github/workflows/rebuild.yml`'s `actions/setup-python` version and the local `python` interpreter).
- New dependencies, installed the same inline way the repo already installs `openpyxl` in CI (no `requirements.txt` in this repo — don't add one): `pip install Pillow pytest`.
- Font files are OFL-licensed static weights downloaded once from Google Fonts into `assets/fonts/` and committed to the repo — Pillow needs local font files and does not font-fallback the way browsers do (this is the exact bug already logged in `CLAUDE.md` item #3).
- Output images are 1080×1350 PNG only (Instagram portrait 4:5).
- This script is **not** part of the automated `.github/workflows/rebuild.yml` pipeline — it's a manual content-creation tool. Do not add it to that workflow.
- Colors are copied verbatim from `DESIGN.md`: `CARDSTOCK #F2E9D8`, `CARDSTOCK_HI #F8F1E3`, `CARD_INK #211B16`, `CARD_INK_SOFT #5B5248`, `GARNET #B21B3E`, `BRASS #B4923F`, `BADGE_TEXT_BRASS #7A6224`, `CAPTION_BLACK #100E13`, `CAPTION_INK #FDF8EE`, `CAPTION_INK_SOFT #B8AF9F`, `CHARCOAL_BACKDROP #151217`, `CREAM_INK #F3ECDD`, `CREAM_INK_SOFT #A79E92`. Foil gradient stops: `#6E5419 → #C9A64C → #EBD08A → #C9A64C → #7A5E1E`.
- English-only content for this version — do not render `meaning_es`/`ex_es`.
- No filtering by the data's `status` field — both `"Verified (web-checked)"` and `"Draft — please double-check"` words are eligible for `--carousel`.
- Per the approved spec (`docs/superpowers/specs/2026-08-09-instagram-carousel-generator-design.md`), slide 1's short tag line uses the real `en_short` field (e.g. `"Comeback"`) — **not** a fabricated Korean phrase; an earlier mockup used invented Korean text that has no corresponding data field, corrected during plan review.

---

## File Structure

- Create: `scripts/generate_instagram_cards.py` — the entire tool (data lookup, rendering, CLI).
- Create: `scripts/test_generate_instagram_cards.py` — pytest suite, colocated with the script per this repo's flat `scripts/` convention (no `tests/` directory exists elsewhere in the repo).
- Create: `assets/fonts/BlackHanSans-Regular.ttf`, `assets/fonts/HankenGrotesk-Bold.ttf`, `assets/fonts/BricolageGrotesque-Bold.ttf`, `assets/fonts/NotoSansKR-Bold.otf`, `assets/fonts/JetBrainsMono-Bold.ttf`, `assets/fonts/JetBrainsMono-Italic.ttf` — binary font assets, downloaded once.
- Modify: `CLAUDE.md` — add a short section documenting the new tool (Task 14), so it isn't lost the way the earlier `og-image.png` generation process was (per `CLAUDE.md`'s own note that this file's context comes from a chat that isn't preserved anywhere else).

---

### Task 1: Fonts + module skeleton

**Files:**
- Create: `assets/fonts/BlackHanSans-Regular.ttf`, `assets/fonts/HankenGrotesk-Bold.ttf`, `assets/fonts/BricolageGrotesque-Bold.ttf`, `assets/fonts/NotoSansKR-Bold.otf`, `assets/fonts/JetBrainsMono-Bold.ttf`, `assets/fonts/JetBrainsMono-Italic.ttf`
- Create: `scripts/generate_instagram_cards.py`
- Create: `scripts/test_generate_instagram_cards.py`

**Interfaces:**
- Produces: module-level constants `W = 1080`, `H = 1350`, `REPO_ROOT`, `FONT_DIR`, `FONTS` (dict), all the color constants listed in Global Constraints, `FOIL_STOPS` (list of 5 RGB tuples), and `load_font(name: str, size: int) -> PIL.ImageFont.FreeTypeFont`, raising `FileNotFoundError` with a clear message if the font file is missing.

- [ ] **Step 1: Install dependencies**

```bash
pip install Pillow pytest
```

- [ ] **Step 2: Download the 6 font files**

Download each from Google Fonts (fonts.google.com → search family → "Download family", or the direct GitHub mirror `github.com/google/fonts`) and place the **exact weight** listed below into `assets/fonts/` under the **exact filename** listed (these names are what `FONTS` in Step 4 references):

| Family | Weight | Save as |
|---|---|---|
| Black Han Sans | Regular | `assets/fonts/BlackHanSans-Regular.ttf` |
| Hanken Grotesk | Bold | `assets/fonts/HankenGrotesk-Bold.ttf` |
| Bricolage Grotesque | Bold (static instance, not the variable font) | `assets/fonts/BricolageGrotesque-Bold.ttf` |
| Noto Sans KR | Bold | `assets/fonts/NotoSansKR-Bold.otf` |
| JetBrains Mono | Bold | `assets/fonts/JetBrainsMono-Bold.ttf` |
| JetBrains Mono | Italic | `assets/fonts/JetBrainsMono-Italic.ttf` |

All six are OFL-licensed — safe to commit to the repo.

- [ ] **Step 3: Write the failing test**

Create `scripts/test_generate_instagram_cards.py`:

```python
# -*- coding: utf-8 -*-
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import generate_instagram_cards as gic


def test_all_fonts_load():
    for name in gic.FONTS:
        font = gic.load_font(name, 40)
        assert font is not None


def test_missing_font_raises_clear_error(tmp_path, monkeypatch):
    monkeypatch.setattr(gic, "FONT_DIR", str(tmp_path))
    try:
        gic.load_font("black_han_sans", 40)
        assert False, "expected FileNotFoundError"
    except FileNotFoundError as e:
        assert "BlackHanSans-Regular.ttf" in str(e)
```

- [ ] **Step 4: Run test to verify it fails**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'generate_instagram_cards'` (the module doesn't exist yet).

- [ ] **Step 5: Write the module skeleton**

Create `scripts/generate_instagram_cards.py`:

```python
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


if __name__ == "__main__":
    pass
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v`
Expected: PASS (2 tests)

- [ ] **Step 7: Commit**

```bash
git add assets/fonts/ scripts/generate_instagram_cards.py scripts/test_generate_instagram_cards.py
git commit -m "Add font assets and module skeleton for Instagram card generator"
```

---

### Task 2: Word lookup

**Files:**
- Modify: `scripts/generate_instagram_cards.py`
- Modify: `scripts/test_generate_instagram_cards.py`

**Interfaces:**
- Consumes: `db.CATEGORIES` (list of `(cat_kr, cat_en, terms)`, each term a `(kr, rom, en_short, meaning_en, meaning_es, ex_kr, ex_en, ex_es, where, status)` 10-tuple) — the exact structure already unpacked the same way in `scripts/update_main_pages.py:27`.
- Produces: `WordNotFoundError(Exception)` and `find_word(kr: str) -> dict` with keys `kr, rom, en_short, meaning_en, meaning_es, ex_kr, ex_en, ex_es, where, status, cat_kr, cat_en`. Raises `WordNotFoundError` (with up to 5 close-match suggestions via `difflib`) when `kr` isn't found.

- [ ] **Step 1: Write the failing test**

Append to `scripts/test_generate_instagram_cards.py`:

```python
def test_find_word_returns_known_word():
    word = gic.find_word("컴백")
    assert word["kr"] == "컴백"
    assert word["rom"] == "keom-baek"
    assert word["en_short"] == "Comeback"
    assert word["cat_en"] == "Idol Essentials"
    assert "comeback" in word["meaning_en"].lower()


def test_find_word_raises_with_suggestions_for_typo():
    try:
        gic.find_word("컴벡")  # typo of 컴백
        assert False, "expected WordNotFoundError"
    except gic.WordNotFoundError as e:
        assert "컴벡" in str(e)


def test_find_word_raises_for_nonsense_input():
    try:
        gic.find_word("zzz-not-a-real-word-zzz")
        assert False, "expected WordNotFoundError"
    except gic.WordNotFoundError as e:
        assert "not found" in str(e).lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k find_word`
Expected: FAIL — `AttributeError: module 'generate_instagram_cards' has no attribute 'find_word'`

- [ ] **Step 3: Implement**

Add to `scripts/generate_instagram_cards.py`, after the `load_font` function:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k find_word`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_instagram_cards.py scripts/test_generate_instagram_cards.py
git commit -m "Add word lookup with typo suggestions to Instagram card generator"
```

---

### Task 3: Output path helpers

**Files:**
- Modify: `scripts/generate_instagram_cards.py`
- Modify: `scripts/test_generate_instagram_cards.py`

**Interfaces:**
- Consumes: `word["rom"]` (str) from `find_word`.
- Produces: `slug_from_rom(rom: str) -> str` and `output_dir(word: dict, date_str: str) -> str` (creates the directory if missing, returns its path).

- [ ] **Step 1: Write the failing test**

```python
def test_slug_from_rom_lowercases_and_keeps_hyphens():
    assert gic.slug_from_rom("keom-baek") == "keom-baek"


def test_slug_from_rom_strips_unsafe_characters():
    assert gic.slug_from_rom("Kkul Jae Mi!") == "kkul-jae-mi"


def test_output_dir_creates_and_returns_path(tmp_path, monkeypatch):
    monkeypatch.setattr(gic, "REPO_ROOT", str(tmp_path))
    word = {"rom": "keom-baek"}
    path = gic.output_dir(word, "2026-08-10")
    assert path == os.path.join(str(tmp_path), "assets", "instagram", "2026-08-10-keom-baek")
    assert os.path.isdir(path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k "slug or output_dir"`
Expected: FAIL — `AttributeError: module 'generate_instagram_cards' has no attribute 'slug_from_rom'`

- [ ] **Step 3: Implement**

Add to `scripts/generate_instagram_cards.py`:

```python
def slug_from_rom(rom):
    slug = re.sub(r"[^a-z0-9]+", "-", rom.lower()).strip("-")
    return slug


def output_dir(word, date_str):
    dir_name = f"{date_str}-{slug_from_rom(word['rom'])}"
    path = os.path.join(REPO_ROOT, "assets", "instagram", dir_name)
    os.makedirs(path, exist_ok=True)
    return path
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k "slug or output_dir"`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_instagram_cards.py scripts/test_generate_instagram_cards.py
git commit -m "Add output path helpers to Instagram card generator"
```

---

### Task 4: Text wrapping helper

**Files:**
- Modify: `scripts/generate_instagram_cards.py`
- Modify: `scripts/test_generate_instagram_cards.py`

**Interfaces:**
- Consumes: `load_font` from Task 1.
- Produces: `wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]`.

- [ ] **Step 1: Write the failing test**

```python
def test_wrap_text_splits_long_text_into_multiple_lines():
    img = Image.new("RGB", (10, 10))
    draw = ImageDraw.Draw(img)
    font = gic.load_font("hanken_bold", 44)
    long_text = ("A group or artist's new release along with its full "
                 "promotion cycle (new song, styling, era).")
    lines = gic.wrap_text(draw, long_text, font, max_width=800)
    assert len(lines) > 1
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        assert bbox[2] - bbox[0] <= 800


def test_wrap_text_keeps_short_text_on_one_line():
    img = Image.new("RGB", (10, 10))
    draw = ImageDraw.Draw(img)
    font = gic.load_font("hanken_bold", 44)
    lines = gic.wrap_text(draw, "Comeback", font, max_width=800)
    assert lines == ["Comeback"]
```

Add these imports at the top of `scripts/test_generate_instagram_cards.py`:

```python
from PIL import Image, ImageDraw
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k wrap_text`
Expected: FAIL — `AttributeError: module 'generate_instagram_cards' has no attribute 'wrap_text'`

- [ ] **Step 3: Implement**

Add to `scripts/generate_instagram_cards.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k wrap_text`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_instagram_cards.py scripts/test_generate_instagram_cards.py
git commit -m "Add text-wrapping helper to Instagram card generator"
```

---

### Task 5: Foil gradient text primitive

**Files:**
- Modify: `scripts/generate_instagram_cards.py`
- Modify: `scripts/test_generate_instagram_cards.py`

**Interfaces:**
- Consumes: `load_font`, `FOIL_STOPS`.
- Produces: `draw_foil_gradient_text(text: str, font: ImageFont.FreeTypeFont) -> Image.Image` (RGBA image sized to the text's bounding box, gradient visible only through the glyph shapes — Pillow's answer to CSS `background-clip: text`, since it has no native equivalent).

- [ ] **Step 1: Write the failing test**

```python
def test_foil_gradient_text_is_transparent_outside_glyphs():
    font = gic.load_font("black_han_sans", 200)
    img = gic.draw_foil_gradient_text("컴백", font)
    assert img.mode == "RGBA"
    assert img.width > 0 and img.height > 0
    corner_alpha = img.getpixel((0, 0))[3]
    assert corner_alpha == 0


def test_foil_gradient_text_has_visible_pixels():
    font = gic.load_font("black_han_sans", 200)
    img = gic.draw_foil_gradient_text("컴백", font)
    center = (img.width // 2, img.height // 2)
    center_alpha = img.getpixel(center)[3]
    assert center_alpha > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k foil`
Expected: FAIL — `AttributeError: module 'generate_instagram_cards' has no attribute 'draw_foil_gradient_text'`

- [ ] **Step 3: Implement**

Add to `scripts/generate_instagram_cards.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k foil`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_instagram_cards.py scripts/test_generate_instagram_cards.py
git commit -m "Add foil gradient text rendering to Instagram card generator"
```

---

### Task 6: Shared card-base renderer

**Files:**
- Modify: `scripts/generate_instagram_cards.py`
- Modify: `scripts/test_generate_instagram_cards.py`

**Interfaces:**
- Consumes: `W, H, INSET, CONTENT_LEFT`, color constants, `load_font`.
- Produces: `draw_card_base(cat_en: str) -> Image.Image` — a `1080x1350` RGB image with the cardstock background, brass inset frame, and garnet category badge (used as the starting point by all 4 slide renderers).

- [ ] **Step 1: Write the failing test**

```python
def test_card_base_has_correct_dimensions():
    img = gic.draw_card_base("Idol Essentials")
    assert img.size == (gic.W, gic.H)
    assert img.mode == "RGB"


def test_card_base_frame_pixel_is_brass():
    img = gic.draw_card_base("Idol Essentials")
    # sample the top edge of the frame, away from the badge
    pixel = img.getpixel((gic.W // 2, gic.INSET))
    assert pixel == gic.BRASS


def test_card_base_background_is_cardstock_family():
    img = gic.draw_card_base("Idol Essentials")
    # sample a background pixel well inside the frame, away from the badge
    pixel = img.getpixel((gic.W - gic.INSET - 5, gic.H - gic.INSET - 5))
    assert pixel in (gic.CARDSTOCK, gic.CARDSTOCK_HI)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k card_base`
Expected: FAIL — `AttributeError: module 'generate_instagram_cards' has no attribute 'draw_card_base'`

- [ ] **Step 3: Implement**

Add to `scripts/generate_instagram_cards.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k card_base`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_instagram_cards.py scripts/test_generate_instagram_cards.py
git commit -m "Add shared card-base renderer to Instagram card generator"
```

---

### Task 7: Slide 1 — Hook

**Files:**
- Modify: `scripts/generate_instagram_cards.py`
- Modify: `scripts/test_generate_instagram_cards.py`

**Interfaces:**
- Consumes: `draw_card_base`, `draw_foil_gradient_text`, `load_font`, a `word` dict from `find_word`.
- Produces: `render_hook_slide(word: dict) -> Image.Image` (1080×1350 RGB).

Layout (per the approved spec's Slide Layout §1, corrected to use `en_short` instead of a fabricated Korean phrase): hero term in Black Han Sans + foil gradient in the upper third; a bottom-anchored block containing the `en_short` tag (JetBrains Mono Bold, brass) above the romanization formatted as phonetic notation (`/rom/`, JetBrains Mono Italic).

- [ ] **Step 1: Write the failing test**

```python
def test_hook_slide_has_correct_dimensions():
    word = gic.find_word("컴백")
    img = gic.render_hook_slide(word)
    assert img.size == (gic.W, gic.H)
    assert img.mode == "RGB"


def test_hook_slide_does_not_crash_on_long_en_short():
    word = dict(gic.find_word("컴백"))
    word["en_short"] = "A Very Long English Tag That Might Wrap Oddly"
    img = gic.render_hook_slide(word)
    assert img.size == (gic.W, gic.H)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k hook_slide`
Expected: FAIL — `AttributeError: module 'generate_instagram_cards' has no attribute 'render_hook_slide'`

- [ ] **Step 3: Implement**

Add to `scripts/generate_instagram_cards.py`:

```python
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
    block_h = len(tag_lines) * (tag_line_h + line_gap) + block_gap + rom_h

    bottom_margin = 90
    y = H - bottom_margin - block_h
    for line in tag_lines:
        draw.text((CONTENT_LEFT, y), line, font=tag_font, fill=BADGE_TEXT_BRASS)
        y += tag_line_h + line_gap
    y += block_gap - line_gap
    draw.text((CONTENT_LEFT, y - rom_bbox[1]), rom_text, font=rom_font, fill=CARD_INK_SOFT)

    return img
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k hook_slide`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_instagram_cards.py scripts/test_generate_instagram_cards.py
git commit -m "Add slide 1 (hook) renderer to Instagram card generator"
```

---

### Task 8: Slide 2 — Meaning

**Files:**
- Modify: `scripts/generate_instagram_cards.py`
- Modify: `scripts/test_generate_instagram_cards.py`

**Interfaces:**
- Consumes: `draw_card_base`, `load_font`, `wrap_text`.
- Produces: `render_meaning_slide(word: dict) -> Image.Image`.

Layout (spec §2): vertically centered; solid-ink Korean term (smaller, no foil — the foil treatment is spent once, on slide 1, per DESIGN.md's "One Foil Rule"), a garnet "MEANING" eyelabel, then the English `meaning_en` in Hanken Grotesk Bold, wrapped. No romanization line (removed during mockup review as redundant with slide 1).

- [ ] **Step 1: Write the failing test**

```python
def test_meaning_slide_has_correct_dimensions():
    word = gic.find_word("컴백")
    img = gic.render_meaning_slide(word)
    assert img.size == (gic.W, gic.H)


def test_meaning_slide_does_not_crash_on_long_definition():
    word = dict(gic.find_word("컴백"))
    word["meaning_en"] = (
        "A very long definition that should wrap across several lines "
        "without overflowing the card or raising any exception at all, "
        "even when it runs on for quite a while."
    )
    img = gic.render_meaning_slide(word)
    assert img.size == (gic.W, gic.H)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k meaning_slide`
Expected: FAIL — `AttributeError: module 'generate_instagram_cards' has no attribute 'render_meaning_slide'`

- [ ] **Step 3: Implement**

Add to `scripts/generate_instagram_cards.py`:

```python
def render_meaning_slide(word):
    img = draw_card_base(word["cat_en"])
    draw = ImageDraw.Draw(img)

    term_font = load_font("black_han_sans", 90)
    eyelabel_font = load_font("mono_bold", 22)
    def_font = load_font("hanken_bold", 44)

    y = int(H * 0.36)

    term_bbox = draw.textbbox((0, 0), word["kr"], font=term_font)
    draw.text((CONTENT_LEFT, y - term_bbox[1]), word["kr"], font=term_font, fill=CARD_INK)
    y += (term_bbox[3] - term_bbox[1]) + 36

    eyelabel = "MEANING"
    eyelabel_bbox = draw.textbbox((0, 0), eyelabel, font=eyelabel_font)
    draw.text((CONTENT_LEFT, y - eyelabel_bbox[1]), eyelabel, font=eyelabel_font, fill=GARNET)
    y += (eyelabel_bbox[3] - eyelabel_bbox[1]) + 24

    def_lines = wrap_text(draw, word["meaning_en"], def_font, CONTENT_WIDTH)
    line_h = def_font.size + 16
    for line in def_lines:
        line_bbox = draw.textbbox((0, 0), line, font=def_font)
        draw.text((CONTENT_LEFT, y - line_bbox[1]), line, font=def_font, fill=CARD_INK)
        y += line_h

    return img
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k meaning_slide`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_instagram_cards.py scripts/test_generate_instagram_cards.py
git commit -m "Add slide 2 (meaning) renderer to Instagram card generator"
```

---

### Task 9: Slide 3 — Real usage

**Files:**
- Modify: `scripts/generate_instagram_cards.py`
- Modify: `scripts/test_generate_instagram_cards.py`

**Interfaces:**
- Consumes: `draw_card_base`, `load_font`, `wrap_text`.
- Produces: `render_usage_slide(word: dict) -> Image.Image`.

Layout (spec §3): "REAL USAGE" eyelabel top-left; the Caption Bar component (near-black rounded box) **vertically centered** in the slide — fixed during mockup review from an earlier bottom-anchored draft. Korean example (`ex_kr`, Noto Sans KR Bold) above the English translation (`ex_en`). The translation uses Hanken Grotesk (matching the real site's Caption Bar component, which has no mono override on `.ds-cap-trans` per `design.json` — the mockup's JetBrains Mono translation was a rough-comp simplification, corrected here for DESIGN.md fidelity).

- [ ] **Step 1: Write the failing test**

```python
def test_usage_slide_has_correct_dimensions():
    word = gic.find_word("컴백")
    img = gic.render_usage_slide(word)
    assert img.size == (gic.W, gic.H)


def test_usage_slide_caption_bar_pixel_is_caption_black():
    word = gic.find_word("컴백")
    img = gic.render_usage_slide(word)
    # sample near vertical center, safely inside the bar's horizontal span
    pixel = img.getpixel((gic.W // 2, gic.H // 2))
    assert pixel == gic.CAPTION_BLACK
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k usage_slide`
Expected: FAIL — `AttributeError: module 'generate_instagram_cards' has no attribute 'render_usage_slide'`

- [ ] **Step 3: Implement**

Add to `scripts/generate_instagram_cards.py`:

```python
def render_usage_slide(word):
    img = draw_card_base(word["cat_en"])
    draw = ImageDraw.Draw(img)

    eyelabel_font = load_font("mono_bold", 22)
    eyelabel = "REAL USAGE"
    eyelabel_bbox = draw.textbbox((0, 0), eyelabel, font=eyelabel_font)
    draw.text(
        (CONTENT_LEFT, INSET + 40 - eyelabel_bbox[1]),
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k usage_slide`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_instagram_cards.py scripts/test_generate_instagram_cards.py
git commit -m "Add slide 3 (real usage) renderer to Instagram card generator"
```

---

### Task 10: Slide 4 — CTA

**Files:**
- Modify: `scripts/generate_instagram_cards.py`
- Modify: `scripts/test_generate_instagram_cards.py`

**Interfaces:**
- Consumes: `load_font`.
- Produces: `render_cta_slide() -> Image.Image` (takes no word — this slide's copy is fixed/site-branded, not per-word).

Layout (spec §4): charcoal background, garnet bookmark-icon outline, "HelloKSlang" wordmark, then "Save this card —" / "see you next time" as two separately-spaced lines (an earlier draft crammed these together), then the URL + "New slang daily" tagline with extra top margin. All copy is English — an earlier draft had this in Korean, corrected during mockup review.

- [ ] **Step 1: Write the failing test**

```python
def test_cta_slide_has_correct_dimensions():
    img = gic.render_cta_slide()
    assert img.size == (gic.W, gic.H)
    assert img.mode == "RGB"


def test_cta_slide_background_is_charcoal():
    img = gic.render_cta_slide()
    # sample a corner, well away from any text/icon
    pixel = img.getpixel((20, 20))
    assert pixel == gic.CHARCOAL_BACKDROP
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k cta_slide`
Expected: FAIL — `AttributeError: module 'generate_instagram_cards' has no attribute 'render_cta_slide'`

- [ ] **Step 3: Implement**

Add to `scripts/generate_instagram_cards.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k cta_slide`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_instagram_cards.py scripts/test_generate_instagram_cards.py
git commit -m "Add slide 4 (CTA) renderer to Instagram card generator"
```

---

### Task 11: `--carousel` CLI mode

**Files:**
- Modify: `scripts/generate_instagram_cards.py`
- Modify: `scripts/test_generate_instagram_cards.py`

**Interfaces:**
- Consumes: `find_word`, `output_dir`, `render_hook_slide`, `render_meaning_slide`, `render_usage_slide`, `render_cta_slide`.
- Produces: `generate_carousel(kr: str, date_str: str = None) -> list[str]` — renders all 4 slides, saves them as `slide-1.png`..`slide-4.png` in `output_dir(...)`, returns the 4 file paths in order. Re-raises `WordNotFoundError` from `find_word` unchanged (already has a clear message from Task 2).

- [ ] **Step 1: Write the failing test**

```python
def test_generate_carousel_writes_four_correctly_sized_pngs(tmp_path, monkeypatch):
    monkeypatch.setattr(gic, "REPO_ROOT", str(tmp_path))
    paths = gic.generate_carousel("컴백", date_str="2026-08-10")
    assert len(paths) == 4
    for path in paths:
        assert os.path.isfile(path)
        with Image.open(path) as img:
            assert img.size == (gic.W, gic.H)
            assert img.format == "PNG"
    assert paths[0].endswith("slide-1.png")
    assert paths[3].endswith("slide-4.png")


def test_generate_carousel_raises_word_not_found(tmp_path, monkeypatch):
    monkeypatch.setattr(gic, "REPO_ROOT", str(tmp_path))
    try:
        gic.generate_carousel("zzz-not-a-real-word-zzz", date_str="2026-08-10")
        assert False, "expected WordNotFoundError"
    except gic.WordNotFoundError:
        pass
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k generate_carousel`
Expected: FAIL — `AttributeError: module 'generate_instagram_cards' has no attribute 'generate_carousel'`

- [ ] **Step 3: Implement**

Add to `scripts/generate_instagram_cards.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k generate_carousel`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_instagram_cards.py scripts/test_generate_instagram_cards.py
git commit -m "Add --carousel generation orchestration to Instagram card generator"
```

---

### Task 12: `--new-word` CLI mode

**Files:**
- Modify: `scripts/generate_instagram_cards.py`
- Modify: `scripts/test_generate_instagram_cards.py`

**Interfaces:**
- Consumes: `db.NEW_WORDS_LOG` (list of `(date_str, [kr_words])`, newest first — same structure `generate_whatsnew.py` reads), `find_word`, `output_dir`, `render_hook_slide`.
- Produces: `generate_new_word_cards() -> list[str]` — for every word in `db.NEW_WORDS_LOG[0]`, renders the hook-slide layout as a single-image announcement and saves it as `slide-1.png` in its own `output_dir`; returns all resulting file paths. Raises `WordNotFoundError` (unchanged, from `find_word`) if a logged word can't be resolved — this is intentional: it means `NEW_WORDS_LOG` and the category tuples have drifted out of sync, which is worth surfacing loudly rather than silently skipping.

- [ ] **Step 1: Write the failing test**

```python
def test_generate_new_word_cards_writes_one_png_per_logged_word(tmp_path, monkeypatch):
    monkeypatch.setattr(gic, "REPO_ROOT", str(tmp_path))
    latest_date, latest_words = gic.db.NEW_WORDS_LOG[0]

    paths = gic.generate_new_word_cards()

    assert len(paths) == len(latest_words)
    for path in paths:
        assert os.path.isfile(path)
        assert path.endswith("slide-1.png")
        with Image.open(path) as img:
            assert img.size == (gic.W, gic.H)


def test_generate_new_word_cards_raises_if_log_word_missing_from_categories(tmp_path, monkeypatch):
    monkeypatch.setattr(gic, "REPO_ROOT", str(tmp_path))
    monkeypatch.setattr(
        gic.db, "NEW_WORDS_LOG",
        [("2026-08-10", ["zzz-not-a-real-word-zzz"])],
    )
    try:
        gic.generate_new_word_cards()
        assert False, "expected WordNotFoundError"
    except gic.WordNotFoundError:
        pass
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k new_word_cards`
Expected: FAIL — `AttributeError: module 'generate_instagram_cards' has no attribute 'generate_new_word_cards'`

- [ ] **Step 3: Implement**

Add to `scripts/generate_instagram_cards.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v -k new_word_cards`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_instagram_cards.py scripts/test_generate_instagram_cards.py
git commit -m "Add --new-word generation orchestration to Instagram card generator"
```

---

### Task 13: CLI entrypoint + end-to-end manual verification

**Files:**
- Modify: `scripts/generate_instagram_cards.py`

**Interfaces:**
- Consumes: `generate_carousel`, `generate_new_word_cards`.
- Produces: a working `python3 generate_instagram_cards.py --carousel "<word>"` / `--new-word` CLI.

- [ ] **Step 1: Replace the skeleton `if __name__ == "__main__": pass` block**

In `scripts/generate_instagram_cards.py`, replace:

```python
if __name__ == "__main__":
    pass
```

with:

```python
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
```

- [ ] **Step 2: Run the full test suite to make sure nothing broke**

Run: `cd scripts && python -m pytest test_generate_instagram_cards.py -v`
Expected: PASS (all tests from Tasks 1–12)

- [ ] **Step 3: Generate a real carousel and visually inspect it**

Run:
```bash
cd scripts
python3 generate_instagram_cards.py --carousel "컴백"
```

Open the 4 PNGs printed to stdout (under `assets/instagram/<today>-keom-baek/`) at real size (not thumbnails) and check, per the spec's Testing/Verification section:
- No text overflow or clipping on any slide
- Hangul renders in the correct font on slides 1 (tag — should be the Latin `en_short`, not Hangul), 2 (term), and 3 (quote) — slide 3's Korean quote is the one place Hangul body text appears
- The foil gradient is visible and legible across the hero term on slide 1
- Slide 3's caption bar is vertically centered, not bottom-anchored
- Slide 4's CTA lines have visible separation, not cramped together

- [ ] **Step 4: Generate new-word cards and visually inspect them**

Run:
```bash
python3 generate_instagram_cards.py --new-word
```

Confirm one PNG per word in the current `NEW_WORDS_LOG[0]` entry, laid out identically to carousel slide 1.

- [ ] **Step 5: Spot-check a long-copy word**

Find a word in `build_kslang_db.py` with a noticeably longer `meaning_en` or `ex_en` than "컴백" (e.g. one of the multi-clause definitions), run `--carousel` on it, and confirm slides 2 and 3 wrap correctly without overflowing the card — the automated tests in Tasks 8–9 check that wrapping doesn't crash, not that it looks good at real size.

- [ ] **Step 6: Commit**

```bash
git add scripts/generate_instagram_cards.py
git commit -m "Wire up CLI entrypoint for Instagram card generator"
```

---

### Task 14: Document the tool in CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Interfaces:** None (documentation only).

- [ ] **Step 1: Add a short section to CLAUDE.md**

Add a new section after the existing "인스타그램 홍보 (@hellokslang)" section (find it via the `## 인스타그램 홍보` heading):

```markdown
## 인스타그램 카드뉴스 자동 생성

`scripts/generate_instagram_cards.py` — `build_kslang_db.py` 데이터에서 인스타그램용 PNG 카드를 만드는 수동 도구. 5개 정기 빌드 스크립트와 달리 자동 리빌드 파이프라인에 안 걸려 있음 (콘텐츠 제작자가 그때그때 수동 실행).

```bash
cd scripts
python3 generate_instagram_cards.py --carousel "컴백"   # 요일별 카테고리 로테이션용 4장 세트
python3 generate_instagram_cards.py --new-word           # NEW_WORDS_LOG 최신 항목 → 신규 단어 발표용 1장씩
```

출력은 `assets/instagram/<날짜>-<로마자슬러그>/slide-N.png`. 폰트는 `assets/fonts/`에 미리 받아둔 로컬 파일 사용 (Pillow는 브라우저처럼 폰트 폴백을 안 해줌 — 위 "겪었던 버그들" #3과 동일한 종류의 함정). 설계 배경은 `docs/superpowers/specs/2026-08-09-instagram-carousel-generator-design.md` 참고.
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "Document the Instagram card generator in CLAUDE.md"
```

---

## Self-Review Notes

- **Spec coverage:** CLI interface (Task 13), data flow via `build_kslang_db` import (Task 2), font handling incl. the CLAUDE.md #3 bug (Task 1), foil gradient technique (Task 5), output naming/dimensions (Tasks 3, 11, 12), all 4 slide layouts (Tasks 7–10) including the two review-driven fixes (slide 1 overlap → real gap in Task 7; slide 3 bottom-anchored → centered in Task 9) and the two copy fixes (slide 2 English def, slide 4 English CTA), error handling for unresolved words in both modes (Tasks 2, 11, 12), and the manual visual-verification step from the spec's Testing section (Task 13) are all covered.
- **Placeholder scan:** no TBD/TODO; every step has runnable code.
- **Type/signature consistency:** `word` is a `dict` with a fixed key set from `find_word` (Task 2) and is threaded unchanged through Tasks 7–12; `render_cta_slide()` intentionally takes no `word` argument since its copy is fixed, called with no args in both Task 10's tests and Task 11's `generate_carousel`. `output_dir(word, date_str)` signature (Task 3) matches every call site in Tasks 11–12.
- **Known gap resolved during planning:** the spec originally described a Korean meaning line on slide 1 that has no backing data field — corrected in the spec (commit `7ab9eb9`) and reflected consistently in Task 7's implementation.

---

**Plan complete and saved to `docs/superpowers/plans/2026-08-10-instagram-carousel-generator.md`.** Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

**Which approach?**
