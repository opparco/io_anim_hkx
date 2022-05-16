#!/usr/bin/env python

"""skeleton.bin anim.bin importer for blender ^2.8
"""

import os
import bpy
from mathutils import Euler, Matrix, Quaternion, Vector
import numpy as np
from .io.hka import hkaSkeleton, hkaAnimation
from .utility.help import Help

def import_hkaSkeleton(skeleton):

    def import_armature():
        # object If there is no poll, it will fail.
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode="OBJECT")

        armature = bpy.data.armatures.new('Armature')
        armature.show_axes = True  # Axis
        arm_ob = bpy.data.objects.new(armature.name, armature)

        bpy.context.collection.objects.link(arm_ob)
        bpy.context.view_layer.objects.active = arm_ob
        bpy.context.active_object.select_set(state=True)
        world_scale = 0.1

        bpy.ops.object.mode_set(mode="EDIT")
        for bone in skeleton.bones:
            b_bone_name = Help.get_bone_name_for_blender(bone.name)
            b_bone = armature.edit_bones.new(b_bone_name)
            armature.edit_bones.active = b_bone

            b_bone.parent = bone.parent.b_bone if bone.parent else None

            b_bone.tail.y = world_scale
            b_bone.transform(bone.world_coordinate().to_matrix())

            bone.b_bone = b_bone

        return arm_ob

    # 既存のarmatureを使う場合
    armature_object = Help.detect_armature()

    if armature_object is None:
        # skeleton.bonesをimportしてarmatureを作成する場合
        armature_object = import_armature()


def import_hkaAnimation(anim, skeleton, use_anim=False):

    # create bone map
    # map pose_bone name to bone_idx

    bone_indices = {}

    nbones = len(skeleton.bones)

    # len(p.transforms) for p in anim.pose は全て同値
    # 仮にidx=0をみる
    # t = anim.pose[0].transforms
    ntransforms = len(anim.pose[0].transforms)

    # ntransforms
    # I want to ignore names that exceed ntransforms,
    # so evaluate with min
    for i in range(min(ntransforms, nbones)):
        bone = skeleton.bones[i]
        # blender naming convention
        # io_scene_nifに合わせる
        p_bone_name = Help.get_bone_name_for_blender(bone.name)
        bone_indices[p_bone_name] = i

    def import_pose():
        arm_ob = Help.detect_armature()

        bpy.context.view_layer.objects.active = arm_ob
        arm_ob.select_set(True)

        pose = anim.pose[0]

        bpy.ops.object.mode_set(mode="POSE")

        for p_bone in arm_ob.pose.bones:
            # bone mapに含まれないnameは無視する
            if p_bone.name not in bone_indices:
                continue
            bone_i = bone_indices[p_bone.name]

            t = pose.transforms[bone_i]

            # NOTE: bone.matrix_local
            # 4x4 bone matrix relative to armature

            if p_bone.bone.parent:
                pose_local = p_bone.bone.parent.matrix_local @ t.to_matrix()
            else:
                pose_local = t.to_matrix()

            p_bone_inverted = p_bone.bone.matrix_local.inverted()
            p_bone.matrix_basis = p_bone_inverted @ pose_local

    def import_motion():

        # constants
        # euler order
        order = 'XYZ'

        # action_group name
        location_group = 'Location'
        angle_group = 'Rotation'

        arm_ob = Help.detect_armature()
        bpy.context.view_layer.objects.active = arm_ob
        arm_ob.select_set(True)

        arm_ob.animation_data_create()
        action = bpy.data.actions.new(name='Action')
        arm_ob.animation_data.action = action
        npose = len(anim.pose)
        print("#pose: {0}".format(npose))

        time = np.zeros(npose, dtype=np.float32)
        locations = np.zeros((npose, 3), dtype=np.float32)
        angles = np.zeros((npose, 3), dtype=np.float32)

        for i in range(npose): #164 poses
            pose = anim.pose[i]
            time[i] = 1.0 + pose.time * 30.0

        bpy.ops.object.mode_set(mode="POSE")

        for p_bone in arm_ob.pose.bones: # 99 bones
            # bone mapに含まれないnameは無視する
            if p_bone.name not in bone_indices:
                continue
            bone_i = bone_indices[p_bone.name]

            p_bone.rotation_mode = order

            angle = Euler((0, 0, 0))

            for i in range(npose):
                pose = anim.pose[i]

                t = pose.transforms[bone_i]

                # NOTE: bone.matrix_local
                # 4x4 bone matrix relative to armature

                if p_bone.bone.parent:
                    p_bone_local = p_bone.bone.parent.matrix_local
                    pose_local = p_bone_local @ t.to_matrix()
                else:
                    pose_local = t.to_matrix()

                matrix_basis = p_bone.bone.matrix_local.inverted() @ pose_local

                location, rotation, scale = matrix_basis.decompose()

                angle = rotation.to_euler(order, angle)

                locations[i] = location
                angles[i] = angle

            location_path = 'pose.bones["{0}"].location'.format(p_bone.name)

            for axis_i in range(3):  # xyz
                curve = action.fcurves.new(
                    data_path=location_path,
                    index=axis_i,
                    action_group=location_group)
                keyframe_points = curve.keyframe_points
                test = npose
                curve.keyframe_points.add(npose)

                for i in range(npose):
                    bez = keyframe_points[i]
                    bez.co = time[i], locations[i, axis_i]

            angle_path = 'pose.bones["{0}"].rotation_euler'.format(p_bone.name)

            for axis_i in range(3):  # xyz
                curve = action.fcurves.new(
                    data_path=angle_path,
                    index=axis_i,
                    action_group=angle_group)
                keyframe_points = curve.keyframe_points
                curve.keyframe_points.add(npose)

                for i in range(npose):
                    bez = keyframe_points[i]
                    bez.co = time[i], angles[i, axis_i]

        for cu in action.fcurves:
            for bez in cu.keyframe_points:
                bez.interpolation = 'LINEAR'

    if use_anim:
        import_motion()
    else:
        import_pose()


def import_hkafile(skeleton_file, anim_file, use_anim=False):

    skeleton = hkaSkeleton()
    skeleton.load(skeleton_file)

    import_hkaSkeleton(skeleton)

    anim = hkaAnimation()
    anim.load(anim_file)

    import_hkaAnimation(anim, skeleton, use_anim)

if __name__ == "__main__":
    from time import time

    start_time = time()

    skeleton_file = os.path.join(os.environ['HOME'], "resources/skeleton.bin")
    anim_file = os.path.join(os.environ['HOME'], "resources/idle.bin")
    import_hkafile(skeleton_file, anim_file)

    end_time = time()
    print('bin import time:', end_time - start_time)
