# --------------------------------------------------------------------------------
# ADDON DESCRIPTION
# --------------------------------------------------------------------------------

bl_info = {
    "name": "Visual Tracker Simulator",
    'author': 'Luka Kuzman',
    "version" : (0, 0, 1),
    "blender": (2, 92, 0),
    "location" : "View3D > Sidebar > Edit Tab",
    "description" : "Gets text file with some parameters as an input, export rendered scene and a mask.",
    "category": "Render",
}



# --------------------------------------------------------------------------------
# IMPORTS AND GLOBAL VARIABLES
# --------------------------------------------------------------------------------

import bpy
import math
import os
import random
from bpy.types import (Panel, Operator, PropertyGroup)
from bpy.props import (StringProperty, BoolProperty, IntProperty, FloatProperty)


# --------------------------------------------------------------------------------
# Stuff that executes every frame
# --------------------------------------------------------------------------------

# Camera distance function parameters
fun_param_a = 0
fun_param_b = 0
fun_param_c = 0
fun_param_d = 0
fun_param_e = 0
fun_param_f = 0
fun_param_g = 0
fun_param_h = 0
fun_param_i = 0

camera_speed = 0


# Fog lowest strength, speed and its max
fog_low = 0
fog_strength = 0
fog_speed = 0
fog_start_offset = 0


# Light lowest strenght, speed and its max
light_low = 0
light_strenght = 0
light_speed = 0
light_start_offset = 0


# Change focal lenght
focal_low = 0
focal_diff = 0
focal_speed = 0
focal_start_offset = 0


def my_handler(scene):
    # For position of camera relative to it's path
    bpy.context.scene.camera.location[0] = fun_param_a + abs(fun_param_b * math.sin(fun_param_c * bpy.context.scene.frame_current * 0.01))
    bpy.context.scene.camera.location[1] = fun_param_d + fun_param_e * math.sin(fun_param_f * bpy.context.scene.frame_current * 0.01)
    bpy.context.scene.camera.location[2] = fun_param_g + fun_param_h * math.sin(fun_param_i * bpy.context.scene.frame_current * 0.01)

    bpy.context.scene.camera.constraints["Follow Path"].offset_factor = ((camera_speed * bpy.context.scene.frame_current * 0.01) % 1)

    # For fog strenth
    fog_mat = bpy.data.materials['FogCube']
    fog_mat.use_nodes = True
    nodes = fog_mat.node_tree.nodes
    volume_node = nodes.get("Volume Scatter")

    volume_node.inputs[1].default_value = fog_low + fog_strength *  abs(math.sin(fog_speed * (bpy.context.scene.frame_current + fog_start_offset) * 0.01))

    world = bpy.data.worlds['World']
    bg = world.node_tree.nodes['Background']
    bg.inputs[1].default_value = light_low + light_strenght * abs(math.sin(light_speed * (bpy.context.scene.frame_current + light_start_offset) * 0.01))

    bpy.data.cameras[0].lens = focal_low + focal_diff * math.sin(focal_speed * (bpy.context.scene.frame_current + focal_start_offset) * 0.01)



# --------------------------------------------------------------------------------
# LOADING PARAMETERS FROM FILES
# --------------------------------------------------------------------------------

file_path = ""

followed_object = ""

