"""
build_zoom_blur_cop.py — headless build script for Zoom/Radial Blur COP HDA (Houdini 21 Copernicus)

Usage (run from plugins/houdini/src/):
    /opt/hfs21.0/bin/hython build_zoom_blur_cop.py
"""

import os, sys, subprocess
import hou

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HDA_FILE   = os.path.join(SCRIPT_DIR, "zoom_blur_cop.hda")


def _git_version():
    try:
        count = subprocess.check_output(
            ["git", "rev-list", "--count", "HEAD"],
            text=True, cwd=SCRIPT_DIR, stderr=subprocess.PIPE
        ).strip()
        short_hash = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            text=True, cwd=SCRIPT_DIR, stderr=subprocess.PIPE
        ).strip()
        return f"v0.1.{count} ({short_hash})"
    except Exception as e:
        print(f"  [version] git failed: {e}")
        return "v0.1.0 (unknown)"


# ---------------------------------------------------------------------------
# VEX
# ---------------------------------------------------------------------------
# @P in Copernicus is aspect-ratio-corrected and normalised by image width:
#   @P.x ∈ [−1, +1],  @P.y ∈ [−h/w, +h/w]
# px_to_img = 2.0 / resx converts one pixel to that @P space.
#
# Zoom mode:  samples along the radial direction (pos → center), creating
#             a scale/explosion blur.  blur_pixels controls the reach.
#
# Radial mode: samples along an arc of blur_angle degrees around center,
#              at constant distance — a true spin blur.
#
# Center can be specified in screen space [-1,1] or in pixels (0,0 = bottom-left).
WRANGLE_VEX = r"""
int   nsamples  = max(chi("../samples"), 1);
int   mode      = chi("../blur_mode");
float blur_px   = chf("../blur_pixels");
float angle_deg = chf("../blur_angle");
int   ctr_mode  = chi("../center_mode");

float cx, cy;
if (ctr_mode == 0) {
    cx = chf("../centerx");
    cy = chf("../centery");
} else {
    cx = (chf("../center_px_x") / float(i@resx)) * 2.0 - 1.0;
    cy = (chf("../center_px_y") / float(i@resy)) * 2.0 - 1.0;
}

vector2 center = set(cx, cy);
vector2 pos    = set(@P.x, @P.y);
vector2 dir    = pos - center;

float px_to_img = 2.0 / float(i@resx);

// volumesamplep returns vector4 (RGBA) — required to preserve alpha.
// volumesamplev only returns RGB and "A" is not a separate layer in Copernicus.
vector4 rgba_sum = {0, 0, 0, 0};

for (int i = 0; i < nsamples; i++) {
    float t = (nsamples > 1)
        ? fit01(float(i) / float(nsamples - 1), -0.5, 0.5)
        : 0.0;

    vector2 suv;
    if (mode == 0) {
        // Zoom blur: sample along the radial direction
        float scale = blur_px * px_to_img;
        suv = pos + dir * t * scale;
    } else {
        // Radial blur: sample along an arc around center
        float len        = length(dir);
        float base_angle = atan2(dir.y, dir.x);
        float sa         = base_angle + radians(angle_deg) * t;
        suv = center + set(cos(sa), sin(sa)) * len;
    }

    rgba_sum += volumesamplep(0, "C", set(suv.x, suv.y, 0));
}

vector4 avg = rgba_sum / float(nsamples);
@C = avg;
@A = avg.w;
"""


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build(work_parent=None):
    """Build the HDA.  Pass work_parent to avoid clearing the hip file
    (used when calling from a live session).  Omit for headless hython builds.
    """
    if work_parent is None:
        hou.hipFile.clear(suppress_save_prompt=True)
        work_parent = hou.node("/img")

    work_net = work_parent.createNode("copnet", "zoom_blur_build_work")

    # ---- Prototype subnet --------------------------------------------------
    proto  = work_net.createNode("subnet", "zoom_blur_cop")
    inp_nd = proto.node("inputs")
    out_nd = proto.node("outputs")
    out_nd.setInput(0, None)

    # ---- Internal wrangle --------------------------------------------------
    wgl = proto.createNode("wrangle", "zoom_blur_wrangle")
    wgl.setInput(0, inp_nd, 0)

    wgl.parm("aovs").set(1)
    wgl.parm("type1").set(3);     wgl.parm("layer1").set("C"); wgl.parm("geoinput1").set(1)
    wgl.parm("vex_exportlist").set("*")
    wgl.parm("vexsnippet").set(WRANGLE_VEX)

    out_nd.setInput(0, wgl)

    # Layout
    inp_nd.setPosition(hou.Vector2(0,  1))
    wgl.setPosition(   hou.Vector2(0,  0))
    out_nd.setPosition(hou.Vector2(0, -1))

    # ---- Convert to HDA ----------------------------------------------------
    hda_node = proto.createDigitalAsset(
        name="zoom_blur_cop",
        hda_file_name=HDA_FILE,
        description="Zoom / Radial Blur COP",
        min_num_inputs=1,
        max_num_inputs=1,
        ignore_external_references=True,
    )

    # ---- Parameter template group ------------------------------------------
    hda_def = hda_node.type().definition()
    ptg     = hou.ParmTemplateGroup()
    H_cond  = hou.parmCondType.HideWhen

    # -- Blur -----------------------------------------------------------------
    f_blur = hou.FolderParmTemplate(
        "folder_blur", "Blur", folder_type=hou.folderType.Simple
    )

    f_blur.addParmTemplate(hou.MenuParmTemplate(
        "blur_mode", "Blur Mode",
        menu_items=["0", "1"],
        menu_labels=["Zoom Blur", "Radial Blur"],
        default_value=0,
        help="Zoom: radial scale blur from center. Radial: spin/arc blur around center.",
    ))

    f_blur.addParmTemplate(hou.IntParmTemplate(
        "samples", "Samples", 1,
        default_value=[20], min=1, max=256, min_is_strict=True,
    ))

    bp = hou.FloatParmTemplate(
        "blur_pixels", "Blur Pixels", 1,
        default_value=[600.0], min=0.0, max=3840.0,
        help="Radial reach of the zoom blur in pixels.",
    )
    bp.setConditional(H_cond, "{ blur_mode == 1 }")
    f_blur.addParmTemplate(bp)

    ba = hou.FloatParmTemplate(
        "blur_angle", "Blur Angle", 1,
        default_value=[15.0], min=0.0, max=180.0,
        help="Arc angle (degrees) of the rotational blur around center.",
    )
    ba.setConditional(H_cond, "{ blur_mode == 0 }")
    f_blur.addParmTemplate(ba)

    ptg.append(f_blur)

    # -- Center ---------------------------------------------------------------
    f_ctr = hou.FolderParmTemplate(
        "folder_center", "Center", folder_type=hou.folderType.Simple
    )

    f_ctr.addParmTemplate(hou.MenuParmTemplate(
        "center_mode", "Center Space",
        menu_items=["0", "1"],
        menu_labels=["Screen Space", "Pixels"],
        default_value=0,
        help="Screen Space: normalized −1..1 (aspect-corrected). Pixels: 0,0 = bottom-left.",
    ))

    cx = hou.FloatParmTemplate(
        "centerx", "Center X", 1,
        default_value=[0.5], min=-1.0, max=1.0,
        min_is_strict=False, max_is_strict=False,
    )
    cx.setConditional(H_cond, "{ center_mode == 1 }")
    f_ctr.addParmTemplate(cx)

    cy = hou.FloatParmTemplate(
        "centery", "Center Y", 1,
        default_value=[0.5], min=-1.0, max=1.0,
        min_is_strict=False, max_is_strict=False,
    )
    cy.setConditional(H_cond, "{ center_mode == 1 }")
    f_ctr.addParmTemplate(cy)

    cpx = hou.FloatParmTemplate(
        "center_px_x", "Center X (px)", 1,
        default_value=[960.0], min=0.0, max=4096.0,
        min_is_strict=False, max_is_strict=False,
        help="Horizontal center in pixels (0 = left edge).",
    )
    cpx.setConditional(H_cond, "{ center_mode == 0 }")
    f_ctr.addParmTemplate(cpx)

    cpy = hou.FloatParmTemplate(
        "center_px_y", "Center Y (px)", 1,
        default_value=[540.0], min=0.0, max=4096.0,
        min_is_strict=False, max_is_strict=False,
        help="Vertical center in pixels (0 = bottom edge).",
    )
    cpy.setConditional(H_cond, "{ center_mode == 0 }")
    f_ctr.addParmTemplate(cpy)

    ptg.append(f_ctr)

    # -- Version footer -------------------------------------------------------
    btn_ver = hou.ButtonParmTemplate(
        "btn_update_version", "Update Version",
        script_callback=(
            "import subprocess, hou\n"
            "node = kwargs['node']\n"
            "defn = node.type().definition()\n"
            "tmpl = defn.parmTemplateGroup()\n"
            "pt = tmpl.find('hda_version')\n"
            "try:\n"
            "    import os; _d = os.path.dirname(defn.libraryFilePath())\n"
            "    count = subprocess.check_output(['git','rev-list','--count','HEAD'], text=True, cwd=_d, stderr=subprocess.PIPE).strip()\n"
            "    h = subprocess.check_output(['git','rev-parse','--short','HEAD'], text=True, cwd=_d, stderr=subprocess.PIPE).strip()\n"
            "    v = f'v0.1.{count} ({h})'\n"
            "except Exception:\n"
            "    v = 'v0.1.0 (unknown)'\n"
            "pt.setDefaultValue((v,))\n"
            "tmpl.replace('hda_version', pt)\n"
            "defn.setParmTemplateGroup(tmpl)\n"
            "defn.save(defn.libraryFilePath())\n"
            "node.parm('hda_version').revertToDefaults()\n"
        ),
        script_callback_language=hou.scriptLanguage.Python,
    )
    ptg.append(btn_ver)

    ver_parm = hou.StringParmTemplate(
        "hda_version", "Version", 1,
        default_value=(_git_version(),),
    )
    ver_parm.setConditional(
        hou.parmCondType.DisableWhen,
        "{ hda_version == '' } { hda_version != '' }",
    )
    ptg.append(ver_parm)

    hda_def.setParmTemplateGroup(ptg)
    hda_def.setMaxNumInputs(1)
    hda_def.setMinNumInputs(1)
    hda_def.save(HDA_FILE)

    print(f"HDA saved: {HDA_FILE}")
    return work_net


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Building Zoom/Radial Blur COP HDA...")
    work_net = build()
    work_net.destroy()
