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


CAT_ORDER = ["Idol Essentials", "Fandom Feels", "Broadcast & Variety", "Online Memes", "Dating & Romance"]
CAT_KEY = {"Idol Essentials": "idol", "Fandom Feels": "fandom", "Broadcast & Variety": "broadcast",
           "Online Memes": "meme", "Dating & Romance": "dating"}
CAT_LABELS = {
    "Idol Essentials": {"en": "Idol Essentials", "es": "Esenciales del ídolo", "zh": "偶像必修詞彙", "cn": "偶像必修词汇", "ja": "アイドル基本用語"},
    "Fandom Feels": {"en": "Fandom Feels", "es": "Sentimientos del fandom", "zh": "飯圈心情", "cn": "饭圈心情", "ja": "ファンダムの気持ち"},
    "Broadcast & Variety": {"en": "Broadcast & Variety", "es": "TV y Variedades", "zh": "廣播與綜藝", "cn": "广播与综艺", "ja": "放送・バラエティ"},
    "Online Memes": {"en": "Online Memes", "es": "Memes de internet", "zh": "網路迷因", "cn": "网络迷因", "ja": "ネットミーム"},
    "Dating & Romance": {"en": "Dating & Romance", "es": "Citas y romance", "zh": "戀愛與曖昧", "cn": "恋爱与暧昧", "ja": "恋愛表現"},
}
ALL_LABEL = {"en": "All", "es": "Todas", "zh": "全部", "cn": "全部", "ja": "すべて"}


def attrs(d):
    return " ".join(f'data-{l}="{esc(d[l])}"' for l in ("en", "es", "zh", "cn", "ja"))


