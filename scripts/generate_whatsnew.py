# -*- coding: utf-8 -*-
"""
Generates whatsnew.html — a reverse-chronological feed of newly added words,
built from NEW_WORDS_LOG in build_kslang_db.py.

Words added before NEW_WORDS_LOG existed aren't included (no real date to
show them under). Re-run any time NEW_WORDS_LOG changes.
"""
import os
import sys
import html as html_escape_lib
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(SCRIPT_DIR, "..")
sys.path.insert(0, SCRIPT_DIR)
import build_kslang_db as db

GA_ID = "G-F475ZTL1ZV"

CATEGORY_URL = {
    "Idol Essentials": "category.html?cat=Idol%20Essentials",
    "Fandom Feels": "category.html?cat=Fandom%20Feels",
    "Broadcast & Variety": "category.html?cat=Broadcast%20%26%20Variety",
    "Online Memes": "category.html?cat=Online%20Memes",
    "Dating & Romance": "category.html?cat=Dating%20%26%20Romance",
}


def esc(s):
    return html_escape_lib.escape(s, quote=True)


def build_lookup():
    """Map Korean term -> (full tuple, category_kr, category_en)."""
    lookup = {}
    for cat_kr, cat_en, terms in db.CATEGORIES:
        for t in terms:
            lookup[t[0]] = (t, cat_kr, cat_en)
    return lookup


def slugify(rom):
    import re
    s = rom.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def format_date(iso_date):
    dt = datetime.strptime(iso_date, "%Y-%m-%d")
    return dt.strftime("%B %-d, %Y") if os.name != "nt" else dt.strftime("%B %d, %Y")


def main():
    lookup = build_lookup()

    groups_html = ""
    total_new = 0
    missing = []

    for iso_date, terms in db.NEW_WORDS_LOG:
        cards = ""
        for term in terms:
            entry = lookup.get(term)
            if not entry:
                missing.append((iso_date, term))
                continue
            t, cat_kr, cat_en = entry
            kr, rom, en_short, meaning_en, meaning_es, ex_kr, ex_en, ex_es, where, status = t
            slug = slugify(rom)
            cat_url = CATEGORY_URL.get(cat_en, "category.html")
            total_new += 1
            cards += f'''
      <a class="new-card" href="word/{esc(slug)}.html">
        <div class="new-card-top">
          <div class="kr-big">{esc(kr)}</div>
          <div class="rom-big">{esc(rom)}</div>
          <span class="cat-pill">{esc(cat_kr)} · {esc(cat_en)}</span>
        </div>
        <p class="def" data-en="{esc(meaning_en)}" data-es="{esc(meaning_es)}">{esc(meaning_en)}</p>
      </a>'''
        if not cards:
            continue
        groups_html += f'''
    <div class="date-group">
      <div class="date-label">{esc(format_date(iso_date))}</div>
      <div class="new-grid">{cards}
      </div>
    </div>'''

    if missing:
        print("WARNING: terms in NEW_WORDS_LOG not found in CATEGORIES (skipped):")
        for d, t in missing:
            print(f"  {d}: {t}")

    word_label_en = "word" if total_new == 1 else "words"
    word_label_es = "palabra" if total_new == 1 else "palabras"
    added_label_es = "agregada" if total_new == 1 else "agregadas"
    sub_en = f"{total_new} {word_label_en} added so far — newest first. (Words added before this page existed aren't shown here.)"
    sub_es = f"{total_new} {word_label_es} {added_label_es} hasta ahora — las más recientes primero. (Las palabras agregadas antes de esta página no aparecen aquí.)"

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
<title>What's New — HelloKSlang Dictionary</title>
<meta name="description" content="The newest K-pop and K-drama slang words added to HelloKSlang Dictionary, newest first.">
<link rel="canonical" href="https://hellokslang.com/whatsnew.html">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
{SHARED_CSS}{PAGE_CSS}
</style>
</head>
<body>

{HEADER_HTML}

<main class="wrap">
  <section class="page-head">
    <a href="index.html" class="back-link" data-en="&larr; Back to search" data-es="&larr; Volver a la búsqueda">&larr; Back to search</a>
    <span class="section-eyebrow" data-en="Updates" data-es="Novedades">Updates</span>
    <h1 class="page-title" data-en="What's New" data-es="Novedades">What's New</h1>
    <p class="page-sub" data-en="{esc(sub_en)}" data-es="{esc(sub_es)}">{esc(sub_en)}</p>
  </section>

  <div class="new-feed">{groups_html}
  </div>
