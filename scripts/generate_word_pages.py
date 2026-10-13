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

# Presentation-layer category name translations (es/zh/cn/ja). The category
# tuples in build_kslang_db only carry kr/en — this stays local to the word
# template rather than touching the single source of truth.
CATEGORY_TRANSLATIONS = {
    "Idol Essentials": {"es": "Esenciales del ídolo", "zh": "偶像必修詞彙", "cn": "偶像必修词汇", "ja": "アイドル基本用語"},
    "Fandom Feels": {"es": "Sentimientos del fandom", "zh": "飯圈心情", "cn": "饭圈心情", "ja": "ファンダムの気持ち"},
    "Broadcast & Variety": {"es": "TV y Variedades", "zh": "廣播與綜藝", "cn": "广播与综艺", "ja": "放送・バラエティ"},
    "Online Memes": {"es": "Memes de internet", "zh": "網路迷因", "cn": "网络迷因", "ja": "ネットミーム"},
    "Dating & Romance": {"es": "Citas y romance", "zh": "戀愛與曖昧", "cn": "恋爱与暧昧", "ja": "恋愛表現"},
}

# Static UI chrome strings. Content (meanings/examples) stays sourced from
# build_kslang_db / ZH_TW_TRANSLATIONS / ZH_CN_TRANSLATIONS / JA_TRANSLATIONS
# as before and is always shown stacked across all five languages — that
# part is deliberately NOT gated by the toggle, since these are SEO landing
# pages and hiding four-fifths of the indexable translation text on load
# would cost more than the toggle is worth. The toggle instead switches the
# page's own interface language (nav, headers, buttons), exactly like it
# does on the rest of the site.
UI = {
    "dict_nav": {"en": "사전 Dictionary", "es": "사전 Diccionario", "zh": "사전 詞典", "cn": "사전 词典", "ja": "사전 辞書"},
    "whatsnew_nav": {"en": "신규 What's New", "es": "신규 Novedades", "zh": "신규 最新消息", "cn": "신규 最新消息", "ja": "신규 新着"},
    "category_nav": {"en": "카테고리 Categories", "es": "카테고리 Categorías", "zh": "카테고리 分類", "cn": "카테고리 分类", "ja": "카테고리 カテゴリー"},
    "trending_nav": {"en": "추천 Editor's Picks", "es": "추천 Selección", "zh": "추천 編輯精選", "cn": "추천 编辑精选", "ja": "추천 編集部ピック"},
    "submit_nav": {"en": "제보하기 Submit a word", "es": "제보하기 Enviar una palabra", "zh": "제보하기 提交詞彙", "cn": "제보하기 提交词汇", "ja": "제보하기 単語を送る"},
    "dict_badge": {"en": "Dictionary", "es": "Diccionario", "zh": "詞典", "cn": "词典", "ja": "辞書"},
    "back_link": {"en": "← Back to K-Slang Dictionary", "es": "← Volver al diccionario", "zh": "← 返回詞典", "cn": "← 返回词典", "ja": "← 辞書に戻る"},
    "meaning_h2": {"en": "Meaning", "es": "Significado", "zh": "意思", "cn": "意思", "ja": "意味"},
    "usage_h2": {"en": "Real usage", "es": "Uso real", "zh": "實際用法", "cn": "实际用法", "ja": "実際の使い方"},
    "seen_on": {"en": "Commonly seen on:", "es": "Uso frecuente en:", "zh": "常見於：", "cn": "常见于：", "ja": "よく見られる場所："},
    "search_full": {"en": "Search the full dictionary", "es": "Buscar en todo el diccionario", "zh": "搜尋完整詞典", "cn": "搜索完整词典", "ja": "辞書全体を検索"},
    "related_h3": {"en": "Related words", "es": "Palabras relacionadas", "zh": "相關詞彙", "cn": "相关词汇", "ja": "関連する単語"},
    "nuance_h2": {"en": "Nuance", "es": "Matiz", "zh": "細微語感", "cn": "细微语感", "ja": "ニュアンス"},
    "howto_h2": {"en": "When to use it", "es": "Cuándo usarlo", "zh": "什麼時候用", "cn": "什么时候用", "ja": "使い方"},
    "culture_h2": {"en": "Cultural context", "es": "Contexto cultural", "zh": "文化背景", "cn": "文化背景", "ja": "文化的な背景"},
    "tone_h2": {"en": "Tone", "es": "Tono", "zh": "語氣", "cn": "语气", "ja": "トーン"},
    "similar_h2": {"en": "Similar expressions", "es": "Expresiones similares", "zh": "相似說法", "cn": "相似说法", "ja": "似た表現"},
    "sources_h2": {"en": "Sources", "es": "Fuentes", "zh": "參考來源", "cn": "参考来源", "ja": "出典"},
    "featured_h2": {"en": "Featured in", "es": "Aparece en", "zh": "收錄於", "cn": "收录于", "ja": "掲載ガイド"},
    "share_btn": {"en": "Share this word", "es": "Compartir esta palabra", "zh": "分享這個詞", "cn": "分享这个词", "ja": "この単語をシェア"},
    "share_copied": {"en": "Link copied!", "es": "¡Enlace copiado!", "zh": "已複製連結！", "cn": "已复制链接！", "ja": "リンクをコピーしました！"},
    "about": {"en": "About", "es": "Acerca de", "zh": "關於我們", "cn": "关于我们", "ja": "サイトについて"},
    "privacy": {"en": "Privacy Policy", "es": "Política de privacidad", "zh": "隱私權政策", "cn": "隐私政策", "ja": "プライバシーポリシー"},
    "contact": {"en": "Contact", "es": "Contacto", "zh": "聯絡我們", "cn": "联系我们", "ja": "お問い合わせ"},
    "foot_tag": {
        "en": "Made for anyone who loves K-pop, K-dramas, or Korean culture — and wants to understand it a little better.",
        "es": "Hecho para quienes aman el K-pop, los K-dramas o la cultura coreana — y quieren entenderla un poco mejor.",
        "zh": "為所有熱愛K-pop、韓劇或韓國文化，並想更了解這些內容的人所打造。",
        "cn": "为所有热爱K-pop、韩剧或韩国文化，并想更了解这些内容的人所打造。",
        "ja": "K-popやK-dramaや韓国文化が好きで、もっと理解したい人のために作りました。",
    },
}


