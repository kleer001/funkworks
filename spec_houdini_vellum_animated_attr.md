# Plugin Spec: Vellum Animated SOP Attribute Streamer

## Problem Statement

Vellum's DOP solver reads SOP attributes once — at the start frame — and freezes them
into the simulation state. Animated attributes (color masks, wind weights, stiffness
overrides) that change over time are silently ignored after that first cook. Artists
discover the issue when their per-point `Cd` color mask, painted to drive dye behavior
or selective constraint stiffness, stays locked at frame 1 values for the entire sim.

The standard fix requires knowing to wire a SOP Solver inside the Vellum Solver, write
a VEX wrangle that manually samples the upstream SOP geometry each frame, and use
`setpointattrib()` to push the value into the live sim. Each attribute needs its own
wrangle block. This is a non-obvious architectural requirement that trips up intermediate
Houdini users who understand SOPs and Vellum separately but not the DOP data flow.

Two independent forum threads show the same confusion, one on r/Houdini and one on the
SideFX forums, both specifically about animated `Cd` failing to update.

## Proposed Solution

A single HDA — **Vellum SOP Attr Stream** — dropped inside a Vellum Solver (in its
`vellumsolver` context). It:

1. Accepts a reference path to the upstream SOP geometry node (the animated source)
2. Takes a list of attribute names to stream (default: `Cd`)
3. Each frame, samples the referenced SOP at the current time and copies the listed
   attributes from the SOP points to the corresponding Vellum geometry points by `id`
   or `ptnum` (configurable)
4. Works for any point attribute type (float, vector, integer)

Drop it in once. No manual VEX. The solver re-evaluates it every frame automatically
because it lives inside the DOP network.

A shelf tool companion simplifies setup: select a Vellum Solver node, run the tool,
and it inserts Vellum SOP Attr Stream inside the solver with the upstream geo path
pre-filled.

## Host Application

- Application: Houdini
- Minimum version: 19.5 (Vellum Solver SOP Solver subnetwork pattern is long-stable)
- API surfaces used:
  - `hou.DopNode`, `hou.SopNode` — navigating inside DOP network
  - VEX `prim()`, `point()`, `setpointattrib()` inside a SOP Solver wrangle
  - `opinputpath()` expression for the upstream SOP reference parameter
  - `hou.shelves` — shelf tool for auto-insert

## Scope

~120 lines. One SOP Solver wrangle HDA with two parameters (SOP path, attribute name
list). One shelf tool.

Not in scope: streaming primitive or vertex attributes (point-to-point is the common
case), handling topology-changing SOPs mid-sim, or integration with Vellum Constraints
(separate data stream).

## Engagement Signal

- "How to update/fetch an animated custom SOP attribute inside a Vellum Solver every frame?" — 3 replies
- "Houdini 20.5 – Is it possible to force Vellum Solver to re-evaluate animated Cd attribute every frame?" — 6 replies
- Total: 9 replies across 2 independent posts
