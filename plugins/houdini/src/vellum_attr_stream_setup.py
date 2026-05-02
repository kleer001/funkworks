"""Funkworks Vellum Attr Stream — one-shot setup.

The user-facing entry point is `vellum_attr_stream_setup.cmd` (Houdini's
File > Run Script... only accepts .cmd files). The .cmd is a one-line
HScript dispatcher that exec's this file with `__file__` set, so the
HDA is resolved via the sibling-path pattern below.

Installs the DOP HDA if needed, unlocks the solver wrapper, inserts the
streamer DOP into the popsolver Pre-Solve chain, and adds a SOP-level
init wrangle upstream of the solver to seed frame-1 attribs. Idempotent.
"""

import os
import hou

HERE     = os.path.dirname(os.path.abspath(__file__))
HDA_PATH = os.path.join(HERE, "vellum_attr_stream.hda")

SETUP_NODE_NAME = "vellum_attr_stream_setup"
INIT_NODE_NAME  = "vellum_attr_stream_init"


def _err(msg):
    hou.ui.displayMessage(msg, severity=hou.severityType.Error)


def _warn(msg):
    hou.ui.displayMessage(msg, severity=hou.severityType.Warning)


def _info(msg):
    hou.ui.displayMessage(msg)


def _ensure_hda_installed():
    """Install the DOP HDA into this session if it isn't already loaded."""
    if hou.dopNodeTypeCategory().nodeTypes().get("vellum_attr_stream"):
        return True
    if not os.path.isfile(HDA_PATH):
        _err(f"Can't find vellum_attr_stream.hda next to this script:\n{HDA_PATH}\n\n"
             "Place the .hda, the .cmd, and the .py in the same folder.")
        return False

    # installFile() can succeed silently on a malformed/truncated HDA without
    # registering the operator type. Re-check after install and surface a
    # clear error rather than letting downstream lookups fail mysteriously.
    hou.hda.installFile(HDA_PATH)
    if hou.dopNodeTypeCategory().nodeTypes().get("vellum_attr_stream"):
        return True

    size = os.path.getsize(HDA_PATH)
    _err(
        f"Installed vellum_attr_stream.hda but the 'vellum_attr_stream' DOP "
        f"operator did not register.\n\n"
        f"File: {HDA_PATH}\n"
        f"Size: {size} bytes\n\n"
        "The .hda is likely malformed or truncated. Re-download it, or "
        "rebuild from source with `hython build_vellum_attr_stream.py`. "
        "A healthy build is typically 8-10 KB."
    )
    return False


def _resolve_unlock(node):
    try:
        node.allowEditingOfContents()
    except hou.OperationFailed as e:
        _err(f"Couldn't unlock {node.path()}: {e}")
        return False
    return True


def _read_init_vex():
    """Read the init wrangle's VEX from the HDA's 'init_vex' section.
    Single source of truth: build_vellum_attr_stream.py VEX_TEMPLATE."""
    nt = hou.dopNodeTypeCategory().nodeTypes().get("vellum_attr_stream")
    if nt is None or nt.definition() is None:
        return None
    section = nt.definition().sections().get("init_vex")
    return section.contents() if section else None


def _insert_init_wrangle(vsolve, streamer, init_vex):
    parent = vsolve.parent()
    upstream = vsolve.input(0)
    if upstream is None:
        return None, "vellumsolver has no upstream input — frame-1 init skipped."

    existing = parent.node(INIT_NODE_NAME)
    if existing is not None:
        return existing, "init wrangle already present (idempotent)"

    init_w = parent.createNode("attribwrangle", INIT_NODE_NAME)
    init_w.parm("class").set(2)
    init_w.parm("snippet").set(init_vex)

    spares = hou.ParmTemplateGroup()
    folder = hou.FolderParmTemplate("vas_folder", "Vellum Attr Stream",
                                    folder_type=hou.folderType.Simple)
    folder.addParmTemplate(hou.StringParmTemplate(
        "sop_path", "Animated SOP", 1,
        string_type=hou.stringParmType.NodeReference,
    ))
    folder.addParmTemplate(hou.StringParmTemplate("attribs", "Attributes", 1))
    folder.addParmTemplate(hou.IntParmTemplate("match_by", "Match By", 1))
    spares.append(folder)
    init_w.setParmTemplateGroup(spares)

    streamer_path = streamer.path()
    init_w.parm("sop_path").setExpression(
        f'chs("{streamer_path}/sop_path")', hou.exprLanguage.Hscript)
    init_w.parm("attribs").setExpression(
        f'chs("{streamer_path}/attribs")', hou.exprLanguage.Hscript)
    init_w.parm("match_by").setExpression(
        f'ch("{streamer_path}/match_by")', hou.exprLanguage.Hscript)

    init_w.setInput(0, upstream)
    vsolve.setInput(0, init_w)
    parent.layoutChildren()
    return init_w, None


