# Instagram Carousel Card Generator — Design

**Date:** 2026-08-09
**Status:** Approved by user, pending implementation plan

## Overview

A Python script that auto-generates Instagram carousel/single-image PNGs from HelloKSlang's existing 651-word database, so `@hellokslang` can produce on-brand card content without hand-designing each post.

Two output modes:
- **Carousel (4 slides)** for the regular weekday category-rotation content (per CLAUDE.md's 인스타그램 홍보 section: idol terms Mon, memes Tue, fandom Wed, broadcast/variety Thu, dating/romance Fri).
- **New-word announcement (1 slide)** for words freshly added to the dictionary, sourced from the same `NEW_WORDS_LOG` that powers `whatsnew.html`.

## Goals

- Reuse the site's existing "Photocard Pull" materials (charcoal/cardstock/garnet/brass/foil) but scaled up and simplified for a bold, scroll-stopping SNS crop — not a literal 1:1 reuse of the site's card component.
- Zero new data entry: read directly from `scripts/build_kslang_db.py`, the single source of truth.
- Output ready-to-upload PNGs, no manual post-processing step.

## Non-goals (explicitly deferred)

- Spanish-language card variants (PRODUCT.md lists ES as a target audience, but the user chose English-only for this first version; revisit once the English pipeline is validated).
- Automatic word selection by weekday/category rotation — a human picks the word and passes it as a CLI argument for now, to avoid duplicate-avoidance/scheduling logic that isn't needed yet.
- Filtering by data `status` field (`Verified (web-checked)` vs `Draft — please double-check`) — the user chose to include both for now.
- Actual Instagram posting/scheduling (Meta Business Suite, per CLAUDE.md, remains a manual/separate step).

## CLI Interface

```bash
cd scripts
python3 generate_instagram_cards.py --carousel "컴백"
python3 generate_instagram_cards.py --new-word
```

- `--carousel "<한글 단어>"`: generates the 4-slide deep-dive set for one word. The word must match a `kr` field exactly in `build_kslang_db.py` (same matching convention already used by `NEW_WORDS_LOG`); exit with a clear error listing near-matches if not found.
- `--new-word`: reads `db.NEW_WORDS_LOG[0]` (the newest date entry) and generates one single-slide announcement card per word in that entry's word list.

## Data Flow

Follows the exact pattern already established in `scripts/update_main_pages.py`:

```python
sys.path.insert(0, SCRIPT_DIR)
import build_kslang_db as db
```

Then iterate `db.CATEGORIES` to find the matching `(kr, rom, en_short, meaning_en, meaning_es, ex_kr, ex_en, ex_es, where, status)` tuple by `kr`, plus the owning `(cat_kr, cat_en)`. No xlsx parsing, no JSON export step — this script reads the same Python data every other generator script reads.

## Rendering Approach

Pillow (PIL), matching the precedent already set by `assets/og-image.png`. No browser/Node rendering pipeline — this is a pure Python script consistent with the rest of `scripts/`.

**Fonts:** the site links all fonts from Google Fonts CDN (`index.html`); Pillow needs local font files, so this project adds `assets/fonts/` with the specific weights actually used below, downloaded once from Google Fonts (all OFL-licensed, safe to commit):
- Black Han Sans (Regular) — Korean display face, term + CTA wordmark
- Hanken Grotesk (Bold) — English definition (slide 2)
- Bricolage Grotesque (Bold) — CTA headline (slide 4)
- Noto Sans KR (Bold) — every other place Korean text appears (slide 1 meaning line, slide 3 caption bar quote) — this is the specific fix for the bug already logged in CLAUDE.md #3: Pillow does not font-fallback the way browsers do, so any Hangul glyph must be explicitly set in a Hangul-capable font or it renders as tofu/wrong-font.
- JetBrains Mono (Bold + Italic) — category badge, romanization, mono labels, caption source line

**Foil gradient text** (slide 1 hero term only, matching DESIGN.md's "One Foil Rule"): Pillow has no native CSS-style `background-clip: text`. Implemented as: render the term as a white-on-black mask via `ImageDraw.text`, generate the foil gradient (`#6E5419 → #C9A64C → #EBD08A → #C9A64C → #7A5E1E`) as a separate image, then `Image.composite()` the gradient through the text mask.

## Output

- **Dimensions:** 1080×1350px (Instagram portrait 4:5) for every slide.
- **Format:** PNG.
- **Location/naming:** `assets/instagram/<YYYY-MM-DD>-<word-romanization-slug>/slide-1.png` … `slide-4.png` (carousel) or a single `slide-1.png` (new-word). Date is generation date; romanization slug (e.g. `keom-baek`) keeps filenames ASCII-safe and matches the `rom` field already in the data.

## Slide Layout Spec

Confirmed through interactive mockup review (`.superpowers/brainstorm/631-1786286060/content/carousel-sequence-v5.html`). All four slides share: cardstock gradient background (`#F2E9D8` → `#F8F1E3` → `#F2E9D8`), a 2px brass (`#B4923F`) inset frame, brass category badge top-left (`#B21B3E` pill, white JetBrains Mono uppercase), except slide 4 which is charcoal (`#151217`).

1. **Hook.** Hero term in Black Han Sans + foil gradient, positioned upper-third. Below it, a bottom-anchored block (flex column, real gap — this fixes an earlier text-overlap bug found during review) containing: the short English tag (`en_short` field, e.g. "Comeback") in JetBrains Mono/brass (`#7A6224`) — corrected during plan review from an earlier mockup that used an invented Korean phrase with no corresponding data field — then romanization in JetBrains Mono italic, formatted as phonetic notation (`/keom-baek/`, not bare `keom-baek`).
2. **Meaning.** Centered vertically. Korean term (smaller, Black Han Sans, solid ink color — no foil here, per "One Foil Rule": only spent once per card and slide 1 already spent it), "Meaning" eyelabel in garnet JetBrains Mono, then the **English** definition (`meaning_en` field) in Hanken Grotesk Bold. No romanization line on this slide (removed during review — redundant with slide 1).
3. **Real usage.** Cardstock background, "Real usage" eyelabel top-left, and the Caption Bar component (near-black `#100E13` box, matching DESIGN.md's Caption Bar) **vertically centered** in the slide (not bottom-anchored, per review feedback) — Korean example quote (`ex_kr`, Noto Sans KR Bold) then the English translation (`ex_en`, JetBrains Mono, muted) beneath it.
4. **CTA.** Charcoal background. Save/bookmark icon (garnet outline SVG-equivalent line-draw), "HelloKSlang" wordmark (Black Han Sans), then "Save this card —" / "see you next time" as two separately-spaced lines (Bricolage Grotesque Bold — an earlier draft crammed these into one cramped block; each line now gets explicit margin), then the site URL + "New slang daily" tagline in muted JetBrains Mono, with extra top margin so it doesn't crowd the line above it. All CTA copy is English (an earlier draft had this in Korean; corrected during review). Slide 1's meaning line stays Korean deliberately — it's the scroll-stopping hook, not explanatory copy.

The new-word single-slide format reuses slide 1's exact layout as a standalone image.

## Error Handling

- `--carousel` with a `kr` not found in any category: print the closest matches (simple substring/fuzzy check against all `kr` fields) and exit non-zero — don't silently generate a blank card.
- `--new-word` when `NEW_WORDS_LOG` is empty or the latest entry's words don't resolve in `CATEGORIES`: exit with a clear error naming the missing word — this would indicate `NEW_WORDS_LOG` and the category tuples have drifted out of sync, which is also possible today and worth surfacing rather than crashing on a `None` lookup.
- Missing font files in `assets/fonts/`: fail fast at script start with a message naming the missing file, before any partial output is written.

## Testing / Verification

- Generate the `--carousel "컴백"` and `--new-word` cases and visually inspect the PNGs at real size (not just thumbnails) for text overflow, Hangul rendering, and gradient/mask correctness — same categories of bug already found during the mockup review (overlap, wrong font, off-center element) apply here since it's the same composition, just rendered a different way.
- Spot-check one long-definition word and one long-example word to make sure `meaning_en`/`ex_en` text wrapping doesn't overflow the card at 1080×1350 (the mockup review only tested "컴백", which has short copy).

## Open Follow-ups (not blocking this script)

- Spanish card variant, once English is validated.
- Category/weekday-rotation auto-selection, if manual picking proves to be a bottleneck.
- Whether to also filter out `Draft — please double-check` entries once real posting cadence starts (currently: no filter).
