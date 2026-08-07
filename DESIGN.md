---
name: HelloKSlang Dictionary
description: A K-pop/K-drama slang dictionary built as a photocard binder — every lookup is a pull, every entry a two-sided card.
colors:
  charcoal-backdrop: "#151217"
  charcoal-surface: "#1E1A22"
  charcoal-surface-raised: "#27222C"
  ink-cream: "#F3ECDD"
  ink-cream-soft: "#A79E92"
  ink-cream-faint: "#6E665C"
  cardstock: "#F2E9D8"
  cardstock-hi: "#F8F1E3"
  card-ink: "#211B16"
  card-ink-soft: "#5B5248"
  garnet: "#B21B3E"
  garnet-bright: "#D42953"
  brass: "#B4923F"
  caption-black: "#100E13"
  caption-ink: "#FDF8EE"
  caption-ink-soft: "#B8AF9F"
typography:
  display-kr:
    fontFamily: "'Black Han Sans', sans-serif"
    fontSize: "clamp(2.1rem, 5vw, 3.4rem)"
    fontWeight: 400
    lineHeight: 1.22
    letterSpacing: "-0.01em"
  card-term:
    fontFamily: "'Black Han Sans', sans-serif"
    fontSize: "clamp(2.2rem, 7vw, 3.1rem)"
    fontWeight: 400
    lineHeight: 1.05
  headline:
    fontFamily: "'Bricolage Grotesque', sans-serif"
    fontSize: "19px"
    fontWeight: 700
    lineHeight: 1.3
  body:
    fontFamily: "'Hanken Grotesk', sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
  body-lead:
    fontFamily: "'Hanken Grotesk', sans-serif"
    fontSize: "1.05rem"
    fontWeight: 500
    lineHeight: 1.6
  label:
    fontFamily: "'JetBrains Mono', monospace"
    fontSize: "11px"
    fontWeight: 700
    letterSpacing: "0.4px"
  romanization:
    fontFamily: "'JetBrains Mono', monospace"
    fontSize: "14.5px"
    fontWeight: 400
    letterSpacing: "normal"
rounded:
  card: "16px"
  ui: "14px"
  related-card: "12px"
  caption-bar: "10px"
  pill: "999px"
spacing:
  page-max: "1180px"
  word-max: "860px"
  page-gutter: "28px"
  card-front-padding: "36px 36px 26px"
  card-back-padding: "26px 36px 34px"
components:
  button-search-submit:
    backgroundColor: "{colors.garnet}"
    textColor: "#FFFFFF"
    rounded: "999px"
    size: "42px"
  button-search-submit-hover:
    backgroundColor: "{colors.garnet-bright}"
  cta-primary:
    backgroundColor: "{colors.garnet}"
    textColor: "#FFFFFF"
    rounded: "{rounded.pill}"
    padding: "12px 22px"
  cta-primary-hover:
    backgroundColor: "{colors.garnet-bright}"
  cta-secondary:
    backgroundColor: "rgba(33,27,22,.06)"
    textColor: "{colors.card-ink}"
    rounded: "{rounded.pill}"
    padding: "12px 22px"
  chip-category-tag:
    backgroundColor: "rgba(180,146,63,.16)"
    textColor: "#7A6224"
    rounded: "{rounded.pill}"
    typography: "{typography.label}"
    padding: "4px 10px"
  chip-lang-switch-active:
    backgroundColor: "{colors.garnet}"
    textColor: "#FFFFFF"
    rounded: "{rounded.pill}"
  input-search:
    backgroundColor: "{colors.charcoal-surface}"
    textColor: "{colors.ink-cream}"
    rounded: "{rounded.ui}"
    typography: "{typography.body}"
---

# Design System: HelloKSlang Dictionary

## Overview

**Creative North Star: "The Photocard Pull"**

