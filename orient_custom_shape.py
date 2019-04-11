# <pep8 compliant>
#
# orient_custom_shape.py
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from mathutils import *
from bpy.props import BoolProperty

class POSE_OT_extract_custom_shape(bpy.types.Operator):
    '''Extract the bone's selected custom shape as a new object'''
    bl_idname = "pose.extract_custom_shape"
    bl_label = "Extract custom shape"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        if (context.mode == 'POSE' and context.selected_pose_bones):
            return True
        else:
            return False

    def execute(self, context):

        armatureName = bpy.context.active_object.name
        armature = bpy.data.objects[armatureName]

        activePoseBone = bpy.context.active_pose_bone
        boneName = bpy.context.active_pose_bone.name
        bone = armature.data.bones[boneName]

        # If the user didn't pick a custom_shape return
        if not activePoseBone.custom_shape:
            return {'CANCELLED'}

        objectName = activePoseBone.custom_shape.name
        shapeObject = bpy.data.objects[objectName]

        # Create new mesh
        name = objectName
        mesh = bpy.data.meshes.new(name)
        # Create new object associated with the mesh
        ob_new = bpy.data.objects.new(name, mesh)
 
        # Copy data block from the old object into the new object
        ob_new.data = shapeObject.data.copy()
        ob_new.scale = shapeObject.scale
        ob_new.rotation_euler = shapeObject.rotation_euler
        ob_new.location = shapeObject.location
        
        # Link new object to the given scene and select it
        bpy.context.scene.collection.objects.link(ob_new)

        # switch from Pose mode to Object mode & select the new duplicated custom shape
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        ob_new.select_set(True)

        return {'FINISHED'}

class POSE_OT_snap_selected_to_bone(bpy.types.Operator):
    '''Align selected object to selected bone'''
    bl_idname = "pose.snap_selected_to_bone"
    bl_label = "Snap selected to bone"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        if (context.mode == 'POSE' 
        and context.selected_pose_bones 
        and [sel for sel in context.selected_objects if sel.type=='MESH']):
            return True
        else:
            return False

    def execute(self, context):
        objects = [sel for sel in context.selected_objects if sel.type=='MESH']
     
        shape = objects[0]
        bone = context.selected_pose_bones[0]
        armature = context.view_layer.objects.active

        mat = armature.matrix_world @ bone.matrix
        shape.matrix_world = mat

        return {'FINISHED'}

class POSE_OT_align_bone_shape(bpy.types.Operator):
    '''Align selected bone's bone shape '''
    bl_idname = "pose.align_bone_shape"
    bl_label = "Align bone shape"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(self, context):
        if (context.mode == 'POSE' 
        and context.selected_pose_bones 
        and context.selected_pose_bones[0].custom_shape):
            return True
        else:
            return False

    def execute(self, context):
        bone = context.selected_pose_bones[0]
        shape = bone.custom_shape
        armature = context.view_layer.objects.active

        bone.use_custom_shape_bone_size = False

        mat = armature.matrix_world @ bone.matrix
        mat.invert()

        shape.matrix_world = mat @ shape.matrix_world

        bpy.ops.object.posemode_toggle()
        bpy.ops.object.select_all(action='DESELECT')
        shape.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        shape.matrix_world = armature.matrix_world @ bone.matrix
        shape.select_set(False)
        armature.select_set(True)
        bpy.ops.object.posemode_toggle()

        return {'FINISHED'}


class POSE_OT_set_bone_shape_in_place(bpy.types.Operator):
    '''Set bone shape in place'''
    bl_idname = "pose.set_bone_shape_in_place"
    bl_label = "Set the bone shape of the selected bone to the selected object, and transform the custom shape object so that the bone shape appears in the same place"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(self, context):
        if (context.mode == 'POSE' 
        and context.selected_pose_bones
        and [sel for sel in context.selected_objects if sel.type=='MESH']):
            return True
        else:
            return False

    def execute(self, context):
        objects = [sel for sel in context.selected_objects if sel.type=='MESH']
        shape = objects[0]

        bone = context.selected_pose_bones[0]
        armature = context.view_layer.objects.active
        bone.custom_shape = shape
        bone.use_custom_shape_bone_size = False

        mat = armature.matrix_world @ bone.matrix
        mat.invert()

        shape.matrix_world = mat @ shape.matrix_world

        bpy.ops.object.posemode_toggle()
        bpy.ops.object.select_all(action='DESELECT')
        shape.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        shape.matrix_world = armature.matrix_world @ bone.matrix
        shape.select_set(False)
        armature.select_set(True)
        bpy.ops.object.posemode_toggle()

        return {'FINISHED'}


def render_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator('pose.snap_selected_to_bone', text="Snap to bone")
    layout.operator('pose.align_bone_shape', text="Align bone shape")
    layout.operator('pose.extract_custom_shape', text="Extract custom bone shape")
    layout.operator('pose.set_bone_shape_in_place', text="Set and align bone shape")


def register():
    bpy.utils.register_class(POSE_OT_snap_selected_to_bone)
    bpy.utils.register_class(POSE_OT_align_bone_shape)
    bpy.utils.register_class(POSE_OT_set_bone_shape_in_place)
    bpy.utils.register_class(POSE_OT_extract_custom_shape)
    bpy.types.VIEW3D_MT_pose_context_menu.append(render_menu)

def unregister():
    bpy.utils.unregister_class(POSE_OT_snap_selected_to_bone)
    bpy.utils.unregister_class(POSE_OT_align_bone_shape)
    bpy.utils.unregister_class(POSE_OT_set_bone_shape_in_place)
    bpy.utils.unregister_class(POSE_OT_extract_custom_shape)
    bpy.types.VIEW3D_MT_pose_context_menu.remove(render_menu)