class SceneControlOperator(Operator):
    """Scene Control"""
    bl_idname = "object.scene_control"
    bl_label = "Scene control"

    def execute(self, context):
        # Delete all the objects that the program might have generated previously
        self.delete_generated_controler()

        with open(file_path) as f:
            lines = f.readlines()
            
            for i in range(0, len(lines)):
                self.parse_parameters(lines[i])

        return {'FINISHED'}
    
    # File read
    def parse_parameters(self, current_line):
        values = current_line.split(" ")

        if values[0] == "following":
            print("Following")
            self.choose_following_object(values[1], values[2], values[3], values[4], values[5])
        elif values[0] == "camera":
            print("Camera")
            self.camera_control(
                values[1], values[2], values[3],
                values[4], values[5], values[6],
                values[7], values[8], values[9],
                values[10])
        elif values[0] == "distractors":
            print("Distractors")
            self.density_control(values[1])
        elif values[0] == "fog":
            print("Fog")
            self.fog_control(values[1], values[2], values[3], values[4])
        elif values[0] == "light":
            print("Light")
            self.light_control(values[1], values[2], values[3], values[4])
        elif values[0] == "focal":
            print("Focal")
            self.focal_control(values[1], values[2], values[3], values[4])
        else:
            print("Unassigned")

    def delete_generated_controler(self):
        print("Deleted previously generated objects")
        for object in bpy.data.collections['GeneratedObjects'].all_objects:
            bpy.data.objects.remove(object, do_unlink=True)


    # ----------------------------------------------------------------------------------------------
    # STUFF THAT CONTROLS THE SCENE
    # ----------------------------------------------------------------------------------------------

    # Choose following object
    def choose_following_object(self, object_name, camera_path, x, y, z):
        global followed_object
        followed_object = object_name

        camera = bpy.context.scene.camera

        # Make the followed object the center of the camera
        for object in bpy.data.collections['MainObjects'].all_objects:
            if object_name == object.name:
                for constraint in camera.constraints:
                    if constraint.type == 'TRACK_TO':
                        constraint.target = object

                        object.location[0] = float(x)
                        object.location[1] = float(y)
                        object.location[2] = float(z)

        # Choose an apropriate camera path
        for object in bpy.data.collections['CameraParents'].all_objects:
            if camera_path == object.name:
                for constraint in camera.constraints:
                    if constraint.type == 'FOLLOW_PATH':
                        constraint.target = object
                        return

        

    # Camera control
    def camera_control(self, a, b, c, d, e, f, g, h, i, speed):
        global fun_param_a, fun_param_b, fun_param_c
        global fun_param_d, fun_param_e, fun_param_f
        global fun_param_g, fun_param_h, fun_param_i
        global camera_speed
        
        fun_param_a = float(a)
        fun_param_b = float(b)
        fun_param_c = float(c)

        fun_param_d = float(d)
        fun_param_e = float(e)
        fun_param_f = float(f)

        fun_param_g = float(g)
        fun_param_h = float(h)
        fun_param_i = float(i)

        camera_speed = float(speed)


    # Object density conrol
    def density_control(self, generate_density):
        # First delete all the objects that were previously there
        for object in bpy.data.collections['GeneratedObjects'].all_objects:
            bpy.data.objects.remove(object, do_unlink=True)

        layer_collection = bpy.data.collections['GeneratedObjects']

        # Duplicate objects as given by the txt file
        for i in range(int(generate_density)):
            # Choose random object to duplicate
            choose_random = random.randint(0, len(bpy.data.collections['GeneratingObjects'].all_objects) - 1)
            index = 0

            for object in bpy.data.collections['GeneratingObjects'].all_objects:
                if index == choose_random: 
                    generated_object = object.copy()

                    action = generated_object.animation_data.action
                    generated_object.animation_data.action = action.copy()

                    generated_animation_legth = generated_object.animation_data.action.fcurves[0].keyframe_points[1].co[0] - generated_object.animation_data.action.fcurves[0].keyframe_points[0].co[0]
                    offset = int((i + 1)*generated_animation_legth/(int(generate_density)+1))

                    # Setting which path the object should follow
                    number_of_paths = len(bpy.data.collections['FollowingPaths'].all_objects)
                    choose_random_path = random.randint(0, number_of_paths - 1)

                    current_path = 0
                    for path in bpy.data.collections['FollowingPaths'].all_objects:
                        if current_path == choose_random_path:
                            for constraint in generated_object.constraints:
                                if constraint.type == 'FOLLOW_PATH':
                                    constraint.target = path

                        current_path += 1

                    # Adjusting the path data
                    generated_object.animation_data.action.fcurves[0].keyframe_points[0].co[0] = generated_object.animation_data.action.fcurves[0].keyframe_points[0].co[0] - offset
                    generated_object.animation_data.action.fcurves[0].keyframe_points[1].co[0] = generated_object.animation_data.action.fcurves[0].keyframe_points[1].co[0] - offset

                    fc = generated_object.animation_data.action.fcurves[0]

                    for mod in fc.modifiers:
                        fc.modifiers.remove(mod)

                    fc.modifiers.new(type='CYCLES')

                    layer_collection.objects.link(generated_object)
                index += 1

    def fog_control(self, low, strength, speed, offset):
        global fog_low, fog_strength, fog_speed, fog_start_offset
        fog_low = float(low)
        fog_speed = float(speed)
        fog_strength = float(strength)
        fog_start_offset = float(offset)


    def light_control(self, low, strength, speed, offset):
        global light_low, light_strenght, light_speed, light_start_offset
        light_low = float(low)
        light_speed =float(speed)
        light_strenght = float(strength)
        light_start_offset =float(offset)


    def focal_control(self, low, strength, speed, offset):
        global focal_low, focal_diff, focal_speed, focal_start_offset
        focal_low = float(low)
        focal_speed =float(speed)
        focal_diff = float(strength)
        focal_start_offset = float(offset)


