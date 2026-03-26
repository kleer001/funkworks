# Plugin Factory: Build Pipeline

## Philosophy

One tight loop: opportunity in, tested plugin + tutorial out. Start with a single host application. Get the loop working end to end. Then expand hosts.

The build pipeline answers one question: **"Can we turn an approved opportunity into a shippable plugin with minimal human intervention?"** The answer is yes — if the host application has an MCP connection that gives agents real-time feedback.

---

## Architecture Overview

```
Approved Opportunity (from Research Queue, rated "Build This")
    ↓
Stage 1 — Spec Agent (writes plugin brief)
    ↓
Human Review (approve / revise spec)
    ↓
Stage 2 — Build Agent(s) (write plugin code)
    ↓
Stage 3 — Test Agent (smoke tests via MCP)
    ↓                   ↑
    ↓            (fail → back to Build Agent with error log)
    ↓
Stage 4 — Doc Agent (writes tutorial page)
    ↓
Stage 5 — Publish (repo + static site)
```

**Human checkpoints:** Two total — rating the opportunity (in the Research pipeline) and approving the spec. Everything else is automated.

---

## Host Application Selection and Sequencing

### Tier 1: Blender (Start Here)

**Why Blender first:**

| Factor | Detail |
|--------|--------|
| **API** | Python API (`bpy`) is extensive, open-source (GPL), and well-documented at [docs.blender.org/api](https://docs.blender.org/api/current/) |
| **License** | Free and open-source — no license cost to develop or distribute |
| **MCP** | Can be built using the same pattern as the existing Houdini MCP — Python server communicating with a running Blender instance |
| **Community** | Largest of the four (r/blender alone has ~1.4M members) — maximum distribution potential |
| **Distribution** | Free plugins have zero friction to adoption; users can install a `.py` addon directly |
| **Testing loop** | MCP enables: install addon → call functions → inspect results → iterate — all without human interaction |

**The loop from "agent writes plugin" to "agent tests plugin in a live Blender session" is achievable fast.** This is the critical advantage. Build agents that work blind (no MCP) produce worse code and require human testing at every iteration.

### Tier 2: After Effects (Second)

**Why AE is harder:**

| Factor | Detail |
|--------|--------|
| **Scripting landscape** | In transition. ExtendScript (.jsx) is the legacy but still primary scripting method. CEP panels are deprecated (CEP 12 is the final version, shipped with AE 25.0). Adobe's replacement is UXP (Unified Extensibility Platform), but UXP support for AE is still in beta/limited availability as of early 2026. UXP is fully available in Photoshop but AE lags behind. |
| **Expression engine** | AE expressions now support a modern JavaScript engine (selectable in Project Settings), separate from ExtendScript. This is a third scripting context. |
| **No MCP** | No existing MCP connection for After Effects. The build agent would write code it cannot run or test itself. Every iteration requires a human to install and verify. |
| **License** | Adobe Creative Cloud subscription required for development and testing |

**Practical AE scripting targets for 2026:**
- **ExtendScript (.jsx):** Broadest compatibility. Most existing scripts and tools use this. Safe default for now.
- **CEP panels:** Still functional but deprecated — avoid building new ones. Existing CEP plugins will stop working as Adobe phases out support.
- **UXP panels:** The future, but premature to target for AE until it reaches general availability. Monitor Adobe's roadmap.
- **Expressions:** Lightweight, no installation needed, but limited in scope — good for utility tools, not full plugins.

**The build loop for AE is longer.** Without MCP, the Test Agent cannot run automated smoke tests. Plan for a semi-manual loop initially: agent writes code → human installs and reports results → agent iterates.

### Tier 3: Houdini

**Advantages:** MCP already exists (your Houdini MCP). The agent-to-live-session loop is already proven. Houdini's Python API (`hou` module) is well-documented.

**Disadvantages:** Smaller community (~7K on r/Houdini, though SideFX forums are active). Plugin ecosystem is more specialized — tools tend to be HDAs (Houdini Digital Assets) rather than standalone scripts, which may require a different build pattern. Houdini licenses (Indie: ~$269/year, FX: significantly more) limit the user base.

### Tier 4: Nuke

**Advantages:** MCP exists. Python API (`nuke` module) is mature. Professional compositing users value well-built tools.

**Disadvantages:** Smallest community of the four. Nuke licenses are expensive (Nuke Non-Commercial is free but limited). The user base is almost entirely professional studios — different distribution dynamics than Blender's hobbyist/indie majority.

---

## Stage 1 — Spec Agent

### Input

An approved opportunity from the Research Queue, containing:
- One-paragraph summary of the need
- Source links (community posts describing the problem)
- Feasibility notes from the Synthesis Agent
- Host application tag

### Process

The Spec Agent reads the opportunity and source posts, then writes a plugin brief. It does not write code — it writes a specification that a Build Agent can execute against.

### Output: Plugin Brief

```markdown
# Plugin Brief: [Name]

## Problem Statement
One sentence. What is the user trying to do that they currently can't, or that is
currently painful?

## Proposed Solution
What the plugin does, described in terms of user-visible behavior. Not implementation
details — what the user sees and interacts with.

## Host Application
- Application: [Blender / AE / Houdini / Nuke]
- Minimum version: [e.g., Blender 4.0+]
- API surfaces required: [e.g., bpy.ops.mesh, bpy.types.Panel, bmesh]

## User Interface
- Where does the plugin appear? (menu, panel, toolbar, shortcut)
- What inputs does the user provide?
- What feedback does the user see during execution?

## Inputs and Outputs
- Input: [e.g., selected mesh objects]
- Output: [e.g., modified UV maps on those objects]
- Side effects: [e.g., creates an undo step]

## Edge Cases
- What happens with no selection?
- What happens with incompatible object types?
- What happens with very large inputs (performance)?

## Known Limitations
Things this plugin explicitly does NOT do. Setting boundaries prevents scope creep
during the build stage.

## Acceptance Criteria
Numbered list of testable conditions that the Test Agent will verify.

1. Plugin installs without error on [host app] [version]
2. UI element appears at [location]
3. Primary function executes on a default scene without error
4. [Specific functional test based on the problem being solved]
5. Undo restores the previous state
6. Empty selection produces a user-facing message, not a crash
```

### Human Review

You review the spec before build begins. This is the second and final human checkpoint. If the spec is wrong, the build will be wrong — garbage in, garbage out.

**Review checklist:**
- Does the problem statement match the original community need?
- Is the proposed solution the simplest thing that solves the problem?
- Are the API surfaces listed actually available in the target app version?
- Are the acceptance criteria specific enough that an agent can verify them?

---

## Stage 2 — Build Agents

### Blender Build (MCP-Assisted)

The Build Agent writes a `.py` addon file using the Blender Python API. The MCP connection allows the agent to:

1. Create the addon file
2. Install it into a live Blender session (`bpy.ops.preferences.addon_install`)
3. Enable it (`bpy.ops.preferences.addon_enable`)
4. Call its functions programmatically
5. Inspect results (check object states, read attributes, verify UI registration)
6. Iterate on failures with real error messages

**This is the key advantage of MCP.** The build agent gets real feedback from the running application, not just syntax checking or linting. A build agent with MCP will converge on working code faster than one without.

### After Effects Build (No MCP — Semi-Manual)

The Build Agent writes an ExtendScript file (`.jsx`). Without MCP:

1. Agent writes the script
2. Agent cannot test it directly
3. A human installs the script in AE and reports:
   - Did it load without errors?
   - Does the UI appear?
   - Does the primary function work?
4. Human pastes error messages or observations back to the agent
5. Agent iterates

**This loop is slower but functional.** The semi-manual step adds latency but doesn't block the pipeline — it just means AE plugins take longer to produce.

### Multi-Agent Builds

For larger plugins, multiple agents can work in parallel:

| Agent | Responsibility |
|-------|---------------|
| Core Logic Agent | Writes the main functionality — the algorithm or operation the plugin performs |
| UI Agent | Writes the user interface (panels, menus, operators) that wraps the core logic |
| Review Agent | Reads the combined output and checks for API correctness, naming conventions, and integration issues before handoff to Test |

Multi-agent builds make sense when the plugin has both significant logic and significant UI. For simple plugins (a single operator with a menu entry), one agent is sufficient.

### Build Agent Prompt Structure

The Build Agent receives:
- The full Plugin Brief from Stage 1
- The host application's API documentation (or a curated subset relevant to the required API surfaces)
- A starter template for the addon structure (register/unregister boilerplate)
- Access to MCP for the target application (if available)

The agent writes code iteratively:
1. Write initial implementation
2. Install and test via MCP
3. If errors, read the error, fix the code, reinstall
4. Repeat until acceptance criteria pass or max iterations reached (cap at 10 to prevent infinite loops)

---

## Stage 3 — Test Agent

### Purpose

The Test Agent runs a fixed set of smoke tests against the installed plugin. These are not comprehensive tests — they are a **crash gate**. The goal is to catch obvious failures before the plugin reaches documentation and publishing.

### Smoke Test Suite

| Test | What It Checks | Pass Condition |
|------|---------------|----------------|
| **Install** | Plugin installs without Python errors | No exceptions during install/enable |
| **UI Registration** | UI elements appear where specified | Panel/menu/operator exists and is accessible |
| **Default Scene Execution** | Primary function runs on a fresh default scene | No crash, no unhandled exception |
| **Empty Selection** | Primary function runs with nothing selected | Graceful message or no-op, not a traceback |
| **Undo** | After execution, Ctrl+Z restores previous state | Scene state matches pre-execution state |
| **Disable/Uninstall** | Plugin can be cleanly removed | No residual UI elements or errors on disable |

### Additional Tests (Per-Plugin)

The acceptance criteria from the Plugin Brief generate additional tests specific to each plugin. These are the functional tests — does the plugin actually do what it claims?

Example: If the plugin is "Batch Rename UV Maps," the test agent would:
1. Create 5 objects with UV maps named "UVMap.001" through "UVMap.005"
2. Run the plugin with a rename pattern
3. Verify all UV maps were renamed correctly

### Failure Handling

If any smoke test fails, the Test Agent:
1. Captures the full error traceback
2. Captures the scene state at the time of failure
3. Sends both back to the Build Agent with a request to fix
4. The Build Agent gets up to 3 fix attempts per failing test
5. If the plugin still fails after 3 attempts, it is flagged for human review

### Platform Notes

| Host App | Test Automation | Notes |
|----------|----------------|-------|
| Blender | Fully automated via MCP | All smoke tests can run without human interaction |
| Houdini | Fully automated via MCP | Same pattern as Blender; tests use `hou` module |
| Nuke | Fully automated via MCP | Same pattern; tests use `nuke` module |
| After Effects | Partially manual | Install test requires human; some script-level tests can run via command line (`afterfx -r script.jsx`) but UI tests need a human |

---

## Stage 4 — Doc Agent

### Purpose

Once the plugin passes smoke tests, the Doc Agent writes a tutorial page. This serves two purposes: **documentation** (users understand how to use the plugin) and **discoverability** (the page gets indexed by search engines, users find the plugin through search).

### Tutorial Page Structure

```markdown
# [Plugin Name]

> One-sentence description of what this plugin does.

## What It Does

One paragraph, plain language. No jargon. Describe the problem it solves
and how it solves it.

## Requirements

- [Host application] [minimum version]+
- [Any other dependencies]

## Installation

Step-by-step installation instructions specific to the host application.
For Blender: Edit → Preferences → Add-ons → Install → select the .py file → enable.

## Usage

Step-by-step walkthrough of the primary workflow:
1. Open [host app]
2. Navigate to [panel/menu location]
3. Select [input objects/layers]
4. Click [button] or run [command]
5. [Expected result]

Include descriptions of example scenarios. Note where screenshots or example
renders should be captured (these are added manually or by a future screenshot agent).

## Options and Settings

Table of all user-facing settings with descriptions and default values.

## Known Limitations

Bulleted list of things the plugin does not handle. Set expectations upfront.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | [date] | Initial release |

## License

[License type] — link to full license text.
```

### SEO Considerations

The tutorial page title should include the host application name and the problem being solved, not just the plugin name. Example: "Batch Rename UV Maps — Blender Addon" not "UV Renamer v1.0."

---

## Stage 5 — Publish

### Distribution

Everything is free and open-source. Always.

| Component | Approach |
|-----------|----------|
| **Code hosting** | GitHub — one repo per plugin, or a monorepo with subdirectories per plugin |
| **Documentation** | GitHub Pages or a simple static site (Hugo, Astro, or plain HTML) |
| **Distribution** | Direct download from GitHub Releases; link from the tutorial page |
| **In-app distribution** | Blender Extensions Platform (when plugins are mature enough for review process) |
| **Licensing** | GPL for Blender addons (required by Blender's license); MIT or Apache 2.0 for others |
| **Support** | Tutorial page serves as self-service support; GitHub Issues for bug reports |

The Doc Agent's tutorial page links to the repo. The repo's README links back to the tutorial page. That's the distribution loop. No marketplace friction, no paywalls.

---

## MVP Milestone Definition

The MVP is complete when:

1. **One Blender plugin** has been produced entirely by the agent loop
2. Only **two human touchpoints** were needed: rating the opportunity and approving the spec
3. The plugin **installs without error** on the target Blender version
4. The plugin **passes all smoke tests** (automated via MCP)
5. A **published tutorial page** exists and is publicly accessible
6. The entire loop (spec → build → test → doc → publish) took **less than one working day of agent compute time**

That's the proof of concept. Everything after that is tuning the loop and expanding to additional host applications.

---

## Dependency Map

| Component | Depends On | Status |
|-----------|-----------|--------|
| Spec Agent | LLM API (Claude), approved opportunity from Research Queue | Ready to build — no infrastructure dependency |
| Build Agent (Blender) | LLM API, **Blender MCP** | **Blender MCP is the critical path item** — must be built before Build or Test agents work |
| Build Agent (AE) | LLM API, AE scripting documentation | Can work without MCP (semi-manual testing) |
| Build Agent (Houdini) | LLM API, Houdini MCP | MCP already exists |
| Build Agent (Nuke) | LLM API, Nuke MCP | MCP already exists |
| Test Agent | Host app MCP (for automated testing), predefined smoke test scripts | Blocked on Blender MCP for the MVP path |
| Doc Agent | LLM API, static site or GitHub Pages setup | No infrastructure dependency; can use a simple template |
| Publish | GitHub repo, static site hosting | Trivial setup |

### Critical Path

```
Build Blender MCP  →  Build Agent + Test Agent work  →  Full loop operational
```

Nothing else in the Blender pipeline works without the MCP. The Spec Agent and Doc Agent can be developed and tested independently, but the Build-Test loop — the core of the factory — requires MCP.

For Houdini and Nuke, the MCP already exists, so the critical path is just building the agents themselves.

---

## Expansion Roadmap (Post-MVP)

| Phase | Milestone | Key Work |
|-------|-----------|----------|
| **MVP** | First Blender plugin shipped via full agent loop | Build Blender MCP, all 5 agents, smoke test suite |
| **Phase 2** | 10 Blender plugins shipped; loop time under 4 hours | Tune prompts, expand smoke tests, add automated screenshot capture |
| **Phase 3** | Houdini plugins via existing MCP | Adapt Build and Test agents for HDA workflow; Houdini smoke test suite |
| **Phase 4** | AE plugins via semi-manual loop | Build Agent writes ExtendScript; human-in-the-loop testing until AE MCP exists |
| **Phase 5** | Nuke plugins via existing MCP | Adapt agents for Nuke Python API; Nuke smoke test suite |
| **Phase 6** | Multi-DCC maturity | All four host apps producing plugins through the full agent loop |

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Blender MCP is harder to build than expected | Delays the entire MVP | Prototype early; the Houdini MCP is a proven pattern to follow |
| Build Agent produces code that passes smoke tests but is low quality | Bad reputation, user complaints | Add a Review Agent pass before Test; spot-check early plugins manually |
| Host app API changes break existing plugins | Published plugins stop working | Pin minimum version in specs; monitor release notes for breaking changes |
| AE scripting landscape shifts (UXP becomes required) | ExtendScript plugins become obsolete | Monitor Adobe's UXP rollout for AE; delay major AE investment until the target is stable |
| Loop takes too long (>1 day per plugin) | Pipeline isn't demonstrating efficiency | Profile each stage; the Build-Test loop is usually the bottleneck — improve prompts and increase MCP feedback granularity |
| Generated plugins are too similar to existing tools | Redundancy, wasted effort | Novelty check is in the Research pipeline (Tier 2); Review Agent should also check for existing free tools before publishing |
