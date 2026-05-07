bl_info = {
    "name": "Subdivide Select New",
    "author": "Funkworks",
    "version": (1, 1, 0),
    "blender": (4, 0, 0),
    "location": "Edit Mode > Mesh menu / Right-click context menu",
    "description": "Subdivide and leave only the newly-created vertices and edges selected",
    "category": "Mesh",
}

import bpy
import bmesh


class MESH_OT_subdivide_select_new(bpy.types.Operator):
    bl_idname = "mesh.subdivide_select_new"
    bl_label = "Subdivide (Select New)"
    bl_description = (
        "Subdivide the current selection and leave only the newly-created "
        "vertices and edges selected"
    )
    bl_options = {'REGISTER', 'UNDO'}

    number_cuts: bpy.props.IntProperty(
        name="Number of Cuts",
        description="Number of subdivisions per edge",
        default=1, min=1, soft_max=10, max=100,
    )
    smoothness: bpy.props.FloatProperty(
        name="Smoothness",
        description="Smoothness factor (0 = sharp, 1 = subsurf-like)",
        default=0.0, min=0.0, soft_max=1.0, max=1000.0,
    )
    ngon: bpy.props.BoolProperty(
        name="Create N-Gons",
        description="When disabled, newly-created faces are limited to triangles and quads",
        default=True,
    )
    quadcorner: bpy.props.EnumProperty(
        name="Quad Corner Type",
        description="How to subdivide quad corners (anything other than Straight Cut produces some triangles)",
        items=[
            ('INNERVERT', "Inner Vert", ""),
            ('PATH', "Path", ""),
            ('STRAIGHT_CUT', "Straight Cut", ""),
            ('FAN', "Fan", ""),
        ],
        default='STRAIGHT_CUT',
    )
    fractal: bpy.props.FloatProperty(
        name="Fractal",
        description="Fractal randomness factor",
        default=0.0, min=0.0, soft_max=1000.0, max=1000000.0,
    )
    fractal_along_normal: bpy.props.FloatProperty(
        name="Along Normal",
        description="Apply fractal displacement along normal (0 = any direction, 1 = along normal only)",
        default=0.0, min=0.0, max=1.0,
    )
    seed: bpy.props.IntProperty(
        name="Random Seed",
        description="Seed for the random number generator",
        default=0, min=0,
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj is not None
            and obj.type == 'MESH'
            and context.mode == 'EDIT_MESH'
        )

    def execute(self, context):
        mesh = context.active_object.data

        # Tag every existing element so post-subdivide we can find untagged = new.
        # bmesh .tag is a runtime boolean on each element, preserved across
        # mesh.subdivide because the operator mutates the same edit-mesh in place.
        bm = bmesh.from_edit_mesh(mesh)
        for v in bm.verts:
            v.tag = True
        for e in bm.edges:
            e.tag = True
        for f in bm.faces:
            f.tag = True

        bpy.ops.mesh.subdivide(
            number_cuts=self.number_cuts,
            smoothness=self.smoothness,
            ngon=self.ngon,
            quadcorner=self.quadcorner,
            fractal=self.fractal,
            fractal_along_normal=self.fractal_along_normal,
            seed=self.seed,
        )

        bm = bmesh.from_edit_mesh(mesh)

        for v in bm.verts:
            v.select_set(False)
        for e in bm.edges:
            e.select_set(False)
        for f in bm.faces:
            f.select_set(False)

        new_verts = 0
        new_edges = 0
        for v in bm.verts:
            if not v.tag:
                v.select_set(True)
                new_verts += 1
        for e in bm.edges:
            if not e.tag:
                e.select_set(True)
                new_edges += 1

        bm.select_flush_mode()
        bmesh.update_edit_mesh(mesh)

        self.report(
            {'INFO'},
            f"Subdivided: {new_verts} new vertex(es), {new_edges} new edge(s) selected",
        )
        return {'FINISHED'}


def _menu_draw(self, context):
    self.layout.operator(MESH_OT_subdivide_select_new.bl_idname)


_CLASSES = [MESH_OT_subdivide_select_new]


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh.append(_menu_draw)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(_menu_draw)


def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(_menu_draw)
    bpy.types.VIEW3D_MT_edit_mesh.remove(_menu_draw)
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
