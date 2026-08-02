# -*- coding: utf-8 -*-
"""
Generates one lightweight, SEO-friendly static HTML page per HelloKSlang dictionary
word (517 pages), from the same source data used for the xlsx / main site.

No server, no database — just run this script and it writes word/*.html files.
Re-run any time the word list in build_kslang_db.py changes.
"""
import re
import os
import sys
import json
import html as html_escape_lib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_kslang_db as db

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "word")

# Single place to update if the domain ever changes again.
SITE_URL = "https://hellokslang.com"
GA_ID = "G-F475ZTL1ZV"

CATEGORY_URL = {
    "Idol Essentials": "category.html?cat=Idol%20Essentials",
    "Fandom Feels": "category.html?cat=Fandom%20Feels",
    "Broadcast & Variety": "category.html?cat=Broadcast%20%26%20Variety",
    "Online Memes": "category.html?cat=Online%20Memes",
    "Dating & Romance": "category.html?cat=Dating%20%26%20Romance",
}


def slugify(rom):
    s = rom.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def esc(s):
    return html_escape_lib.escape(s, quote=True)


SHARED_CSS = """
  :root{
    --bg: #0D0817;
    --surface: #17111F;
    --surface-2: #1E1729;
    --line: #2E2440;
    --ink: #F6F2FB;
    --ink-soft: #A99FBD;
    --pink: #FF3D9A;
    --violet: #A855F7;
    --cyan: #38BDF8;
    --gold: #FBBF24;
    --holo: linear-gradient(115deg, #FF3D9A 0%, #A855F7 25%, #38BDF8 50%, #FBBF24 75%, #FF3D9A 100%);
    --display: 'Black Han Sans', sans-serif;
    --body: 'Plus Jakarta Sans', sans-serif;
    --mono: 'JetBrains Mono', monospace;
  }
  *{ box-sizing: border-box; margin:0; padding:0; }
  body{
    background: var(--bg); color: var(--ink); font-family: var(--body);
    -webkit-font-smoothing: antialiased; overflow-x: hidden; position: relative;
  }
  body::before, body::after{
    content:""; position:fixed; width: 420px; height: 420px; border-radius:50%;
    filter: blur(140px); opacity:.22; z-index:0; pointer-events:none;
  }
  body::before{ background: var(--pink); top:-120px; left:-120px; }
  body::after{ background: var(--cyan); bottom:-140px; right:-120px; }
  a{ color:inherit; text-decoration:none; }
  .wrap{ max-width: 860px; margin: 0 auto; padding: 0 28px; position: relative; z-index: 1; }
  @keyframes holoShift{ 0%,100%{ background-position: 0% 50%; } 50%{ background-position: 100% 50%; } }
  @keyframes playPulse{ 0%,100%{ transform: scale(1); } 50%{ transform: scale(1.18); } }
  @media (prefers-reduced-motion: reduce){ *{ animation-duration: 0.001ms !important; animation-iteration-count: 1 !important; } }

  header{
    position: sticky; top: 0; z-index: 50;
    background: rgba(13,8,23,0.72); backdrop-filter: blur(14px);
    border-bottom: 1px solid var(--line);
  }
  .nav{ display:flex; align-items:center; justify-content:space-between; height: 76px; max-width:1180px; margin:0 auto; padding:0 28px; }
  .logo{ display:flex; align-items:center; gap: 8px; font-family: var(--display); font-size: 24px; letter-spacing: 0.5px; }
  .logo .dot{ color: var(--pink); }
  .logo-badge{
    font-family: var(--mono); font-size: 10px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;
    color: var(--violet); background: rgba(168,85,247,.15); border: 1px solid rgba(168,85,247,.4);
    padding: 3px 8px; border-radius: 999px; white-space: nowrap;
  }
  .nav-links{ display:flex; gap: 28px; font-weight: 600; font-size: 14px; color: var(--ink-soft); }
  .nav-links a:hover{ color: var(--ink); }
  .menu-toggle{
    display:none; width: 38px; height: 38px; align-items:center; justify-content:center;
    border-radius: 999px; border: 1px solid var(--line); background: var(--surface); color: var(--ink);
    font-size: 16px; cursor:pointer; flex-shrink:0;
  }
  .menu-toggle:hover{ border-color: var(--pink); }
  .mobile-menu{ display:none; flex-direction:column; background: var(--surface); border-top: 1px solid var(--line); padding: 6px 28px 18px; }
  .mobile-menu.open{ display:flex; }
  .mobile-menu a{ padding: 14px 0; font-weight: 700; font-size: 15px; color: var(--ink); border-bottom: 1px solid var(--line); }
  .mobile-menu a:last-child{ border-bottom:none; }

  main{ padding: 44px 0 60px; }
  .back-link{ display:inline-flex; align-items:center; gap: 6px; font-size: 13.5px; font-weight: 700; color: var(--violet); margin-bottom: 26px; }
  .back-link:hover{ text-decoration: underline; }
  .cat-pill{
    display:inline-block; font-size: 11px; font-weight:700; letter-spacing:.4px; text-transform:uppercase;
    padding: 5px 12px; border-radius: 999px; background: rgba(168,85,247,.15); color: var(--violet); margin-bottom: 18px;
  }
  .cat-pill:hover{ background: rgba(168,85,247,.28); }

  .word-card{
    background: var(--surface); border: 1px solid var(--line); border-radius: 22px;
    padding: 36px; position: relative; overflow: hidden;
  }
  .word-card::before{
    content:""; position:absolute; top:0; left:0; right:0; height: 3px;
    background: var(--holo); background-size: 300% 300%; animation: holoShift 6s ease infinite;
  }
  .kr-huge{ font-family: var(--display); font-size: clamp(44px, 9vw, 64px); line-height:1; color: var(--ink); }
  .rom-row{ display:flex; align-items:center; gap: 10px; margin-top: 12px; }
  .rom-row .rom{ font-family: var(--mono); font-size: 16px; color: var(--ink-soft); }
  .play-btn{
    width: 34px; height:34px; border-radius:50%; background: var(--pink); color:#fff;
    display:inline-flex; align-items:center; justify-content:center; cursor:pointer; flex-shrink:0;
    transition: background .2s ease; border: none; font-size: 13px;
  }
  .play-btn:hover{ background: var(--violet); }
  .play-btn.playing{ background: var(--violet); animation: playPulse .6s ease-in-out infinite; }

  .meaning-block{ margin-top: 28px; }
  .meaning-block h2{ font-family: var(--mono); font-size: 11.5px; letter-spacing:1.2px; text-transform:uppercase; color: var(--pink); margin-bottom: 8px; }
  .meaning-block p{ font-size: 16px; font-weight:600; color: var(--ink); line-height:1.6; }
  .meaning-es{ margin-top: 6px; font-size: 14px; color: var(--ink-soft); font-weight:500; line-height:1.6; }
  .meaning-zh{ margin-top: 6px; font-size: 14px; color: var(--ink-soft); font-weight:500; line-height:1.6; }
  .meaning-cn{ margin-top: 6px; font-size: 14px; color: var(--ink-soft); font-weight:500; line-height:1.6; }
  .meaning-ja{ margin-top: 6px; font-size: 14px; color: var(--ink-soft); font-weight:500; line-height:1.6; }

  .example-block{
    margin-top: 24px; background: var(--surface-2); border-left: 3px solid var(--pink);
    padding: 16px 20px; border-radius: 0 12px 12px 0;
  }
  .example-block .ex-kr{ font-size: 15px; font-weight:700; color: var(--ink); }
  .example-block .ex-trans{ margin-top: 6px; font-size: 13.5px; color: var(--ink-soft); }
  .example-block .ex-trans + .ex-trans{ margin-top: 3px; }

  .source-note{ margin-top: 20px; font-family: var(--mono); font-size: 12px; color: var(--ink-soft); }

  .cta-row{ margin-top: 32px; display:flex; gap: 14px; flex-wrap:wrap; }
  .cta-btn{
    font-weight: 700; font-size: 13.5px; padding: 12px 22px; border-radius: 999px; transition: all .2s;
  }
  .cta-primary{ background: var(--pink); color:#fff; }
  .cta-primary:hover{ background: var(--violet); }
  .cta-secondary{ background: var(--surface-2); color: var(--ink); border: 1px solid var(--line); }
  .cta-secondary:hover{ border-color: var(--pink); }

  .related{ margin-top: 48px; }
  .related h3{ font-family: var(--display); font-size: 20px; margin-bottom: 16px; color: var(--ink); }
  .related-grid{ display:grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .related-card{
    background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 16px 18px; transition: border-color .2s;
  }
  .related-card:hover{ border-color: var(--pink); }
  .related-card .r-kr{ font-family: var(--display); font-size: 19px; color: var(--ink); }
  .related-card .r-gloss{ margin-top: 4px; font-size: 12px; color: var(--ink-soft); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }

  footer{ margin-top: 40px; border-top: 1px solid var(--line); padding: 32px 0; position: relative; z-index: 1; }
  .foot-row{ max-width:1180px; margin:0 auto; padding:0 28px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap: 14px; }
  .foot-logo{ font-family: var(--display); font-size: 17px; color: var(--ink); }
  .foot-tag{ font-size: 12.5px; color: var(--ink-soft); margin-top:4px; max-width: 440px; }

  @media (max-width: 640px){
    .nav-links{ display:none; }
    .menu-toggle{ display:flex; }
    .word-card{ padding: 24px; }
    .related-grid{ grid-template-columns: 1fr; }
  }
"""