HelloKSlang is built as a photocard binder, not a search-engine results page. Every lookup is a pull: a single card resolves out of a dark, gallery-lit backdrop, printed on warm cardstock with an ecru fiber grain, foil-stamped on its one hero term, and read across two zones — the name on the front, the story on the back. The build's own direction contract states its refusal plainly: neither the pastel-hologram-photocard cliché (soft gradients, sparkle, holographic sheen everywhere) nor its opposite, the generic clean-SaaS-dictionary look. It also deliberately steers away from the near-black-plus-neon-glow "AI dark mode" that a slang/AI-adjacent product could easily default to — the backdrop here reads as studio darkness behind a physical object, not ambient glow.

The system is genuinely bi-material: a charcoal, backlit "photography backdrop" world for site chrome (nav, search, footer), and a warm, textured "cardstock" world for the one recurring object that is the whole product — the word card. The two zones never blend into each other; the card is always a discrete printed object sitting in front of a dark room, not a panel embedded in the page.

Garnet is the single committed interactive/ink accent across both materials; brass is reserved for category and status labels; the foil-stamp gradient is spent on exactly one thing per card — the hero Korean term — and nowhere else. This scarcity is deliberate and load-bearing, not an oversight.

**Key Characteristics:**
- A dark charcoal chrome layer and a warm ecru cardstock card layer, never merged into one flat surface
- Fractal-noise grain, multiplied into the card fill, standing in for gradients wherever "material" is being claimed
- One foil-stamp treatment, spent on one hero term per card, nowhere else
- Card-cornered radii (14–16px) everywhere the card system itself lives; pill radii (999px) reserved for UI chrome (nav, tags, buttons)
- Two build-specific realizations of the same card object: a 3D flip on the interactive search surface, a static perforated seam on the SEO-facing word template

## Colors

The palette is a deliberate two-material system: cool charcoal darks for the site's "room," and warm cream/cardstock tones for the card object itself, pinned together by one committed red accent and one supporting metal accent.

### Primary
- **Garnet** (`#B21B3E`): the single committed interactive/ink accent — search submit button, play buttons, active language pill, card top-edge stripe, focus/selection color, link-hover underline. Used at rest.
- **Garnet Bright** (`#D42953`): the hover/active state of garnet — search submit hover, play-button hover, active nav underline, focus ring color, and the color of "stroke" emphasis text in the hero headline.

### Secondary
- **Brass** (`#B4923F`): the secondary accent, reserved for category/status language — the "Dictionary" logo badge, category tags and pills, search-result category chips, back-link color. Never used for primary interactive affordances; it marks metadata, garnet marks action.

### Tertiary
- **Foil Gradient** (`linear-gradient(115deg, #6E5419, #C9A64C, #EBD08A, #C9A64C, #7A5E1E, #B5924A, #6E5419)`): an engraved metallic multi-stop gradient, clipped to text (`background-clip: text`), reserved for exactly one element per card — the hero Korean term. Not a general-purpose gradient-text device.

### Neutral — Charcoal (chrome/backdrop material)
- **Charcoal Backdrop** (`#151217`): page background, the "room" the cards sit in.
- **Charcoal Surface** (`#1E1A22`): header, search box, lang-switch, mobile menu, search-dropdown backgrounds.
- **Charcoal Surface Raised** (`#27222C`): hover state for list rows inside the search dropdown.
- **Cream Ink** (`#F3ECDD`): primary text color on charcoal.
- **Cream Ink Soft** (`#A79E92`): secondary text on charcoal (subheads, nav, placeholders).
- **Cream Ink Faint** (`#6E665C`): tertiary/least-emphasis text on charcoal (timecodes).

### Neutral — Cardstock (card material)
- **Cardstock** (`#F2E9D8`): the card face base tone.
- **Cardstock Hi** (`#F8F1E3`): the lighter gradient stop blended under the card's grain texture.
- **Card Ink** (`#211B16`): primary text on the card face (definitions).
- **Card Ink Soft** (`#5B5248`): secondary text on the card face (romanization, example prose, source line).