def setup():
    sel = hou.selectedNodes()
    if not sel:
        _warn("Select a Vellum Solver SOP first, then re-run this script.")
        return

    vsolve = sel[0]
    if vsolve.type().name() != "vellumsolver":
        _err(f"Selected node is '{vsolve.type().name()}', not a vellumsolver SOP.")
        return

    if not _ensure_hda_installed():
        return

    init_vex = _read_init_vex()
    if init_vex is None:
        _err("Couldn't read 'init_vex' section from the vellum_attr_stream HDA. "
             "The HDA may be from an older build — rebuild it with "
             "build_vellum_attr_stream.py.")
        return

    upstream      = vsolve.input(0)
    upstream_path = upstream.path() if upstream else ""

    if not _resolve_unlock(vsolve): return

    dopnet = vsolve.node("dopnet1")
    if dopnet is None:
        _err("Couldn't find dopnet1 inside the Vellum Solver. Wrapper layout "
             "may have changed in this Houdini version.")
        return

    inner_vsolve = dopnet.node("vellumsolver1")
    if inner_vsolve is None:
        _err("Couldn't find vellumsolver1 DOP inside dopnet1.")
        return
    if not _resolve_unlock(inner_vsolve): return

    popsolver = inner_vsolve.node("popsolver")
    if popsolver is None:
        _err("Couldn't find popsolver inside vellumsolver1.")
        return
    if not _resolve_unlock(popsolver): return

    pre_solve = popsolver.input(1)
    if pre_solve is None:
        _err("popsolver has no Pre-Solve input wired. Unexpected wrapper state.")
        return

    if pre_solve.type().name() != "merge":
        _err(f"Expected a merge feeding popsolver Pre-Solve, found "
             f"'{pre_solve.type().name()}' ({pre_solve.path()}). Aborting "
             f"to avoid breaking the wrapper.")
        return

    existing = inner_vsolve.node(SETUP_NODE_NAME)
    if existing is not None:
        _warn(f"{vsolve.path()} already has a Vellum Attr Stream attached.\n\n"
              f"Open {existing.path()} to edit its parameters.")
        existing.setSelected(True, clear_all_selected=True)
        return

    streamer = inner_vsolve.createNode("vellum_attr_stream", SETUP_NODE_NAME)
    if upstream_path:
        streamer.parm("sop_path").set(upstream_path)

    free_idx = len(pre_solve.inputs())
    pre_solve.setInput(free_idx, streamer)
    inner_vsolve.layoutChildren()

    init_w, init_warning = _insert_init_wrangle(vsolve, streamer, init_vex)

    streamer.setSelected(True, clear_all_selected=True)

    msg = (
        f"Vellum Attr Stream attached to {vsolve.path()}.\n\n"
        f"Streamer (DOP) : {streamer.path()}\n"
        f"Init   (SOP)  : {init_w.path() if init_w else '(none)'}\n"
        f"Source SOP    : {upstream_path or '(set manually on streamer)'}\n\n"
        "Edit the 'Attributes' parm on the DOP streamer (default: Cd). "
        "The SOP init wrangle reads its parms from the streamer via channel "
        "references, so they stay synced. Re-running this script is a no-op."
    )
    if init_warning:
        msg += f"\n\nNote: {init_warning}"
    _info(msg)


setup()
