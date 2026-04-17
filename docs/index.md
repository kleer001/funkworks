---
title: All Addons
layout: home
---

<p align="center">
  <img src="images/banner.svg" alt="Funkworks — Addons built from real problems." width="700"/>
</p>

Free tools that eliminate repetitive workflow steps for digital artists. Built from real pain points, shipped as single-file addons and HDAs.

---

<style>
.plugin-grid { display: flex; flex-direction: column; gap: 2rem; margin: 2rem 0; }
.plugin-card { border: 1px solid #ddd; border-radius: 6px; overflow: hidden; }
.plugin-card img { width: 100%; display: block; }
.plugin-card-body { padding: 1rem 1.25rem; }
.plugin-card-body h3 { margin: 0 0 0.4rem; font-size: 1.1rem; }
.plugin-card-body p { margin: 0 0 0.75rem; font-size: 0.95rem; color: #444; }
.plugin-meta { font-size: 0.8rem; color: #777; margin-bottom: 0.75rem; }
.plugin-links a { margin-right: 1rem; font-size: 0.9rem; }
.posts-section h2 { margin-top: 2.5rem; }
.posts-list { list-style: none; padding: 0; }
.posts-list li { padding: 0.4rem 0; border-bottom: 1px solid #eee; font-size: 0.95rem; }
.posts-list li:last-child { border-bottom: none; }
.posts-list .post-plugin { font-size: 0.8rem; color: #888; margin-left: 0.5rem; }
</style>

<div class="plugin-grid">

  <div class="plugin-card">
    <a href="selective_edge_split"><img src="{{ "/images/banners/selective_edge_split_banner.png" | relative_url }}" alt="Selective Edge Split banner"/></a>
    <div class="plugin-card-body">
      <h3><a href="selective_edge_split">Selective Edge Split</a></h3>
      <p>Split panel gap edges without touching your render sharps. Tag edges once with Ctrl+E, apply a scoped split when ready.</p>
      <div class="plugin-meta">Blender 4.0+ &middot; Free</div>
      <div class="plugin-links">
        <a href="selective_edge_split">Tutorial</a>
        <a href="https://github.com/kleer001/funkworks/releases/tag/selective_edge_split-v1.0.0">Download</a>
        <a href="https://github.com/kleer001/funkworks/tree/main/plugins/blender/src/selective_edge_split.py">Source</a>
      </div>
    </div>
  </div>

  <div class="plugin-card">
    <a href="fluid-domain-visibility"><img src="{{ "/images/banners/fluid_domain_visibility_banner.png" | relative_url }}" alt="Fluid Domain Auto-Visibility banner"/></a>
    <div class="plugin-card-body">
      <h3><a href="fluid-domain-visibility">Fluid Domain Auto-Visibility</a></h3>
      <p>One-click visibility keyframing for fluid simulation domains. Automatically hides the domain box before your sim starts.</p>
      <div class="plugin-meta">Blender 4.0+ &middot; Free</div>
      <div class="plugin-links">
        <a href="fluid-domain-visibility">Tutorial</a>
        <a href="https://github.com/kleer001/funkworks/releases/tag/fluid_domain_visibility-v1.0.0">Download</a>
        <a href="https://github.com/kleer001/funkworks/tree/main/plugins/blender/src/fluid_domain_visibility.py">Source</a>
      </div>
    </div>
  </div>

  <div class="plugin-card">
    <a href="scale_cop"><img src="{{ "/images/banners/scale_cop_banner.png" | relative_url }}" alt="Scale COP banner"/></a>
    <div class="plugin-card-body">
      <h3><a href="scale_cop">Scale COP</a></h3>
      <p>Resize and reposition an image in Houdini Copernicus with independent fit mode, tiling, and resampling filter. Letterbox, fill, crop, and tile in one node.</p>
      <div class="plugin-meta">Houdini 20+ &middot; Free</div>
      <div class="plugin-links">
        <a href="scale_cop">Tutorial</a>
        <a href="https://github.com/kleer001/funkworks/releases/tag/scale_cop-v0.1.99">Download HDA</a>
        <a href="https://github.com/kleer001/funkworks/tree/main/plugins/houdini/src/build_scale_cop.py">Source</a>
      </div>
    </div>
  </div>

</div>

---

<div class="posts-section">
<h2>In the Wild</h2>

<ul class="posts-list">
  <li>
    <a href="https://www.reddit.com/r/blender/comments/1s4ep4o/free_addon_stop_manually_hiding_your_fluid_domain/">Free addon: stop manually hiding your fluid domain before the sim starts</a>
    <span class="post-plugin">r/blender &middot; Fluid Domain Auto-Visibility</span>
  </li>
  <li>
    <a href="https://blenderartists.org/t/free-addon-stop-manually-hiding-your-fluid-domain-before-the-sim-starts/1635474">Free addon: stop manually hiding your fluid domain before the sim starts</a>
    <span class="post-plugin">BlenderArtists &middot; Fluid Domain Auto-Visibility</span>
  </li>
  <li>
    <a href="https://www.sidefx.com/forum/topic/103565/?page=1#post-458117">Scale COP — free Houdini node for fit modes, tiling, and canvas resize</a>
    <span class="post-plugin">SideFX Forums &middot; Scale COP</span>
  </li>
  <li>
    <a href="https://forums.odforce.net/topic/67424-scale-cop-%E2%80%94-free-houdini-node-for-fit-modes-tiling-and-canvas-resize-letterbox-fill-crop/#comment-277858">Scale COP — free Houdini node for fit modes, tiling, and canvas resize</a>
    <span class="post-plugin">OdForce &middot; Scale COP</span>
  </li>
</ul>
</div>

---

[View on GitHub](https://github.com/kleer001/funkworks)