### Neutral — Caption bar (a third, deliberately distinct material)
- **Caption Black** (`#100E13`): the burned-in-subtitle bar background inside the card's back zone — near-black, distinct from both the charcoal chrome and the cardstock face it sits on.
- **Caption Ink** (`#FDF8EE`): bold caption text.
- **Caption Ink Soft** (`#B8AF9F`): translated caption lines beneath the primary caption line.

### Named Rules
**The Grain, Not Gradient Rule.** Card surfaces get their material read from a multiplied fractal-noise SVG texture blended over a two-stop gradient (`background-blend-mode: multiply`), never a flat or unblended gradient alone. This was a specific fix after review flagged flat gradients as insufficiently material — the grain is what makes the card read as printed stock rather than a colored panel.

**The One Foil Rule.** The foil-stamp gradient is spent on exactly one element per card: the hero Korean term. It is never applied to body text, buttons, or more than one heading per card. An earlier version added a repeating hairline overlay on top of the gradient and it was reverted — it aliased against thin Hangul strokes at small sizes and made whole glyphs read as a solid block. The gradient alone, with dark stops kept deep enough to hold contrast against the cardstock, is the standing implementation.

**The Garnet-Acts, Brass-Labels Rule.** Garnet is reserved for interactive/action affordances (buttons, active states, focus, links). Brass is reserved for passive metadata (category tags, badges, status labels). The two accents are never swapped in role.

## Typography

**Display Font (Korean):** Black Han Sans (with sans-serif fallback)
**Display Font (Latin/UI):** Bricolage Grotesque (with sans-serif fallback)
**Body Font:** Hanken Grotesk (with sans-serif fallback)
**Label/Mono Font:** JetBrains Mono (with monospace fallback)

**Character:** A bold, single-weight Korean display face carries every hero term with poster-like weight; Bricolage Grotesque handles the Latin wordmark and UI voice with a lighter editorial confidence; Hanken Grotesk is the workhorse body voice; JetBrains Mono marks anything that reads as "printed metadata" — romanization, category codes, timecodes — reinforcing the card-as-printed-object metaphor.

### Hierarchy
- **Display (Korean hero)** (400, `clamp(2.1rem, 5vw, 3.4rem)`, line-height 1.22): the homepage hero headline, mixing Korean and English in one line — this is why Black Han Sans, not Bricolage Grotesque, carries even the bilingual hero heading.
- **Card Term** (400, `clamp(2.2rem, 7vw, 3.1rem)` on the search card / `clamp(42px, 8.5vw, 62px)` on the word template, line-height 1.05): the single hero Korean term per card, foil-stamped.
- **Headline** (700, 19px, Bricolage Grotesque): section headings like "Related words."
- **Body** (400–700, 15.5–16.5px, Hanken Grotesk, line-height 1.5–1.6): definitions and example prose on the card back.
- **Body Lead** (500, 1.05rem, line-height 1.6): the hero subhead beneath the search headline.
- **Label** (700, 10–11px, JetBrains Mono, uppercase, letter-spacing 0.4–1.2px): category tags, section eyelabels ("Meaning", "Real usage"), badges.
- **Romanization/Mono** (400, italic, 14.5–15.5px, JetBrains Mono): romanized term display, source/timecode lines.

### Named Rules
**The Korean-Carries-Bilingual-Type Rule.** Any heading that mixes Korean and Latin script in one line (the hero tagline, the card term) is set entirely in Black Han Sans, not split across two font families — the Korean face is treated as the display face for the whole system's bilingual moments, not a special case bolted onto a Latin headline font.

## Layout

Two container widths, by surface role: the full chrome (header/footer/nav) spans up to 1180px; the word-detail template's content column narrows to 860px, since a single card and its related-word grid don't need the wider measure. Both use a consistent 28px side gutter that collapses to 18–22px under 640px.

The homepage is a single centered hero: tagline, then a card-shaped search bar, then (on search) one result card filling the frame. The word template stacks vertically: back-link, category pill, the card object, then a two-column related-word grid (collapsing to one column under 640px).