def cat_button(key, count, labels, active=False):
    lab = {l: f"{labels[l]} {count}" for l in ("en", "es", "zh", "cn", "ja")}
    cls = "cat-chip active" if active else "cat-chip"
    return (f'\n        <button type="button" class="{cls}" data-filter="{key}" aria-pressed="{str(active).lower()}" '
            f'{attrs(lab)}>{esc(lab["en"])}</button>')


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

    for gi, (iso_date, terms) in enumerate(db.NEW_WORDS_LOG):
        chips = ""
        counts = {}
        for term in terms:
            entry = lookup.get(term)
            if not entry:
                missing.append((iso_date, term))
                continue
            t, cat_kr, cat_en = entry
            kr, rom, en_short = t[0], t[1], t[2]
            slug = slugify(rom)
            key = CAT_KEY[cat_en]
            counts[cat_en] = counts.get(cat_en, 0) + 1
            total_new += 1
            chips += f'''
        <a class="word-chip" data-cat="{key}" href="word/{esc(slug)}.html" title="{esc(en_short)}"><span class="chip-dot" aria-hidden="true"></span><span class="chip-kr">{esc(kr)}</span><span class="chip-rom">{esc(rom)}</span></a>'''
        if not chips:
            continue
        n = sum(counts.values())
        filters = cat_button("all", n, ALL_LABEL, active=True)
        for cat_en in CAT_ORDER:
            if counts.get(cat_en):
                filters += cat_button(CAT_KEY[cat_en], counts[cat_en], CAT_LABELS[cat_en])
        cnt = {"en": f"{n} new word" + ("" if n == 1 else "s"), "es": f"{n} palabra" + ("" if n == 1 else "s") + " nueva" + ("" if n == 1 else "s"),
               "zh": f"新增 {n} 個詞", "cn": f"新增 {n} 个词", "ja": f"{n}語を追加"}
        groups_html += f'''
    <details class="date-group"{" open" if gi == 0 else ""}>
      <summary class="date-head"><span class="date-label">{esc(format_date(iso_date))}</span><span class="date-count" {attrs(cnt)}>{esc(cnt["en"])}</span><span class="date-toggle" aria-hidden="true"></span></summary>
      <div class="cat-filter" role="group" aria-label="Filter by category">{filters}
      </div>
      <div class="chip-grid">{chips}
      </div>
    </details>'''

    if missing:
        print("WARNING: terms in NEW_WORDS_LOG not found in CATEGORIES (skipped):")
        for d, t in missing:
            print(f"  {d}: {t}")

    word_label_en = "word" if total_new == 1 else "words"
    word_label_es = "palabra" if total_new == 1 else "palabras"
    added_label_es = "agregada" if total_new == 1 else "agregadas"
    sub_en = f"{total_new} {word_label_en} added so far — newest first. (Words added before this page existed aren't shown here.)"
    sub_es = f"{total_new} {word_label_es} {added_label_es} hasta ahora — las más recientes primero. (Las palabras agregadas antes de esta página no aparecen aquí.)"
    sub_zh = f"目前已新增 {total_new} 個詞彙——最新排在最前面。（此頁面建立之前新增的詞彙不會顯示在這裡。）"
    sub_cn = f"目前已新增 {total_new} 个词汇——最新排在最前面。（此页面建立之前新增的词汇不会显示在这里。）"
    sub_ja = f"現在までに {total_new} 語が追加されています——新しい順。（このページができる前に追加された単語はここには表示されません。）"

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
<meta property="og:type" content="website">
<meta property="og:url" content="https://hellokslang.com/whatsnew.html">
<meta property="og:site_name" content="HelloKSlang">
<meta property="og:title" content="What's New — HelloKSlang Dictionary">
<meta property="og:description" content="The newest K-pop and K-drama slang words added to HelloKSlang Dictionary, newest first.">
<meta property="og:image" content="https://hellokslang.com/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="What's New — HelloKSlang Dictionary">
<meta name="twitter:description" content="The newest K-pop and K-drama slang words added to HelloKSlang Dictionary, newest first.">
<meta name="twitter:image" content="https://hellokslang.com/assets/og-image.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700;12..96,800&family=Hanken+Grotesk:ital,wght@0,400;0,500;0,600;0,700;0,800;1,500&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
{SHARED_CSS}{PAGE_CSS}
</style>
<link rel="stylesheet" href="assets/pokku.css">
</head>
<body>
<!--
  DIRECTION CONTRACT (extends the established Photocard Pull world; see
  DESIGN.md — ordinary surface extension, not a new direction)
  THESIS: a dated feed of freshly-added cards, grouped by pull date —
  same cardstock miniatures as every other card grid in the system.
  FINISH: unreviewed and undocumented is unfinished.
-->
<a class="skip-link" href="#main">Skip to content</a>

{HEADER_HTML}

<main class="wrap" id="main">
  <section class="page-head">
    <a href="index.html" class="back-link" data-en="&larr; Back to search" data-es="&larr; Volver a la búsqueda" data-zh="&larr; 返回搜尋" data-cn="&larr; 返回搜索" data-ja="&larr; 検索に戻る">&larr; Back to search</a>
    <h1 class="page-title" data-en="What's New" data-es="Novedades" data-zh="最新消息" data-cn="最新消息" data-ja="新着">What's New</h1>
    <p class="page-sub" data-en="{esc(sub_en)}" data-es="{esc(sub_es)}" data-zh="{esc(sub_zh)}" data-cn="{esc(sub_cn)}" data-ja="{esc(sub_ja)}">{esc(sub_en)}</p>
  </section>

  <div class="new-feed">{groups_html}
  </div>
</main>

{FOOTER_HTML}

