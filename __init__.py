bl_info = {
    "name": "Import Panda3D .egg models",
    "author": "rdb",
    "version": (2, 3),
    "blender": (2, 80, 0),
    "location": "File > Import > Panda3D (.egg)",
    "description": "",
    "warning": "",
    "category": "Import-Export",
}

import bpy
if bpy.app.version < (2, 80):
    bl_info["blender"] = (2, 74, 0) # Needed for normals_split_custom_set


if "loaded" in locals():
    import importlib
    importlib.reload(eggparser)
    importlib.reload(importer)
else:
    from . import eggparser
    from . import importer

loaded = True

import os.path
import bpy.types
from bpy import props
from bpy_extras.io_utils import ImportHelper


class IMPORT_OT_egg(bpy.types.Operator, ImportHelper):
    """Import .egg Operator"""
    bl_idname = "import_scene.egg"
    bl_label = "Import .egg"
    bl_description = "Import a Panda3D .egg file"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".egg"
    filter_glob: props.StringProperty(default="*.egg;*.egg.pz;*.egg.gz", options={'HIDDEN'})

    directory: props.StringProperty(name="Directory", subtype='DIR_PATH', options={'HIDDEN'})
    files: props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN'})

    load_external: props.BoolProperty(name="Load external references", description="Loads other .egg files referenced by this file as separate scenes, and instantiates them using DupliGroups.")
    auto_bind: props.BoolProperty(name="Auto bind", default=True, description="Automatically tries to bind actions to armatures.")
    import_textures: props.BoolProperty(name="Textures", default=True, description="Load texture image files referenced by the .egg.")
    import_materials: props.BoolProperty(name="Materials", default=True, description="Create Blender materials and shader nodes from .egg material and texture state.")
    import_vertex_colors: props.BoolProperty(name="Vertex colors", default=True, description="Import per-vertex color data.")
    import_custom_normals: props.BoolProperty(name="Custom normals", default=True, description="Import explicit .egg normal data instead of letting Blender calculate normals.")
    import_shape_keys: props.BoolProperty(name="Shape keys", default=True, description="Import DXYZ morph targets as Blender shape keys.")
    import_animations: props.BoolProperty(name="Animations", default=True, description="Import animation tables and bind them to matching armatures.")
    import_vertex_groups: props.BoolProperty(name="Vertex groups", default=True, description="Import joint and group vertex membership as Blender vertex groups.")
    import_texture_settings: props.BoolProperty(name="Texture settings", default=True, description="Import texture filter and wrapping settings.")
    import_alpha_masks: props.BoolProperty(name="Alpha masks", default=True, description="Import separate alpha-file textures and connect them to material alpha.")
    validate_meshes: props.BoolProperty(name="Validate meshes", default=True, description="Run Blender mesh validation to clean duplicate or invalid geometry after import.")

    def execute(self, context):
        context = importer.EggContext()
        context.info = lambda msg: self.report({'INFO'}, context.prefix_message(msg))
        context.warn = lambda msg: self.report({'WARNING'}, context.prefix_message(msg))
        context.error = lambda msg: self.report({'ERROR'}, context.prefix_message(msg))
        context.search_dir = self.directory
        context.settings.load_textures = self.import_textures
        context.settings.import_materials = self.import_materials
        context.settings.import_vertex_colors = self.import_vertex_colors
        context.settings.import_custom_normals = self.import_custom_normals
        context.settings.import_shape_keys = self.import_shape_keys
        context.settings.import_animations = self.import_animations
        context.settings.import_vertex_groups = self.import_vertex_groups
        context.settings.import_texture_settings = self.import_texture_settings
        context.settings.import_alpha_masks = self.import_alpha_masks
        context.settings.validate_meshes = self.validate_meshes
        roots = []

        for file in self.files:
            path = os.path.join(self.directory, file.name)
            root = context.read_file(path)
            roots.append(root)

        for root in roots:
            root.build_tree(context)
        context.assign_vertex_groups()

        if self.load_external:
            context.load_external_references()

        if self.auto_bind and context.settings.import_animations:
            context.auto_bind()

        context.final_report()
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "load_external")
        row = layout.row()
        row.prop(self, "auto_bind")
        row = layout.row()
        row.prop(self, "import_textures")
        row.prop(self, "import_materials")
        row = layout.row()
        row.prop(self, "import_vertex_colors")
        row.prop(self, "import_custom_normals")
        row = layout.row()
        row.prop(self, "import_shape_keys")
        row.prop(self, "import_animations")
        row = layout.row()
        row.prop(self, "import_vertex_groups")
        row.prop(self, "import_texture_settings")
        row = layout.row()
        row.prop(self, "import_alpha_masks")
        row.prop(self, "validate_meshes")


def menu_func(self, context):
    self.layout.operator(IMPORT_OT_egg.bl_idname, text="Panda3D (.egg)")

def register():
    bpy.utils.register_class(IMPORT_OT_egg)

    if bpy.app.version >= (2, 80):
        bpy.types.TOPBAR_MT_file_import.append(menu_func)
    else:
        bpy.types.INFO_MT_file_import.append(menu_func)

def unregister():
    if bpy.app.version >= (2, 80):
        bpy.types.TOPBAR_MT_file_import.remove(menu_func)
    else:
        bpy.types.INFO_MT_file_import.remove(menu_func)

    bpy.utils.unregister_class(IMPORT_OT_egg)

if __name__ == "__main__":
    register()
