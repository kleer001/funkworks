bl_info = {
    "name": "Fluid Domain Auto-Visibility",
    "author": "Funkworks",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "Properties > Physics > Fluid",
    "description": "Insert visibility keyframes around a fluid simulation's start frame",
    "category": "Animation",
}

import bpy


def _find_fluid_domain_modifier(obj):
    for mod in obj.modifiers:
        if mod.type == 'FLUID' and mod.fluid_type == 'DOMAIN':
            return mod
    return None


class FLUID_OT_auto_keyframe_visibility(bpy.types.Operator):
    bl_idname = "fluid.auto_keyframe_visibility"
    bl_label = "Auto-Keyframe Visibility"
    bl_description = "Insert hide/show keyframes around the fluid simulation start frame"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        return _find_fluid_domain_modifier(obj) is not None

    def execute(self, context):
        obj = context.active_object
        mod = _find_fluid_domain_modifier(obj)
        start_frame = mod.domain_settings.cache_frame_start
        hide_frame = start_frame - 1

        scene_start = context.scene.frame_start

        obj.hide_viewport = True
        obj.hide_render = True
        if scene_start < hide_frame:
            obj.keyframe_insert(data_path="hide_viewport", frame=scene_start)
            obj.keyframe_insert(data_path="hide_render", frame=scene_start)
        obj.keyframe_insert(data_path="hide_viewport", frame=hide_frame)
        obj.keyframe_insert(data_path="hide_render", frame=hide_frame)

        obj.hide_viewport = False
        obj.hide_render = False
        obj.keyframe_insert(data_path="hide_viewport", frame=start_frame)
        obj.keyframe_insert(data_path="hide_render", frame=start_frame)

        if start_frame == 1:
            self.report(
                {'WARNING'},
                "Sim starts at frame 1; no pre-sim frames to hide. "
                f"Keyframes inserted at frame {hide_frame} (hidden) and frame {start_frame} (visible)."
            )
        else:
            self.report(
                {'INFO'},
                f"Visibility keyframes set: hidden from frame {scene_start}, visible at frame {start_frame}."
            )

        return {'FINISHED'}


class FLUID_PT_auto_visibility(bpy.types.Panel):
    bl_label = "Auto-Visibility"
    bl_idname = "FLUID_PT_auto_visibility"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_parent_id = "PHYSICS_PT_fluid"
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        return _find_fluid_domain_modifier(obj) is not None

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        mod = _find_fluid_domain_modifier(obj)
        start_frame = mod.domain_settings.cache_frame_start
        hide_frame = start_frame - 1
        col = layout.column()
        col.label(text=f"Hidden at frame: {hide_frame}")
        col.label(text=f"Visible at frame: {start_frame}")
        col.operator("fluid.auto_keyframe_visibility")


def register():
    bpy.utils.register_class(FLUID_OT_auto_keyframe_visibility)
    bpy.utils.register_class(FLUID_PT_auto_visibility)


def unregister():
    bpy.utils.unregister_class(FLUID_PT_auto_visibility)
    bpy.utils.unregister_class(FLUID_OT_auto_keyframe_visibility)


if __name__ == "__main__":
    register()
