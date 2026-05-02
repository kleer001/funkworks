"""
build_vellum_attr_stream.py — headless build script for the Vellum Attr Stream HDA.

A DOP-context HDA wrapping a popwrangle microsolver. Lives inside a Vellum
Solver SOP (specifically, inside its inner vellumsolver1 DOP, wired into the
popsolver Pre-Solve input via merge7). Each substep, the popwrangle samples a
referenced animated SOP and copies listed point attributes onto the live sim
points (matched by `id` or `ptnum`).

This pattern was reverse-engineered from SideFX's `muscleupdatevellum` HDA
(/opt/hfs21.0.631/houdini/otls/OPlibDop.hda, Dop_1muscleupdatevellum), which
uses the same popwrangle-microsolver-in-Pre-Solve structure for time-varying
muscle attributes. We diverge in one detail: muscleupdatevellum uses
`bindinputmenu2=sop` to bind the source SOP to VEX input 1; we use VEX
`op:` references instead, so the same VEX template can be shared with the
SOP-level init wrangle the setup script inserts upstream.

Usage (run from plugins/houdini/src/):
    /opt/hfs21.0.631/bin/hython build_vellum_attr_stream.py
"""

import os
import subprocess
import hou

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HDA_FILE   = os.path.join(SCRIPT_DIR, "vellum_attr_stream.hda")


def _git_version():
    try:
        count = subprocess.check_output(
            ["git", "rev-list", "--count", "HEAD"],
            text=True, cwd=SCRIPT_DIR, stderr=subprocess.PIPE,
        ).strip()
        h = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            text=True, cwd=SCRIPT_DIR, stderr=subprocess.PIPE,
        ).strip()
        return f"v0.1.{count} ({h})"
    except Exception as e:
        print(f"  [version] git failed: {e}")
        return "v0.1.0 (unknown)"


# ---------------------------------------------------------------------------
# VEX template (single source of truth)
# ---------------------------------------------------------------------------
# {prefix} is the relative path to the parent that holds the parms:
#   "../"  for the popwrangle inside the HDA (parms live one level up)
#   "./"   for the SOP-level init wrangle (parms live on the wrangle itself)
#
# Input 0 in both contexts is the geometry being modified:
#   popwrangle: the live sim cloth (selfraw mode)
#   SOP wrangle: the upstream cloth source feeding into vellumsolver
#
# The source SOP is fetched via VEX `op:` reference so the same template
# works in both contexts. Houdini caches op: cooks within a VEX run, so
# repeated `point(ref, ...)` calls don't re-cook.
#
# pointattribtype() returns: 0=invalid, 1=float family, 2=integer, 3=string.
# We support float scalar/vector/vector4 and integer scalar — the common cases.
VEX_TEMPLATE = r"""
string sop_path = chs("{prefix}sop_path");
string attr_str = chs("{prefix}attribs");
int    match_by = chi("{prefix}match_by");  // 0 = id, 1 = ptnum

if (sop_path == "" || attr_str == "") return;

string ref     = "op:" + sop_path;
int    npts1   = npoints(ref);
if (npts1 == 0) return;

string attrs[] = split(attr_str, " ");

// Use the runtime attrib() reader — NOT i@id — for the local id lookup.
// `i@id` is a compile-time binding that declares a writable point
// attribute even when the if-branch is short-circuited at runtime, and
// since `id` is a Houdini-known special attribute it initializes to -1.
// On a SOP-level wrangle whose input has no id, that creates id=-1 on
// every point and trips Vellum's "Duplicate point id attributes" check.
int src_pt;
if (match_by == 0 && haspointattrib(ref, "id") && hasattrib(0, "point", "id")) {{
    int my_id = attrib(0, "point", "id", @ptnum);
    src_pt = findattribval(ref, "point", "id", my_id);
}} else {{
    src_pt = (@ptnum < npts1) ? @ptnum : -1;
}}
if (src_pt < 0) return;

foreach (string a; attrs) {{
    if (a == "" || !haspointattrib(ref, a)) continue;
    int t  = pointattribtype(ref, a);
    int sz = pointattribsize(ref, a);

    if (t == 1) {{
        if (sz == 1)      {{ float   v = point(ref, a, src_pt); setpointattrib(0, a, @ptnum, v, "set"); }}
        else if (sz == 3) {{ vector  v = point(ref, a, src_pt); setpointattrib(0, a, @ptnum, v, "set"); }}
        else if (sz == 4) {{ vector4 v = point(ref, a, src_pt); setpointattrib(0, a, @ptnum, v, "set"); }}
    }} else if (t == 2) {{
        int v = point(ref, a, src_pt);
        setpointattrib(0, a, @ptnum, v, "set");
    }}
}}
"""