# ----------------------------------------------------------------------------------------------
# RENDERING THE SCENE AND ITS MASK
# ----------------------------------------------------------------------------------------------

class RenderSceneOperator(Operator):
    """Render Scene"""
    bl_idname = "object.render_scene"
    bl_label = "Render scene"
    
    def execute(self, context):
        # Render scene
        self.render_scene()

        return {'FINISHED'}

    def render_scene(self):
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree

        # Clearning default nodes
        for node in tree.nodes:
            tree.nodes.remove(node)

        # Create render output node
        default_render_layer = tree.nodes.new(type='CompositorNodeRLayers')
        default_render_layer.layer = bpy.context.scene.view_layers[0].name
        default_render_layer.location = 0,0

        output_node = tree.nodes.new(type='CompositorNodeComposite')
        output_node.location = 400,0

        links = tree.links
        link = links.new(default_render_layer.outputs[0], output_node.inputs[0])

        bpy.context.scene.render.use_lock_interface = True

        bpy.ops.render.render('INVOKE_DEFAULT', animation=True)



class RenderMaskOperator(Operator):
    """Render Mask"""
    bl_idname = "object.render_mask"
    bl_label = "Render mask"
    
    def execute(self, context):
        # Render mask
        self.render_mask()

        return {'FINISHED'}

    def render_mask(self):
        # Change render engine to Eevee to render the mask
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'

        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree

        # Clearning default nodes
        for node in tree.nodes:
            tree.nodes.remove(node)

        # Create render output node
        default_render_layer = tree.nodes.new(type='CompositorNodeRLayers')
        default_render_layer.layer =  bpy.context.scene.view_layers[followed_object].name
        default_render_layer.location = 0,0

        alpha_over_node = tree.nodes.new(type='CompositorNodeAlphaOver')
        alpha_over_node.location = 400,0

        links = tree.links
        link = links.new(default_render_layer.outputs[1], alpha_over_node.inputs[2])

        blur_node = tree.nodes.new(type='CompositorNodeBlur')
        blur_node.location = 800,0

        links = tree.links
        link = links.new(alpha_over_node.outputs[0], blur_node.inputs[0])

        output_node = tree.nodes.new(type='CompositorNodeComposite')
        output_node.location = 1200,0

        links = tree.links
        link = links.new(blur_node.outputs[0], output_node.inputs[0])

        bpy.context.scene.render.use_lock_interface = True

        bpy.ops.render.render('INVOKE_DEFAULT', animation=True)



# ----------------------------------------------------------------------------------------------
# FILE LOADING
# ----------------------------------------------------------------------------------------------

class FileSettings(bpy.types.PropertyGroup):
    path : bpy.props.StringProperty(name="File path",
                                        description="",
                                        default="",
                                        maxlen=1024,
                                        subtype="FILE_PATH")



class FileSelector(Operator):
    bl_idname = "object.file_selector"
    bl_label = "File select"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        display = "filepath= "+self.filepath  
        print(display)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



# ----------------------------------------------------------------------------------------------
# UI
# ----------------------------------------------------------------------------------------------

class SceneControlPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Visual Tracking Simulator"
    bl_options = {"DEFAULT_CLOSED"}
    bl_context = "objectmode"
    bl_idname = "object.scene_control_panel"
    bl_label = "Visual Tracker Simulator"

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        global file_path
        layout = self.layout
        col = layout.column(align=True)
        file_tool = context.scene.file_tool
        col.prop(file_tool, "path")
        file_path = bpy.path.abspath("//") + file_tool.path
        col.operator(SceneControlOperator.bl_idname, text="Load", icon="PLAY")

        layout = self.layout
        col = layout.column(align=True)
        col.operator(RenderSceneOperator.bl_idname, text="Render Scene", icon="SEQUENCE")
        col.operator(RenderMaskOperator.bl_idname, text="Render Mask", icon="CLIPUV_DEHLT")

classes = (
    SceneControlOperator,
    RenderSceneOperator,
    RenderMaskOperator,
    SceneControlPanel,
    FileSettings,
    FileSelector
)

# --------------------------------------------------------------------------------
# CLASS REGISTRATION
# --------------------------------------------------------------------------------

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.file_tool = bpy.props.PointerProperty(type=FileSettings)
    bpy.app.handlers.frame_change_post.append(my_handler)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.file_tool
    # bpy.app.handlers.frame_change_post.remove(my_handler)

if __name__ == "__main__":
    register()