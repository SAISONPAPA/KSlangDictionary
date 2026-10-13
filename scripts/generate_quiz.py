# -*- coding: utf-8 -*-
"""
Generates the mini quiz page quiz/index.html from QUIZ / QUIZ_UI in
build_kslang_db.py.

Every option is a Korean word from the database, so one question set works in
all five languages: "meaning" questions show the word's existing five-language
meaning, "situation" questions show a hand-written situation. After each
answer the reader sees the correct word's meaning and a link to its card.
No backend — the questions are embedded as JSON; the final score is only sent
to Google Analytics as a `quiz_complete` event.

Page chrome is reused from generate_word_pages.py (one level deep, ../ paths).
Run after generate_word_pages.py. Also wired into .github/workflows/rebuild.yml.
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_kslang_db as db
import generate_word_pages as wp
import generate_collections as gc

OUTPUT_DIR = os.path.join(wp.SCRIPT_DIR, "..", "quiz")
esc = wp.esc
attrs = gc.attrs

QUIZ_CSS = """
  .quiz-wrap{ max-width: 720px; margin: 0 auto; }
  .quiz-head{ margin: 6px 0 26px; }
  .quiz-head .page-title{ font-family: var(--display); font-weight: 800; font-size: clamp(28px, 4.6vw, 42px); line-height: 1.12; letter-spacing: -0.02em; color: var(--ink); }
  .quiz-intro{ margin-top: 12px; font-size: 15.5px; line-height: 1.7; color: var(--ink-soft); }
  .quiz-card{ position: relative; padding: 28px 26px 26px; border-radius: var(--radius-card); border: 1px solid var(--card-line);
    background: linear-gradient(135deg, var(--card-face) 0%, var(--card-face-hi) 42%, var(--card-face) 100%); color: var(--card-ink);
    box-shadow: 0 24px 60px -24px rgba(0,0,0,.5); }
  .quiz-card::before{ content:""; position:absolute; top:0; left:0; right:0; height:3px; background: var(--garnet); border-radius: var(--radius-card) var(--radius-card) 0 0; }
  .quiz-meta{ display:flex; align-items:center; gap: 12px; font-family: var(--mono); font-size: 11.5px; font-weight: 700; color: var(--card-ink-soft); letter-spacing: .4px; }
  .quiz-bar{ flex:1; height: 6px; border-radius: 999px; background: rgba(33,27,22,.1); overflow:hidden; }
  .quiz-bar span{ display:block; height:100%; background: var(--garnet); border-radius: 999px; transition: width .35s ease; }
  .quiz-ask{ margin-top: 20px; font-family: var(--mono); font-size: 11px; letter-spacing: 1.2px; text-transform: uppercase; color: var(--garnet); font-weight: 700; }
  .quiz-prompt{ margin-top: 10px; font-size: 18px; font-weight: 700; line-height: 1.55; color: var(--card-ink); }
  .quiz-options{ margin-top: 20px; display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 12px; }
  .quiz-opt{ font: inherit; cursor:pointer; text-align:left; padding: 14px 16px; border-radius: 14px; border: 1.5px solid var(--card-line);
    background: var(--card-face-hi); color: var(--card-ink); display:flex; flex-direction:column; gap: 3px; min-height: 64px;
    transition: border-color .2s, transform .2s, background .2s; }
  .quiz-opt b{ font-family: var(--font-kr); font-weight: 400; font-size: 22px; line-height: 1.15; }
  .quiz-opt span{ font-family: var(--mono); font-style: italic; font-size: 12px; color: var(--card-ink-soft); }
  .quiz-opt:hover:not(:disabled){ border-color: var(--garnet); transform: translateY(-2px); }
  .quiz-opt:disabled{ cursor: default; }
  .quiz-opt.is-right{ border-color: #2E7D5A; background: rgba(46,125,90,.12); }
  .quiz-opt.is-wrong{ border-color: var(--garnet); background: rgba(178,27,62,.08); }
  .quiz-feedback{ margin-top: 20px; padding: 16px 18px; border-radius: 12px; background: #100E13; color: #FDF8EE; }
  .quiz-feedback .fb-title{ font-weight: 800; font-size: 15px; }
  .quiz-feedback .fb-word{ font-family: var(--font-kr); font-size: 20px; margin: 0 4px; }
  .quiz-feedback .fb-text{ margin-top: 8px; font-size: 14px; line-height: 1.6; color: #D8CCBE; }
  .quiz-feedback a{ display:inline-block; margin-top: 10px; color: #F0567E; font-weight: 700; font-size: 13.5px; }
  .quiz-actions{ margin-top: 20px; display:flex; gap: 12px; flex-wrap: wrap; }
  .quiz-btn{ font: inherit; cursor:pointer; border: none; border-radius: 999px; padding: 13px 22px; font-weight: 800; font-size: 14.5px; background: var(--garnet); color: #fff; }
  .quiz-btn.secondary{ background: transparent; color: var(--card-ink); border: 1.5px solid var(--card-ink-soft); }
  .quiz-btn:hover{ filter: brightness(1.08); }
  .quiz-score{ font-family: var(--display); font-weight: 800; font-size: 54px; color: var(--card-ink); line-height: 1; margin-top: 8px; }
  .quiz-result{ margin-top: 12px; font-size: 17px; font-weight: 700; line-height: 1.5; }
  .quiz-links{ margin-top: 18px; display:flex; flex-wrap: wrap; gap: 8px; }
  .quiz-links a{ padding: 9px 14px; border-radius: 999px; border: 1px solid var(--card-line); background: var(--card-face-hi); color: var(--card-ink); font-size: 13px; font-weight: 700; }
  [hidden]{ display:none !important; }
  @media (max-width: 600px){ .quiz-options{ grid-template-columns: 1fr; } .quiz-card{ padding: 24px 18px 20px; } }
"""


def build_data(by_kr):
    words = {}
    for q in db.QUIZ:
        for kr in q["options"]:
            it = by_kr[kr]
            words[kr] = {"kr": kr, "rom": it[1], "short": it[2],
                         "slug": wp.slugify(it[1]), "meaning": gc.meanings(it)}
    questions = [{k: q[k] for k in ("type", "answer", "options", "situation", "note") if k in q} for q in db.QUIZ]
    guides = [{"slug": c["slug"], "title": c["title"]} for c in getattr(db, "COLLECTIONS", [])]
    return {"ui": db.QUIZ_UI, "questions": questions, "words": words, "guides": guides}


QUIZ_JS = r"""<script>
(function(){
  var DATA = JSON.parse(document.getElementById('quiz-data').textContent);
  var UI = DATA.ui, Q = DATA.questions, W = DATA.words;
  var state = { i: -1, score: 0, answered: false, picked: null, order: [] };
  function L(){ return (typeof currentLang !== 'undefined' && UI.title[currentLang]) ? currentLang : 'en'; }
  function t(key){ return UI[key][L()] || UI[key].en; }
  function el(id){ return document.getElementById(id); }
  function esc(s){ return String(s).replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
  function shuffle(a){ a = a.slice(); for(var i=a.length-1;i>0;i--){ var j=Math.floor(Math.random()*(i+1)); var x=a[i]; a[i]=a[j]; a[j]=x; } return a; }

  function render(){
    var lang = L();
    el('quiz-start').hidden = state.i !== -1;
    el('quiz-play').hidden = state.i < 0 || state.i >= Q.length;
    el('quiz-done').hidden = state.i < Q.length;
    if(state.i === -1){ el('quiz-start-btn').textContent = t('start'); return; }
    if(state.i >= Q.length){ renderDone(lang); return; }
    var q = Q[state.i];
    el('quiz-count').textContent = (state.i + 1) + ' / ' + Q.length;
    el('quiz-bar').style.width = (100 * state.i / Q.length) + '%';
    el('quiz-ask').textContent = t(q.type === 'meaning' ? 'ask_meaning' : 'ask_situation');
    el('quiz-prompt').textContent = q.type === 'meaning' ? W[q.answer].meaning[lang] : q.situation[lang];
    el('quiz-options').innerHTML = state.order.map(function(kr){
      var w = W[kr], cls = '';
      if(state.answered){ if(kr === q.answer) cls = ' is-right'; else if(kr === state.picked) cls = ' is-wrong'; }
      return '<button type="button" class="quiz-opt' + cls + '" data-kr="' + esc(kr) + '"' + (state.answered ? ' disabled' : '') +
             '><b lang="ko">' + esc(kr) + '</b><span>' + esc(w.rom) + '</span></button>';
    }).join('');
    var fb = el('quiz-feedback');
    fb.hidden = !state.answered;
    el('quiz-next').hidden = !state.answered;
    if(state.answered){
      var a = W[q.answer], ok = state.picked === q.answer;
      fb.innerHTML = '<div class="fb-title">' + (ok ? esc(t('correct')) + ' <span class="fb-word" lang="ko">' + esc(a.kr) + '</span>'
                                                     : esc(t('wrong')) + ' <span class="fb-word" lang="ko">' + esc(a.kr) + '</span>') + '</div>' +
        '<div class="fb-text">' + esc(a.meaning[lang]) + (q.note ? ' ' + esc(q.note[lang]) : '') + '</div>' +
        '<a href="../word/' + esc(a.slug) + '.html">' + esc(t('see_card')) + '</a>';
      el('quiz-next').textContent = t(state.i === Q.length - 1 ? 'finish' : 'next');
    }
  }

  function renderDone(lang){
    var s = state.score, n = Q.length;
    el('quiz-score').textContent = s + ' / ' + n;
    el('quiz-score-label').textContent = t('score_label');
    el('quiz-result').textContent = t(s >= 10 ? 'result_high' : s >= 6 ? 'result_mid' : 'result_low');
    el('quiz-retry').textContent = t('retry');
    el('quiz-keep').textContent = t('keep_learning');
    el('quiz-guides').innerHTML = DATA.guides.map(function(g){
      return '<a href="../guides/' + esc(g.slug) + '.html">' + esc(g.title[lang] || g.title.en) + '</a>';
    }).join('');
  }

  function start(){ state = { i: 0, score: 0, answered: false, picked: null, order: shuffle(Q[0].options) }; render(); }
  document.getElementById('quiz-start-btn').addEventListener('click', start);
  document.getElementById('quiz-retry').addEventListener('click', start);
  document.getElementById('quiz-options').addEventListener('click', function(e){
    var b = e.target.closest('.quiz-opt'); if(!b || state.answered) return;
    state.answered = true; state.picked = b.getAttribute('data-kr');
    if(state.picked === Q[state.i].answer) state.score++;
    render();
    el('quiz-feedback').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  });
  document.getElementById('quiz-next').addEventListener('click', function(){
    state.i++; state.answered = false; state.picked = null;
    if(state.i < Q.length){ state.order = shuffle(Q[state.i].options); }
    else if(typeof gtag === 'function'){ gtag('event', 'quiz_complete', { score: state.score, total: Q.length }); }
    render();
    document.getElementById('quiz-root').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  // re-render quiz text whenever the language toggle changes
  var baseSetLang = window.setLang;
  window.setLang = function(lang){ baseSetLang(lang); render(); };
  render();
})();
</script>"""


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    by_kr = {it[0]: it for _, _, terms in db.CATEGORIES for it in terms}
    for i, q in enumerate(db.QUIZ, 1):
        bad = [w for w in q["options"] if w not in by_kr]
        if bad or q["answer"] not in q["options"]:
            raise SystemExit(f"QUIZ question {i}: unknown words {bad} or answer not among options")
    data = json.dumps(build_data(by_kr), ensure_ascii=False).replace("</", "<\\/")
    ui = db.QUIZ_UI
    url = f"{wp.SITE_URL}/quiz/"
    body = f'''  <div class="quiz-wrap">
  <a href="../index.html" class="back-link" {attrs(gc.GUIDE_UI["back_dict"])}>{esc(gc.GUIDE_UI["back_dict"]["en"])}</a>
  <div class="quiz-head">
    <h1 class="page-title" {attrs(ui["title"])}>{esc(ui["title"]["en"])}</h1>
    <p class="quiz-intro" {attrs(ui["intro"])}>{esc(ui["intro"]["en"])}</p>
  </div>
  <div class="quiz-card" id="quiz-root" aria-live="polite">
    <div id="quiz-start">
      <button type="button" class="quiz-btn" id="quiz-start-btn">{esc(ui["start"]["en"])}</button>
    </div>
    <div id="quiz-play" hidden>
      <div class="quiz-meta"><span id="quiz-count"></span><div class="quiz-bar"><span id="quiz-bar"></span></div></div>
      <p class="quiz-ask" id="quiz-ask"></p>
      <p class="quiz-prompt" id="quiz-prompt"></p>
      <div class="quiz-options" id="quiz-options"></div>
      <div class="quiz-feedback" id="quiz-feedback" hidden></div>
      <div class="quiz-actions"><button type="button" class="quiz-btn" id="quiz-next" hidden></button></div>
    </div>
    <div id="quiz-done" hidden>
      <p class="quiz-ask" id="quiz-score-label"></p>
      <div class="quiz-score" id="quiz-score"></div>
      <p class="quiz-result" id="quiz-result"></p>
      <div class="quiz-actions"><button type="button" class="quiz-btn" id="quiz-retry"></button></div>
      <p class="quiz-ask" id="quiz-keep"></p>
      <div class="quiz-links" id="quiz-guides"></div>
    </div>
  </div>
  </div>
<script type="application/json" id="quiz-data">{data}</script>'''
    ld = {"@context": "https://schema.org", "@type": "Quiz", "name": ui["title"]["en"],
          "description": ui["intro"]["en"], "url": url, "inLanguage": "en",
          "educationalLevel": "Beginner", "about": "Korean slang"}
    html = gc.page_shell(f'{ui["title"]["en"]} | HelloKSlang', gc.short_desc(ui["intro"]["en"]),
                         url, ld, body)
    # quiz needs its own CSS and script; inject next to the shared ones
    html = html.replace("</style>\n<link rel=\"stylesheet\" href=\"../assets/pokku.css\">",
                        QUIZ_CSS + "</style>\n<link rel=\"stylesheet\" href=\"../assets/pokku.css\">", 1)
    html = html.replace("</body>", QUIZ_JS + "\n</body>", 1)
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"quiz generated: {len(db.QUIZ)} questions → ./quiz/index.html")


if __name__ == "__main__":
    main()
