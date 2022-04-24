#!/usr/bin/env python

"""anim.bin exporter for blender ^2.8
"""

import os
import bpy
from math import radians
from mathutils import Euler, Matrix, Quaternion, Vector
import numpy as np

# import numpy as np
from .io.hka import hkaSkeleton, hkaAnimation, hkaPose, Transform
from .naming import get_bone_name_for_blender


def export_hkaAnimation(anim, skeleton):

    # create bone map
    # map pose_bone name to bone_idx

    bone_indices = {}

    nbones = len(skeleton.bones)

    for i in range(nbones):
        bone = skeleton.bones[i]
        # blender naming convention
        # io_scene_nifに合わせる
        p_bone_name = get_bone_name_for_blender(bone.name)
        bone_indices[p_bone_name] = i

    def detect_armature():
        found = None
        for ob in bpy.context.selected_objects:
            if ob.type == 'ARMATURE':
                found = ob
                break
        return found

    def export_pose():
        selected_obj = bpy.context.selected_objects
        frame_range = selected_obj[0].animation_data.action.frame_range
        arm_ob = detect_armature()
        # bpy.context.view_layer.objects.active = arm_ob
        # bpy.context.active_object.select_set(state=True)
        # arm_ob.select_set(True)

        keyframes = int(frame_range.length) # type: int
        duration = float(keyframes) / 30.0 # type: float

        time = np.zeros(keyframes, dtype=np.float32)
        locations = np.zeros((keyframes, 3), dtype=np.float32)
        angles = np.zeros((keyframes, 3), dtype=np.float32)

        for i in range(keyframes):
            t = float(keyframes) / 30.0
            t = t / float(keyframes)
            t = t * float(i)
            time[i] = float(1.0 + t * 30.0)

        anim.numOriginalFrames = keyframes
        anim.duration = duration

        del anim.pose[:]
        for i in range(keyframes):
            pose = hkaPose()
            anim.pose.append(pose)

        pose.time = 0.0

        for bone in skeleton.bones:
            t = bone.local.copy()
            pose[i].transforms.append(t)

        for p_bone in arm_ob.pose.bones:
            # bone mapに含まれないnameは無視する
            if p_bone.name not in bone_indices:
                continue
            bone_i = bone_indices[p_bone.name]

            bone = p_bone.bone  # rest bone

            if bone.parent:
                m = bone.parent.matrix_local.inverted() @ bone.matrix_local
                m = m @ p_bone.matrix_basis
            else:
                m = bone.matrix_local @ p_bone.matrix_basis

            location, rotation, scale = m.decompose()

            t = pose.transforms[bone_i]
            t.translation = location
            t.rotation = rotation
            t.scale = scale.z


    def export_motion():
        # arm = bpy.context.selected_objects[0].animation_data['action'].frame_range
        arm_ob = detect_armature()
        pass

    export_pose()
    export_motion()



def export_hkafile(skeleton_file, anim_file):

    skeleton = hkaSkeleton()
    skeleton.load(skeleton_file)

    anim = hkaAnimation()
    export_hkaAnimation(anim, skeleton)

    anim.save(anim_file)

if __name__ == "__main__":
    from time import time

    start_time = time()

    skeleton_file = os.path.join(os.environ['HOME'], "resources/skeleton.bin")
    anim_file = "anim.bin"
    export_hkafile(skeleton_file, anim_file)

    end_time = time()
    print('bin export time:', end_time - start_time)
