
"""hka import operator
"""

import os
import subprocess

import bpy
from bpy.props import BoolProperty
from bpy_extras.io_utils import ImportHelper
from .hka_import import import_hkafile


class hkaImportOperator(bpy.types.Operator, ImportHelper):
    """Import a hkaAnimationContainer file
    """
    bl_idname = "import_anim.hkx"

    bl_label = "Import hkx"

    filename_ext = ".hkx"
    filter_glob : bpy.props.StringProperty(default="*.hkx", options={'HIDDEN'})

    use_anim: BoolProperty(
            name="Import to Animation",
            description="if uncheck then import to Pose",
            default=True,
            )

    def execute(self, context):
        dirname = os.path.dirname(os.path.abspath(__file__))

        skeleton_file = dirname + "/resources/skeleton.bin" # type: str

        # 'anim_hkx_file' path to hkx file
        anim_hkx_file = self.properties.filepath # type: str

        basename = os.path.basename(anim_hkx_file)
        basename, extension = os.path.splitext(basename)
        anim_bin_file = dirname + '/tmp/' + basename + '.bin'

        command = dirname + '/bin/hkdump-bin.exe'
        process = subprocess.run([command, '-o', anim_bin_file, anim_hkx_file])

        # 'use_anim' value from default settings addons
        use_anim = self.properties.use_anim # type: bool

        if process.returncode == 0:
            import_hkafile(skeleton_file, anim_bin_file, use_anim)

        return {'FINISHED'}
