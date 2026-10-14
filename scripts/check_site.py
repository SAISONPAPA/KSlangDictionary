# -*- coding: utf-8 -*-
"""Post-build sanity checks. Run AFTER the full build pipeline; exits non-zero on problems.

  python3 check_site.py

Checks:
  - no "null"/"undefined" leaked into visible HTML text
  - every element with data-en also has data-es / data-zh / data-cn / data-ja
  - EDITOR_PICKS / TODAYS_CARD_POOL / QUIZ only use words that exist; quiz words are Verified
  - every word has all 3 translations + DETAILS
  - every page in word/ that the DB expects exists
"""
import os, re, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import build_kslang_db as db
from generate_word_pages import slugify

problems = []
terms = {t[0]: t for _, _, ts in db.CATEGORIES for t in ts}

for name, d in (("ZH_TW", db.ZH_TW_TRANSLATIONS), ("ZH_CN", db.ZH_CN_TRANSLATIONS), ("JA", db.JA_TRANSLATIONS), ("DETAILS", db.DETAILS)):
    miss = [k for k in terms if k not in d]
    if miss: problems.append(f"{name} missing for: {miss[:10]}")

for k, t in terms.items():
    if not os.path.exists(os.path.join(ROOT, "word", slugify(t[1]) + ".html")):
        problems.append(f"word page missing: {k} ({t[1]})")

for name in ("EDITOR_PICKS", "TODAYS_CARD_POOL"):
    bad = [w for w in getattr(db, name) if w not in terms]
    if bad: problems.append(f"{name}: not in DB {bad}")
if len(db.EDITOR_PICKS) < 3: problems.append("EDITOR_PICKS needs at least 3 words")

for i, q in enumerate(db.QUIZ, 1):
    for w in q["options"]:
        if w not in terms: problems.append(f"QUIZ {i}: {w} not in DB")
        elif not terms[w][-1].startswith("Verified"): problems.append(f"QUIZ {i}: {w} is not Verified")
    if q["answer"] not in q["options"]: problems.append(f"QUIZ {i}: answer not in options")
    if len(set(q["options"])) != len(q["options"]): problems.append(f"QUIZ {i}: duplicate options")

pages = [p for p in glob.glob(os.path.join(ROOT, "*.html")) + glob.glob(os.path.join(ROOT, "word", "*.html"))
         + glob.glob(os.path.join(ROOT, "guides", "*.html")) + glob.glob(os.path.join(ROOT, "quiz", "*.html"))]
for p in pages:
    h = open(p, encoding="utf-8").read()
    rel = os.path.relpath(p, ROOT)
    if re.search(r">\s*(null|undefined)\s*<", h) or re.search(r'data-(en|es|zh|cn|ja)="(null|undefined)"', h):
        problems.append(f"{rel}: null/undefined leaked")
    if rel == "privacy.html": continue
    for el in re.findall(r'<[^>]*\sdata-en="[^"]*"[^>]*>', h):
        lack = [l for l in ("es", "zh", "cn", "ja") if f"data-{l}=" not in el]
        if lack:
            problems.append(f"{rel}: element missing data-{'/'.join(lack)}: {el[:90]}")
            break

if problems:
    print("CHECK FAILED:")
    for x in problems: print(" -", x)
    sys.exit(1)
print(f"check_site OK — {len(terms)} words, {len(pages)} pages, {len(db.QUIZ)} quiz questions, picks {db.EDITOR_PICKS}")