POPWRANGLE_VEX = VEX_TEMPLATE.format(prefix="../")
INIT_WRANGLE_VEX = VEX_TEMPLATE.format(prefix="./")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build(work_parent=None):
    if work_parent is None:
        hou.hipFile.clear(suppress_save_prompt=True)
        work_parent = hou.node("/obj")

    geo = work_parent.createNode("geo", "vellum_attr_stream_build_work")
    dopnet = geo.createNode("dopnet", "build_dopnet")

    # Prototype subnet at DOP level.
    proto = dopnet.createNode("subnet", "vellum_attr_stream")

    # First indirect input is the upstream DOP data stream (microsolver pattern).
    inp = proto.indirectInputs()[0]

    # popwrangle: the actual streaming worker.
    pw = proto.createNode("popwrangle", "stream")
    pw.parm("bindgeo").set("Geometry")          # operate on the Geometry data field
    pw.parm("bindinputmenu1").set("selfraw")    # input 0 of VEX = raw self (the live sim)
    pw.parm("snippet").set(POPWRANGLE_VEX)
    pw.setInput(0, inp)

    # Subnet output passes the popwrangle's data through.
    out_inner = proto.createNode("output", "output0")
    out_inner.setInput(0, pw)

    pw.setPosition(hou.Vector2(0, 0))
    out_inner.setPosition(hou.Vector2(0, -1))
    proto.layoutChildren()

    # Promote subnet to a DOP digital asset.
    hda_node = proto.createDigitalAsset(
        name="vellum_attr_stream",
        hda_file_name=HDA_FILE,
        description="Vellum Attr Stream",
        min_num_inputs=1,
        max_num_inputs=1,
        ignore_external_references=True,
    )

    hda_def = hda_node.type().definition()
    ptg     = hou.ParmTemplateGroup()

    # -- Source ---------------------------------------------------------------
    f_src = hou.FolderParmTemplate(
        "folder_source", "Source", folder_type=hou.folderType.Simple,
    )

    f_src.addParmTemplate(hou.StringParmTemplate(
        "sop_path", "Animated SOP", 1,
        default_value=("",),
        string_type=hou.stringParmType.NodeReference,
        help="Path to the upstream animated SOP node whose attributes you want "
             "to stream into the live Vellum sim every substep.",
    ))

    f_src.addParmTemplate(hou.StringParmTemplate(
        "attribs", "Attributes", 1,
        default_value=("Cd",),
        help="Space-separated list of point attribute names to copy each "
             "substep from the animated SOP onto the live sim points.",
    ))

    f_src.addParmTemplate(hou.MenuParmTemplate(
        "match_by", "Match Points By",
        menu_items=["0", "1"],
        menu_labels=["id", "ptnum"],
        default_value=0,
        help="`id`: match by point `id` attribute (recommended; survives "
             "topology changes upstream of the sim). `ptnum`: match by point "
             "number — only safe if both geos have identical point order.",
    ))

    ptg.append(f_src)

    # -- Version footer -------------------------------------------------------
    btn_ver = hou.ButtonParmTemplate(
        "btn_update_version", "Update Version",
        script_callback=(
            "import subprocess, os, hou\n"
            "node = kwargs['node']\n"
            "defn = node.type().definition()\n"
            "tmpl = defn.parmTemplateGroup()\n"
            "pt = tmpl.find('hda_version')\n"
            "try:\n"
            "    _d = os.path.dirname(defn.libraryFilePath())\n"
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

    # Save the SOP-side VEX as an HDA section so the setup script can read it
    # at insert time. Single source of truth: this build script's VEX_TEMPLATE.
    hda_def.addSection("init_vex", INIT_WRANGLE_VEX)

    hda_def.save(HDA_FILE)

    print(f"HDA saved: {HDA_FILE}")
    return geo


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Building Vellum Attr Stream HDA (DOP context)...")
    work = build()
    work.destroy()
