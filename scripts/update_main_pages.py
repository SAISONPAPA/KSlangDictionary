# -*- coding: utf-8 -*-
"""
Regenerates the embedded SLANG_DB JavaScript array inside the 4 main site
pages (index.html, category.html, trending.html, submit.html) from the
current word list in build_kslang_db.py.

This replaces the manual "extract JSON, regex-replace into each file" step
that used to be done by hand after every word-list update. Run directly,
or let the GitHub Actions workflow run it automatically.
"""
import os
import re
import sys
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(SCRIPT_DIR, "..")
sys.path.insert(0, SCRIPT_DIR)
import build_kslang_db as db

MAIN_PAGES = ["index.html", "category.html", "trending.html", "submit.html"]


def js_list(words):
    return "[" + ", ".join("'" + w.replace("'", "\\'") + "'" for w in words) + "]"


PICK_ARRAYS = {
    # page: [(JS const name, word list)]
    "index.html": [("HOME_TRENDING", lambda: db.EDITOR_PICKS[:3]),
                   ("TODAYS_CARD_POOL", lambda: db.TODAYS_CARD_POOL)],
    "trending.html": [("TRENDING_ORDER", lambda: db.EDITOR_PICKS)],
}


def inject_picks(fname, html):
    """Write EDITOR_PICKS / TODAYS_CARD_POOL from build_kslang_db.py into the page's JS."""
    all_kr = {t[0] for _, _, terms in db.CATEGORIES for t in terms}
    for const, get in PICK_ARRAYS.get(fname, []):
        words = get()
        missing = [w for w in words if w not in all_kr]
        if missing:
            raise SystemExit(f"ERROR: {const} has words not in the DB: {missing}")
        html, n = re.subn(r"const " + const + r" = \[[^\]]*\];",
                          "const " + const + " = " + js_list(words) + ";", html, count=1)
        if n != 1:
            print(f"WARNING: {fname} — {const} not found. Left unchanged.")
    return html


def main():
    data = []
    for cat_kr, cat_en, terms in db.CATEGORIES:
        for (kr, rom, en_short, meaning_en, meaning_es, ex_kr, ex_en, ex_es, where, status) in terms:
            zh_tw = db.ZH_TW_TRANSLATIONS.get(kr)
            meaning_zh, ex_zh = zh_tw if zh_tw else (meaning_en, ex_en)
            zh_cn = db.ZH_CN_TRANSLATIONS.get(kr)
            meaning_zh_cn, ex_zh_cn = zh_cn if zh_cn else (meaning_en, ex_en)
            ja = db.JA_TRANSLATIONS.get(kr)
            meaning_ja, ex_ja = ja if ja else (meaning_en, ex_en)
            data.append({
                "kr": kr, "rom": rom, "catKr": cat_kr, "catEn": cat_en,
                "meaningEn": meaning_en, "meaningEs": meaning_es,
                "meaningZh": meaning_zh, "meaningZhCn": meaning_zh_cn, "meaningJa": meaning_ja,
                "exKr": ex_kr, "exEn": ex_en, "exEs": ex_es,
                "exZh": ex_zh, "exZhCn": ex_zh_cn, "exJa": ex_ja, "where": where,
            })
    new_json = json.dumps(data, ensure_ascii=False)

    pattern = re.compile(r"const SLANG_DB = \[.*?\];", re.S)

    for fname in MAIN_PAGES:
        path = os.path.join(REPO_ROOT, fname)
        with open(path, encoding="utf-8") as f:
            html = f.read()
        new_html, n = pattern.subn("const SLANG_DB = " + new_json + ";", html, count=1)
        if n != 1:
            print(f"WARNING: {fname} — expected 1 replacement, got {n}. Left unchanged.")
            continue
        new_html = inject_picks(fname, new_html)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_html)
        print(f"{fname}: updated ({len(data)} terms, {len(db.ZH_TW_TRANSLATIONS)} 繁中 / {len(db.ZH_CN_TRANSLATIONS)} 简中 / {len(db.JA_TRANSLATIONS)} 日本語)")


if __name__ == "__main__":
    main()
