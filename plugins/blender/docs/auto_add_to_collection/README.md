# New Collection with Selection

Make a new collection and move the selected objects into it in one click.

## The Problem

Blender already has an operator that creates a collection and moves your selection into
it: **M ▸ Move to Collection ▸ New Collection**. The catch is *where* it lives. When you
want to group a few objects, your hand goes to the **New Collection** button in the
Outliner — and that button ignores your selection, handing you an *empty* collection with
your objects still loose beside it. So you drag them in by hand, or undo and go hunting
for the buried New Collection entry in the M menu. Making the Outliner button respect the
selection has been a [standing request](https://blender.community/c/rightclickselect/V9fbbc/)
since 2020.

## The Solution

This addon doesn't add a new capability — it puts the create-and-move operation where you
already reach for it. A **New Collection with Selection** command appears in the
**Outliner right-click menu** and the 3D viewport's **Object ▸ Collection** menu. One
click creates a new collection nested under the active collection, moves your selected
objects into it, and makes it active — the same result as M ▸ New Collection, without the
menu hunt.

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
