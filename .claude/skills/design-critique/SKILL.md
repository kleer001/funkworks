---
name: design-critique
description: |
  Design-direction advisor + 5-dimensional design review for visual work.
  Pick a design philosophy from a library of 20 named styles (Pentagram, Field.io,
  Kenya Hara, Sagmeister, etc.) before designing, or score a finished design on
  philosophy alignment / visual hierarchy / craft quality / functionality / originality
  (each 0-10) with a Keep / Fix / Quick-Win list. Includes an anti-AI-slop checklist
  for resisting generic AI default aesthetics. Derived from
  alchaincyf/huashu-design (Personal Use License — see LICENSE + ATTRIBUTION.md).
triggers:
  - design review
  - critique this design
  - rate this design
  - 5-dim review
  - design direction
  - design philosophy
  - what style should this be
  - pick a style
  - is this generic
  - anti ai slop
  - score this design
---

# design-critique

A judgment skill, not a production pipeline. Use this when the question is
"is this design any good?" or "what direction should this design take?" —
**not** when the question is "make a design for me." If you need to produce
HTML, slides, animations, or video, this is the wrong skill.

## When to invoke

- Reviewing a tutorial page, landing page, banner, plugin card, palette,
  or any other shipped visual artefact and you want a structured critique.
- Picking between several design directions for a piece of work that
  hasn't started yet.
- Auditing a piece of design for the "generic AI slop" failure mode where
  the output reads as "yet another AI-generated page" with no brand
  identity.

## When NOT to invoke

- Editing copy for veracity → use the `honest-copy` skill instead.
- Generating an Excalidraw diagram → use the `hand-drawn-diagrams` skill.
- Choosing colours from a palette → use the `color-expert` skill (or
  consult `references/design-philosophies.md` here for style-driven
  palette starting points).
- Producing slides, animations, or videos — this skill explicitly does
  not cover production pipelines (the upstream skill does, that material
  was stripped).

## References (read these as needed)

| File | When to consult |
|---|---|
| `references/design-philosophies.md` | Before designing, when picking a style direction. 20 named philosophies grouped in 5 schools (Information Architecture / Motion Poetics / Eastern Minimalism / Experimental Avant-garde / Asian-Contemporary), each with core characteristics + an English prompt DNA block usable directly for AI image generation or HTML design. Bilingual EN/CN. |
| `references/critique-rubric.md` | When reviewing a finished design. The 5-dimensional rubric with 1-10 scoring tables for each dimension, per-scene emphasis notes (web / PPT / PDF / infographic), and a common-cliché checklist. |
| `references/anti-slop.md` | When the work risks looking generic-AI. Lists what to avoid (purple gradients, emoji icons, rounded card + left border accent, SVG-drawn people, Inter-as-display, etc.) and what to do instead. |

## Eight core principles (condensed from upstream)

These apply whether you're directing a design or critiquing one.

1. **From existing context first.** Designing from scratch is the last
   resort. Look for a design system, brand kit, codebase, Figma file, or
   reference screenshots before generating anything. If none exists and
   requirements are vague, switch to direction-advisor mode (propose 3
   differentiated directions from `design-philosophies.md`) before
   producing pixels.
2. **Asset protocol.** When the work involves a specific brand or product,
   find the real logo, product imagery, and UI screenshots first. CSS
   silhouettes and SVG-drawn approximations destroy brand recognition —
   the whole point of a brand design is to be recognisable. (For
   non-funkworks brand work; funkworks itself uses its own banner +
   mascot.)
3. **Show assumptions before executing.** When the brief is ambiguous,
   state what you're about to do and why before doing it. Treat the user
   as your manager.
4. **Give variations, not "final answers."** When time allows, produce
   2-3 differentiated takes rather than one polished output. Lets the
   user steer based on what they see.
5. **Placeholder beats bad implementation.** Honest `[product photo
   pending]` placeholder beats a generic AI-generated stand-in that
   degrades brand identity.
6. **System first, don't fill.** Empty space is design content. Don't
   pad with decoration to "fill the page." Negative space is a tool.
7. **Anti-AI-slop is brand protection, not snobbery.** Default AI
   aesthetics (purple gradients, rounded cards with left accents,
   stock-emoji bullets, Inter-as-display) average across all training
   data, so they erase the brand you're trying to surface. Resist them
   in favour of brand-specific choices.
8. **Fact-verify before claiming product specs.** Any assertion about a
   specific product's existence, version, release date, or hard specs
   demands a WebSearch before being written into copy or design. Don't
   design around "I think Pocket 4 hasn't launched yet" — search first.

## Critique output format

When invoked for a review, structure the output like this:

```
## 5-Dimensional Review · <artefact name>

| Dimension              | Score | Notes |
|------------------------|:-----:|-------|
| Philosophy alignment   |  N/10 | …     |
| Visual hierarchy       |  N/10 | …     |
| Craft quality          |  N/10 | …     |
| Functionality          |  N/10 | …     |
| Originality            |  N/10 | …     |
| **Total**              | NN/50 |       |

### Keep
- What's working that should not change.

### Fix
- ⚠️ **Critical** — must address before ship
- ⚡ **Important** — should address this pass
- 💡 **Optimisation** — nice-to-have

### Quick Wins (5-minute fixes, ranked)
1. …
2. …
3. …
```

Critique the design, not the designer. Per-dimension rubrics live in
`references/critique-rubric.md` — consult them rather than improvising
scoring criteria.

## Attribution

Derived from [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design)
under the Huashu Design Personal Use License. The animation / video / slide /
TTS / HTML-as-medium production pipeline material from the upstream was
intentionally stripped — this skill keeps only the design-judgment portion.
Full upstream license terms in `LICENSE`; see `ATTRIBUTION.md` for what was
kept versus dropped.