def data_attrs(key, extra=""):
    """Renders data-en/es/zh/cn/ja attributes from a UI dict entry."""
    d = UI[key]
    return " ".join(f'data-{lang}="{esc(d[lang])}"' for lang in ("en", "es", "zh", "cn", "ja")) + extra


def slugify(rom):
    s = rom.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def esc(s):
    return html_escape_lib.escape(s, quote=True)


# ---------------------------------------------------------------------------
# DIRECTION CONTRACT
# THESIS: The dictionary is a photocard binder — every entry is a two-sided
# card. Refuses both the pastel-hologram photocard cliche and the generic
# clean-SaaS-dictionary opposite.
# OWN-WORLD: Charcoal card-photography backdrop (#151217); ecru cardstock
# card face (#F2E9D8, fractal-noise grain multiplied into the fill, not a
# flat gradient); garnet foil (#B21B3E) as the committed accent; brass foil
# (#B4923F) for stat labels; an engraved metallic foil-stamp treatment
# (hairline texture + gradient, background-clip:text) reserved for the one
# hero term per card. Black Han Sans for the Korean term, Bricolage
# Grotesque for Latin display/UI, Hanken Grotesk body, JetBrains Mono for
# romanization. Card corners, not pills.
# STORY: A fan arrives already holding one word (from search or a share).
# The card shows its name on top, its full story below the seam — no flip
# gate, since a landing page must be legible to a crawler and instant to a
# reader. The example sentence renders as a burned-in fansub caption, since
# captioning real usage is the product's whole job. The site's five-language
# toggle carries over to this page's own interface chrome (nav/headers/
# buttons); the stacked multi-language content blocks stay always-visible
# regardless of toggle state, since hiding indexable translation text on an
# SEO landing page would cost more than the toggle is worth.
# FIRST VIEWPORT: category tag, then the card: term on the front zone, a
# perforated seam, romanization + meanings + captioned example below.
# FORM: word-template candidate 6/7, seed ae84ab06, "Show-and-Tell Caption
# Card", built inside the world assigned by seed 15184609 (candidate 4/7).
# FINISH: unreviewed and undocumented is unfinished; this build ends with
# the finish review, the verdict, and DESIGN.md.
# ---------------------------------------------------------------------------

