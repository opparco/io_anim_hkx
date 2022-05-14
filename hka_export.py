#!/usr/bin/env python

"""anim.bin exporter for blender ^2.8
"""

import os
import bpy
from math import radians
from mathutils import Euler, Matrix, Quaternion, Vector
import numpy as np
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

    def export_motion():
        arm_ob = detect_armature()
        bpy.context.view_layer.objects.active = arm_ob
        bpy.context.active_object.select_set(state=True)

        # Armature of this object
        object_armature = bpy.data.objects.get('Armature')
        # Animation data of this object
        animation_data = object_armature.animation_data
        animation_action = animation_data.action

        # get the number of frames from the rendering settings
        fps = bpy.context.scene.render.fps # type: int
        # fps = 30 # type: int
        anim.numOriginalFrames = int(animation_action.frame_range[1] + 1)
        anim.duration = float(anim.numOriginalFrames) / float(fps)

        del anim.pose[:]
        bpy.context.scene.frame_set(0)
        for i in range(anim.numOriginalFrames):
            bpy.context.scene.frame_set(i)
            pose = hkaPose()
            pose.time = (i * anim.duration) / anim.numOriginalFrames
            anim.pose.append(pose)
            for bone in skeleton.bones:
                t = bone.local.copy()
                pose.transforms.append(t)

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

    def export_pose():
        arm_ob = detect_armature()
        bpy.context.view_layer.objects.active = arm_ob
        bpy.context.active_object.select_set(state=True)

        anim.numOriginalFrames = 1
        anim.duration = 0.033333

        del anim.pose[:]
        pose = hkaPose()
        anim.pose.append(pose)

        pose.time = 0.0
        for bone in skeleton.bones:
            t = bone.local.copy()
            pose.transforms.append(t)

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

    def matrix_world(armature_ob, bone_name):
        local = armature_ob.data.bones[bone_name].matrix_local
        basis = armature_ob.pose.bones[bone_name].matrix_basis

        parent = armature_ob.pose.bones[bone_name].parent
        if parent == None:
            return  local * basis
        else:
            parent_local = armature_ob.data.bones[parent.name].matrix_local
            return matrix_world(armature_ob, parent.name) * (parent_local.inverted() * local) * basis

    # export_pose()
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