Responsive behavior is chrome-first: the desktop language-switch button row and horizontal nav links disappear under 860px in favor of a hamburger mobile menu and a native `<select>` language dropdown — this swap exists specifically because five language buttons overflow at narrow widths.

## Elevation & Depth

The system is a hybrid: the chrome layer is flat (no shadows on header, nav, or footer beyond a hairline border), while the card object is genuinely lifted off the dark backdrop with a soft, wide, downward shadow that reads as a physical object under a single overhead light rather than a UI panel with a drop shadow. The `body::before` vignette (a soft radial highlight near the top, a soft radial darkening near the bottom) reinforces this as a photography-backdrop light source, not a decorative color-blob glow.

### Shadow Vocabulary
- **Card lift** (`box-shadow: 0 24px 60px -24px rgba(0,0,0,.5)` on the search-result card; `0 28px 70px -28px rgba(0,0,0,.55)` on the word-template card object): the card's resting elevation off the charcoal backdrop.
- **Dropdown lift** (`box-shadow: 0 24px 60px -20px rgba(0,0,0,.6)`): the search-result dropdown panel.
- **Related-card hover lift** (`box-shadow: 0 14px 30px -16px rgba(0,0,0,.5)`, paired with `translateY(-2px)`): the only shadow that changes on interaction rather than sitting at rest.
- **Caption-bar inset** (`box-shadow: inset 0 0 0 1px rgba(243,236,221,.06)`): a hairline inner edge, not a drop shadow — keeps the caption bar reading as a separate inset material rather than a raised one.