DIRECTION_CONTRACT_HTML = """<!--
  DIRECTION CONTRACT
  THESIS: The dictionary is a photocard binder — every entry is a two-sided
  card. Refuses both the pastel-hologram photocard cliche and the generic
  clean-SaaS-dictionary opposite.
  OWN-WORLD: Charcoal card-photography backdrop (#151217); ecru cardstock
  card face (#F2E9D8, fractal-noise grain multiplied into the fill, not a
  flat gradient); garnet foil (#B21B3E) as the committed accent; brass foil
  (#B4923F) for stat labels; an engraved foil-stamp treatment reserved for
  the hero term. Black Han Sans (Korean term), Bricolage Grotesque (Latin
  display/UI), Hanken Grotesk (body), JetBrains Mono (romanization). Card
  corners, not pills.
  STORY: A fan arrives already holding one word. The card shows its name on
  top, its full story below a static seam — no flip gate, so the page stays
  legible to a crawler and instant to a reader. The example sentence renders
  as a burned-in fansub caption. The site's language toggle carries over to
  this page's chrome; stacked multi-language content stays always-visible.
  FIRST VIEWPORT: category tag, then the card: term, seam, romanization +
  meanings + captioned example.
  FORM: word-template candidate 6/7, seed ae84ab06, "Show-and-Tell Caption
  Card", inside the world assigned by seed 15184609 (candidate 4/7).
  FINISH: unreviewed and undocumented is unfinished; this build ends with
  the finish review, the verdict, and DESIGN.md.
-->"""

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
  html{ overflow-x: hidden; }
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
  .wrap{ max-width: 860px; margin: 0 auto; padding: 0 28px; position: relative; z-index: 1; }
  @media (prefers-reduced-motion: reduce){ *{ animation-duration: 0.001ms !important; animation-iteration-count: 1 !important; } }

  header{
    position: sticky; top: 0; z-index: 50;
    background: rgba(21,18,23,0.86); backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--line);
  }
  .nav{ display:flex; align-items:center; justify-content:space-between; height: 76px; max-width:1180px; margin:0 auto; padding:0 28px; gap:20px; }
  .logo{ display:flex; align-items:center; gap: 8px; font-family: var(--display); font-weight:700; font-size: 22px; }
  .logo .dot{ color: var(--garnet-bright); }
  .logo-badge{
    font-family: var(--mono); font-size: 10px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;
    color: var(--brass); background: var(--brass-soft); border: 1px solid rgba(180,146,63,.35);
    padding: 3px 8px; border-radius: 999px; white-space: nowrap;
  }
  .nav-links{ display:flex; gap: 28px; font-weight: 600; font-size: 14px; color: var(--ink-soft); }
  .nav-links a{ position:relative; padding:6px 0; transition:color .2s var(--ease-flip); }
  .nav-links a:hover{ color: var(--ink); }
  .nav-links a::after{
    content:""; position:absolute; left:0; right:0; bottom:-2px; height:2px;
    background: var(--garnet-bright); transform: scaleX(0); transform-origin:left;
    transition: transform .25s var(--ease-flip);
  }
  .nav-links a:hover::after{ transform: scaleX(1); }

  .nav-right{ display:flex; align-items:center; gap:14px; }
  .lang-switch{ display:flex; align-items:center; background: var(--surface); border:1px solid var(--line); border-radius:999px; padding:3px; }
  .lang-switch button{
    border:none; cursor:pointer; background:transparent; font-family: var(--mono); font-size:11px; font-weight:700;
    padding:6px 9px; border-radius:999px; color: var(--ink-soft); transition: all .2s var(--ease-flip); white-space:nowrap;
  }
  .lang-switch button.active{ background: var(--garnet); color:#fff; }
  .lang-switch button:not(.active):hover{ color: var(--ink); }
  .lang-select{
    display:none; background: var(--surface); border:1px solid var(--line); border-radius:999px;
    padding:7px 26px 7px 12px; color: var(--ink); font-family: var(--mono); font-size:12px; font-weight:700;
    cursor:pointer; appearance:none; -webkit-appearance:none; -moz-appearance:none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%23A79E92' stroke-width='1.5' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
    background-repeat:no-repeat; background-position: right 10px center;
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
  .mobile-menu a:last-child{ border-bottom:none; }

  main{ padding: 44px 0 60px; }
  .back-link{ display:inline-flex; align-items:center; gap: 6px; font-size: 13.5px; font-weight: 700; color: var(--brass); margin-bottom: 26px; }
  .back-link:hover{ text-decoration: underline; }
  .cat-pill{
    display:inline-block; font-family: var(--mono); font-size: 11px; font-weight:700; letter-spacing:.4px; text-transform:uppercase;
    padding: 5px 12px; border-radius: 999px; background: var(--brass-soft); color: var(--brass); margin-bottom: 18px;
  }
  .cat-pill:hover{ background: rgba(180,146,63,.28); }

  /* ---------- the card: one object, front zone on top, back zone below a
     perforated seam — both always visible, never gated behind a flip, so
     the page is legible to a crawler and instant to a reader ---------- */
  .card-object{
    /* cardstock: fractal-noise grain multiplied into the fill, not a flat
       color ramp — the fiber texture of a printed card, not a gradient */
    background-image:
      url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E"),
      linear-gradient(160deg, var(--card-face) 0%, var(--card-face-hi) 30%, var(--card-face) 100%);
    background-size: 140px 140px, cover;
    background-blend-mode: multiply, normal;
    color: var(--card-ink);
    border: 1px solid var(--card-line);
    border-radius: var(--radius-card);
    overflow: hidden;
    box-shadow: 0 28px 70px -28px rgba(0,0,0,.55);
    position: relative;
  }
  .card-object::before{
    content:""; position:absolute; top:0; left:0; right:0; height: 3px; background: var(--garnet);
  }
  .card-front-zone{ padding: 36px 36px 26px; }
  .card-tag{
    display:inline-block; font-family: var(--mono); font-size: 10.5px; font-weight:700; letter-spacing:.4px; text-transform:uppercase;
    padding: 4px 10px; border-radius: 999px; background: var(--brass-soft); color: #7A6224; margin-bottom: 18px;
  }
  /* foil stamp: an engraved metallic fill (fine hairline + brass gradient),
     not a plain gradient wash — reserved for the one hero term per card */
  .foil-text{
    /* metallic multi-stop gradient only — a repeating hairline overlay was
       tried and dropped: it aliased against thin Hangul strokes at small
       sizes and made whole glyphs read as a solid block. Dark stops are
       kept deep enough to hold contrast against the cardstock ground. */
    background-image: linear-gradient(115deg, #6E5419 0%, #C9A64C 20%, #EBD08A 32%, #C9A64C 44%, #7A5E1E 62%, #B5924A 80%, #6E5419 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent;
  }
  .kr-huge{ font-family: var(--font-kr); font-size: clamp(42px, 8.5vw, 62px); line-height:1; }
  .rom-row{ display:flex; align-items:center; gap: 10px; margin-top: 16px; }
  .rom-row .rom{ font-family: var(--mono); font-style: italic; font-size: 15.5px; color: var(--card-ink-soft); }
  .play-btn{
    position:relative;
    width: 34px; height:34px; border-radius:50%; background: var(--garnet); color:#fff;
    display:inline-flex; align-items:center; justify-content:center; cursor:pointer; flex-shrink:0;
    transition: background .2s var(--ease-flip); border: none;
  }
  /* invisible hit-area expansion toward the 44px touch-target guideline,
     without inflating the visual circle */
  .play-btn::before{ content:""; position:absolute; inset:-5px; }
  .play-btn svg{ width:13px; height:13px; }
  .play-btn:hover{ background: var(--garnet-bright); }
  .play-btn.playing{ background: var(--garnet-bright); animation: playPulse .6s ease-in-out infinite; }
  @keyframes playPulse{ 0%,100%{ transform: scale(1); } 50%{ transform: scale(1.18); } }

  /* the seam — a perforated tear line between the card's two zones */
  .card-seam{
    position:relative; height:1px; margin: 0 28px;
    background: repeating-linear-gradient(90deg, var(--card-line) 0 8px, transparent 8px 16px);
  }
  .card-seam::before, .card-seam::after{
    content:""; position:absolute; top:50%; width:16px; height:16px; border-radius:50%;
    background: var(--bg); transform: translateY(-50%);
  }
  .card-seam::before{ left:-36px; }
  .card-seam::after{ right:-36px; }

  .card-back-zone{ padding: 26px 36px 34px; }
  .meaning-block h2{ font-family: var(--mono); font-size: 11px; letter-spacing:1.2px; text-transform:uppercase; color: var(--garnet); margin-bottom: 10px; }
  .meaning-block p{ font-size: 16.5px; font-weight:700; color: var(--card-ink); line-height:1.6; }
  .meaning-es, .meaning-zh, .meaning-cn, .meaning-ja{ margin-top: 7px; font-size: 14px; color: var(--card-ink-soft); font-weight:500; line-height:1.6; }

  /* the caption bar — the example sentence rendered like a burned-in
     fansub caption, since captioning real usage is the whole product */
  .caption-block{ margin-top: 26px; }
  .caption-block h2{ font-family: var(--mono); font-size: 11px; letter-spacing:1.2px; text-transform:uppercase; color: var(--garnet); margin-bottom: 10px; }
  .caption-bar{
    background: #100E13; border-radius: 10px; padding: 16px 20px;
    box-shadow: inset 0 0 0 1px rgba(243,236,221,.06);
  }
  .caption-bar .cap-kr{ font-size: 16px; font-weight:800; color: #FDF8EE; line-height:1.5; }
  .caption-bar .cap-trans{ margin-top: 8px; font-size: 13px; color: #B8AF9F; line-height:1.55; }
  .caption-bar .cap-trans + .cap-trans{ margin-top: 4px; }
  .caption-bar .cap-timecode{ font-family: var(--mono); font-size: 10px; letter-spacing:.4px; color: #6E665C; margin-top: 12px; }

  .cta-row{ margin-top: 30px; display:flex; gap: 14px; flex-wrap:wrap; }
  /* ---- optional deep-dive sections (DETAILS in build_kslang_db.py) ----
     Unlike the stacked meaning/example above, these longer blocks show only
     the reader's language: all five are in the HTML (crawlers read them,
     English is the no-JS default), and html[lang] picks the visible one. */
  .detail-block{ margin-top: 26px; }
  .detail-block h2{ font-family: var(--mono); font-size: 11px; letter-spacing:1.2px; text-transform:uppercase; color: var(--garnet); margin-bottom: 8px; }
  .detail-block p{ font-size: 15px; color: var(--card-ink); line-height:1.65; }
  .lx{ display:none; }
  html[lang="en"] .lx[data-l="en"], html[lang="es"] .lx[data-l="es"], html[lang="zh"] .lx[data-l="zh"],
  html[lang="cn"] .lx[data-l="cn"], html[lang="ja"] .lx[data-l="ja"]{ display:block; }
  .tone-pill{ display:inline-block; font-size: 13px; font-weight:700; color: var(--card-ink); background: rgba(33,27,22,.07); border: 1px solid var(--card-line); border-radius: 10px; padding: 7px 12px; }
  .similar-row{ display:flex; flex-wrap:wrap; gap: 8px; }
  .similar-chip{ display:inline-flex; align-items:baseline; gap: 7px; padding: 8px 13px; border-radius: 999px; border: 1px solid var(--card-line); background: var(--card-face-hi); color: var(--card-ink); font-size: 13px; transition: border-color .2s; }
  .similar-chip b{ font-family: var(--font-kr); font-weight:400; font-size: 16px; }
  .similar-chip:hover{ border-color: var(--garnet); }
  .source-list{ list-style:none; padding:0; margin:0; }
  .source-list li{ font-size: 13px; color: var(--card-ink-soft); line-height:1.55; margin-bottom: 6px; }
  .source-list a{ color: var(--garnet); font-weight:700; text-decoration: underline; text-underline-offset: 2px; word-break: break-word; }
  .share-btn{ cursor:pointer; font-family: inherit; border: 1.5px dashed var(--card-ink-soft); background: transparent; color: var(--card-ink); }
  .cta-btn{ font-weight: 700; font-size: 13.5px; padding: 12px 22px; border-radius: 999px; transition: all .2s var(--ease-flip); }
  .cta-primary{ background: var(--garnet); color:#fff; }
  .cta-primary:hover{ background: var(--garnet-bright); }
  .cta-secondary{ background: rgba(33,27,22,.06); color: var(--card-ink); border: 1px solid var(--card-line); }
  .cta-secondary:hover{ border-color: var(--garnet); }

  .related{ margin-top: 48px; }
  .related h3{ font-family: var(--display); font-weight:700; font-size: 19px; margin-bottom: 16px; color: var(--ink); }
  .related-grid{ display:grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .related-card{
    background-image:
      url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E"),
      linear-gradient(160deg, var(--card-face) 0%, var(--card-face-hi) 100%);
    background-size: 140px 140px, cover;
    background-blend-mode: multiply, normal;
    border: 1px solid var(--card-line); border-radius: 12px; padding: 16px 18px; transition: transform .15s var(--ease-flip), box-shadow .15s var(--ease-flip);
    min-width: 0;
  }
  .related-card:hover{ transform: translateY(-2px); box-shadow: 0 14px 30px -16px rgba(0,0,0,.5); }
  .related-card .r-kr{ font-family: var(--font-kr); font-size: 19px; color: var(--card-ink); }
  .related-card .r-gloss{ margin-top: 4px; font-size: 12px; color: var(--card-ink-soft); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }

  footer{ margin-top: 40px; border-top: 1px solid var(--line); padding: 32px 0; position: relative; z-index: 1; }
  .foot-row{ max-width:1180px; margin:0 auto; padding:0 28px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap: 14px; }
  .foot-logo{ font-family: var(--display); font-weight:700; font-size: 16px; color: var(--ink); }
  .foot-tag{ font-size: 12.5px; color: var(--ink-soft); margin-top:4px; max-width: 440px; }
  .foot-links{ display:flex; gap:18px; flex-wrap:wrap; }
  .foot-links a{ font-size:12.5px; color:var(--ink-soft); font-weight:600; }
  .foot-links a:hover{ color: var(--ink); }

  @media (max-width: 640px){
    .nav-links{ display:none; }
    .menu-toggle{ display:flex; }
    .lang-switch{ display:none; }
    .lang-select{ display:block; }
    .card-front-zone{ padding: 24px 22px 18px; }
    .card-back-zone{ padding: 18px 22px 26px; }
    .card-seam{ margin: 0 18px; }
    .card-seam::before{ left:-27px; }
    .card-seam::after{ right:-27px; }
    .related-grid{ grid-template-columns: 1fr; }
  }
  @media (max-width: 420px){
    .logo-badge{ display:none; }
  }
"""

HEADER_HTML = f"""<header>
  <div class="nav">
    <a href="../index.html" class="logo"><span>HelloKSlang</span><span class="dot">.</span><span class="logo-badge" {data_attrs('dict_badge')}>Dictionary</span></a>
    <nav class="nav-links">
      <a href="../index.html#dictionary" {data_attrs('dict_nav')}>사전 Dictionary</a>
      <a href="../whatsnew.html" {data_attrs('whatsnew_nav')}>신규 What's New</a>
      <a href="../category.html" {data_attrs('category_nav')}>카테고리 Categories</a>
      <a href="../trending.html" {data_attrs('trending_nav')}>추천 Editor's Picks</a>
      <a href="../submit.html" {data_attrs('submit_nav')}>제보하기 Submit a word</a>
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
    <a href="../index.html#dictionary" {data_attrs('dict_nav')}>사전 Dictionary</a>
    <a href="../whatsnew.html" {data_attrs('whatsnew_nav')}>신규 What's New</a>
    <a href="../category.html" {data_attrs('category_nav')}>카테고리 Categories</a>
    <a href="../trending.html" {data_attrs('trending_nav')}>추천 Editor's Picks</a>
    <a href="../submit.html" {data_attrs('submit_nav')}>제보하기 Submit a word</a>
  </div>
</header>"""

FOOTER_HTML = f"""<footer>
  <div class="foot-row">
    <div>
      <div class="foot-logo">HelloKSlang.</div>
      <div class="foot-tag" {data_attrs('foot_tag')}>Made for anyone who loves K-pop, K-dramas, or Korean culture — and wants to understand it a little better.</div>
    </div>
    <div class="foot-links">
      <a href="../about.html" {data_attrs('about')}>About</a>
      <a href="../contact.html" {data_attrs('contact')}>Contact</a>
      <a href="../privacy.html" {data_attrs('privacy')}>Privacy Policy</a>
    </div>
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

  var currentLang = (function(){
    try { return localStorage.getItem('kslang_lang') || 'en'; }
    catch(e){ return 'en'; }
  })();

  function setLang(lang){
    currentLang = lang;
    try { localStorage.setItem('kslang_lang', lang); } catch(e){}
    document.querySelectorAll('[data-en]').forEach(function(el){
      el.textContent = el.getAttribute('data-' + lang);
    });
    document.querySelectorAll('.lang-btn').forEach(function(btn){
      btn.classList.toggle('active', btn.dataset.lang === lang);
    });
    var selectEl = document.getElementById('langSelect');
    if(selectEl) selectEl.value = lang;
    document.documentElement.lang = lang;
  }

  // Share: native share sheet on phones, copy-link fallback elsewhere.
  function shareWord(btn){
    var data = { title: document.title, url: location.href };
    if(navigator.share){
      navigator.share(data).catch(function(){});
      return;
    }
    var done = function(){
      var original = btn.textContent;
      btn.textContent = btn.getAttribute('data-copied-' + currentLang) || 'Link copied!';
      setTimeout(function(){ btn.textContent = btn.getAttribute('data-' + currentLang) || original; }, 1800);
    };
    if(navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(location.href).then(done, function(){ window.prompt('Copy this link:', location.href); });
    } else {
      window.prompt('Copy this link:', location.href);
    }
  }

  // Apply whatever language the visitor picked last time (persisted via
  // localStorage in setLang above) — without this, every fresh page load
  // would silently reset back to English.
  setLang(currentLang);
</script>"""


LANGS = ("en", "es", "zh", "cn", "ja")
DETAILS = getattr(db, "DETAILS", {})
REGISTER_LABELS = getattr(db, "REGISTER_LABELS", {})
BY_KR = {}  # kr -> item tuple, filled in main()
# kr -> list of guides (COLLECTIONS) that feature the word
GUIDES_BY_WORD = {}
for _c in getattr(db, "COLLECTIONS", []):
    for _s in _c["sections"]:
        for _w in _s["words"]:
            GUIDES_BY_WORD.setdefault(_w, []).append(_c)


def render_featured(kr):
    """Links to the topic guides this word appears in (any word, details or not)."""
    guides = GUIDES_BY_WORD.get(kr)
    if not guides:
        return ""
    chips = "".join(
        f'\n          <a class="similar-chip" href="../guides/{esc(g["slug"])}.html" '
        + " ".join(f'data-{l}="{esc(g["title"][l])}"' for l in LANGS)
        + f'>{esc(g["title"]["en"])}</a>'
        for g in guides
    )
    return (f'      <div class="detail-block">\n        <h2 {data_attrs("featured_h2")}>Featured in</h2>\n'
            f'        <div class="similar-row">{chips}\n        </div>\n      </div>\n')


def _lx_paragraphs(texts):
    """One <p> per language; CSS shows only the reader's language."""
    return "".join(
        f'\n        <p class="lx" data-l="{l}" lang="{ {"zh": "zh-Hant", "cn": "zh-Hans"}.get(l, l) }">{esc(texts[l])}</p>'
        for l in LANGS if texts.get(l)
    )


def render_details(kr):
    """Optional deep-dive sections for a word. Anything missing is skipped."""
    d = DETAILS.get(kr)
    if not d:
        return ""
    out = []
    for field, label in (("nuance", "nuance_h2"), ("usage", "howto_h2"), ("culture", "culture_h2")):
        if d.get(field):
            out.append(f'      <div class="detail-block">\n        <h2 {data_attrs(label)}>{UI[label]["en"]}</h2>{_lx_paragraphs(d[field])}\n      </div>')
    if d.get("register") in REGISTER_LABELS:
        labels = REGISTER_LABELS[d["register"]]
        out.append(f'      <div class="detail-block">\n        <h2 {data_attrs("tone_h2")}>Tone</h2>\n        <span class="tone-pill" '
                   + " ".join(f'data-{l}="{esc(labels[l])}"' for l in LANGS) + f'>{esc(labels["en"])}</span>\n      </div>')
    sims = [BY_KR[s] for s in d.get("similar", []) if s in BY_KR and s != kr]
    if sims:
        chips = "".join(
            f'\n          <a class="similar-chip" href="{esc(slugify(s[1]))}.html"><b>{esc(s[0])}</b>{esc(s[2])}</a>'
            for s in sims
        )
        out.append(f'      <div class="detail-block">\n        <h2 {data_attrs("similar_h2")}>Similar expressions</h2>\n        <div class="similar-row">{chips}\n        </div>\n      </div>')
    if d.get("sources"):
        items = "".join(
            f'\n          <li><a href="{esc(s["url"])}" target="_blank" rel="noopener nofollow">{esc(s["title"])}</a> — {esc(s["publisher"])}, {esc(s["date"])}</li>'
            for s in d["sources"]
        )
        out.append(f'      <div class="detail-block">\n        <h2 {data_attrs("sources_h2")}>Sources</h2>\n        <ul class="source-list">{items}\n        </ul>\n      </div>')
    return "\n".join(out) + ("\n" if out else "")


def pick_related(item, cat_en, all_items, idx, n=4):
    """Related words: similar expressions first, then words sharing a topic
    tag, then the old same-category fill so every page still gets n."""
    kr = item[0]
    picked, seen = [], {kr}
    def add(it):
        if it and it[0] not in seen and len(picked) < n:
            picked.append(it); seen.add(it[0])
    d = DETAILS.get(kr, {})
    for s in d.get("similar", []):
        add(BY_KR.get(s))
    tags = set(d.get("tags", []))
    if tags:
        for other, od in DETAILS.items():
            if tags & set(od.get("tags", [])):
                add(BY_KR.get(other))
    same_cat = [it for (ck, ce, it) in all_items if ce == cat_en and it[0] != kr]
    start = idx % max(1, len(same_cat))
    for it in same_cat[start:] + same_cat[:start]:
        add(it)
    return picked


def build_page(item, category_kr, category_en, related):
    kr, rom, en_short, meaning_en, meaning_es, ex_kr, ex_en, ex_es, where, status = item
    slug = slugify(rom)
    cat_url = CATEGORY_URL.get(category_en, "category.html")
    cat_t = CATEGORY_TRANSLATIONS.get(category_en, {})
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
        ex_zh_html = f'\n        <div class="cap-trans" lang="zh-Hant">→ "{esc(ex_zh)}"</div>'
    else:
        meaning_zh_html = ""
        ex_zh_html = ""

    cn = db.ZH_CN_TRANSLATIONS.get(kr)
    if cn:
        meaning_cn, ex_cn = cn
        meaning_cn_html = f'\n      <p class="meaning-cn" lang="zh-Hans">{esc(meaning_cn)}</p>'
        ex_cn_html = f'\n        <div class="cap-trans" lang="zh-Hans">→ "{esc(ex_cn)}"</div>'
    else:
        meaning_cn_html = ""
        ex_cn_html = ""

    ja = db.JA_TRANSLATIONS.get(kr)
    if ja:
        meaning_ja, ex_ja = ja
        meaning_ja_html = f'\n      <p class="meaning-ja" lang="ja">{esc(meaning_ja)}</p>'
        ex_ja_html = f'\n        <div class="cap-trans" lang="ja">→ "{esc(ex_ja)}"</div>'
    else:
        meaning_ja_html = ""
        ex_ja_html = ""

    # 폴꾸 sticker on the card corner — stable per word (derived from the slug)
    pin_sticker = ["♥", "✦", "ㅋㅋ", "★", "♪"][sum(map(ord, slugify(rom))) % 5]

    details_html = render_details(kr) + render_featured(kr)
    copied_attrs = " ".join(f'data-copied-{l}="{esc(UI["share_copied"][l])}"' for l in LANGS)

    related_html = ""
    for r in related:
        r_kr, r_rom, r_en_short, r_meaning_en = r[0], r[1], r[2], r[3]
        r_slug = slugify(r_rom)
        related_html += f'''
      <a class="related-card" href="{esc(r_slug)}.html">
        <div class="r-kr">{esc(r_kr)}</div>
        <div class="r-gloss">{esc(r_meaning_en)}</div>
      </a>'''

    # cat-pill follows the same "Korean word · translated label" convention
    # used site-wide in the main nav (the Korean half never translates).
    cat_pill_attrs = " ".join(
        f'data-{lang}="{esc(category_kr)} · {esc(v)}"'
        for lang, v in (
            ("en", category_en), ("es", cat_t.get("es", category_en)),
            ("zh", cat_t.get("zh", category_en)), ("cn", cat_t.get("cn", category_en)),
            ("ja", cat_t.get("ja", category_en)),
        )
    )

    cta_primary_attrs = " ".join(
        f'data-{lang}="{esc(v)}"'
        for lang, v in (
            ("en", f"Browse more {category_en} words"),
            ("es", f"Ver más palabras de {cat_t.get('es', category_en)}"),
            ("zh", f"瀏覽更多「{cat_t.get('zh', category_en)}」相關詞彙"),
            ("cn", f"浏览更多「{cat_t.get('cn', category_en)}」相关词汇"),
            ("ja", f"「{cat_t.get('ja', category_en)}」の単語をもっと見る"),
        )
    )

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
<meta property="og:type" content="article">
<meta property="og:url" content="{SITE_URL}/word/{esc(slug)}.html">
<meta property="og:site_name" content="HelloKSlang">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(meta_desc)}">
<meta property="og:image" content="{SITE_URL}/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(meta_desc)}">
<meta name="twitter:image" content="{SITE_URL}/assets/og-image.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700;12..96,800&family=Hanken+Grotesk:ital,wght@0,400;0,500;0,600;0,700;0,800;1,500&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
{json_ld}
<style>
{SHARED_CSS}</style>
<link rel="stylesheet" href="../assets/pokku.css">
</head>
<body>
{DIRECTION_CONTRACT_HTML}
<a class="skip-link" href="#main">Skip to content</a>

{HEADER_HTML}

<main class="wrap" id="main">
  <a href="../index.html" class="back-link" {data_attrs('back_link')}>&larr; Back to K-Slang Dictionary</a>
  <a href="../{esc(cat_url)}" class="cat-pill" {cat_pill_attrs}>{esc(category_kr)} · {esc(category_en)}</a>

  <div class="card-pin">
  <span class="pin-tape" aria-hidden="true"></span>
  <span class="pin-stk" aria-hidden="true">{pin_sticker}</span>
  <div class="card-object">
    <div class="card-front-zone">
      <span class="card-tag">{esc(category_en)}</span>
      <h1 class="kr-huge foil-text">{esc(kr)}</h1>
      <div class="rom-row">
        <button class="play-btn" onclick="playPronunciation('{kr_js_escaped}', this)" aria-label="Play pronunciation"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2.5v11l9-5.5-9-5.5z" fill="currentColor"/></svg></button>
        <span class="rom">{esc(rom)}</span>
      </div>
    </div>

    <div class="card-seam" aria-hidden="true"></div>

    <div class="card-back-zone">
      <div class="meaning-block">
        <h2 {data_attrs('meaning_h2')}>Meaning</h2>
        <p>{esc(meaning_en)}</p>
        <p class="meaning-es">{esc(meaning_es)}</p>{meaning_zh_html}{meaning_cn_html}{meaning_ja_html}
      </div>

      <div class="caption-block">
        <h2 {data_attrs('usage_h2')}>Real usage</h2>
        <div class="caption-bar">
          <div class="cap-kr">"{esc(ex_kr)}"</div>
          <div class="cap-trans">→ "{esc(ex_en)}"</div>
          <div class="cap-trans">→ "{esc(ex_es)}"</div>{ex_zh_html}{ex_cn_html}{ex_ja_html}
          <div class="cap-timecode"><span {data_attrs('seen_on')}>Commonly seen on:</span> {esc(where)}</div>
        </div>
      </div>

{details_html}
      <div class="cta-row">
        <a href="../{esc(cat_url)}" class="cta-btn cta-primary" {cta_primary_attrs}>Browse more {esc(category_en)} words</a>
        <a href="../index.html#dictionary" class="cta-btn cta-secondary" {data_attrs('search_full')}>Search the full dictionary</a>
        <button type="button" class="cta-btn share-btn" onclick="shareWord(this)" {data_attrs('share_btn')} {copied_attrs}>Share this word</button>
      </div>
    </div>
  </div>
  </div>

  <div class="related">
    <h3 {data_attrs('related_h3')}>Related words</h3>
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

    BY_KR.update({it[0]: it for (_, _, it) in all_items})
    count = 0
    for idx, (cat_kr, cat_en, item) in enumerate(all_items):
        related = pick_related(item, cat_en, all_items, idx)

        slug, page_html = build_page(item, cat_kr, cat_en, related)
        out_path = os.path.join(OUTPUT_DIR, slug + ".html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(page_html)
        count += 1

    print(f"Generated {count} word pages in ./{OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
