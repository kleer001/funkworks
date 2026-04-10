---
name: honest-copy
description: >-
  Audit announcement copy for false, unverifiable, or fabricated claims.
  TRIGGER when the user asks to check, audit, or honest-check any copy,
  or when writing or reviewing any announce.md file.
argument-hint: "[path/to/announce.md or inline copy]"
allowed-tools: Read, Glob, Grep, Bash
---

Audit the announcement copy at **$ARGUMENTS** for honesty.

Read the file. Then go line by line through every claim and flag anything that fails
one of these tests:

---

## The Four Tests

**1. First-person experience claims**
Any sentence starting with "I", "I've", "Every time I", "I got tired of", etc.
Ask: is this verifiably true based on the git history, issue tracker, or something
the user has explicitly stated? If not, flag it.

> Bad: "The Houdini COP I got tired of rebuilding from scratch"
> Bad: "Every time I needed to fit an image, I'd rebuild the same node chain"
> OK: "Houdini's Resample COP only does Stretch" ← verifiable fact about the software

**2. Ordinal and superlative claims**
"First release", "first Houdini release", "most complete", "the only", etc.
Run `gh release list` to verify any ordinal claim. Flag unsupported superlatives.

**3. Implied repeated personal experience**
Narrative framing like "every time", "I kept having to", "I always ended up" implies
something happened repeatedly. This is fabricated unless the user has said so.
Rephrase as a description of the problem in second or third person instead.

**4. Emotional/rhetorical filler**
"which feels right", "that's the way it should be", "finally", "at last" —
these add sentiment without adding information. Flag and suggest cutting.

---

## Output Format

List each flagged item as:

```
LINE: [quote the sentence]
PROBLEM: [which test it fails and why]
FIX: [a replacement that says the same thing honestly, or "cut it"]
```

If nothing is flagged, say so explicitly: "No issues found."

After the audit, ask the user which fixes to apply, then edit the file.

---

## When to Run This

The publish skill calls for a factual audit in Step 6. This skill is the
implementation of that audit. Run it on every announce.md before outputting
final copy.
