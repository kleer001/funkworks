# Marketplace Listing — New Collection with Selection

## Short Description (160 chars)
Create a new collection and move your selected objects into it in one click — from the Outliner right-click or the viewport's Object menu.

## Long Description

Blender can already create a collection and move your selection into it — the operator is
tucked away in M ▸ Move to Collection ▸ New Collection. But that's not where your hand
goes. When you want to group objects you reach for the Outliner's New Collection button,
and that button ignores your selection: it hands you an empty collection with your objects
still loose. So you drag them in by hand, or go digging for the M-menu entry.

**How it works:**
- Select the objects you want to group
- Right-click in the Outliner, or open Object ▸ Collection in the viewport
- Choose **New Collection with Selection** — a new collection appears with your objects inside it

The new collection nests under the active collection and becomes active — the same result
you'd get from the M-menu's New Collection entry, surfaced where you actually click. It's
a true move (one collection membership per object, no duplicates), fully undoable, with no
setup.

## Features

- One click to create a collection and move the selection into it
- Available in the Outliner right-click menu and the viewport Object ▸ Collection menu
- Nests under the active collection and makes the new one active, matching native behavior
- True move semantics — no duplicate collection links to clean up
- Full undo support; rename from the redo panel

## Requirements

- Blender 4.0 or later (verified on 4.2 LTS)

## Tags

collection, outliner, organize, workflow, selection, grouping
