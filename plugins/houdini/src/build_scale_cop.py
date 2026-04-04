"""
build_scale_cop.py — headless build script for Scale COP HDA (Houdini 21 Copernicus)

Usage (run from plugins/houdini/src/):
    /opt/hfs21.0/bin/hython build_scale_cop.py
"""

import os, sys
import hou

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HDA_FILE   = os.path.join(SCRIPT_DIR, "scale_cop.hda")

# ---------------------------------------------------------------------------
# VEX snippet for tile_wrangle
# ---------------------------------------------------------------------------
TILE_VEX = r"""
// Scale COP — tile_wrangle
// Input 0 (layer "C") = resample_scale (forced to STRETCH when tiling is on).
//
// When tiling is active the resample is in STRETCH mode, so its image space
// is identical to the source's image space (both span -1..+1).  We can
// therefore tile the source by calling volumesamplep(0, "C", tiled_P) on
// the resample — it produces the same values as sampling the source directly.
//
// COP VEX coordinate system: @P is in image space (-1,-1) to (+1,+1).
// Convert tile UV (0..1) to image space: P = 2*u - 1.
// Source pixel dims come from HDA hidden parms _src_w/_src_h (set by Python).
int mode = chi("../tile_mode_int");
if (mode == 0) {
    @C = @C;   // no tiling: pass through fit/scaled content from resample
} else {
    float src_w = float(chi("../_src_w"));
    float src_h = float(chi("../_src_h"));
    // Guard: fall back to output dims if source dims not yet populated.
    if (src_w < 1.0f) src_w = float(@xres);
    if (src_h < 1.0f) src_h = float(@yres);
    float off_u = chf("../tile_offset_u");
    float off_v = chf("../tile_offset_v");
    // tile-space coords: 0..1 = one tile of the source
    float u = float(@ix) / src_w + off_u;
    float v = float(@iy) / src_h + off_v;
    if (mode == 1) {           // Repeat
        u = frac(u); v = frac(v);
    } else if (mode == 2) {    // Mirror X
        float tu = frac(u * 0.5f);
        u = (tu < 0.5f) ? tu * 2.0f : 2.0f - tu * 2.0f;
        v = frac(v);
    } else if (mode == 3) {    // Mirror Y
        u = frac(u);
        float tv = frac(v * 0.5f);
        v = (tv < 0.5f) ? tv * 2.0f : 2.0f - tv * 2.0f;
    } else {                   // Mirror Both (4)
        float tu = frac(u * 0.5f);
        u = (tu < 0.5f) ? tu * 2.0f : 2.0f - tu * 2.0f;
        float tv = frac(v * 0.5f);
        v = (tv < 0.5f) ? tv * 2.0f : 2.0f - tv * 2.0f;
    }
    // Convert tile UV (0..1) to image-space voxel CENTER coords (-1..+1).
    // The +1/src_w shift maps u=0 to the first voxel center (P.x = -1+1/sw)
    // rather than the exact left boundary, avoiding bilinear boundary bleed.
    // Since resample is in STRETCH mode when tiling, image space coords
    // are shared with the source — this tiles the source correctly.
    float ip_x = 2.0f*u - 1.0f + 1.0f/src_w;
    float ip_y = 2.0f*v - 1.0f + 1.0f/src_h;
    @C = volumesamplep(0, "C", set(ip_x, ip_y, 0.0f));
}
"""

