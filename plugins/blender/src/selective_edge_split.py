bl_info = {
    "name": "Selective Edge Split",
    "author": "Funkworks",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "Ctrl+E menu (Edit Mode) / N-panel > Item > Panel Gap",
    "description": "Split only tagged panel gap edges, leaving render sharps untouched",
    "category": "Mesh",
}

import bpy
import bmesh


class MESH_OT_mark_panel_gap(bpy.types.Operator):
    bl_idname = "mesh.mark_panel_gap"
    bl_label = "Mark Panel Gap"
    bl_description = "Tag selected edges as panel gap edges for selective split"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj is not None
            and obj.type == 'MESH'
            and context.mode == 'EDIT_MESH'
        )

    def execute(self, context):
        obj = context.active_object

        # Capture selection while still in Edit Mode
        bm = bmesh.from_edit_mesh(obj.data)
        selected_indices = [e.index for e in bm.edges if e.select]

        if not selected_indices:
            self.report({'WARNING'}, "No edges selected")
            return {'CANCELLED'}

        # RNA attribute writes require Object Mode
        bpy.ops.object.mode_set(mode='OBJECT')

        mesh = obj.data
        if "panel_gap" not in mesh.attributes:
            mesh.attributes.new(name="panel_gap", type='BOOLEAN', domain='EDGE')

        attr = mesh.attributes["panel_gap"]
        for i in selected_indices:
            attr.data[i].value = True

        bpy.ops.object.mode_set(mode='EDIT')

        self.report({'INFO'}, f"Marked {len(selected_indices)} edge(s) as panel gap")
        return {'FINISHED'}


class MESH_OT_clear_panel_gap(bpy.types.Operator):
    bl_idname = "mesh.clear_panel_gap"
    bl_label = "Clear Panel Gap"
    bl_description = "Remove panel gap tag from selected edges"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj is not None
            and obj.type == 'MESH'
            and context.mode == 'EDIT_MESH'
        )

    def execute(self, context):
        obj = context.active_object
        mesh = obj.data

        if "panel_gap" not in mesh.attributes:
            self.report({'INFO'}, "No panel gap edges exist on this mesh")
            return {'FINISHED'}

        # Capture selection while still in Edit Mode
        bm = bmesh.from_edit_mesh(mesh)
        selected_indices = [e.index for e in bm.edges if e.select]

        if not selected_indices:
            self.report({'WARNING'}, "No edges selected")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='OBJECT')

        attr = mesh.attributes["panel_gap"]
        for i in selected_indices:
            attr.data[i].value = False

        bpy.ops.object.mode_set(mode='EDIT')

        self.report({'INFO'}, f"Cleared panel gap on {len(selected_indices)} edge(s)")
        return {'FINISHED'}


class OBJECT_OT_apply_panel_gap_split(bpy.types.Operator):
    bl_idname = "object.apply_panel_gap_split"
    bl_label = "Apply Panel Gap Split"
    bl_description = "Split all edges tagged as panel gap; removes the tag after apply"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None or obj.type != 'MESH' or context.mode != 'OBJECT':
            return False
        mesh = obj.data
        if "panel_gap" not in mesh.attributes:
            return False
        return any(e.value for e in mesh.attributes["panel_gap"].data)

    def execute(self, context):
        obj = context.active_object
        mesh = obj.data

        # BOOLEAN edge attributes do not appear in bmesh edge layers (Blender 4.x).
        # Read tagged indices from RNA before entering bmesh.
        tagged = sorted(
            i for i, e in enumerate(mesh.attributes["panel_gap"].data) if e.value
        )

        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.edges.ensure_lookup_table()

        bmesh.ops.split_edges(bm, edges=[bm.edges[i] for i in tagged])

        bm.to_mesh(mesh)
        bm.free()

        # Attribute is invalid after topology change — remove it
        mesh.attributes.remove(mesh.attributes["panel_gap"])

        self.report({'INFO'}, f"Split {len(tagged)} panel gap edge(s)")
        return {'FINISHED'}


class VIEW3D_PT_panel_gap_edit(bpy.types.Panel):
    bl_label = "Panel Gap"
    bl_idname = "VIEW3D_PT_panel_gap_edit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj is not None
            and obj.type == 'MESH'
            and context.mode == 'EDIT_MESH'
        )

    def draw(self, context):
        row = self.layout.row(align=True)
        row.operator("mesh.mark_panel_gap")
        row.operator("mesh.clear_panel_gap")


class VIEW3D_PT_panel_gap_object(bpy.types.Panel):
    bl_label = "Panel Gap"
    bl_idname = "VIEW3D_PT_panel_gap_object"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj is not None
            and obj.type == 'MESH'
            and context.mode == 'OBJECT'
        )

    def draw(self, context):
        layout = self.layout
        mesh = context.active_object.data

        count = 0
        if "panel_gap" in mesh.attributes:
            count = sum(1 for e in mesh.attributes["panel_gap"].data if e.value)

        layout.label(text=f"Tagged edges: {count}")
        col = layout.column()
        col.enabled = count > 0
        col.operator("object.apply_panel_gap_split")


def _menu_draw(self, context):
    self.layout.separator()
    self.layout.operator("mesh.mark_panel_gap")
    self.layout.operator("mesh.clear_panel_gap")


_CLASSES = [
    MESH_OT_mark_panel_gap,
    MESH_OT_clear_panel_gap,
    OBJECT_OT_apply_panel_gap_split,
    VIEW3D_PT_panel_gap_edit,
    VIEW3D_PT_panel_gap_object,
]


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh_edges.append(_menu_draw)


def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_edges.remove(_menu_draw)
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
