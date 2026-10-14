# -*- coding: utf-8 -*-
"""
Generates the topic guides from COLLECTIONS / GUIDES_HUB in build_kslang_db.py:

    guides/index.html          — hub listing every guide
    guides/<slug>.html         — one page per collection

A guide = short intro + themed sections + each word's existing five-language
meaning, linking to its word page. Page chrome (header, footer, base styles,
language toggle script) is reused from generate_word_pages.py so guides look
and behave exactly like word pages (same ../ relative paths, one level deep).

Run after generate_word_pages.py. Also wired into .github/workflows/rebuild.yml.
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_kslang_db as db
import generate_word_pages as wp

OUTPUT_DIR = os.path.join(wp.SCRIPT_DIR, "..", "guides")
LANGS = wp.LANGS
esc = wp.esc

GUIDE_UI = {
    "all_guides": {"en": "← All guides", "es": "← Todas las guías", "zh": "← 所有指南", "cn": "← 所有指南", "ja": "← ガイド一覧"},
    "more_guides": {"en": "More guides", "es": "Más guías", "zh": "更多指南", "cn": "更多指南", "ja": "ほかのガイド"},
    "words_count": {"en": "words", "es": "palabras", "zh": "個詞", "cn": "个词", "ja": "語"},
    "open_guide": {"en": "Open guide →", "es": "Abrir guía →", "zh": "打開指南 →", "cn": "打开指南 →", "ja": "ガイドを見る →"},
    "back_dict": {"en": "← Back to search", "es": "← Volver a la búsqueda", "zh": "← 回到搜尋", "cn": "← 返回搜索", "ja": "← 検索に戻る"},
}


def attrs(d):
    """data-en/es/zh/cn/ja attributes from a {lang: text} dict."""
    return " ".join(f'data-{l}="{esc(d[l])}"' for l in LANGS)


def meanings(item):
    """Five-language meaning for a word, using the same sources as word pages."""
    kr = item[0]
    return {
        "en": item[3],
        "es": item[4],
        "zh": db.ZH_TW_TRANSLATIONS.get(kr, (item[3],))[0],
        "cn": db.ZH_CN_TRANSLATIONS.get(kr, (item[3],))[0],
        "ja": db.JA_TRANSLATIONS.get(kr, (item[3],))[0],
    }


GUIDE_CSS = """
  .guide-head{ margin: 6px 0 30px; max-width: 760px; }
  .guide-head .page-title{ font-family: var(--display); font-weight: 800; font-size: clamp(30px, 5vw, 46px); line-height: 1.12; letter-spacing: -0.02em; color: var(--ink); }
  .guide-intro{ margin-top: 14px; font-size: 16px; line-height: 1.7; color: var(--ink-soft); }
  .guide-section{ margin-top: 40px; }
  .guide-section h2{ font-family: var(--display); font-weight: 700; font-size: 21px; color: var(--ink); margin-bottom: 18px; }
  .guide-grid{ display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 18px 16px; padding-top: 8px; }
  .guide-grid .related-card{ display:block; }
  .guide-grid .r-top{ display:flex; align-items:baseline; gap: 10px; flex-wrap: wrap; }
  .guide-grid .r-rom{ font-family: var(--mono); font-style: italic; font-size: 12px; color: var(--card-ink-soft); }
  .guide-grid .r-short{ margin-top: 2px; font-size: 13px; font-weight: 700; color: var(--card-ink); }
  .guide-grid .r-gloss{ white-space: normal; overflow: visible; text-overflow: clip; margin-top: 6px; font-size: 13.5px; line-height: 1.55; }
  .hub-grid{ display:grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 20px 18px; padding-top: 10px; }
  .hub-card{ display:flex; flex-direction:column; gap: 10px; }
  .hub-card h2{ font-family: var(--display); font-weight: 800; font-size: 20px; color: var(--card-ink); line-height: 1.25; }
  .hub-card .hub-intro{ font-size: 13.5px; line-height: 1.6; color: var(--card-ink-soft); }
  .hub-card .hub-sample{ font-family: var(--font-kr); font-size: 17px; color: var(--card-ink); }
  .hub-card .hub-meta{ margin-top: auto; font-family: var(--mono); font-size: 11px; color: var(--garnet); font-weight: 700; letter-spacing: .4px; }
  .more-guides{ margin-top: 48px; display:flex; flex-wrap:wrap; gap: 10px; }
  .more-guides h2{ width:100%; font-family: var(--display); font-weight:700; font-size: 19px; color: var(--ink); margin-bottom: 6px; }
  .more-guides a{ padding: 10px 16px; border-radius: 999px; border: 1px solid var(--line-strong, rgba(243,236,221,.22)); color: var(--ink); font-weight: 700; font-size: 14px; }
  .more-guides a:hover{ border-color: var(--garnet-bright); }
  @media (max-width: 860px){ .hub-grid{ grid-template-columns: 1fr; } }
  @media (max-width: 600px){ .guide-grid{ grid-template-columns: 1fr; } }