# ---------------------------------------------------------------------------
# HDA Python module (embedded as string, baked into HDA definition)
# ---------------------------------------------------------------------------
PYTHON_MODULE = r'''
# Scale COP — HDA Python module
# Modifies ONLY the HDA node's own hidden parameters (_res_w, _res_h,
# _has_ref_res, _constrain_ar). The internal resample reads those via
# channel reference expressions set at build time.

PRESET_RES = [
    (1280,  720),   # 720p
    (1920, 1080),   # 1080p
    (2048, 1080),   # 2K
    (3840, 2160),   # 4K
    (7680, 4320),   # 8K
    (4096, 2160),   # 4K DCI
    (1024, 1024),   # Sq 1K
    (2048, 2048),   # Sq 2K
    (4096, 4096),   # Sq 4K
]


def _src_res(node):
    """Return (w, h) of the connected source, or None."""
    src = node.input(0)
    if src is None:
        return None
    try:
        src.cook(force=False)
        lyr = src.layer()
        return lyr.bufferResolution() if lyr else None
    except Exception:
        return None


def _update(node):
    """Recompute hidden parms: _res_w/_res_h, _src_w/_src_h, tile_mode_int."""
    scale_mode = node.parm("scale_mode").evalAsString()
    sr = _src_res(node)   # call once; also used for _src_w/_src_h

    if scale_mode == "explicit":
        w = node.parm("width").eval()
        h = node.parm("height").eval()

    elif scale_mode == "preset":
        idx = node.parm("preset").eval()
        w, h = PRESET_RES[idx]

    elif scale_mode == "uniform":
        if sr:
            s = node.parm("uniform_scale").eval()
            w, h = max(1, int(sr[0] * s)), max(1, int(sr[1] * s))
        else:
            w = node.parm("_res_w").eval()
            h = node.parm("_res_h").eval()

    elif scale_mode == "nonuniform":
        if sr:
            sx = node.parm("scale_x").eval()
            sy = node.parm("scale_y").eval()
            w, h = max(1, int(sr[0] * sx)), max(1, int(sr[1] * sy))
        else:
            w = node.parm("_res_w").eval()
            h = node.parm("_res_h").eval()

    else:
        w = node.parm("_res_w").eval()
        h = node.parm("_res_h").eval()

    # Keep _src_w/_src_h current so tiling VEX can read source dimensions.
    if sr:
        node.parm("_src_w").set(sr[0])
        node.parm("_src_h").set(sr[1])

    node.parm("_res_w").set(w)
    node.parm("_res_h").set(h)

    # Sync tile_mode integer mirror — expressions set on instances aren't
    # saved into the HDA type definition, so we maintain this via Python.
    node.parm("tile_mode_int").set(node.parm("tile_mode").eval())


def _update_ref_res(node):
    """Sync _has_ref_res; if ref_res is wired, pull its resolution."""
    ref = node.input(1)
    if ref is not None:
        node.parm("_has_ref_res").set(1)
        # Also update _res_w/_res_h from ref_res so the hidden parms stay
        # consistent (resample uses basesize=input when _has_ref_res==1, so
        # the _res_w/_res_h values are unused — but keep them tidy).
        try:
            ref.cook(force=False)
            lyr = ref.layer()
            if lyr:
                rw, rh = lyr.bufferResolution()
                node.parm("_res_w").set(rw)
                node.parm("_res_h").set(rh)
        except Exception:
            pass
    else:
        node.parm("_has_ref_res").set(0)
        _update(node)
    # Always refresh source dims for tiling (input 0 doesn't change here,
    # but _update() may not have been called yet on first creation).
    sr = _src_res(node)
    if sr:
        node.parm("_src_w").set(sr[0])
        node.parm("_src_h").set(sr[1])


def onCreated(kwargs):
    node = kwargs["node"]
    node.parm("tile_mode_int").set(node.parm("tile_mode").eval())
    _update(node)
    _update_ref_res(node)


def onInputChanged(kwargs):
    node = kwargs["node"]
    _update_ref_res(node)


def onParmChanged(kwargs):
    node = kwargs["node"]
    parm = kwargs.get("parm_name", "")

    # Constrain proportions
    if parm in ("width", "height") and node.parm("constrain").eval():
        ar = node.parm("_constrain_ar").eval()
        if ar > 0:
            if parm == "width":
                node.parm("height").set(max(1, int(round(
                    node.parm("width").eval() / ar))))
            else:
                node.parm("width").set(max(1, int(round(
                    node.parm("height").eval() * ar))))

    # Lock AR when constrain is toggled on
    if parm == "constrain" and node.parm("constrain").eval():
        w = node.parm("width").eval()
        h = node.parm("height").eval()
        if h > 0:
            node.parm("_constrain_ar").set(w / h)

    _update(node)
'''

