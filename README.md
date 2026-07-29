# K-SLANG — K-Pop & K-Drama Slang Dictionary

A slang dictionary for international (English/Spanish-speaking) K-pop and K-drama fans, aged roughly 10–30. Look up a word, hear it pronounced, browse by category, or see what's newly trending.

**Live status:** Not yet deployed. See "Deploy to GitHub Pages" below.

---

## 📁 What's in this repo

| File | What it is |
|---|---|
| `index.html` | Homepage — search only (Chrome/Google-style minimal landing) |
| `category.html` | Browse all words by category, sorted 가나다순, paginated |
| `trending.html` | Curated "recently emerged" slang (manually refreshed, see below) |
| `submit.html` | Fan submission form (wired to Formspree — see below) |
| `privacy.html` | Privacy policy — required for Google AdSense, linked in every page's footer |
| `data/kslang-slang-database.xlsx` | The master word list (517 terms) — **source of truth**. If you add/edit words here, they still need to be manually copied into the `SLANG_DB` array embedded in each HTML file (see "How word data works" below). |
| `word/*.html` | **517 individual SEO landing pages**, one per word (e.g. `word/jon-beo.html` for 존버). Auto-generated — see below. |
| `scripts/build_kslang_db.py` | Regenerates `data/kslang-slang-database.xlsx` from the master word list defined inside this script. |
| `scripts/generate_word_pages.py` | Regenerates all 517 files in `word/` from that same master word list. |

Each HTML file is **fully self-contained** — all CSS and JS (including the entire word database) is inlined in the file itself. No build step, no server, no dependencies. You can open any of these files directly in a browser and they work.

---

## ✅ Design is now consistent across all 4 pages

All four pages (`index.html`, `category.html`, `trending.html`, `submit.html`) now share the same **dark "holographic photocard" theme** — dark background, gradient (pink/violet/cyan/gold) accents on borders and headings, and scroll-fade effects on page headings. Each file is still fully self-contained (its own inlined CSS/JS), so the shared look is duplicated across files rather than pulled from one shared stylesheet — that's a deliberate tradeoff for reliability (see note below).

---

## 🚀 Deploy to GitHub Pages

1. Push this repo's contents to a GitHub repository (root of `main` branch is simplest — no `/docs` folder needed).
2. In the repo: **Settings → Pages → Source** → select `main` branch, `/ (root)` folder → Save.
3. GitHub gives you a live URL like `https://yourusername.github.io/reponame/index.html`.
4. **(Optional) Custom domain:** In the same Pages settings, enter your domain (e.g. `kslangdictionary.com`). This creates a `CNAME` file in the repo automatically. Then at your domain registrar, add:
   - 4 **A records** for the root domain pointing to: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - 1 **CNAME record** for `www` pointing to `yourusername.github.io`
   - Once DNS propagates (can take a few hours), enable **"Enforce HTTPS"** in Pages settings.

---

## 🔍 The 517 individual word pages (`word/*.html`) — why they exist

These exist purely for **Google search traffic**. Someone searching "daebak meaning" or "jonbeo 뜻" can land directly on `word/dae-bak.html` or `word/jon-beo.html` instead of needing to already know about K-SLANG and use its search bar. Each page:

- Has its own unique `<title>` and `<meta description>` (what shows up in Google results)
- Includes `DefinedTerm` structured data (JSON-LD) so Google can potentially show a rich snippet
- Links to 4 related words in the same category (helps Google understand the site's structure and keeps visitors browsing)
- Is much lighter than the main 4 pages (~15KB vs ~300KB) since it only needs its own word's data, not all 517

**✅ Domain set:** all canonical URLs point to `https://hellokslang.com`. If the domain ever changes again, there's one constant to edit — `SITE_URL` near the top of `scripts/generate_word_pages.py` — then re-run the script to regenerate all 517 pages with the new domain.

**To regenerate these pages** (after editing the word list in `scripts/build_kslang_db.py`):
```bash
cd scripts
python3 build_kslang_db.py        # rebuilds data/kslang-slang-database.xlsx
python3 generate_word_pages.py    # rebuilds all word/*.html from the same data
```
Both scripts need `openpyxl` installed (`pip install openpyxl`).

---

## 📝 Before applying for Google AdSense

- [x] ~~Add a Privacy Policy page~~ ✅ Done — `privacy.html`, linked in every page's footer. Covers AdSense/cookie disclosure, Google Fonts, Formspree, and an opt-out link (adssettings.google.com). Contact email used: kslangdictionary@gmail.com
- [ ] Let the domain "age" at least a few weeks before applying (better approval odds)

---

## ✉️ How the "Submit a word" form works

`submit.html` posts directly to [Formspree](https://formspree.io) — no backend server involved. The endpoint is already configured:

```js
const FORMSPREE_ENDPOINT = 'https://formspree.io/f/mykrlpwk';
```

Submissions land in the inbox of whatever email is attached to that Formspree account. Free tier caps at 50 submissions/month — upgrade on formspree.io if you outgrow that.

---

## 📖 How word data works (read this before adding words)

There is **no live database and no backend**. The 517-word dictionary is a plain JavaScript array (`SLANG_DB`) that's copy-pasted into all four HTML files identically. This means:

- Searching, category browsing, and pronunciation all run **entirely in the visitor's browser**.
- Anyone can view the full word list via "View Page Source" — there's no scraping protection.
- **To add or edit a word, you currently have to update the array in all 4 files by hand** (or ask Claude to do it, which is how this list was built and kept in sync). The `.xlsx` file in `/data` is meant to be the editable master copy going forward, but it is not automatically synced to the HTML — someone (or Claude) has to regenerate the embedded array from it.

## Word list makeup (517 terms)

| Category | Count |
|---|---|
| Idol Essentials | ~123 |
| Online Memes | ~119 |
| Broadcast & Variety | ~101 |
| Fandom Feels | ~95 |
| Dating & Romance | ~62 |

Each entry has: Korean term, romanization, category, English meaning, Spanish meaning, an example sentence (KR/EN/ES), and a note on where it's typically used. A `Status` column in the `.xlsx` marks entries as `Verified (web-checked)` vs `Draft — please double-check`.

---

## 🔮 Not built yet (roadmap ideas from earlier planning)

- ~~Individual per-word static pages~~ ✅ Done — see `word/` folder above
- Cross-linking: `category.html`'s word cards don't yet link to their matching `word/*.html` page (nice-to-have for more internal linking / SEO)
- Real backend + database (only needed if: automating community-slang crawling, computing real trending data, or wanting to protect the word list from being copied wholesale)
