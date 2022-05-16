import bpy


class Help():

  def detect_armature():
      found = None
      for ob in bpy.context.selected_objects:
          if ob.type == 'ARMATURE':
              found = ob
              break
      return found

  # bone naming convention for blender
  def get_bone_name_for_blender(name):
      """Convert a bone name to a name that can be used by Blender: turns
      'Bip01 R xxx' into 'Bip01 xxx.R', and similar for L.

      :param name: The bone name as in the nif file.
      :type name: :class:`str`
      :return: Bone name in Blender convention.
      :rtype: :class:`str`
      """
      if name.startswith("Bip01 L "):
          return "Bip01 " + name[8:] + ".L"
      elif name.startswith("Bip01 R "):
          return "Bip01 " + name[8:] + ".R"
      elif name.startswith("NPC L ") and name.endswith("]"):
          name = name.replace("NPC L", "NPC")
          name = name.replace("[L", "[")
          name = name.replace("]", "].L")
          return name
      elif name.startswith("NPC R ") and name.endswith("]"):
          name = name.replace("NPC R", "NPC")
          name = name.replace("[R", "[")
          name = name.replace("]", "].R")
          return name

      return name