# ---------------------------------------------------------------------------
# HScript expressions for resample internal parms
# Use integer index comparisons (ch() returns menu index, not string token).
# ---------------------------------------------------------------------------
# fit_mode indices: stretch=0, fitinside=1, fitoutside=2, pinwidth=3, pinheight=4, original=5
# resample stretch values: 0=stretch, 1=horz(pinW), 2=vert(pinH), 3=max(fitOut), 4=min(fitIn)
# When tiling is active (tile_mode > 0): force STRETCH so that source image space
# and resample image space are identical — required for volumesamplep tiling to work.
STRETCH_EXPR = (
    'if(ch("../tile_mode")>0, 0, '    # tiling active → force stretch
    'if(ch("../fit_mode")==0, 0, '    # stretch
    'if(ch("../fit_mode")==1, 4, '    # fitinside  → min
    'if(ch("../fit_mode")==2, 3, '    # fitoutside → max
    'if(ch("../fit_mode")==3, 1, '    # pinwidth   → horz
    'if(ch("../fit_mode")==4, 2, '    # pinheight  → vert
    '0))))))'                          # original/default → stretch (canvas=src)
)

# filter_mode indices: auto=0, point=1, bilinear=2, box=3, bartlett=4, catmullrom=5, mitchell=6, bspline=7
# resample filter values: 0=point, 1=bilinear, 2=box, 3=triangle(bartlett), 4=cubic(catmullrom), 5=mitchell, 6=bspline
FILTER_EXPR = (
    'if(ch("../filter_mode")==0, 4, '   # auto      → catmullrom (safe for both up/down)
    'if(ch("../filter_mode")==1, 0, '   # point
    'if(ch("../filter_mode")==2, 1, '   # bilinear
    'if(ch("../filter_mode")==3, 2, '   # box
    'if(ch("../filter_mode")==4, 3, '   # bartlett
    'if(ch("../filter_mode")==5, 4, '   # catmullrom
    'if(ch("../filter_mode")==6, 5, '   # mitchell
    'if(ch("../filter_mode")==7, 6, '   # bspline
    '1))))))))'                          # fallback: bilinear
)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build():
    hou.hipFile.clear(suppress_save_prompt=True)

    img_mgr  = hou.node("/img")
    work_net = img_mgr.createNode("copnet", "build_work")

    # ---- Prototype subnet -----------------------------------------------
    proto   = work_net.createNode("subnet", "scale_cop")
    inp_nd  = proto.node("inputs")
    out_nd  = proto.node("outputs")
    out_nd.setInput(0, None)   # remove default passthrough

    # ---- Internal: resample_scale ----------------------------------------
    rs = proto.createNode("resample", "resample_scale")
    rs.setInput(0, inp_nd, 0)   # source
    rs.setInput(1, inp_nd, 1)   # ref_res (used when _has_ref_res==1)

    # Constant parms (not expression-driven)
    rs.parm("sizecontrol").set(0)   # res mode
    rs.parm("reframe").set(1)       # always reframe

    # Expression-driven: resolved at cook time from HDA parms
    H = hou.exprLanguage.Hscript
    rs.parm("resolution1").setExpression('ch("../_res_w")', language=H)
    rs.parm("resolution2").setExpression('ch("../_res_h")', language=H)
    rs.parm("basesize").setExpression('ch("../_has_ref_res")', language=H)
    rs.parm("stretch").setExpression(STRETCH_EXPR, language=H)
    rs.parm("filter").setExpression(FILTER_EXPR, language=H)

    # ---- Internal: tile_wrangle ------------------------------------------
    tw = proto.createNode("wrangle", "tile_wrangle")
    tw.setInput(0, rs)   # canvas / scaled image (STRETCH when tiling)

    tw.parm("aovs").set(1)
    tw.parm("type1").set("vector"); tw.parm("layer1").set("C"); tw.parm("geoinput1").set(1)
    tw.parm("vex_exportlist").set("C")
    tw.parm("vexsnippet").set(TILE_VEX)

    out_nd.setInput(0, tw)

    # ---- Layout ----------------------------------------------------------
    inp_nd.setPosition(hou.Vector2(-3, 2))
    rs.setPosition(hou.Vector2(0, 1))
    tw.setPosition(hou.Vector2(0, 0))
    out_nd.setPosition(hou.Vector2(0, -1))

    # ---- Convert to HDA --------------------------------------------------
    hda_node = proto.createDigitalAsset(
        name="scale_cop",
        hda_file_name=HDA_FILE,
        description="Scale COP",
        min_num_inputs=1,
        max_num_inputs=2,
        ignore_external_references=True,
    )

    # ---- Parameter template group ----------------------------------------
    hda_def = hda_node.type().definition()
    ptg     = hou.ParmTemplateGroup()
    H_cond  = hou.parmCondType.HideWhen
    D_cond  = hou.parmCondType.DisableWhen

    # Per-parm script callbacks — fires on interactive change, persists to new instances.
    # (OnParmChanged HDA event section is NOT fired by Houdini; per-parm callbacks are.)
    def _cb(pt):
        pt.setScriptCallback("kwargs['node'].hdaModule().onParmChanged(kwargs)")
        pt.setScriptCallbackLanguage(hou.scriptLanguage.Python)
        return pt

    # -- Section 1: Target Resolution -------------------------------------
    f_res = hou.FolderParmTemplate("folder_res", "Target Resolution",
                                    folder_type=hou.folderType.Simple)

    sm = hou.MenuParmTemplate(
        "scale_mode", "Scale Mode",
        menu_items  = ["preset", "explicit", "uniform", "nonuniform"],
        menu_labels = ["Preset", "Explicit", "Uniform Scale", "Non-Uniform Scale"],
        default_value = 1,
    )
    sm.setConditional(D_cond, '{ _has_ref_res == 1 }')
    _cb(sm)
    f_res.addParmTemplate(sm)

    pr = hou.MenuParmTemplate(
        "preset", "Preset",
        menu_items  = ["720p","1080p","2k","4k","8k","4kdci","sq1k","sq2k","sq4k"],
        menu_labels = [
            "720p   (1280 × 720)", "1080p  (1920 × 1080)", "2K     (2048 × 1080)",
            "4K     (3840 × 2160)", "8K     (7680 × 4320)", "4K DCI (4096 × 2160)",
            "Sq 1K  (1024 × 1024)", "Sq 2K  (2048 × 2048)", "Sq 4K  (4096 × 4096)",
        ],
        default_value = 1,
    )
    pr.setConditional(H_cond, '{ scale_mode != "preset" } { _has_ref_res == 1 }')
    _cb(pr)
    f_res.addParmTemplate(pr)

    pw = hou.IntParmTemplate("width", "Width", 1, default_value=[1920],
                              min=1, max=16384, min_is_strict=True)
    pw.setConditional(H_cond, '{ scale_mode != "explicit" } { _has_ref_res == 1 }')
    _cb(pw)
    f_res.addParmTemplate(pw)

    ph = hou.IntParmTemplate("height", "Height", 1, default_value=[1080],
                              min=1, max=16384, min_is_strict=True)
    ph.setConditional(H_cond, '{ scale_mode != "explicit" } { _has_ref_res == 1 }')
    _cb(ph)
    f_res.addParmTemplate(ph)

    pc = hou.ToggleParmTemplate("constrain", "Constrain Proportions", default_value=1)
    pc.setConditional(H_cond, '{ scale_mode != "explicit" } { _has_ref_res == 1 }')
    _cb(pc)
    f_res.addParmTemplate(pc)

    pus = hou.FloatParmTemplate("uniform_scale", "Scale", 1, default_value=[1.0],
                                 min=0.001, max=32.0)
    pus.setConditional(H_cond, '{ scale_mode != "uniform" } { _has_ref_res == 1 }')
    _cb(pus)
    f_res.addParmTemplate(pus)

    psx = hou.FloatParmTemplate("scale_x", "Scale X", 1, default_value=[1.0],
                                 min=0.001, max=32.0)
    psx.setConditional(H_cond, '{ scale_mode != "nonuniform" } { _has_ref_res == 1 }')
    _cb(psx)
    f_res.addParmTemplate(psx)

    psy = hou.FloatParmTemplate("scale_y", "Scale Y", 1, default_value=[1.0],
                                 min=0.001, max=32.0)
    psy.setConditional(H_cond, '{ scale_mode != "nonuniform" } { _has_ref_res == 1 }')
    _cb(psy)
    f_res.addParmTemplate(psy)

    # ref_res informational label (visible only when ref_res is wired)
    lbl = hou.LabelParmTemplate("ref_res_label", "  Resolution inherited from ref_res input.")
    lbl.setConditional(H_cond, '{ _has_ref_res == 0 }')
    f_res.addParmTemplate(lbl)

    ptg.append(f_res)

    # -- Section 2: Fit Mode -----------------------------------------------
    f_fit = hou.FolderParmTemplate("folder_fit", "Fit Mode",
                                    folder_type=hou.folderType.Simple)

    fm = hou.MenuParmTemplate(
        "fit_mode", "Fit Mode",
        menu_items  = ["stretch","fitinside","fitoutside","pinwidth","pinheight","original"],
        menu_labels = ["Stretch", "Fit Inside (Letterbox)", "Fit Outside (Crop to Fill)",
                       "Pin Width", "Pin Height", "Original Size"],
        default_value = 1,
    )
    fm.setConditional(D_cond, '{ tile_mode != "none" }')
    f_fit.addParmTemplate(fm)

    bg = hou.FloatParmTemplate(
        "bg_color", "Background Color", 4,
        default_value=[0.0, 0.0, 0.0, 0.0],
        min=0.0, max=1.0,
        look=hou.parmLook.ColorSquare,
        naming_scheme=hou.parmNamingScheme.RGBA,
    )
    bg.setConditional(H_cond, '{ fit_mode != "fitinside" } { tile_mode != "none" }')
    f_fit.addParmTemplate(bg)

    ptg.append(f_fit)

    # -- Section 3: Tiling -------------------------------------------------
    f_tile = hou.FolderParmTemplate("folder_tile", "Tiling",
                                     folder_type=hou.folderType.Simple)

    tm = hou.MenuParmTemplate(
        "tile_mode", "Tile Mode",
        menu_items  = ["none","repeat","mirrorx","mirrory","mirrorboth"],
        menu_labels = ["None","Repeat","Mirror X","Mirror Y","Mirror Both"],
        default_value = 0,
    )
    _cb(tm)
    f_tile.addParmTemplate(tm)

    ou = hou.FloatParmTemplate("tile_offset_u", "Tile Offset X", 1,
                                default_value=[0.0], min=-1.0, max=1.0)
    ou.setConditional(H_cond, '{ tile_mode == "none" }')
    f_tile.addParmTemplate(ou)

    ov = hou.FloatParmTemplate("tile_offset_v", "Tile Offset Y", 1,
                                default_value=[0.0], min=-1.0, max=1.0)
    ov.setConditional(H_cond, '{ tile_mode == "none" }')
    f_tile.addParmTemplate(ov)

    ptg.append(f_tile)

    # -- Section 4: Resampling ---------------------------------------------
    f_samp = hou.FolderParmTemplate("folder_samp", "Resampling",
                                     folder_type=hou.folderType.Simple)

    fi = hou.MenuParmTemplate(
        "filter_mode", "Filter",
        menu_items  = ["auto","point","bilinear","box","bartlett","catmullrom","mitchell","bspline"],
        menu_labels = ["Automatic","Point","Bilinear","Box","Bartlett",
                       "Catmull-Rom","Mitchell","B-Spline"],
        default_value = 0,
    )
    f_samp.addParmTemplate(fi)

    ptg.append(f_samp)

    # -- Hidden computed/state parms ---------------------------------------
    def _hidden(pt):
        pt.hide(True)
        return pt

    ptg.append(_hidden(hou.IntParmTemplate("_res_w", "Res W", 1, default_value=[1920])))
    ptg.append(_hidden(hou.IntParmTemplate("_res_h", "Res H", 1, default_value=[1080])))
    ptg.append(_hidden(hou.IntParmTemplate("_has_ref_res", "Has ref_res", 1, default_value=[0])))
    ptg.append(_hidden(hou.FloatParmTemplate("_constrain_ar", "Constrain AR", 1, default_value=[1.7778])))
    # Source dimensions for tiling VEX — kept current by Python callbacks.
    ptg.append(_hidden(hou.IntParmTemplate("_src_w", "Src W", 1, default_value=[1024])))
    ptg.append(_hidden(hou.IntParmTemplate("_src_h", "Src H", 1, default_value=[1024])))
    # tile_mode_int: integer mirror of tile_mode for VEX chi() access
    tmi = hou.IntParmTemplate("tile_mode_int", "Tile Mode Int", 1, default_value=[0])
    tmi.hide(True)
    ptg.append(tmi)

    hda_def.setParmTemplateGroup(ptg)

    # ---- Input count and labels -----------------------------------------
    hda_def.setMaxNumInputs(2)
    hda_def.setMinNumInputs(1)
    try:
        hda_def.setInputLabel(0, "source")
        hda_def.setInputLabel(1, "ref_res")
    except AttributeError:
        pass

    # ---- Python module and event handlers --------------------------------
    hda_def.addSection("PythonModule", PYTHON_MODULE)
    hda_def.setExtraFileOption("PythonModule/IsPython", True)

    for event, code in [
        ("OnCreated",      "kwargs['node'].hdaModule().onCreated(kwargs)"),
        ("OnInputChanged", "kwargs['node'].hdaModule().onInputChanged(kwargs)"),
    ]:
        hda_def.addSection(event, code)
        hda_def.setExtraFileOption(f"{event}/IsPython", True)

    # ---- Save -----------------------------------------------------------
    hda_def.save(HDA_FILE)
    print(f"HDA saved: {HDA_FILE}")
    return hda_node


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------
def test(hda_node):
    img_mgr  = hou.node("/img")
    test_net = img_mgr.createNode("copnet", "test_net")

    src = test_net.createNode("checkerboard", "src")
    src.parm("rows").set(4)
    src.parm("cols").set(4)
    # checkerboard default res = 1024×1024

    sc = test_net.createNode("scale_cop", "sc1")
    sc.setInput(0, src)

    # Helper: manually call the update function (hython: parm.set doesn't
    # fire OnParmChanged automatically).
    def sync(node=sc):
        node.hdaModule()._update(node)

    fails = []

    def chk(label, expected_res):
        sync()
        try:
            sc.cook(force=True)
            got = sc.layer().bufferResolution()
            ok  = (got == expected_res)
            mark = "PASS" if ok else "FAIL"
            print(f"  {mark}  {label}: {got}" + ("" if ok else f"  (expected {expected_res})"))
            if not ok:
                fails.append(label)
        except Exception as e:
            print(f"  ERR   {label}: {e}")
            fails.append(label)

    # ---- Scale mode: explicit -------------------------------------------
    print("\n--- Scale Mode (explicit) ---")
    sc.parm("scale_mode").set("explicit")
    sc.parm("width").set(1920); sc.parm("height").set(1080)
    sc.parm("constrain").set(0)
    chk("1920×1080", (1920, 1080))

    sc.parm("width").set(512); sc.parm("height").set(256)
    chk("512×256", (512, 256))

    # ---- Scale mode: preset --------------------------------------------
    print("\n--- Scale Mode (preset) ---")
    sc.parm("scale_mode").set("preset")
    sc.parm("preset").set(0)  # 720p = 1280×720
    chk("720p (1280×720)", (1280, 720))
    sc.parm("preset").set(1)  # 1080p = 1920×1080
    chk("1080p (1920×1080)", (1920, 1080))
    sc.parm("preset").set(6)  # Sq 1K = 1024×1024
    chk("Sq1K (1024×1024)", (1024, 1024))

    # ---- Scale mode: uniform -------------------------------------------
    print("\n--- Scale Mode (uniform) ---")
    sc.parm("scale_mode").set("uniform")
    sc.parm("uniform_scale").set(1.0)
    chk("uniform 1.0× (1024×1024)", (1024, 1024))
    sc.parm("uniform_scale").set(2.0)
    chk("uniform 2.0× (2048×2048)", (2048, 2048))
    sc.parm("uniform_scale").set(0.5)
    chk("uniform 0.5× (512×512)", (512, 512))

    # ---- Scale mode: nonuniform ----------------------------------------
    print("\n--- Scale Mode (nonuniform) ---")
    sc.parm("scale_mode").set("nonuniform")
    sc.parm("scale_x").set(2.0)
    sc.parm("scale_y").set(0.5)
    chk("nonuniform 2×0.5 (2048×512)", (2048, 512))

    # ---- Fit modes -------------------------------------------------------
    print("\n--- Fit Mode ---")
    sc.parm("scale_mode").set("explicit")
    sc.parm("width").set(1920); sc.parm("height").set(1080)
    sc.parm("tile_mode").set("none")
    for fmode in ["stretch","fitinside","fitoutside","pinwidth","pinheight","original"]:
        sc.parm("fit_mode").set(fmode)
        sync()
        try:
            sc.cook(force=True)
            print(f"  PASS  fit_mode={fmode}: {sc.layer().bufferResolution()}")
        except Exception as e:
            print(f"  FAIL  fit_mode={fmode}: {e}")
            fails.append(f"fit_{fmode}")

    # ---- Tile modes -------------------------------------------------------
    print("\n--- Tile Mode ---")
    sc.parm("scale_mode").set("explicit")
    sc.parm("width").set(2048); sc.parm("height").set(2048)
    for tmode in ["none","repeat","mirrorx","mirrory","mirrorboth"]:
        sc.parm("tile_mode").set(tmode)
        sync()
        try:
            sc.cook(force=True)
            res = sc.layer().bufferResolution()
            print(f"  PASS  tile_mode={tmode}: {res}")
        except Exception as e:
            print(f"  FAIL  tile_mode={tmode}: {e}")
            fails.append(f"tile_{tmode}")

    # ---- Tile offset -------------------------------------------------------
    sc.parm("tile_mode").set("repeat")
    sc.parm("tile_offset_u").set(0.5)
    sc.parm("tile_offset_v").set(0.25)
    sync()
    try:
        sc.cook(force=True)
        print(f"  PASS  tile offset: {sc.layer().bufferResolution()}")
    except Exception as e:
        print(f"  FAIL  tile offset: {e}")
        fails.append("tile_offset")

    # ---- Tile pixel correctness ------------------------------------------
    print("\n--- Tile Pixel Correctness ---")
    # checkerboard 4×4 at 1024×1024: cells are 256×256 px (black/white alternating).
    # Scale output to 2048×2048 with repeat tiling, no offset.
    # Check pixels well inside cells to avoid bilinear boundary interpolation:
    #   px(128,0)  → source px(128)  = cell(0,0) WHITE
    #   px(384,0)  → source px(384)  = cell(1,0) BLACK
    #   px(1152,0) → source px(1152%1024=128) = same as px(128) WHITE (repeat)
    sc.parm("scale_mode").set("explicit")
    sc.parm("width").set(2048); sc.parm("height").set(2048)
    sc.parm("fit_mode").set("stretch")
    sc.parm("tile_mode").set("repeat")
    sc.parm("tile_offset_u").set(0.0)
    sc.parm("tile_offset_v").set(0.0)
    sync()   # updates _src_w/_src_h in addition to _res_w/_res_h
    try:
        sc.cook(force=True)
        lyr = sc.layer()
        p128  = lyr.bufferIndex(128,  0)   # source px 128  = WHITE
        p384  = lyr.bufferIndex(384,  0)   # source px 384  = BLACK
        p1152 = lyr.bufferIndex(1152, 0)   # source px 128 (repeat) = WHITE

        def near(a, b):
            return all(abs(a[i] - b[i]) < 0.1 for i in range(len(a)))

        same_repeat = near(p128, p1152)
        diff_cell   = not near(p128, p384)
        ok = same_repeat and diff_cell
        mark = "PASS" if ok else "FAIL"
        print(f"  {mark}  repeat: p(128,0)={[round(x,3) for x in p128[:3]]}"
              f"  p(1152,0)={[round(x,3) for x in p1152[:3]]}"
              f"  p(384,0)={[round(x,3) for x in p384[:3]]}"
              f"  same={same_repeat} diff={diff_cell}")
        if not ok:
            fails.append("tile_pixel_repeat")
    except Exception as e:
        print(f"  ERR   tile pixel correctness: {e}")
        fails.append("tile_pixel_repeat")

    # ---- Filter modes -------------------------------------------------------
    print("\n--- Filter ---")
    sc.parm("tile_mode").set("none")
    sc.parm("fit_mode").set("stretch")
    sc.parm("width").set(1920); sc.parm("height").set(1080)
    for flt in ["auto","point","bilinear","catmullrom","mitchell","bspline"]:
        sc.parm("filter_mode").set(flt)
        sync()
        try:
            sc.cook(force=True)
            print(f"  PASS  filter={flt}")
        except Exception as e:
            print(f"  FAIL  filter={flt}: {e}")
            fails.append(f"filter_{flt}")

    # ---- ref_res input -------------------------------------------------------
    print("\n--- ref_res input ---")
    ref_src = test_net.createNode("resample", "ref")
    ref_src.setInput(0, src)
    ref_src.parm("basesize").set(0)
    ref_src.parm("sizecontrol").set(0)
    ref_src.parm("resolution1").set(800)
    ref_src.parm("resolution2").set(600)
    ref_src.parm("reframe").set(1)
    sc.parm("scale_mode").set("explicit")
    sc.parm("width").set(1920); sc.parm("height").set(1080)
    sc.setInput(1, ref_src)
    sc.hdaModule().onInputChanged({"node": sc})   # fire manually in hython
    try:
        sc.cook(force=True)
        got = sc.layer().bufferResolution()
        if got == (800, 600):
            print(f"  PASS  ref_res overrides to 800×600: {got}")
        else:
            print(f"  FAIL  ref_res: expected (800,600), got {got}")
            fails.append("ref_res")
    except Exception as e:
        print(f"  ERR   ref_res: {e}")
        fails.append("ref_res")

    # Disconnect ref_res and verify scale params resume control
    sc.setInput(1, None)
    sc.hdaModule().onInputChanged({"node": sc})
    sync()
    try:
        sc.cook(force=True)
        got = sc.layer().bufferResolution()
        if got == (1920, 1080):
            print(f"  PASS  ref_res disconnected, back to 1920×1080: {got}")
        else:
            print(f"  FAIL  ref_res disconnect: expected (1920,1080), got {got}")
            fails.append("ref_res_disconnect")
    except Exception as e:
        print(f"  ERR   ref_res_disconnect: {e}")
        fails.append("ref_res_disconnect")

    test_net.destroy()

    print("\n--- Summary ---")
    if fails:
        print(f"FAILURES ({len(fails)}): {fails}")
        return False
    print("All tests passed.")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Building Scale COP HDA...")
    hda_node = build()
    print("\nRunning tests...")
    ok = test(hda_node)
    sys.exit(0 if ok else 1)
