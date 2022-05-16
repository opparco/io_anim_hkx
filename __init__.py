import os
import bpy
import bpy.utils.previews
from . import hka_import_op
from . import hka_export_op

bl_info = {
  "author":  "opparco",
  "blender": (2, 80, 0),
  "category": "Import-Export",
  "description": "Import-Expots skyrim hkx format",
  "location": "File > Import > Skyrim hkx (.hkx)",
  "name": "Skyrim hkx format",
  "version": (0, 0, 3, 0),
  "warning": "",
  "wiki_url": "https://github.com/opparco/io_anim_hkx",
  "tracker_url": "https://github.com/opparco/io_anim_hkx",
  "support": "COMMUNITY",
}


class Panel(bpy.types.Panel):
    """Creates a Panel in the 3D view Tools panel"""
    bl_label = "Custom Icon Preview Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):
        global hkx_icons
        icon_id = hkx_icons["custom_icon"].icon_id
        self.layout.label(text="Blender SE", icon_value=icon_id)

# global variable to store icons in
hkx_icons = None


def menu_func_import(self, context):
    bl_idname = hka_import_op.hkaImportOperator.bl_idname
    icon_id = hkx_icons["skyrim_hkx_icon"].icon_id
    text = "Skyrim hkx (.hkx)"
    self.layout.operator(bl_idname, icon_value=icon_id, text=text)


def menu_func_export(self, context):
    bl_idname = hka_export_op.hkaExportOperator.bl_idname
    icon_id = hkx_icons["skyrim_hkx_icon"].icon_id
    text = "Skyrim hkx (.hkx)"
    self.layout.operator(bl_idname, icon_value=icon_id, text=text)


def register():
    # External Icons
    global hkx_icons
    hkx_icons = bpy.utils.previews.new()
    # Use this for an addon.
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    icons_path = os.path.join(icons_dir, "skyrim.png")
    hkx_icons.load("skyrim_hkx_icon", icons_path, 'IMAGE')

    bpy.utils.register_class(hka_import_op.hkaImportOperator)
    bpy.utils.register_class(hka_export_op.hkaExportOperator)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.previews.remove(hkx_icons)
    bpy.utils.unregister_class(hka_import_op.hkaImportOperator)
    bpy.utils.unregister_class(hka_export_op.hkaExportOperator)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
