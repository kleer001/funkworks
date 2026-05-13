# Attribution

This skill is **derived from
[alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design)**
under its **Personal Use License**. The complete upstream licence is
preserved verbatim at `LICENSE` in this directory and supersedes anything
written here in case of conflict.

Upstream author: alchaincyf (花叔 · 花生) — alchaincyf@gmail.com

## What was kept (verbatim copies)

| Upstream path | Local path |
|---|---|
| `references/design-styles.md` | `references/design-philosophies.md` |
| `references/critique-guide.md` | `references/critique-rubric.md` |
| `LICENSE` | `LICENSE` |

## What was extracted

- `references/anti-slop.md` was newly written from the upstream
  `SKILL.md` section "6. 反AI slop" plus the "反AI slop速查" table, with
  animation-pitfall-specific entries removed.

## What was written from scratch

- `SKILL.md` — a thin English-leaning wrapper that lists triggers,
  declares scope (judgment only, no production pipelines), points at the
  three references, and condenses the upstream's eight core principles
  into a compact list.
- `ATTRIBUTION.md` — this file.

## What was dropped (and why)

The upstream skill is a 60 KB SKILL.md plus 21 reference files and
~30 MB of assets covering HTML high-fidelity prototypes, slide decks
(1920×1080 HTML), motion design, App / iOS prototype rules, the
Tweaks variant system, Speaker Notes, Starter Components (jsx),
Playwright verification, HTML → MP4 / GIF video export with BGM, and a
Doubao-TTS narrated-animation pipeline.

None of that matches Funkworks's actual production workflow (markdown
tutorials, screenshots, Flux-generated banners, single-file plugins),
so it was excluded to keep the installed skill lean and the trigger
surface accurate.

Excluded files:
- `assets/` (BGM, jsx components, SVG, sfx, showcases) — 30 MB
- `demos/` (10 HTML demo files)
- `scripts/` (render-video, tts-doubao, html2pptx, narrate-pipeline,
  export_deck_*, mix-voiceover, verify.py)
- `test-prompts.json`
- `README.md` / `README.zh.md`
- All upstream `references/*` files except `design-styles.md` and
  `critique-guide.md`.
- Upstream `SKILL.md` sections not relevant to design judgment:
  "App / iOS 原型专属守则", "工作流程" (the TaskCreate/Playwright/video
  flow), "技术红线" (React-Babel rules), "Starter Components",
  "References路由表" (for the dropped files), "跨 Agent 环境适配说明",
  "产出要求" (HTML deliverable rules), "Skill 推广水印" (animation
  watermark), the animation-specific entries in "反AI slop速查".

## License compliance

Per upstream LICENSE clause 1.4, derivative skills require:
1. The derivative is in a **personal repository** — `kleer001/funkworks`
   is an individual GitHub account; Funkworks's `CLAUDE.md` explicitly
   asserts portfolio status with no commercial layer.
2. **Visible credit to the source** — this `ATTRIBUTION.md`, the
   verbatim `LICENSE`, and the credit line at the bottom of `SKILL.md`
   satisfy this. The SKILL.md description block also surfaces the
   derivation in the skill picker.

Commercial use of Funkworks (transferring the repo to a company,
delivering it to paying clients, building paid products on top, etc.)
would require a commercial licence from alchaincyf — contact details
in `LICENSE`.
