bl_info = {
	"name": "Skyrim hkx format",
  "description": "Import-Expots skyrim hkx format",
  "blender": (2, 90, 0),
  "author" :  "opparco, UsingSession",
  "warning": "",
	"category": "Import-Export"
}

import bpy
from io_anim_hkx import hka_import_op, hka_export_op


def menu_func_import(self, context):
    self.layout.operator(hka_import_op.hkaImportOperator.bl_idname, text="Skyrim hkx (.hkx)")

def menu_func_export(self, context):
    self.layout.operator(hka_export_op.hkaExportOperator.bl_idname, text="Skyrim hkx (.hkx)")

def register():
    bpy.utils.register_class(hka_import_op.hkaImportOperator)
    bpy.utils.register_class(hka_export_op.hkaExportOperator)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(hka_import_op.hkaImportOperator)
    bpy.utils.unregister_class(hka_export_op.hkaExportOperator)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()

