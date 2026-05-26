bl_info = {
    "name": "New Collection with Selection",
    "author": "Funkworks",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "Outliner right-click / Object > Collection menu",
    "description": "Create a new collection and move the selected objects into it in one step",
    "category": "Object",
}

import bpy


def _find_layer_collection(layer_coll, collection):
    """Walk the view-layer tree to find the LayerCollection wrapping a collection."""
    if layer_coll.collection == collection:
        return layer_coll
    for child in layer_coll.children:
        found = _find_layer_collection(child, collection)
        if found is not None:
            return found
    return None


class OBJECT_OT_new_collection_with_selection(bpy.types.Operator):
    bl_idname = "object.new_collection_with_selection"
    bl_label = "New Collection with Selection"
    bl_description = (
        "Create a new collection nested under the active collection and move "
        "the selected objects into it"
    )
    bl_options = {'REGISTER', 'UNDO'}

    collection_name: bpy.props.StringProperty(
        name="Name",
        description="Name for the new collection",
        default="Collection",
    )

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        view_layer = context.view_layer
        parent = view_layer.active_layer_collection.collection

        new_coll = bpy.data.collections.new(self.collection_name)
        parent.children.link(new_coll)

        objects = list(context.selected_objects)
        for obj in objects:
            for coll in list(obj.users_collection):
                coll.objects.unlink(obj)
            new_coll.objects.link(obj)

        # Make the new collection active so subsequent additions land inside it,
        # matching Blender's native New Collection behaviour.
        new_layer_coll = _find_layer_collection(view_layer.layer_collection, new_coll)
        if new_layer_coll is not None:
            view_layer.active_layer_collection = new_layer_coll

        self.report(
            {'INFO'},
            f"Moved {len(objects)} object(s) into '{new_coll.name}'",
        )
        return {'FINISHED'}


def _menu_draw(self, context):
    self.layout.operator(
        OBJECT_OT_new_collection_with_selection.bl_idname,
        icon='COLLECTION_NEW',
    )


_CLASSES = [OBJECT_OT_new_collection_with_selection]

_MENUS = [
    "OUTLINER_MT_object",
    "OUTLINER_MT_collection",
    "VIEW3D_MT_object_collection",
]


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    for menu in _MENUS:
        getattr(bpy.types, menu).append(_menu_draw)


def unregister():
    for menu in _MENUS:
        getattr(bpy.types, menu).remove(_menu_draw)
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
