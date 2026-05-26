# New Collection with Selection

Make a new collection and move the selected objects into it in one click.

## The Problem

You select a few objects and click the Outliner's **New Collection** button to group
them — but Blender creates an *empty* collection and leaves your objects loose. You then
drag them in by hand, or undo and reach for the **M** (Move to Collection) shortcut
instead. The Outliner's New Collection action simply ignores your selection. This has
been the [top-requested fix](https://blender.community/c/rightclickselect/V9fbbc/) for
this part of the UI since 2020.

## The Solution

Adds a **New Collection with Selection** command to the places you already create
collections — the **Outliner right-click menu** and the 3D viewport's **Object ▸
Collection** menu. One click creates a new collection nested under the active collection,
moves your selected objects into it, and makes it the active collection. It behaves like
the native New Collection button, but brings your selection along.

## Installation

1. Download `auto_add_to_collection.py`
2. In Blender: **Edit > Preferences > Add-ons > Install**
3. Select the downloaded file and enable the addon

## Usage

1. Select the objects you want to group
2. Right-click in the Outliner (or open **Object > Collection** in the viewport)
3. Choose **New Collection with Selection** — done
4. Optional: rename the collection in the redo panel (F9)

## Distribution

- **GitHub releases** — primary distribution channel; attach the `.py` file to a tagged release
- **Blender Extensions Platform** ([extensions.blender.org](https://extensions.blender.org/)) — for discoverability inside Blender's built-in extension browser. Requires GPL, a review process, and a `blender_manifest.toml`. Not yet pursued; revisit when plugins are mature.

## Compatibility

- Blender 4.0+ (verified on 4.2 LTS)

## Notes

- **True move, not copy.** Selected objects are unlinked from their current collections
  and linked into the new one — exactly one collection membership each, matching Blender's
  Move to Collection semantics.
- **Nests under the active collection**, then makes the new collection active.
- **Greyed out when nothing is selected** — the command requires at least one selected object.
- Objects in linked/library collections can't be moved; make the collection local first.