HEADER_HTML = """<header>
  <div class="nav">
    <a href="../index.html" class="logo"><span>HelloKSlang</span><span class="dot">.</span><span class="logo-badge">Dictionary</span></a>
    <nav class="nav-links">
      <a href="../index.html#dictionary">사전 Dictionary</a>
      <a href="../whatsnew.html">신규 What's New</a>
      <a href="../category.html">카테고리 Categories</a>
      <a href="../trending.html">대세 Popular</a>
      <a href="../submit.html">제보하기 Submit a word</a>
    </nav>
    <button class="menu-toggle" id="menuToggle" onclick="toggleMobileMenu()" aria-label="Menu">☰</button>
  </div>
  <div class="mobile-menu" id="mobileMenu">
    <a href="../index.html#dictionary">사전 Dictionary</a>
    <a href="../whatsnew.html">신규 What's New</a>
    <a href="../category.html">카테고리 Categories</a>
    <a href="../trending.html">대세 Popular</a>
    <a href="../submit.html">제보하기 Submit a word</a>
  </div>
</header>"""

FOOTER_HTML = """<footer>
  <div class="foot-row">
    <div>
      <div class="foot-logo">HelloKSlang.</div>
      <div class="foot-tag">Made for anyone who loves K-pop, K-dramas, or Korean culture — and wants to understand it a little better.</div>
    </div>
    <a href="../privacy.html" style="font-size:12.5px; color:var(--ink-soft); font-weight:600;">Privacy Policy</a>
  </div>
</footer>"""

