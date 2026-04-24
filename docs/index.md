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
.plugin-grid { display: flex; flex-direction: column; gap: 0.75rem; margin: 2rem 0; width: calc(100% + 4rem); margin-left: -2rem; }
.plugin-card { display: flex; flex-direction: row; border: 1px solid #ddd; border-radius: 6px; overflow: hidden; height: 160px; width: 100%; }
.plugin-card-thumb { flex: 0 0 160px; overflow: hidden; }
.plugin-card-thumb a { display: block; width: 100%; height: 100%; }
.plugin-card-thumb img { width: 100%; height: 100%; object-fit: cover; object-position: center; display: block; }
.plugin-card-body { flex: 2; padding: 0.75rem 1rem; display: flex; flex-direction: column; justify-content: center; min-width: 0; border-right: 1px solid #eee; }
.plugin-card-body h3 { margin: 0 0 0.35rem; font-size: 1rem; }
.plugin-card-body p { margin: 0 0 0.5rem; font-size: 0.88rem; color: #444; }
.plugin-meta { font-size: 0.78rem; color: #777; margin-bottom: 0.5rem; }
.plugin-links a { margin-right: 0.75rem; font-size: 0.85rem; }
.plugin-card-posts { flex: 1; padding: 0.6rem 0.75rem; overflow-y: auto; display: flex; flex-direction: column; justify-content: flex-start; }
.plugin-card-posts ul { list-style: none; padding: 0; margin: 0; }
.plugin-card-posts li { padding: 0.25rem 0; border-bottom: 1px solid #f0f0f0; }
.plugin-card-posts li:last-child { border-bottom: none; }
.plugin-card-posts a { font-size: 0.85rem; font-family: "Courier New", Courier, monospace; color: #0000EE; text-decoration: underline; display: block; line-height: 1.5; }
.plugin-card-posts a:visited { color: #551A8B; }
.plugin-card-posts a:hover { color: #0000BB; }
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
        <a href="https://kleer001.github.io/funkworks/selective_edge_split">Tutorial &amp; Download</a>
        <a href="https://github.com/kleer001/funkworks/tree/main/plugins/blender/src/selective_edge_split.py">Source</a>
      </div>
    </div>
    <div class="plugin-card-posts">
      <ul>
        <li><a href="https://old.reddit.com/r/blender/comments/1soevvw/free_addon_split_panel_gap_edges_without_touching/">r/blender</a></li>
        <li><a href="https://blenderartists.org/t/free-addon-split-panel-gap-edges-without-touching-your-render-sharps/1637935">BlenderArtists</a></li>
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
        <a href="https://kleer001.github.io/funkworks/fluid-domain-visibility">Tutorial &amp; Download</a>
        <a href="https://github.com/kleer001/funkworks/tree/main/plugins/blender/src/fluid_domain_visibility.py">Source</a>
      </div>
    </div>
    <div class="plugin-card-posts">
      <ul>
        <li><a href="https://www.reddit.com/r/blender/comments/1s4ep4o/free_addon_stop_manually_hiding_your_fluid_domain/">r/blender</a></li>
        <li><a href="https://blenderartists.org/t/free-addon-stop-manually-hiding-your-fluid-domain-before-the-sim-starts/1635474">BlenderArtists</a></li>
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
        <a href="https://kleer001.github.io/funkworks/scale_cop">Tutorial &amp; Download</a>
        <a href="https://github.com/kleer001/funkworks/tree/main/plugins/houdini/src/build_scale_cop.py">Source</a>
      </div>
    </div>
    <div class="plugin-card-posts">
      <ul>
        <li><a href="https://www.sidefx.com/forum/topic/103565/?page=1#post-458117">SideFX Forums</a></li>
        <li><a href="https://forums.odforce.net/topic/67424-scale-cop-%E2%80%94-free-houdini-node-for-fit-modes-tiling-and-canvas-resize-letterbox-fill-crop/#comment-277858">OdForce</a></li>
      </ul>
    </div>
  </div>

  <div class="plugin-card">
    <div class="plugin-card-thumb">
      <a href="zoom_blur_cop"><img src="{{ "/images/banners/zoom_blur_cop_banner.png" | relative_url }}" alt="Zoom / Radial Blur COP banner"/></a>
    </div>
    <div class="plugin-card-body">
      <h3><a href="zoom_blur_cop">Zoom / Radial Blur COP</a></h3>
      <p>Zoom blur and spin blur in one Houdini Copernicus node. Switch between radial scale and arc modes, place the center in screen space or pixels, tune sample count for quality vs. speed.</p>
      <div class="plugin-meta">Houdini 20.5+ &middot; Free</div>
      <div class="plugin-links">
        <a href="https://kleer001.github.io/funkworks/zoom_blur_cop">Tutorial &amp; Download</a>
        <a href="https://github.com/kleer001/funkworks/tree/main/plugins/houdini/src/build_zoom_blur_cop.py">Source</a>
      </div>
    </div>
    <div class="plugin-card-posts">
      <ul>
        <li><a href="https://www.sidefx.com/forum/topic/103658/?page=1#post-458829">SideFX Forums</a></li>
        <li><a href="https://forums.odforce.net/topic/67448-zoom-radial-blur-cop/">OdForce</a></li>
      </ul>
    </div>
  </div>

</div>

---

[View on GitHub](https://github.com/kleer001/funkworks)
