bl_info = {
    "name": "Bevel Modifier Presets",
    "author": "Funkworks",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "Properties > Modifier > Bevel Presets",
    "description": "Save and recall Bevel modifier parameter sets across .blend files",
    "category": "Modifiers",
}

import bpy
from bl_operators.presets import AddPresetBase

PRESET_SUBDIR = "bevel_modifier"

# RNA paths captured into each preset file. Reading these at save time evaluates
# them against the active modifier; writing them back at load time targets the
# same path on whatever modifier is active when the preset is executed.
# Mirrors the full writable property surface of bpy.types.BevelModifier in
# Blender 4.2 LTS (22 properties). custom_profile (CurveProfile pointer) is
# intentionally excluded — it can't be serialised as a single assignment;
# Blender's separate Save Profile As mechanism handles curve persistence.
PRESET_VALUES = [
    "bpy.context.active_object.modifiers.active.affect",
    "bpy.context.active_object.modifiers.active.angle_limit",
    "bpy.context.active_object.modifiers.active.face_strength_mode",
    "bpy.context.active_object.modifiers.active.harden_normals",
    "bpy.context.active_object.modifiers.active.invert_vertex_group",
    "bpy.context.active_object.modifiers.active.limit_method",
    "bpy.context.active_object.modifiers.active.loop_slide",
    "bpy.context.active_object.modifiers.active.mark_seam",
    "bpy.context.active_object.modifiers.active.mark_sharp",
    "bpy.context.active_object.modifiers.active.material",
    "bpy.context.active_object.modifiers.active.miter_inner",
    "bpy.context.active_object.modifiers.active.miter_outer",
    "bpy.context.active_object.modifiers.active.offset_type",
    "bpy.context.active_object.modifiers.active.profile",
    "bpy.context.active_object.modifiers.active.profile_type",
    "bpy.context.active_object.modifiers.active.segments",
    "bpy.context.active_object.modifiers.active.spread",
    "bpy.context.active_object.modifiers.active.use_clamp_overlap",
    "bpy.context.active_object.modifiers.active.vertex_group",
    "bpy.context.active_object.modifiers.active.vmesh_method",
    "bpy.context.active_object.modifiers.active.width",
    "bpy.context.active_object.modifiers.active.width_pct",
]


def _active_bevel(context):
    obj = context.active_object
    if obj is None:
        return None
    mod = obj.modifiers.active
    if mod is None or mod.type != 'BEVEL':
        return None
    return mod


class MODIFIER_MT_bevel_presets(bpy.types.Menu):
    bl_label = "Bevel Presets"
    preset_subdir = PRESET_SUBDIR
    preset_operator = "script.execute_preset"
    draw = bpy.types.Menu.draw_preset


class MODIFIER_OT_bevel_preset_add(AddPresetBase, bpy.types.Operator):
    bl_idname = "modifier.bevel_preset_add"
    bl_label = "Add Bevel Preset"
    bl_description = "Save the active Bevel modifier's parameters as a named preset"
    preset_menu = "MODIFIER_MT_bevel_presets"
    preset_subdir = PRESET_SUBDIR
    preset_values = PRESET_VALUES

    @classmethod
    def poll(cls, context):
        return _active_bevel(context) is not None


class PROPERTIES_PT_bevel_presets(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "modifier"
    bl_label = "Bevel Presets"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return _active_bevel(context) is not None

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.menu(MODIFIER_MT_bevel_presets.__name__,
                 text=MODIFIER_MT_bevel_presets.bl_label)
        row.operator(MODIFIER_OT_bevel_preset_add.bl_idname,
                     text="", icon='ADD')
        remove_op = row.operator(MODIFIER_OT_bevel_preset_add.bl_idname,
                                 text="", icon='REMOVE')
        remove_op.remove_active = True


_CLASSES = [
    MODIFIER_MT_bevel_presets,
    MODIFIER_OT_bevel_preset_add,
    PROPERTIES_PT_bevel_presets,
]


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
