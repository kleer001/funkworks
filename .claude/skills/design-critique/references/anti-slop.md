# Anti-AI-slop reference

Extracted from `alchaincyf/huashu-design` `SKILL.md` section 6 and the
"反AI slop速查" table, condensed into English and trimmed of animation-
specific entries. The original is bilingual EN/CN; this version keeps
only the design-judgment material relevant to the Funkworks scope
(markdown tutorials, screenshots, banners, plugin cards).

---

## 1. What "AI slop" means and why it matters

**AI slop** is the visual lowest-common-denominator embedded in AI
training data: purple gradients, stock-emoji icons, rounded cards with
left-coloured border accents, SVG-drawn faces and figures. These
elements aren't ugly in isolation — they're slop because they're the
default mode of AI generation, and **they carry no brand information**.

The logic chain that makes anti-slop a design rule, not aesthetic
snobbery:

1. The user asked you to design something because they want **their**
   brand to be recognised.
2. AI default output ≈ training-data average ≈ all brands averaged
   together ≈ **no specific brand recognised**.
3. Therefore, AI default output = diluting the user's brand into "yet
   another AI-made page."
4. Anti-slop isn't about taste, it's about **protecting brand
   recognition for the user**.

This is why finding and using real brand assets (logo, product images,
brand fonts, declared palette) is the strongest positive form of
anti-slop — doing the right thing crowds out the wrong thing
automatically. The checklist below is the negative form: things to
avoid when no positive direction exists.

---

## 2. What to avoid (with reasons)

| Element | Why it's slop | When it's OK |
|---|---|---|
| Aggressive purple gradients | AI training data's universal "tech vibe" formula — appears on every SaaS / AI / web3 landing page | The brand actually uses purple gradients in its declared spec (e.g. Linear in certain contexts), or the task is to satire/exhibit this look |
| Emoji as bullet-list icons | AI training data attaches an emoji to every bullet, signalling "couldn't think of an icon so dropped an emoji" | The brand uses emoji in its spec (e.g. Notion), or the audience is explicitly informal / kids |
| Rounded card + left-coloured border accent | The 2020-2024 Material / Tailwind cliché — now visual noise | Explicitly requested, or the combination is preserved in the brand spec |
| SVG-drawn imagery (faces, figures, products) | AI-generated SVG figures always have misaligned features and broken proportions | **Almost never.** Use real photography (Wikimedia / Unsplash / Met / AI-generated photo) when there's a real subject; honest "image pending" placeholder when there isn't |
| CSS silhouette or SVG-drawn approximation of a real product | The output reads as "generic tech animation" — black background, orange accent, rounded slabs — and every physical product ends up looking identical. Brand recognition collapses to zero. | **Almost never.** Always try to find the real product image first; fall back to AI image generation with the official reference image as a base; if all else fails, label as honest placeholder ("product photo pending"). |
| Inter / Roboto / Arial / system font set as display type | Too common — readers can't tell whether they're looking at a polished product or a demo page | The brand spec explicitly mandates these (e.g. Stripe uses a heavily customised Söhne / Inter variant — but customised, not raw) |
| Cyberpunk neon / deep navy `#0D1117` background | GitHub-dark-mode aesthetic copied past the point of usefulness | A developer-tools product whose own brand goes this direction |

**The one legitimate exception**: "The brand uses this in its declared
spec." That makes the element a brand signature, not slop. Without that,
the element drains brand identity.

---

## 3. What to do instead (with reasons)

- ✅ Use `text-wrap: pretty`, CSS Grid, modern CSS layout details. These
  are the typography taxes that AI defaults can't replicate — they
  signal that a real designer (or a careful agent) was involved.
- ✅ Pick colours via `oklch()` (or whatever the brand spec uses).
  **Never invent a new colour out of thin air** — every ad-hoc colour
  added dilutes brand recognition.
- ✅ Prefer AI-generated imagery (Flux, Imagen, Lovart) over hand-drawn
  SVG. Use HTML/CSS screenshots only for precise data tables where
  pixel exactness matters — AI images are more accurate AND more
  textured than SVG, and feel more crafted than HTML screenshots.
- ✅ Use curly / typographic quotation marks (" " / ' ') rather than
  straight quotes (" / '). Small detail, signals editorial review.
- ✅ **Do one detail at 120% effort; leave the rest at 80%.** Taste is
  exquisite-where-it-matters, not uniformly intense everywhere.

---

## 4. Quick-reference table

| Category | Avoid | Use instead |
|---|---|---|
| Type | Inter / Roboto / Arial / system fonts as display | Distinct display + body pairing |
| Colour | Purple gradients, freshly invented colours | Brand palette or oklch-defined harmonious set |
| Container | Rounded card + left-coloured border accent | Honest borders / dividers, or no container at all |
| Imagery | SVG-drawn people, objects | Real photography or honest placeholder |
| Icons | Decorative icons on every bullet (slop) | Density elements that carry **differentiating** information — keep those, drop the decorative ones |
| Filler | Invented stats / quotes as decoration | Whitespace, or ask the user for real content |

---

## 5. When showing slop is the point (counter-examples)

When the task itself is to show what slop looks like (e.g. an article
about AI slop, a before-after comparison), **don't let the entire page
become slop**. Isolate the counter-example inside a honest container:
dashed border, "Bad example — don't do this" tag corner. The
counter-example should serve the narrative, not pollute the page's
main aesthetic.

This isn't a hard rule (no template prescription) — it's a principle:
make the counter-example visibly a counter-example, don't let the page
itself drift into the thing you're warning about.
