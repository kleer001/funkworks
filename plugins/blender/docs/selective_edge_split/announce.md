# Announcement Copy — Selective Edge Split

## Medium (BlenderArtists / Reddit r/blender)

**Free addon: split panel gap edges without touching your render sharps**

Hard-surface workflow problem: you mark sharps for two reasons — smooth shading and panel gap cuts. But Blender's Edge Split modifier is global. Scoping it to one category means clearing all sharps, marking only the gaps, applying the split, then re-marking every render sharp by hand. On a complex vehicle mesh that's 100+ actions for one panel gap adjustment.

Selective Edge Split solves this. Tag your panel gap edges with Ctrl+E → Mark Panel Gap. The tag lives on the mesh until you're ready. When you are, Object Mode → N-panel → Apply Panel Gap Split. Only the tagged edges split. Render sharps untouched.

Free download: https://github.com/kleer001/funkworks/releases/tag/selective_edge_split-v1.0.0

Works on Blender 4.0+. Full undo support. Modifier stack (Solidify, Bevel, Armature) is unaffected.

---

## Long (Newsletter / Blog post intro)

**Re-marking sharp edges every time you adjust a panel gap gets old fast**

Hard-surface modeling in Blender means living with two kinds of sharp edges that look identical in the viewport but mean completely different things. Some sharps control smooth shading. Others mark physical gaps between body panels — the seams that need to be split into separate geometry before adding a Solidify modifier. Both kinds are just "sharp edges" to Blender.

The Edge Split modifier doesn't care why you marked an edge sharp. It splits everything, or nothing. So if you want to apply panel gap splits without destroying your render sharps, you do it the hard way: clear every sharp on the mesh, re-mark only the panel gap edges, apply the modifier, and then carefully re-mark every render sharp you just erased. On a dense vehicle mesh, you're looking at 100+ manual operations for a single panel gap adjustment.

Selective Edge Split eliminates that cycle.

The addon adds two entries to the Ctrl+E edge menu: **Mark Panel Gap** and **Clear Panel Gap**. Select edges, hit Ctrl+E, tag them. The tag is a standard boolean edge attribute that survives mode switches, file saves, and undo. It doesn't touch your sharp marks at all. When you're ready to commit the geometry cut, switch to Object Mode, open the N-panel, and hit **Apply Panel Gap Split**. Only the tagged edges are split. Everything else — render sharps, seams, UV maps, materials, modifier stack — stays exactly as it was.

It's free and open source.

Download it free: https://github.com/kleer001/funkworks/releases/tag/selective_edge_split-v1.0.0