### Named Rules
**The One Light Source Rule.** Depth comes from a single implied overhead light (the vignette plus the card's downward shadow), never from multiple colored glows or ambient blur blobs. This is the specific device the direction contract uses to keep the dark backdrop from reading as the "neon AI dark mode" cliché it was built to avoid.

## Shapes

Two distinct corner languages, assigned by role, never mixed within the same element. **The Card Corners, Not Pills Rule.** Anything that is the card system itself — the card object, related-word cards, the caption bar — uses moderate rounding (16px card radius, 12px related-card, 10px caption bar): grounded and card-like, explicitly not the fully-pill/bubbly language of the site's prior "holographic" identity. Anything that is UI chrome — the lang-switch, tag/chip pills, CTA buttons, the search box's outer shell — uses full pill radii (999px) or the 14px `--radius-ui` value. The card's perforated seam (a dashed horizontal rule with two punch-hole circles cut into the card edge) is the system's one custom silhouette device, used only at the front/back boundary of the card object.

## Components

### Buttons
- **Shape:** circular for icon-only actions (search submit, play button, 42/34px), full pill (999px) for text CTAs.
- **Primary (CTA):** garnet background, white text, pill radius, `12px 22px` padding (`.cta-primary`).
- **Hover / Focus:** background shifts to garnet-bright; focus-visible gets a 2px garnet-bright outline with 3px offset system-wide.
- **Secondary:** near-transparent card-tinted background (`rgba(33,27,22,.06)`) with a hairline card-line border; border shifts to garnet on hover (`.cta-secondary`).

### Chips (Category Tags)
- **Style:** brass-tinted translucent background (`rgba(180,146,63,.16)`), deep-brass text (`#7A6224`), pill radius, JetBrains Mono uppercase label type.
- **State:** the same chip styling is reused for the homepage search-result category chip and the word-page category pill/tag — one consistent "metadata badge" across surfaces.

### Cards / Containers (the signature object — see below)
- **Corner Style:** 16px (`--radius-card`).
- **Background:** cardstock gradient + multiplied fractal-noise grain (see Colors → Named Rules).
- **Shadow Strategy:** card lift, see Elevation & Depth.
- **Border:** 1px hairline `rgba(33,27,22,.14)`, plus a 3px garnet stripe across the top edge (`::before`).
- **Internal Padding:** 36px front zone / 26–34px back zone at desktop, tightening to 22–24px under 640px.

### Inputs / Fields
- **Style:** charcoal surface background, 1.5px hairline-strong border, `--radius-ui` (14px), inner content clip at `radius - 4px`.
- **Focus:** border shifts to garnet-bright, plus a soft 4px garnet-bright glow ring (`box-shadow: 0 0 0 4px rgba(212,41,83,.16)`) on `:focus-within` — a "structural" focus response, not ambient decoration.

### Navigation
- **Style:** sticky header, blurred translucent charcoal (`backdrop-filter: blur(10px)`), hairline bottom border. Nav links get a garnet-bright underline that scales in from the left on hover/active. Active page state is a solid underline plus lightened text; the same active state on mobile becomes garnet-bright text with no underline.
- **Language switch:** a pill-shaped segmented control (desktop) with the active language filled garnet-solid; collapses to a native `<select>` styled to match (arrow icon, pill radius) below 860px. Toggle state and page-active-nav state are both driven by the same `--ease-flip` easing curve used for the card flip, tying chrome motion to the card motion.

### The Card (signature component)
The recurring object the whole product is built around, realized two different ways depending on the surface's job:
- **Search surface (`index.html`):** a genuine 3D flip — `perspective`, `transform-style: preserve-3d`, `rotateY(180deg)` on a `.flipped` class, `backface-visibility: hidden` on both faces, eased with `cubic-bezier(0.16, 1, 0.3, 1)` over 600ms, triggered client-side after a result is chosen. Fully disabled under `prefers-reduced-motion: reduce`.
- **Word template (`word/*.html`, 651 pages):** a static "photocard-object" with front and back zones separated by a **perforated seam** (a dashed rule with two punched circles at its ends) — always both visible, never flip-gated. This is a deliberate divergence from the search surface, not an inconsistency: these are SEO/crawler-facing landing pages, and gating content behind a JS-triggered flip would hide it from crawlers and cost the reader a click.
- **Caption bar:** inside the card's back zone, the example sentence renders in a near-black bar styled like a burned-in fansub caption — bold light text, small mono "Commonly seen on:" source line beneath. This is a third material (see Colors → Neutral — Caption bar), deliberately distinct from the cardstock card it's inset into, because captioning real usage is the product's core promise.

## Do's and Don'ts

### Do:
- **Do** build card material from a multiplied fractal-noise grain over a gradient, never a flat or unblended gradient (`background-blend-mode: multiply`).
- **Do** reserve the foil-stamp gradient for exactly one hero term per card.
- **Do** use garnet for action/interactive elements and brass for passive metadata labels — never swap the two roles.
- **Do** use card-style moderate radii (14–16px) for the card system and full pill radii (999px) for UI chrome; never blend the two within one element.
- **Do** author all icons (search, play, menu, arrow, dropdown chevron) as inline SVG.
- **Do** keep the word-template card's front/back zones both statically visible (no flip gate) since those pages are SEO/crawler-facing; reserve the JS-triggered 3D flip for the interactive search result only.

### Don't:
- **Don't** use unicode emoji as functional icons anywhere in the system — every icon in the shipped build is inline SVG.
- **Don't** add colored left/right border accents to cards. The build's own accent device is a top-edge stripe (`::before`, 3px, garnet) — not a side rail — and that is the only border-accent form the system uses.
- **Don't** default to the near-black-plus-neon-glow "AI dark mode" look. Depth here comes from one implied overhead light source (vignette + card shadow), not colored ambient glow — this was a specific rejection named in the build's own direction contract.
- **Don't** apply the foil-stamp gradient to more than one element per card, or add a repeating hairline texture on top of it — a hairline+gradient version was built and reverted because it broke Hangul glyph legibility at small sizes.
- **Don't** revert to the prior identity's fully-pill/rounded-999px card language. Pills are for UI chrome only; the card object itself is deliberately more grounded (14–16px).