</main>

{FOOTER_HTML}

<script>
  var currentLang = 'en';
  function setLang(lang){{
    currentLang = lang;
    document.querySelectorAll('[data-en]').forEach(function(el){{
      el.textContent = el.getAttribute('data-' + lang);
    }});
    document.querySelectorAll('[data-en-html]').forEach(function(el){{
      el.innerHTML = el.getAttribute('data-' + lang + '-html');
    }});
    document.querySelectorAll('.lang-btn').forEach(function(btn){{
      btn.classList.toggle('active', btn.dataset.lang === lang);
    }});
    document.documentElement.lang = lang;
  }}
  function toggleMobileMenu(){{
    var menu = document.getElementById('mobileMenu');
    if(menu) menu.classList.toggle('open');
  }}
  document.querySelectorAll('.mobile-menu a').forEach(function(a){{
    a.addEventListener('click', function(){{
      var menu = document.getElementById('mobileMenu');
      if(menu) menu.classList.remove('open');
    }});
  }});
</script>
</body>
</html>
'''

    out_path = os.path.join(REPO_ROOT, "whatsnew.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"whatsnew.html generated: {total_new} words across {len(db.NEW_WORDS_LOG)} log entries")


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
    --radius: 18px;
    --display: 'Black Han Sans', sans-serif;
    --body: 'Plus Jakarta Sans', sans-serif;
    --mono: 'JetBrains Mono', monospace;
  }

  *{ box-sizing: border-box; margin:0; padding:0; }

  body{
    background: var(--bg);
    color: var(--ink);
    font-family: var(--body);
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
    position: relative;
  }

  body::before, body::after{
    content:"";
    position:fixed;
    width: 480px; height: 480px;
    border-radius:50%;
    filter: blur(140px);
    opacity:.25;
    z-index:0;
    pointer-events:none;
  }
  body::before{ background: var(--pink); top:-140px; left:-140px; }
  body::after{ background: var(--cyan); bottom:-160px; right:-140px; }

  a{ color:inherit; text-decoration:none; }

  .wrap{
    max-width: 1180px;
    margin: 0 auto;
    padding: 0 28px;
    position: relative;
    z-index: 1;
  }

  /* ---------- holographic signature ---------- */
  .holo-text{
    background: var(--holo);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    color: transparent;
    animation: holoShift 6s ease infinite;
  }
  @keyframes holoShift{
    0%,100%{ background-position: 0% 50%; }
    50%{ background-position: 100% 50%; }
  }
  @keyframes floatY{
    0%,100%{ transform: translateY(0); }
    50%{ transform: translateY(-14px); }
  }
  @keyframes playPulse{
    0%,100%{ transform: scale(1); }
    50%{ transform: scale(1.18); }
  }
  @media (prefers-reduced-motion: reduce){
    *{ animation-duration: 0.001ms !important; animation-iteration-count: 1 !important; }
  }

  /* ---------- header ---------- */
  header{
    position: sticky;
    top: 0;
    z-index: 50;
    background: rgba(13,8,23,0.72);
    backdrop-filter: blur(14px);
    border-bottom: 1px solid var(--line);
  }
  .nav{
    display:flex;
    align-items:center;
    justify-content:space-between;
    height: 76px;
  }
  .logo{
    display:flex;
    align-items:center;
    gap: 8px;
    font-family: var(--display);
    font-size: 24px;
    letter-spacing: 0.5px;
  }
  .logo .dot{ color: var(--pink); }
  .logo-badge{
    font-family: var(--mono);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: var(--violet);
    background: rgba(168,85,247,.15);
    border: 1px solid rgba(168,85,247,.4);
    padding: 3px 8px;
    border-radius: 999px;
    white-space: nowrap;
  }
  .nav-links{
    display:flex;
    gap: 32px;
    font-weight: 600;
    font-size: 14.5px;
    color: var(--ink-soft);
  }
  .nav-links a{ position:relative; padding: 6px 0; transition: color .2s; }
  .nav-links a:hover{ color: var(--ink); }
  .nav-links a::after{
    content:"";
    position:absolute; left:0; bottom:-2px;
    width:0%; height:2px;
    background: var(--holo);
    background-size: 300% 300%;
    transition: width .25s ease;
  }
  .nav-links a:hover::after{ width:100%; animation: holoShift 2s linear infinite; }

  .nav-right{ display:flex; align-items:center; gap: 14px; }
  .lang-switch{
    display:flex;
    align-items:center;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 3px;
  }
  .lang-switch button{
    border:none;
    cursor:pointer;
    background:transparent;
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 700;
    padding: 6px 12px;
    border-radius: 999px;
    color: var(--ink-soft);
    transition: all .2s ease;
  }
  .lang-switch button.active{ background: var(--pink); color: #fff; }
  .lang-switch button:not(.active):hover{ color: var(--ink); }

  .menu-toggle{
    display:none;
    width: 38px; height: 38px;
    align-items:center;
    justify-content:center;
    border-radius: 999px;
    border: 1px solid var(--line);
    background: var(--surface);
    color: var(--ink);
    font-size: 16px;
    cursor:pointer;
    flex-shrink:0;
  }
  .menu-toggle:hover{ border-color: var(--pink); }

  .mobile-menu{
    display:none;
    flex-direction:column;
    background: var(--surface);
    border-top: 1px solid var(--line);
    padding: 6px 28px 18px;
  }
  .mobile-menu.open{ display:flex; }
  .mobile-menu a{
    padding: 14px 0;
    font-weight: 700;
    font-size: 15px;
    color: var(--ink);
    border-bottom: 1px solid var(--line);
  }
  .mobile-menu a:last-child{ border-bottom:none; }

  .play-btn{
    width: 30px; height:30px;
    border-radius:50%;
    background: var(--pink);
    color:#fff;
    display:inline-flex;
    align-items:center;
    justify-content:center;
    cursor:pointer;
    flex-shrink:0;
    transition: background .2s ease;
  }
  .play-btn:hover{ background: var(--violet); }
  .play-btn.playing{ background: var(--violet); animation: playPulse .6s ease-in-out infinite; }

  .play-btn-sm{
    display:inline-flex;
    align-items:center;
    justify-content:center;
    width: 18px; height: 18px;
    border-radius: 50%;
    background: var(--line);
    color: var(--ink-soft);
    font-size: 8px;
    margin-left: 7px;
    cursor:pointer;
    vertical-align: middle;
    transition: all .2s ease;
  }
  .play-btn-sm:hover{ background: var(--pink); color: #fff; }
  .play-btn-sm.playing{ background: var(--pink); color: #fff; animation: playPulse .6s ease-in-out infinite; }

  /* ---------- footer ---------- */
  footer{
    margin-top: 40px;
    border-top: 1px solid var(--line);
    padding: 40px 0 32px;
    position: relative;
    z-index: 1;
  }
  .foot-row{
    display:flex;
    justify-content:space-between;
    align-items:center;
    flex-wrap:wrap;
    gap: 18px;
  }
  .foot-logo{
    font-family: var(--display);
    font-size: 19px;
    color: var(--ink);
  }
  .foot-tag{
    font-size: 13px;
    color: var(--ink-soft);
    margin-top:6px;
    max-width: 480px;
  }

  @media (max-width: 420px){
    .logo-badge{ display:none; }
  }
  @media (max-width: 860px){
    .nav-links{ display:none; }
    .menu-toggle{ display:flex; }
  }
  /* ---------- section headers (generic) ---------- */
  .section{ padding: 40px 0; }
  .section-head{ margin-bottom: 28px; }
  .section-eyebrow{
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--pink);
    margin-bottom: 8px;
    display:block;
  }
  .section-title{
    font-family: var(--display);
    font-size: 32px;
    color: var(--ink);
  }

"""


PAGE_CSS = """
  .page-head{ padding: 56px 0 8px; }
  .back-link{ display:inline-flex; align-items:center; gap:6px; font-size:13.5px; font-weight:700; color: var(--violet); margin-bottom:22px; }
  .back-link:hover{ text-decoration:underline; }
  .section-eyebrow{ font-family: var(--mono); font-size:12px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color: var(--pink); margin-bottom:8px; display:block; }
  .page-title{ font-family: var(--display); font-size: clamp(30px, 4.5vw, 46px); line-height:1.1; color: var(--ink); }
  .page-sub{ margin-top:10px; color: var(--ink-soft); font-size:15px; font-weight:500; }

  .new-feed{ margin-top: 8px; padding-bottom: 60px; }
  .date-group{ margin-top: 34px; }
  .date-label{
    font-family: var(--mono); font-size:12.5px; font-weight:700; letter-spacing:.5px;
    color: var(--violet); margin-bottom: 14px; padding-bottom: 8px; border-bottom: 1px solid var(--line);
  }
  .new-grid{ display:grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
  @media (max-width: 700px){ .new-grid{ grid-template-columns: 1fr; } }

  .new-card{
    display:block; background: var(--surface); border: 1px solid var(--line); border-radius: 16px;
    padding: 18px 20px; position: relative; overflow: hidden; transition: border-color .2s;
  }
  .new-card:hover{ border-color: var(--pink); }
  .new-card::before{
    content:""; position:absolute; top:0; left:0; right:0; height:2px;
    background: var(--holo); background-size: 300% 300%; opacity:0; transition: opacity .25s;
  }
  .new-card:hover::before{ opacity:1; animation: holoShift 4s ease infinite; }
  .new-card-top{ display:flex; align-items:baseline; gap:10px; flex-wrap:wrap; margin-bottom:8px; }
  .new-card .kr-big{ font-family: var(--display); font-size:21px; color: var(--ink); }
  .new-card .rom-big{ font-family: var(--mono); font-size:12px; color: var(--ink-soft); }
  .new-card .cat-pill{
    margin-left:auto; font-size:10px; font-weight:700; padding:3px 9px; border-radius:999px;
    background: rgba(168,85,247,.15); color: var(--violet); white-space:nowrap;
  }
  .new-card .def{ font-size:13px; color: var(--ink-soft); line-height:1.5; }
"""

HEADER_HTML = """<header>
  <div class="wrap nav">
    <a href="index.html" class="logo"><span>HelloKSlang</span><span class="dot">.</span><span class="logo-badge" data-en="Dictionary" data-es="Diccionario">Dictionary</span></a>
    <nav class="nav-links">
      <a href="index.html#dictionary" data-en="사전 Dictionary" data-es="사전 Diccionario">사전 Dictionary</a>
      <a href="whatsnew.html" data-en="신규 What's New" data-es="신규 Novedades">신규 What's New</a>
      <a href="category.html" data-en="카테고리 Categories" data-es="카테고리 Categorías">카테고리 Categories</a>
      <a href="trending.html" data-en="대세 Popular" data-es="대세 Popular">대세 Popular</a>
      <a href="submit.html" data-en="제보하기 Submit a word" data-es="제보하기 Enviar una palabra">제보하기 Submit a word</a>
    </nav>
    <div class="nav-right">
      <div class="lang-switch">
        <button class="lang-btn active" data-lang="en" onclick="setLang('en')">EN</button>
        <button class="lang-btn" data-lang="es" onclick="setLang('es')">ES</button>
      </div>
      <button class="menu-toggle" id="menuToggle" onclick="toggleMobileMenu()" aria-label="Menu">☰</button>
    </div>
  </div>
  <div class="mobile-menu" id="mobileMenu">
    <a href="index.html#dictionary" data-en="사전 Dictionary" data-es="사전 Diccionario">사전 Dictionary</a>
    <a href="whatsnew.html" data-en="신규 What's New" data-es="신규 Novedades">신규 What's New</a>
    <a href="category.html" data-en="카테고리 Categories" data-es="카테고리 Categorías">카테고리 Categories</a>
    <a href="trending.html" data-en="대세 Popular" data-es="대세 Popular">대세 Popular</a>
    <a href="submit.html" data-en="제보하기 Submit a word" data-es="제보하기 Enviar una palabra">제보하기 Submit a word</a>
  </div>
</header>"""

FOOTER_HTML = """<footer>
  <div class="wrap foot-row">
    <div>
      <div class="foot-logo">HelloKSlang.</div>
      <div class="foot-tag">Made for anyone who loves K-pop, K-dramas, or Korean culture — and wants to understand it a little better.</div>
    </div>
    <a href="privacy.html" style="font-size:12.5px; color:var(--ink-soft); font-weight:600;">Privacy Policy</a>
  </div>
</footer>"""


if __name__ == "__main__":
    main()
