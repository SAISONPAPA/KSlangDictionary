# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

**Product scope (who the site itself serves):** anyone who loves K-pop, K-dramas, or Korean culture and hits a slang term they don't understand — in a comment section, a fancam caption, a variety show, a group chat. No Korean fluency assumed; they want the meaning, the romanization, and a real usage example fast, without digging through old forum threads or waiting on a Discord reply.

**Marketing/growth scope (who is actively targeted for acquisition):** English- and Spanish-speaking women, roughly 10s–30s, living outside Korea, with an active interest in K-Culture. This is the audience Instagram (@hellokslang) content and campaigns are built for — narrower than who the product welcomes, but it's the acquisition wedge.

## Product Purpose

HelloKSlang is a free, hand-reviewed dictionary of K-pop and K-drama slang and fandom terminology, translated into five languages. It exists because looking up Korean fan-culture slang is currently a scavenger hunt — old forum threads, hoping someone answers in Discord, or guessing from context. HelloKSlang is meant to be the shortcut: type the word, get the meaning, romanization, and a real example sentence.

Current-stage success is organic search traffic growth and domain maturity toward eventually enabling Google AdSense (About page and ad-adjacent infrastructure already exist in anticipation of this).

## Positioning

A slang dictionary is not a novel category (Urban Dictionary, Naver dictionary exist), but HelloKSlang's mechanism is specific to this niche: every entry is hand-reviewed before publishing (not crowd-posted and unmoderated), every entry ships with romanization + a real example sentence (not just a bare definition), and every entry is available in five languages (EN/ES/traditional & simplified Chinese/Japanese) rather than Korean-only or English-only. It is explicitly independent and ad-free — not affiliated with any entertainment company, idol, or drama — which matters to a fandom-literate audience wary of official-sounding but inauthentic sources.

## Operating Context

- Static site hosted on GitHub Pages at hellokslang.com, repo `SAISONPAPA/KSlangDictionary` (public).
- Content pipeline is script-generated from a single source of truth (`scripts/build_kslang_db.py`); word pages, category/trending/search data, sitemap, and the "what's new" page are all regenerated from it rather than hand-edited.
- A GitHub Actions workflow (`.github/workflows/rebuild.yml`) auto-rebuilds generated files when the source data script changes.
- Growth channel today is Instagram (@hellokslang), recently created, promotion not yet ramped up. Content plan rotates the 5 slang categories across weekdays; posting is intended to go through Meta Business Suite (OAuth), not shared credentials.
- No paid acquisition, no CMS, no backend/database — content lives in versioned files.

## Capabilities and Constraints

- 651 slang entries across 5 categories: Idol Essentials, Fandom Feels, Broadcast & Variety, Online Memes, Dating & Romance.
- 5 supported languages, all complete at 651/651: Korean (source) + English + Spanish (base fields), Traditional Chinese, Simplified Chinese, Japanese (each in a separate translation dictionary). Adding a word requires filling all 6 language fields at once — a language silently falls back to English if any field is missed, which has been a recurring real bug.
- Japanese translations cannot be machine-generated from Chinese/Korean (established fandom terms in Japanese, e.g. 최애→推し, don't map mechanically) and must be hand-written per entry.
- User-facing language toggle (5 languages) persists via `localStorage`, independent of and not to be confused with the 5 *content* categories above.
- Individual SEO metadata + JSON-LD structured data exist per word page (651 pages) and must survive any redesign.
- Word submission is via a form (`submit.html`); every submission is manually reviewed before publishing — there is no auto-publish or crowd-editing path.
- No user accounts, no comments, no backend persistence beyond the static generated files plus GA4 pageview/event tracking.
- Undecided: Portuguese (Brazil) support is a known gap against the stated Latin America audience, intentionally deferred as a separate future project, not in current scope.

## Brand Commitments

- Name: HelloKSlang / HelloKSlang Dictionary. Tagline register: "그게 무슨 뜻이야? What did your bias just say?" — playful, insider-fandom voice, bilingual wink.
- Explicitly independent and not affiliated with any entertainment company, idol, or drama — this disclaimer is a standing commitment, not just current About-page copy.
- Ad-free positioning is a current commitment; AdSense is an explicitly anticipated *future* change once traffic/domain maturity justify it, not a contradiction to paper over.
- Existing incumbent visual system (dark "holographic" theme: near-black background, magenta/violet/cyan/gold gradient accents, Black Han Sans display + Plus Jakarta Sans body + JetBrains Mono mono) is mid-renewal per CLAUDE.md — treated as evidence/anti-reference for the pending redesign, not a constraint to preserve, except where CLAUDE.md flags specific *functional* behaviors (language toggle, localStorage persistence, active-nav state, per-word SEO/structured data, search/category filtering) that must survive regardless of visual direction.

## Evidence on Hand

No real traction data yet — no published traffic numbers, follower counts, submission volume, or testimonials. GA4 is wired up (including a `search_word` event intended to eventually drive data-based trending) but nothing has been reported back as evidence. Do not fabricate usage stats, testimonials, press mentions, or user counts in future copy or design work; state absence explicitly where a real product would show this kind of proof.

## Product Principles

1. **Accuracy over speed to publish.** Every entry is hand-reviewed before going live — this is a stated differentiator against unmoderated slang sites, not just a submission-flow detail.
2. **No Korean fluency required, ever.** Romanization and example sentences are not optional extras; they're the core promise of "shortcut" positioning.
3. **Language completeness is non-negotiable per entry.** A word isn't really "added" until all 6 language fields (kr/rom/en/es/zh/cn + separately ja) exist — partial entries silently degrade to English and have caused real bugs.
4. **Independent and ad-free is current identity, not permanent policy.** AdSense is an anticipated milestone tied to traffic/domain maturity, not a betrayal of the "independent" claim — don't treat these as in conflict.
5. **Growth targeting is narrower than product scope.** Instagram/marketing content can speak specifically to young women abroad; the site itself, its copy, and its functionality should stay welcoming to "anyone who loves K-pop, K-dramas, or Korean culture."