SCRIPT_TEMPLATE = """<script>
  function toggleMobileMenu(){
    var menu = document.getElementById('mobileMenu');
    if(menu) menu.classList.toggle('open');
  }
  document.querySelectorAll('.mobile-menu a').forEach(function(a){
    a.addEventListener('click', function(){
      var menu = document.getElementById('mobileMenu');
      if(menu) menu.classList.remove('open');
    });
  });
  function playPronunciation(text, btnEl){
    if(!('speechSynthesis' in window)){ return; }
    window.speechSynthesis.cancel();
    var utter = new SpeechSynthesisUtterance(text);
    utter.lang = 'ko-KR';
    utter.rate = 0.82;
    if(btnEl){
      btnEl.classList.add('playing');
      utter.onend = function(){ btnEl.classList.remove('playing'); };
      utter.onerror = function(){ btnEl.classList.remove('playing'); };
    }
    window.speechSynthesis.speak(utter);
  }
</script>"""


def build_page(item, category_kr, category_en, related):
    kr, rom, en_short, meaning_en, meaning_es, ex_kr, ex_en, ex_es, where, status = item
    slug = slugify(rom)
    cat_url = CATEGORY_URL.get(category_en, "category.html")
    title = f"{kr} ({rom}) Meaning — HelloKSlang Dictionary"
    meta_desc = meaning_en if len(meaning_en) <= 155 else meaning_en[:152].rsplit(" ", 1)[0] + "…"
    # Pre-escape for the JS string literal in onclick="playPronunciation('...', this)".
    # (Kept out of the f-string itself — f-string expressions can't contain
    # backslashes on Python versions before 3.12, and the GitHub Actions
    # runner uses 3.11.)
    kr_js_escaped = kr.replace("'", "\\'")

    zh = db.ZH_TW_TRANSLATIONS.get(kr)
    if zh:
        meaning_zh, ex_zh = zh
        meaning_zh_html = f'\n      <p class="meaning-zh" lang="zh-Hant">{esc(meaning_zh)}</p>'
        ex_zh_html = f'\n      <div class="ex-trans" lang="zh-Hant">→ "{esc(ex_zh)}"</div>'
    else:
        meaning_zh_html = ""
        ex_zh_html = ""

    cn = db.ZH_CN_TRANSLATIONS.get(kr)
    if cn:
        meaning_cn, ex_cn = cn
        meaning_cn_html = f'\n      <p class="meaning-cn" lang="zh-Hans">{esc(meaning_cn)}</p>'
        ex_cn_html = f'\n      <div class="ex-trans" lang="zh-Hans">→ "{esc(ex_cn)}"</div>'
    else:
        meaning_cn_html = ""
        ex_cn_html = ""

    ja = db.JA_TRANSLATIONS.get(kr)
    if ja:
        meaning_ja, ex_ja = ja
        meaning_ja_html = f'\n      <p class="meaning-ja" lang="ja">{esc(meaning_ja)}</p>'
        ex_ja_html = f'\n      <div class="ex-trans" lang="ja">→ "{esc(ex_ja)}"</div>'
    else:
        meaning_ja_html = ""
        ex_ja_html = ""

    related_html = ""
    for r in related:
        r_kr, r_rom, r_en_short, r_meaning_en = r[0], r[1], r[2], r[3]
        r_slug = slugify(r_rom)
        related_html += f'''
      <a class="related-card" href="{esc(r_slug)}.html">
        <div class="r-kr">{esc(r_kr)}</div>
        <div class="r-gloss">{esc(r_meaning_en)}</div>
      </a>'''

    json_ld_obj = {
        "@context": "https://schema.org",
        "@type": "DefinedTerm",
        "name": f"{kr} ({rom})",
        "description": meaning_en,
        "inDefinedTermSet": {
            "@type": "DefinedTermSet",
            "name": "HelloKSlang Dictionary",
        },
    }
    json_ld = (
        '<script type="application/ld+json">\n'
        + json.dumps(json_ld_obj, ensure_ascii=False)
        + "\n</script>"
    )

    html_out = f'''<!DOCTYPE html>
<html lang="en">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_ID}');
</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(meta_desc)}">
<link rel="canonical" href="{SITE_URL}/word/{esc(slug)}.html">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,500&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
{json_ld}
<style>
{SHARED_CSS}</style>
</head>
<body>

{HEADER_HTML}

<main class="wrap">
  <a href="../index.html" class="back-link">&larr; Back to K-Slang Dictionary</a>
  <a href="../{esc(cat_url)}" class="cat-pill">{esc(category_kr)} · {esc(category_en)}</a>

  <div class="word-card">
    <div class="kr-huge">{esc(kr)}</div>
    <div class="rom-row">
      <button class="play-btn" onclick="playPronunciation('{kr_js_escaped}', this)" aria-label="Play pronunciation">▶</button>
      <span class="rom">{esc(rom)}</span>
    </div>

    <div class="meaning-block">
      <h2>Meaning</h2>
      <p>{esc(meaning_en)}</p>
      <p class="meaning-es">{esc(meaning_es)}</p>{meaning_zh_html}{meaning_cn_html}{meaning_ja_html}
    </div>

    <div class="example-block">
      <div class="ex-kr">"{esc(ex_kr)}"</div>
      <div class="ex-trans">→ "{esc(ex_en)}"</div>
      <div class="ex-trans">→ "{esc(ex_es)}"</div>{ex_zh_html}{ex_cn_html}{ex_ja_html}
    </div>

    <div class="source-note">Commonly seen on: {esc(where)}</div>

    <div class="cta-row">
      <a href="../{esc(cat_url)}" class="cta-btn cta-primary">Browse more {esc(category_en)} words</a>
      <a href="../index.html#dictionary" class="cta-btn cta-secondary">Search the full dictionary</a>
    </div>
  </div>

  <div class="related">
    <h3>Related words</h3>
    <div class="related-grid">{related_html}
    </div>
  </div>
</main>

{FOOTER_HTML}

{SCRIPT_TEMPLATE}
</body>
</html>
'''
    return slug, html_out


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_items = []
    for cat_kr, cat_en, terms in db.CATEGORIES:
        for t in terms:
            all_items.append((cat_kr, cat_en, t))

    count = 0
    for idx, (cat_kr, cat_en, item) in enumerate(all_items):
        # pick 4 related words from same category, not including this one
        same_cat = [it for (ck, ce, it) in all_items if ce == cat_en and it[0] != item[0]]
        related = same_cat[idx % max(1, len(same_cat)) : idx % max(1, len(same_cat)) + 4]
        if len(related) < 4:
            related = (related + same_cat)[:4]

        slug, page_html = build_page(item, cat_kr, cat_en, related)
        out_path = os.path.join(OUTPUT_DIR, slug + ".html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(page_html)
        count += 1

    print(f"Generated {count} word pages in ./{OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
