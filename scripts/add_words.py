"""Add brand-new words to build_kslang_db.py in one go:
CATEGORIES tuple + ZH_TW / ZH_CN / JA translations + DETAILS + NEW_WORDS_LOG.

usage (from scripts/):  python3 add_words.py 2026-10-19 batch.py [batch2.py ...]

Each batch file just calls W(...) once per word:

W(cat, kr, rom, title,
  m=[en, es, zh_tw, ja],                   # meaning (zh-CN is auto-converted with OpenCC)
  ex=[kr, en, es, zh_tw, ja],              # example sentence
  ctx="Where it's used (English)",
  n=[en, es, zh_tw, ja],                   # DETAILS nuance
  u=[en, es, zh_tw, ja],                   # DETAILS usage
  reg="casual",                            # REGISTER_LABELS key: casual / everyday / text / vulgar
  sim=["비슷한단어"],                        # existing kr only (others are dropped)
  tags=["chat"],                           # TAG_LABELS keys only
  c=[en, es, zh_tw, ja] or None,           # optional DETAILS culture
  status="Verified (web-checked)",         # or leave default Draft
  sources=[{"title":..., "publisher":..., "date":"YYYY-MM-DD", "url":...}])

cat is one of IDOL / FANDOM / BROADCAST / MEME / DATING. rom becomes the URL slug
(lowercase, digits, hyphens) and must not collide with an existing one.
The script refuses duplicates, unknown tags/registers and slug collisions."""
import sys, json, re
from opencc import OpenCC
cc = OpenCC('tw2sp')
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_kslang_db.py')
FIX = [('原着', '原著'), ('着作', '著作'), ('显着', '显著'), ('录像', '录制')]
def cn(t):
    t = cc.convert(t)
    for a, b in FIX: t = t.replace(a, b)
    return t.replace('「', '“').replace('」', '”').replace('『', '‘').replace('』', '’')
def jd(x): return json.dumps(x, ensure_ascii=False)

src = open(P).read(); ns = {}; exec(src[:src.index('HEADERS = [')], ns)
KRS = {w[0] for c in ns['CATEGORIES'] for w in c[-1]}
ROMS = {w[1] for c in ns['CATEGORIES'] for w in c[-1]}
NEW = []
def W(cat, kr, rom, title, m, ex, ctx, n, u, reg, sim, tags, c=None, status="Draft — please double-check", sources=None):
    assert cat in ('IDOL', 'FANDOM', 'BROADCAST', 'MEME', 'DATING'), cat
    assert kr not in KRS and kr not in [x['kr'] for x in NEW], ('dup', kr)
    for s in (sources or []): assert {'title','publisher','date','url'} <= set(s), ('source needs title/publisher/date/url', kr)
    assert len(m) == 4 and len(ex) == 5 and len(n) == 4 and len(u) == 4, kr
    NEW.append(dict(cat=cat, kr=kr, rom=rom, title=title, m=m, ex=ex, ctx=ctx, n=n, u=u, reg=reg, sim=sim, tags=tags, c=c, status=status, sources=sources))

date = sys.argv[1]
for f in sys.argv[2:]:
    exec(open(f).read(), {'W': W})
allk = KRS | {x['kr'] for x in NEW}
for w in NEW:
    assert w['reg'] in ns['REGISTER_LABELS'], w['kr']
    for t in w['tags']: assert t in ns['TAG_LABELS'], (w['kr'], t)
    assert re.fullmatch(r'[a-z0-9-]+', w['rom']), w['rom']
    assert w['rom'] not in ROMS and [x['rom'] for x in NEW].count(w['rom'])==1, ('rom collision', w['kr'], w['rom'])

def five(x):
    en, es, zh, ja = x
    return {"en": en, "es": es, "zh": zh, "cn": cn(zh), "ja": ja}

# 1) tuples at the end of each category list
for cat in ('IDOL', 'FANDOM', 'BROADCAST', 'MEME', 'DATING'):
    items = [w for w in NEW if w['cat'] == cat]
    if not items: continue
    s = src.index(f'\n{cat} = [\n'); e = src.index('\n]\n', s)
    block = ''.join(
        f'\n    ({jd(w["kr"])}, {jd(w["rom"])}, {jd(w["title"])},\n     {jd(w["m"][0])},\n     {jd(w["m"][1])},\n'
        f'     {jd(w["ex"][0])}, {jd(w["ex"][1])},\n     {jd(w["ex"][2])},\n     {jd(w["ctx"])}, {jd(w["status"])}),'
        for w in items)
    src = src[:e] + block + src[e:]
# 2) translation dicts
for name, idx in (('ZH_TW_TRANSLATIONS', 'zh'), ('ZH_CN_TRANSLATIONS', 'cn'), ('JA_TRANSLATIONS', 'ja')):
    s = src.index(f'\n{name} = {{'); e = src.index('\n}\n', s)
    lines = []
    for w in NEW:
        if idx == 'zh': mm, ee = w['m'][2], w['ex'][3]
        elif idx == 'cn': mm, ee = cn(w['m'][2]), cn(w['ex'][3])
        else: mm, ee = w['m'][3], w['ex'][4]
        lines.append(f'    {jd(w["kr"])}: ({jd(mm)}, {jd(ee)}),')
    pre = src[:e]
    if not pre.rstrip().endswith(',') and not pre.rstrip().endswith('{'): pre = pre.rstrip() + ','
    src = pre + '\n' + '\n'.join(lines) + src[e:]
# 3) DETAILS
s = src.index('DETAILS = {'); e = src.index('\n}\n', s)
dl = []
for w in NEW:
    d = {"nuance": five(w['n']), "usage": five(w['u'])}
    if w['c']: d['culture'] = five(w['c'])
    d['register'] = w['reg']
    d['similar'] = [x for x in w['sim'] if x in allk and x != w['kr']]
    d['tags'] = w['tags']
    if w['sources']: d['sources'] = w['sources']
    dl.append(f'    {jd(w["kr"])}: ' + json.dumps(d, ensure_ascii=False, indent=4).replace('\n', '\n    ') + ',')
src = src[:e] + '\n' + '\n'.join(dl) + src[e:]
# 4) NEW_WORDS_LOG (newest first)
s = src.index('NEW_WORDS_LOG = [\n') + len('NEW_WORDS_LOG = [\n')
src = src[:s] + f'    ({jd(date)}, {jd([w["kr"] for w in NEW])}),\n' + src[s:]
open(P, 'w').write(src)
ns2 = {}; exec(src[:src.index('HEADERS = [')], ns2)
print(len(NEW), 'new words; total', sum(len(c[-1]) for c in ns2['CATEGORIES']), '; details', len(ns2['DETAILS']))