"""


def mark_active(html, href):
    """Highlight the current section in the shared header (desktop + mobile menu)."""
    return html.replace(f'<a href="{href}" ', f'<a href="{href}" class="active" aria-current="page" ')


def page_shell(title, meta_desc, canonical, json_ld_obj, body):
    json_ld = ('<script type="application/ld+json">\n'
               + json.dumps(json_ld_obj, ensure_ascii=False) + "\n</script>")
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={wp.GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{wp.GA_ID}');
</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(meta_desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="HelloKSlang">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(meta_desc)}">
<meta property="og:image" content="{wp.SITE_URL}/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(meta_desc)}">
<meta name="twitter:image" content="{wp.SITE_URL}/assets/og-image.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700;12..96,800&family=Hanken+Grotesk:ital,wght@0,400;0,500;0,600;0,700;0,800;1,500&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
{json_ld}
<style>
{wp.SHARED_CSS}{GUIDE_CSS}</style>
<link rel="stylesheet" href="../assets/pokku.css">
</head>
<body>
{wp.DIRECTION_CONTRACT_HTML}
<a class="skip-link" href="#main">Skip to content</a>

{wp.HEADER_HTML}

<main class="wrap" id="main">
{body}
</main>

{wp.FOOTER_HTML}

{wp.SCRIPT_TEMPLATE}
</body>
</html>
'''


def short_desc(text, limit=155):
    return text if len(text) <= limit else text[:limit - 3].rsplit(" ", 1)[0] + "…"


def build_guide(c, by_kr):
    slug = c["slug"]
    url = f"{wp.SITE_URL}/guides/{slug}.html"
    sections_html, item_urls = [], []
    for s in c["sections"]:
        cards = []
        for kr in s["words"]:
            it = by_kr[kr]
            wslug = wp.slugify(it[1])
            item_urls.append(f"{wp.SITE_URL}/word/{wslug}.html")
            gloss = "".join(
                f'<p class="r-gloss lx" data-l="{l}" lang="{ {"zh": "zh-Hant", "cn": "zh-Hans"}.get(l, l) }">{esc(t)}</p>'
                for l, t in meanings(it).items()
            )
            cards.append(
                f'      <a class="related-card" href="../word/{esc(wslug)}.html">\n'
                f'        <div class="r-top"><span class="r-kr" lang="ko">{esc(kr)}</span><span class="r-rom">{esc(it[1])}</span></div>\n'
                f'        <div class="r-short">{esc(it[2])}</div>\n'
                f'        {gloss}\n'
                f'      </a>'
            )
        sections_html.append(
            f'  <section class="guide-section">\n'
            f'    <h2 {attrs(s["heading"])}>{esc(s["heading"]["en"])}</h2>\n'
            f'    <div class="guide-grid">\n' + "\n".join(cards) + '\n    </div>\n  </section>'
        )
    others = "".join(
        f'\n    <a href="{esc(o["slug"])}.html" {attrs(o["title"])}>{esc(o["title"]["en"])}</a>'
        for o in db.COLLECTIONS if o["slug"] != slug
    )
    body = (
        f'  <a href="index.html" class="back-link" {attrs(GUIDE_UI["all_guides"])}>{esc(GUIDE_UI["all_guides"]["en"])}</a>\n'
        f'  <div class="guide-head">\n'
        f'    <h1 class="page-title" {attrs(c["title"])}>{esc(c["title"]["en"])}</h1>\n'
        f'    <p class="guide-intro" {attrs(c["intro"])}>{esc(c["intro"]["en"])}</p>\n'
        f'  </div>\n' + "\n".join(sections_html) +
        f'\n  <nav class="more-guides" aria-label="More guides">\n    <h2 {attrs(GUIDE_UI["more_guides"])}>More guides</h2>{others}\n  </nav>'
    )
    ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": c["title"]["en"],
        "description": c["intro"]["en"],
        "url": url,
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(item_urls),
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": u} for i, u in enumerate(item_urls)],
        },
    }
    title = f'{c["title"]["en"]} — HelloKSlang Guides'
    return slug, page_shell(title, short_desc(c["intro"]["en"]), url, ld, body)


def build_hub(by_kr):
    url = f"{wp.SITE_URL}/guides/"
    cards = []
    for c in db.COLLECTIONS:
        words = [w for s in c["sections"] for w in s["words"]]
        n = len(words)
        count = {l: f'{n} {GUIDE_UI["words_count"][l]}' for l in LANGS}
        cards.append(
            f'    <a class="related-card hub-card" href="{esc(c["slug"])}.html">\n'
            f'      <h2 {attrs(c["title"])}>{esc(c["title"]["en"])}</h2>\n'
            f'      <div class="hub-sample" lang="ko">{esc(" · ".join(words[:4]))}</div>\n'
            f'      <p class="hub-intro" {attrs(c["intro"])}>{esc(c["intro"]["en"])}</p>\n'
            f'      <span class="hub-meta"><span {attrs(count)}>{esc(count["en"])}</span> · <span {attrs(GUIDE_UI["open_guide"])}>{esc(GUIDE_UI["open_guide"]["en"])}</span></span>\n'
            f'    </a>'
        )
    hub = db.GUIDES_HUB
    body = (
        f'  <a href="../index.html" class="back-link" {attrs(GUIDE_UI["back_dict"])}>{esc(GUIDE_UI["back_dict"]["en"])}</a>\n'
        f'  <div class="guide-head">\n'
        f'    <h1 class="page-title" {attrs(hub["title"])}>{esc(hub["title"]["en"])}</h1>\n'
        f'    <p class="guide-intro" {attrs(hub["intro"])}>{esc(hub["intro"]["en"])}</p>\n'
        f'  </div>\n'
        f'  <div class="hub-grid">\n' + "\n".join(cards) + '\n  </div>'
    )
    ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": hub["title"]["en"],
        "description": hub["intro"]["en"],
        "url": url,
        "hasPart": [{"@type": "CollectionPage", "name": c["title"]["en"],
                     "url": f'{wp.SITE_URL}/guides/{c["slug"]}.html'} for c in db.COLLECTIONS],
    }
    return page_shell(f'{hub["title"]["en"]} — HelloKSlang', short_desc(hub["intro"]["en"]), url, ld, body)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    by_kr = {it[0]: it for _, _, terms in db.CATEGORIES for it in terms}
    for c in db.COLLECTIONS:
        missing = [w for s in c["sections"] for w in s["words"] if w not in by_kr]
        if missing:
            raise SystemExit(f"COLLECTIONS '{c['slug']}' lists words not in the database: {missing}")
    count = 0
    for c in db.COLLECTIONS:
        slug, html = build_guide(c, by_kr)
        with open(os.path.join(OUTPUT_DIR, slug + ".html"), "w", encoding="utf-8") as f:
            f.write(mark_active(html, "../guides/index.html"))
        count += 1
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(mark_active(build_hub(by_kr), "../guides/index.html"))
    print(f"guides generated: hub + {count} collection pages in ./guides/")


if __name__ == "__main__":
    main()
