# -*- coding: utf-8 -*-
"""
Lightweight safety net for the automated rebuild pipeline.

Scans every word entry in build_kslang_db.py for a small set of red-flag
keywords (sexual/explicit content markers). This does NOT replace human
judgment when adding new words by hand — it's a last-resort guard rail so
that if something inappropriate ever slips into build_kslang_db.py, the
GitHub Actions rebuild fails loudly instead of silently publishing it.

Exits with status 1 (failing the CI job) if anything is flagged.
"""
import os
import sys
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import build_kslang_db as db

RISKY_KEYWORDS = [
    "sex", "porn", "fuck", "nude", "explicit", "penis", "vagina", "orgasm",
    "섹스", "19금", "자위", "음란",
]


def main():
    flagged = []
    total = 0
    for cat_kr, cat_en, terms in db.CATEGORIES:
        for t in terms:
            total += 1
            text = json.dumps(t, ensure_ascii=False).lower()
            for kw in RISKY_KEYWORDS:
                if kw.lower() in text:
                    flagged.append((t[0], kw))

    if flagged:
        print("SAFETY CHECK FAILED — flagged terms found:")
        for term, kw in flagged:
            print(f"  {term!r} -> matched keyword {kw!r}")
        print("\nFix or remove these entries in scripts/build_kslang_db.py before merging.")
        sys.exit(1)

    print(f"Safety check passed. {total} terms scanned, 0 flags.")


if __name__ == "__main__":
    main()
