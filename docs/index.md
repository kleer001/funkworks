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
.plugin-grid { display: flex; flex-direction: column; gap: 0.75rem; margin: 2rem 0; }
.plugin-card { display: flex; flex-direction: row; border: 1px solid #ddd; border-radius: 6px; overflow: hidden; height: 160px; }
.plugin-card-thumb { flex: 0 0 160px; overflow: hidden; }
.plugin-card-thumb a { display: block; width: 100%; height: 100%; }
.plugin-card-thumb img { width: 100%; height: 100%; object-fit: cover; object-position: center; display: block; }
.plugin-card-body { flex: 1; padding: 0.75rem 1rem; display: flex; flex-direction: column; justify-content: center; min-width: 0; border-right: 1px solid #eee; }
.plugin-card-body h3 { margin: 0 0 0.35rem; font-size: 1rem; }
.plugin-card-body p { margin: 0 0 0.5rem; font-size: 0.88rem; color: #444; }
.plugin-meta { font-size: 0.78rem; color: #777; margin-bottom: 0.5rem; }
.plugin-links a { margin-right: 0.75rem; font-size: 0.85rem; }
.plugin-card-posts { flex: 0 0 220px; padding: 0.6rem 0.75rem; overflow-y: auto; display: flex; flex-direction: column; justify-content: flex-start; }
.plugin-card-posts .posts-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: #aaa; margin-bottom: 0.4rem; }
.plugin-card-posts ul { list-style: none; padding: 0; margin: 0; }
.plugin-card-posts li { padding: 0.25rem 0; border-bottom: 1px solid #f0f0f0; }
.plugin-card-posts li:last-child { border-bottom: none; }
.plugin-card-posts a { font-size: 0.8rem; color: #555; text-decoration: none; display: block; line-height: 1.3; }
.plugin-card-posts a:hover { color: #000; }
.plugin-card-posts .post-venue { font-size: 0.72rem; color: #aaa; }
.no-posts { font-size: 0.8rem; color: #bbb; font-style: italic; }
</style>

<div class="plugin-grid">

  <div class="plugin-card">
    <div class="plugin-card-thumb">
      <a href="selective_edge_split"><img src="{{ "/images/banners/selective_edge_split_banner.png" | relative_url }}" alt="Selective Edge Split banner"/></a>
    </div>
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
    <div class="plugin-card-posts">
      <div class="posts-label">In the wild</div>
      <ul>
        <li><span class="no-posts">No posts yet</span></li>
      </ul>
    </div>
  </div>

  <div class="plugin-card">
    <div class="plugin-card-thumb">
      <a href="fluid-domain-visibility"><img src="{{ "/images/banners/fluid_domain_visibility_banner.png" | relative_url }}" alt="Fluid Domain Auto-Visibility banner"/></a>
    </div>
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
    <div class="plugin-card-posts">
      <div class="posts-label">In the wild</div>
      <ul>
        <li>
          <a href="https://www.reddit.com/r/blender/comments/1s4ep4o/free_addon_stop_manually_hiding_your_fluid_domain/">Stop manually hiding your fluid domain</a>
          <span class="post-venue">r/blender</span>
        </li>
        <li>
          <a href="https://blenderartists.org/t/free-addon-stop-manually-hiding-your-fluid-domain-before-the-sim-starts/1635474">Stop manually hiding your fluid domain</a>
          <span class="post-venue">BlenderArtists</span>
        </li>
      </ul>
    </div>
  </div>

  <div class="plugin-card">
    <div class="plugin-card-thumb">
      <a href="scale_cop"><img src="{{ "/images/banners/scale_cop_banner.png" | relative_url }}" alt="Scale COP banner"/></a>
    </div>
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
    <div class="plugin-card-posts">
      <div class="posts-label">In the wild</div>
      <ul>
        <li>
          <a href="https://www.sidefx.com/forum/topic/103565/?page=1#post-458117">Scale COP — fit modes, tiling, canvas resize</a>
          <span class="post-venue">SideFX Forums</span>
        </li>
        <li>
          <a href="https://forums.odforce.net/topic/67424-scale-cop-%E2%80%94-free-houdini-node-for-fit-modes-tiling-and-canvas-resize-letterbox-fill-crop/#comment-277858">Scale COP — fit modes, tiling, canvas resize</a>
          <span class="post-venue">OdForce</span>
        </li>
      </ul>
    </div>
  </div>

</div>

---

[View on GitHub](https://github.com/kleer001/funkworks)
