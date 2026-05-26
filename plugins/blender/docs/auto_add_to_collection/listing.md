# Marketplace Listing — New Collection with Selection

## Short Description (160 chars)
Create a new collection and move your selected objects into it in one click — from the Outliner right-click or the viewport's Object menu.

## Long Description

Click the Outliner's New Collection button with objects selected and Blender hands you an
empty collection, leaving your objects loose. You drag them in by hand every time, or
remember to use the M shortcut instead.

**How it works:**
- Select the objects you want to group
- Right-click in the Outliner, or open Object ▸ Collection in the viewport
- Choose **New Collection with Selection** — a new collection appears with your objects inside it

The new collection nests under the active collection and becomes active, just like
Blender's own New Collection button — it just brings your selection along. It's a true
move (one collection membership per object, no duplicates), fully undoable, with no setup.

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