<script>
  var currentLang = (function(){{
    try {{ return localStorage.getItem('kslang_lang') || 'en'; }}
    catch(e){{ return 'en'; }}
  }})();
  function setLang(lang){{
    currentLang = lang;
    try {{ localStorage.setItem('kslang_lang', lang); }} catch(e){{}}
    document.querySelectorAll('[data-en]').forEach(function(el){{
      el.textContent = el.getAttribute('data-' + lang);
    }});
    document.querySelectorAll('[data-en-html]').forEach(function(el){{
      el.innerHTML = el.getAttribute('data-' + lang + '-html');
    }});
    document.querySelectorAll('.lang-btn').forEach(function(btn){{
      btn.classList.toggle('active', btn.dataset.lang === lang);
    }});
    var selectEl = document.getElementById('langSelect');
    if(selectEl) selectEl.value = lang;
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

  document.querySelectorAll('.date-group').forEach(function(group){{
    var buttons = group.querySelectorAll('.cat-chip');
    buttons.forEach(function(btn){{
      btn.addEventListener('click', function(){{
        var f = btn.getAttribute('data-filter');
        buttons.forEach(function(b){{
          var on = b === btn;
          b.classList.toggle('active', on);
          b.setAttribute('aria-pressed', on ? 'true' : 'false');
        }});
        group.querySelectorAll('.word-chip').forEach(function(chip){{
          chip.hidden = !(f === 'all' || chip.getAttribute('data-cat') === f);
        }});
      }});
    }});
  }});

  // Apply whatever language the visitor picked last time (persisted via
  // localStorage in setLang above) — without this, every fresh page load
  // would silently reset back to English.
  setLang(currentLang);
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
    --bg: #151217;
    --surface: #1E1A22;
    --surface-2: #27222C;
    --line: rgba(243,236,221,0.12);
    --line-strong: rgba(243,236,221,0.22);
    --ink: #F3ECDD;
    --ink-soft: #A79E92;

    --card-face: #F2E9D8;
    --card-face-hi: #F8F1E3;
    --card-ink: #211B16;
    --card-ink-soft: #5B5248;
    --card-line: rgba(33,27,22,.14);

    --garnet: #B21B3E;
    --garnet-bright: #D42953;
    --garnet-light: #F0567E;
    --brass: #B4923F;
    --brass-soft: rgba(180,146,63,.16);

    --radius-card: 16px;
    --radius-ui: 14px;
    --ease-flip: cubic-bezier(0.16, 1, 0.3, 1);

    --font-kr: 'Black Han Sans', sans-serif;
    --display: 'Bricolage Grotesque', sans-serif;
    --body: 'Hanken Grotesk', sans-serif;
    --mono: 'JetBrains Mono', monospace;
  }

  *{ box-sizing: border-box; margin:0; padding:0; }

  body{
    background: var(--bg); color: var(--ink); font-family: var(--body);
    font-size: 16px; line-height: 1.5;
    -webkit-font-smoothing: antialiased; overflow-x: hidden; position: relative;
  }
  body::before{
    content:""; position:fixed; inset:0; z-index:0; pointer-events:none;
    background: radial-gradient(120% 90% at 50% 8%, rgba(255,255,255,.05), rgba(0,0,0,0) 55%),
                radial-gradient(140% 100% at 50% 100%, rgba(0,0,0,.35), rgba(0,0,0,0) 60%);
  }
  a{ color:inherit; text-decoration:none; }
  ::selection{ background: var(--garnet); color: var(--card-face-hi); }
  :focus-visible{ outline: 2px solid var(--garnet-bright); outline-offset: 3px; border-radius: 4px; }
  .skip-link{
    position:absolute; left:-999px; top:0;
    background: var(--garnet); color:#fff;
    padding: 0.75rem 1.25rem; z-index: 200;
    border-radius: 0 0 8px 0;
    font-weight:700; font-size:13.5px;
  }
  .skip-link:focus{ left:0; }
  .wrap{ max-width: 1180px; margin: 0 auto; padding: 0 28px; position: relative; z-index: 1; }
  @media (prefers-reduced-motion: reduce){ *{ animation-duration: 0.001ms !important; animation-iteration-count: 1 !important; } }

  /* ---------- header ---------- */
  header{ position: sticky; top: 0; z-index: 50; background: rgba(21,18,23,0.86); backdrop-filter: blur(10px); border-bottom: 1px solid var(--line); }
  .nav{ display:flex; align-items:center; justify-content:space-between; height: 76px; gap:20px; }
  .logo{ display:flex; align-items:center; gap: 8px; font-family: var(--display); font-weight:700; font-size: 22px; letter-spacing: 0.2px; }
  .logo .dot{ color: var(--garnet-bright); }
  .logo-badge{
    font-family: var(--mono); font-size: 10px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;
    color: var(--brass); background: var(--brass-soft); border: 1px solid rgba(180,146,63,.35);
    padding: 3px 8px; border-radius: 999px; white-space: nowrap;
  }
  .nav-links{ display:flex; gap: 32px; font-weight: 600; font-size: 14.5px; color: var(--ink-soft); }
  .nav-links a{ position:relative; padding: 6px 0; transition: color .2s var(--ease-flip); }
  .nav-links a:hover{ color: var(--ink); }
  .nav-links a::after{
    content:""; position:absolute; left:0; right:0; bottom:-2px; height:2px;
    background: var(--garnet-bright); transform: scaleX(0); transform-origin:left;
    transition: transform .25s var(--ease-flip);
  }
  .nav-links a:hover::after{ transform: scaleX(1); }
  .nav-links a.active{ color: var(--ink); }
  .nav-links a.active::after{ transform: scaleX(1); background: var(--garnet-bright); }

  .nav-right{ display:flex; align-items:center; gap: 14px; }
  .lang-switch{ display:flex; align-items:center; background: var(--surface); border: 1px solid var(--line); border-radius: 999px; padding: 3px; }
  .lang-switch button{
    border:none; cursor:pointer; background:transparent; font-family: var(--mono); font-size: 11px; font-weight: 700;
    padding: 6px 9px; border-radius: 999px; color: var(--ink-soft); transition: all .2s var(--ease-flip); white-space: nowrap;
  }
  .lang-switch button.active{ background: var(--garnet); color: #fff; }
  .lang-switch button:not(.active):hover{ color: var(--ink); }

  .lang-select{
    display:none; background: var(--surface); border: 1px solid var(--line); border-radius: 999px;
    padding: 7px 26px 7px 12px; color: var(--ink); font-family: var(--mono); font-size: 12px; font-weight: 700;
    cursor: pointer; appearance: none; -webkit-appearance: none; -moz-appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%23A79E92' stroke-width='1.5' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat; background-position: right 10px center;
  }
  .lang-select option{ background: var(--surface); color: var(--ink); }

  .menu-toggle{
    display:none; width: 38px; height: 38px; align-items:center; justify-content:center;
    border-radius: 999px; border: 1px solid var(--line); background: var(--surface); color: var(--ink);
    cursor:pointer; flex-shrink:0;
  }
  .menu-toggle:hover{ border-color: var(--garnet-bright); }
  .menu-toggle svg{ width:18px; height:18px; }

  .mobile-menu{ display:none; flex-direction:column; background: var(--surface); border-top: 1px solid var(--line); padding: 6px 28px 18px; }
  .mobile-menu.open{ display:flex; }
  .mobile-menu a{ padding: 14px 0; font-weight: 700; font-size: 15px; color: var(--ink); border-bottom: 1px solid var(--line); }
  .mobile-menu a.active{ color: var(--garnet-light); }
  .mobile-menu a:last-child{ border-bottom:none; }

  /* ---------- footer ---------- */
  footer{ margin-top: 40px; border-top: 1px solid var(--line); padding: 40px 0 32px; position: relative; z-index: 1; }
  .foot-row{ display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap: 18px; }
  .foot-logo{ font-family: var(--display); font-weight:700; font-size: 18px; color: var(--ink); }
  .foot-tag{ font-size: 13px; line-height: 1.5; color: var(--ink-soft); margin-top:6px; max-width: 480px; }
  .foot-links{ display:flex; gap:18px; flex-wrap:wrap; }
  .foot-links a{ font-size:12.5px; color:var(--ink-soft); font-weight:600; }
  .foot-links a:hover{ color: var(--ink); }

  @media (max-width: 420px){ .logo-badge{ display:none; } }
  @media (max-width: 860px){
    .nav-links{ display:none; }
    .menu-toggle{ display:flex; }
    .lang-switch{ display:none; }
    .lang-select{ display:block; }
  }
"""


PAGE_CSS = """
  .page-head{ padding: 56px 0 8px; }
  .back-link{ display:inline-flex; align-items:center; gap:6px; font-size:13.5px; font-weight:700; color: var(--brass); margin-bottom:22px; }
  .back-link:hover{ text-decoration:underline; }
  .page-title{ font-family: var(--font-kr); font-size: clamp(28px, 4.5vw, 40px); line-height:1.15; color: var(--ink); }
  .page-sub{ margin-top:10px; color: var(--ink-soft); font-size:15px; font-weight:500; }

  .new-feed{ margin-top: 8px; padding-bottom: 60px; }
  .date-group{ margin-top: 30px; }
  .date-head{ list-style:none; cursor:pointer; display:flex; align-items:center; gap:12px; flex-wrap:wrap; padding: 4px 0 12px; border-bottom: 1px solid var(--line); }
  .date-head::-webkit-details-marker{ display:none; }
  .date-count{ font-size:13px; font-weight:700; color: var(--ink-soft); }
  .date-toggle{ margin-left:auto; width:28px; height:28px; border-radius:50%; border:1px solid var(--line); position:relative; flex:none; }
  .date-toggle::before{ content:""; position:absolute; left:50%; top:45%; width:8px; height:8px; border-right:2px solid var(--ink-soft); border-bottom:2px solid var(--ink-soft); transform: translate(-50%,-50%) rotate(45deg); transition: transform .2s; }
  .date-group[open] .date-toggle::before{ transform: translate(-50%,-30%) rotate(-135deg); }
  .date-head:focus-visible{ outline: 2px solid var(--garnet-bright); outline-offset: 4px; border-radius: 6px; }

  .cat-filter{ display:flex; flex-wrap:wrap; gap:8px; margin: 16px 0 14px; }
  .cat-chip{ font: inherit; font-size:12.5px; font-weight:700; padding:7px 13px; border-radius:999px; cursor:pointer;
    background: transparent; color: var(--ink-soft); border: 1px solid var(--line); transition: transform .25s var(--ease-pop), background .2s, color .2s; }
  .cat-chip:hover{ color: var(--ink); border-color: var(--ink-soft); }
  .cat-chip.active{ background: var(--garnet); color:#fff; border-color: var(--garnet); transform: rotate(-1.5deg); }
  .cat-chip:focus-visible{ outline: 2px solid var(--garnet-bright); outline-offset: 2px; }

  .chip-grid{ display:flex; flex-wrap:wrap; gap:10px; padding-bottom: 6px; }
  .word-chip{
    display:inline-flex; align-items:baseline; gap:7px; padding: 9px 14px 9px 12px; border-radius: 10px;
    background-image:
      url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E"),
      linear-gradient(160deg, var(--card-face) 0%, var(--card-face-hi) 40%, var(--card-face) 100%);
    background-size: 140px 140px, cover; background-blend-mode: multiply, normal;
    color: var(--card-ink); border: 1px solid var(--card-line);
    box-shadow: 0 6px 14px -10px rgba(0,0,0,.6);
    transition: transform .25s var(--ease-pop), box-shadow .2s;
  }
  .word-chip:nth-child(3n+1){ transform: rotate(-.8deg); }
  .word-chip:nth-child(3n+2){ transform: rotate(.6deg); }
  .word-chip:hover{ transform: rotate(0) translateY(-2px) scale(1.04); box-shadow: 0 10px 20px -10px rgba(0,0,0,.6); }
  .word-chip:focus-visible{ outline: 2px solid var(--garnet-bright); outline-offset: 2px; }
  .word-chip[hidden]{ display:none; }
  .chip-dot{ width:8px; height:8px; border-radius:50%; flex:none; align-self:center; box-shadow: 0 0 0 2px var(--sticker-edge, #F8F1E3); }
  .word-chip[data-cat="idol"] .chip-dot{ background: var(--pop-pink, #FF6FAE); }
  .word-chip[data-cat="fandom"] .chip-dot{ background: var(--pop-lilac, #B9A2FF); }
  .word-chip[data-cat="broadcast"] .chip-dot{ background: var(--pop-mint, #74E3C4); }
  .word-chip[data-cat="meme"] .chip-dot{ background: var(--pop-lemon, #FFE16B); }
  .word-chip[data-cat="dating"] .chip-dot{ background: var(--garnet, #B21B3E); }
  .chip-kr{ font-family: var(--font-kr); font-size:17px; line-height:1.1; }
  .chip-rom{ font-family: var(--mono); font-style: italic; font-size:11px; color: var(--card-ink-soft); }
  @media (max-width: 480px){ .chip-rom{ display:none; } .word-chip{ padding: 9px 12px 9px 10px; } }
  @media (prefers-reduced-motion: reduce){ .word-chip, .cat-chip{ transition:none; } .word-chip:nth-child(n){ transform:none; } }
"""

HEADER_HTML = """<header>
  <div class="wrap nav">
    <a href="index.html" class="logo"><span>HelloKSlang</span><span class="dot">.</span><span class="logo-badge" data-en="Dictionary" data-es="Diccionario" data-zh="詞典" data-cn="词典" data-ja="辞書">Dictionary</span></a>
    <nav class="nav-links">
      <a href="index.html#dictionary" data-en="사전 Dictionary" data-es="사전 Diccionario" data-zh="사전 詞典" data-cn="사전 词典" data-ja="사전 辞書">사전 Dictionary</a>
      <a href="whatsnew.html" class="active" data-en="신규 What's New" data-es="신규 Novedades" data-zh="신규 最新消息" data-cn="신규 最新消息" data-ja="신규 新着">신규 What's New</a>
      <a href="category.html" data-en="카테고리 Categories" data-es="카테고리 Categorías" data-zh="카테고리 分類" data-cn="카테고리 分类" data-ja="카테고리 カテゴリー">카테고리 Categories</a>
      <a href="trending.html" data-en="추천 Editor's Picks" data-es="추천 Selección" data-zh="추천 編輯精選" data-cn="추천 编辑精选" data-ja="추천 編集部ピック">추천 Editor's Picks</a>
      <a href="guides/index.html" data-en="가이드 Guides" data-es="가이드 Guías" data-zh="가이드 主題指南" data-cn="가이드 主题指南" data-ja="가이드 ガイド">가이드 Guides</a>
      <a href="quiz/index.html" data-en="퀴즈 Quiz" data-es="퀴즈 Quiz" data-zh="퀴즈 測驗" data-cn="퀴즈 测验" data-ja="퀴즈 クイズ">퀴즈 Quiz</a>
      <a href="submit.html" data-en="제보하기 Submit a word" data-es="제보하기 Enviar una palabra" data-zh="제보하기 提交詞彙" data-cn="제보하기 提交词汇" data-ja="제보하기 単語を送る">제보하기 Submit a word</a>
    </nav>
    <div class="nav-right">
      <div class="lang-switch">
        <button class="lang-btn active" data-lang="en" onclick="setLang('en')">EN</button>
        <button class="lang-btn" data-lang="es" onclick="setLang('es')">ES</button>
        <button class="lang-btn" data-lang="zh" onclick="setLang('zh')">繁</button>
        <button class="lang-btn" data-lang="cn" onclick="setLang('cn')">简</button>
        <button class="lang-btn" data-lang="ja" onclick="setLang('ja')">日</button>
      </div>
      <select class="lang-select" id="langSelect" onchange="setLang(this.value)" aria-label="Language">
        <option value="en">EN</option>
        <option value="es">ES</option>
        <option value="zh">繁</option>
        <option value="cn">简</option>
        <option value="ja">日</option>
      </select>
      <button class="menu-toggle" id="menuToggle" onclick="toggleMobileMenu()" aria-label="Menu"><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M3 5h14M3 10h14M3 15h14" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" fill="none"/></svg></button>
    </div>
  </div>
  <div class="mobile-menu" id="mobileMenu">
    <a href="index.html#dictionary" data-en="사전 Dictionary" data-es="사전 Diccionario" data-zh="사전 詞典" data-cn="사전 词典" data-ja="사전 辞書">사전 Dictionary</a>
    <a href="whatsnew.html" class="active" data-en="신규 What's New" data-es="신규 Novedades" data-zh="신규 最新消息" data-cn="신규 最新消息" data-ja="신규 新着">신규 What's New</a>
    <a href="category.html" data-en="카테고리 Categories" data-es="카테고리 Categorías" data-zh="카테고리 分類" data-cn="카테고리 分类" data-ja="카테고리 カテゴリー">카테고리 Categories</a>
    <a href="trending.html" data-en="추천 Editor's Picks" data-es="추천 Selección" data-zh="추천 編輯精選" data-cn="추천 编辑精选" data-ja="추천 編集部ピック">추천 Editor's Picks</a>
    <a href="guides/index.html" data-en="가이드 Guides" data-es="가이드 Guías" data-zh="가이드 主題指南" data-cn="가이드 主题指南" data-ja="가이드 ガイド">가이드 Guides</a>
    <a href="quiz/index.html" data-en="퀴즈 Quiz" data-es="퀴즈 Quiz" data-zh="퀴즈 測驗" data-cn="퀴즈 测验" data-ja="퀴즈 クイズ">퀴즈 Quiz</a>
    <a href="submit.html" data-en="제보하기 Submit a word" data-es="제보하기 Enviar una palabra" data-zh="제보하기 提交詞彙" data-cn="제보하기 提交词汇" data-ja="제보하기 単語を送る">제보하기 Submit a word</a>
  </div>
</header>"""

FOOTER_HTML = """<footer>
  <div class="wrap foot-row">
    <div>
      <div class="foot-logo">HelloKSlang.</div>
      <div class="foot-tag" data-en="Made for anyone who loves K-pop, K-dramas, or Korean culture — and wants to understand it a little better." data-es="Hecho para quienes aman el K-pop, los K-dramas o la cultura coreana — y quieren entenderla un poco mejor." data-zh="為所有熱愛K-pop、韓劇或韓國文化，並想更了解這些內容的人所打造。" data-cn="为所有热爱K-pop、韩剧或韩国文化，并想更了解这些内容的人所打造。" data-ja="K-popやK-dramaや韓国文化が好きで、もっと理解したい人のために作りました。">Made for anyone who loves K-pop, K-dramas, or Korean culture — and wants to understand it a little better.</div>
    </div>
    <div class="foot-links">
      <a href="about.html" data-en="About" data-es="Acerca de" data-zh="關於我們" data-cn="关于我们" data-ja="サイトについて">About</a>
      <a href="contact.html" data-en="Contact" data-es="Contacto" data-zh="聯絡我們" data-cn="联系我们" data-ja="お問い合わせ">Contact</a>
      <a href="privacy.html" data-en="Privacy Policy" data-es="Política de privacidad" data-zh="隱私權政策" data-cn="隐私政策" data-ja="プライバシーポリシー">Privacy Policy</a>
    </div>
  </div>
</footer>"""


if __name__ == "__main__":
    main()
