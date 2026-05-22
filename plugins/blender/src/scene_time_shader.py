bl_info = {
    "name": "Scene Time Shader Node",
    "author": "Funkworks",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "Shader Editor > Add > Input > Scene Time",
    "description": (
        "Adds a Scene Time node to the Shader Editor with Frame and Seconds "
        "outputs, matching the Compositor and Geometry Nodes versions."
    ),
    "category": "Node",
}

import bpy

_GROUP_NAME = "Scene Time"


def _group_has_expected_outputs(ntree):
    out_names = {
        item.name for item in ntree.interface.items_tree
        if getattr(item, "in_out", None) == "OUTPUT"
    }
    return "Seconds" in out_names and "Frame" in out_names


def _add_scene_driver(socket, expression, include_fps):
    # Driver `id` is bound to the scene that owns the depsgraph at creation time.
    # The driver tracks that scene's frame/fps for the life of the node group;
    # multi-scene files behave as documented in the README.
    scene = bpy.context.scene
    fcurve = socket.driver_add("default_value")
    drv = fcurve.driver
    drv.type = "SCRIPTED"
    drv.expression = expression

    v1 = drv.variables.new()
    v1.name = "frame"
    v1.type = "SINGLE_PROP"
    v1.targets[0].id_type = "SCENE"
    v1.targets[0].id = scene
    v1.targets[0].data_path = "frame_current"

    if include_fps:
        v2 = drv.variables.new()
        v2.name = "fps"
        v2.type = "SINGLE_PROP"
        v2.targets[0].id_type = "SCENE"
        v2.targets[0].id = scene
        v2.targets[0].data_path = "render.fps"

        v3 = drv.variables.new()
        v3.name = "fps_base"
        v3.type = "SINGLE_PROP"
        v3.targets[0].id_type = "SCENE"
        v3.targets[0].id = scene
        v3.targets[0].data_path = "render.fps_base"


def _ensure_scene_time_group():
    ntree = bpy.data.node_groups.get(_GROUP_NAME)
    if (
        ntree is not None
        and ntree.bl_idname == "ShaderNodeTree"
        and _group_has_expected_outputs(ntree)
    ):
        return ntree

    ntree = bpy.data.node_groups.new(_GROUP_NAME, "ShaderNodeTree")
    ntree.interface.new_socket(
        "Seconds", in_out="OUTPUT", socket_type="NodeSocketFloat"
    )
    ntree.interface.new_socket(
        "Frame", in_out="OUTPUT", socket_type="NodeSocketFloat"
    )

    out_node = ntree.nodes.new("NodeGroupOutput")
    out_node.location = (200, 0)

    sec = ntree.nodes.new("ShaderNodeValue")
    sec.label = "Seconds"
    sec.location = (0, 80)

    frm = ntree.nodes.new("ShaderNodeValue")
    frm.label = "Frame"
    frm.location = (0, -80)

    ntree.links.new(sec.outputs[0], out_node.inputs["Seconds"])
    ntree.links.new(frm.outputs[0], out_node.inputs["Frame"])

    # Seconds = frame * fps_base / fps, matching Compositor Scene Time
    # (NTSC: fps=24, fps_base=1.001 → true_fps = 23.976)
    _add_scene_driver(sec.outputs[0], "frame * fps_base / fps", include_fps=True)
    _add_scene_driver(frm.outputs[0], "frame", include_fps=False)

    return ntree


class NODE_OT_add_scene_time(bpy.types.Operator):
    bl_idname = "node.add_scene_time"
    bl_label = "Scene Time"
    bl_description = (
        "Add a Scene Time node group (Frame + Seconds outputs) to the active "
        "shader graph at the cursor position"
    )
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (
            space is not None
            and space.type == 'NODE_EDITOR'
            and space.tree_type == 'ShaderNodeTree'
            and space.edit_tree is not None
        )

    def execute(self, context):
        ntree = _ensure_scene_time_group()
        edit_tree = context.space_data.edit_tree

        node = edit_tree.nodes.new("ShaderNodeGroup")
        node.node_tree = ntree
        node.label = "Scene Time"
        node.location = context.space_data.cursor_location

        for n in edit_tree.nodes:
            n.select = False
        node.select = True
        edit_tree.nodes.active = node

        return {'FINISHED'}


def _menu_draw(self, context):
    self.layout.operator(NODE_OT_add_scene_time.bl_idname, text="Scene Time")


_CLASSES = [NODE_OT_add_scene_time]


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.NODE_MT_category_shader_input.append(_menu_draw)


def unregister():
    bpy.types.NODE_MT_category_shader_input.remove(_menu_draw)
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
