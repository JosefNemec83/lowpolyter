# This script generates a low poly terrain like mesh based on user's input

bl_info = {
    "name": "LowPoly Terrain Generator",
    "description": "Creates a low poly terrain based on user's inputs. Note: Work-in-progress!",
    "author": "Josef Nemec",
    "version": (0, 1),
    "blender": (2, 82, 0),
    "location": "View3D > Add > Mesh > Low Poly Terrain",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "category": "Add Mesh"}

import bpy
from bpy.props import IntProperty, FloatProperty, FloatVectorProperty
from bpy.types import Operator
import random

def terrain_deformation(context, kw, mode, direction):
    """ Deform our terrain mesh using SMOOTH and RANDOM proportional edit mode along the Z-Axis.
        kw: a set of properties sent by our operator (default or inputed by user)
        mode: a mode of the proportional editing (SMOOTH or RANDOM)
        direction: a direction of edit along the Z-Axis (UP or DOWN) """
       
    # pulling some properties
    for property in kw:
        if (mode.lower() and direction.lower()) in property:
            count = kw["prop_" + str(mode.lower()) + "_" + str(direction.lower())] # a number of times the proportional edit will be used
            size = kw["size_" + str(mode.lower()) + "_" + str(direction.lower())] # a size of the proportional edit

    # setting the length of the proportional edit along the Z-Axis.
    # RANDOM is quite aggressive and therefore we want to restrict it to +/- 0.4m (make it adjustable in the future)
    if mode == "RANDOM" and direction == "UP":
        z_transform = 0.4
    elif mode == "RANDOM" and direction == "DOWN":
        z_transform = -0.4
    elif mode == "SMOOTH" and direction == "UP":
        z_transform = random.random()
    else:
        z_transform = -random.random()
        
    our_terrain = context.active_object
    verts_count = len(context.active_object.data.vertices) # pulling the total number of vertices of our mesh
    
    for x in range(count):
        bpy.ops.mesh.select_all(action = 'DESELECT') # first need to deselect all
        bpy.ops.object.mode_set(mode = 'OBJECT') # we need to be in OBJECT mode in order to be able to select some vertices
            
        # selecting a single random vertex from the top half of vertices as the bottom half of the mesh is hidden in order to shield it from any deformation.
        random_vert = random.randint(verts_count//2, verts_count)
        our_terrain.data.vertices[random_vert].select = True
            
        bpy.ops.object.mode_set(mode = 'EDIT') # switching back to EDIT mode so that we can perform the deformation on our selected vertex
        bpy.ops.transform.translate(value=(0, 0, z_transform), 
                                    constraint_axis=(False, False, True), 
                                    use_proportional_edit=True, 
                                    proportional_edit_falloff=mode, 
                                    proportional_size=size)        

def main(context, **kw):
    """ This function right now handles the creation of a new plane, its proper scaling, extrusion and subdivision.
        And then calling on the prepared mesh the terrain_deformation function.
        kw: a set of properties sent by our operator (default or inputed by user) """
    
    # Pulling some properties
    kw_copy = kw.copy()
    x_axis, y_axis, z_axis = kw_copy.pop("terrain_scale")
    sub_level = kw_copy.pop("sub_level")
    
    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, location=(0, 0, 0)) # add a default plane

    our_terrain = bpy.context.active_object # referring to our newly created plane
    our_terrain.name = "LowPolyTerrain" # give our plane a unique name

    bpy.ops.transform.resize(value=(x_axis, y_axis, 1.0)) # resize along X-axis and Y-axis based on user's input
    bpy.ops.object.mode_set(mode = 'EDIT') # going to EDIT mode
    bpy.ops.mesh.select_mode(type = 'VERT') # switching to VERTEX SELECT mode

    # perform a number of subdivisions based on user's input
    for x in range(sub_level):
        bpy.ops.mesh.subdivide()

    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, z_axis)}) # extrude along Z-axis based on user's input

    bpy.ops.mesh.select_all(action = 'DESELECT') # first need to deselect all
    bpy.ops.object.mode_set(mode = 'OBJECT') # we need to be in OBJECT mode in order to be able to select some vertices

    # selecting the first half (bottom) vertices of our mesh
    for x in range(len(our_terrain.data.vertices)//2):
        our_terrain.data.vertices[x].select = True

    bpy.ops.object.mode_set(mode = 'EDIT') # going back to EDIT mode
    bpy.ops.mesh.hide(unselected=False) # hide all selected vertices, which means whole bottom layer of our mesh
    
    # calling our terrain_deformation function 4 times (change to 1 call only and let the function decide what to do based on input)
    terrain_deformation(context, kw, "SMOOTH", "UP")
    terrain_deformation(context, kw, "SMOOTH", "DOWN")
    terrain_deformation(context, kw, "RANDOM", "UP")
    terrain_deformation(context, kw, "RANDOM", "DOWN")   

# -------------------------------------------------- Our Operator Class
class LowpolyTer(Operator):
    bl_idname = "add.add_lowpoly_terrain_object"
    bl_label = "Generate Low Poly Terrain Object"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    
    # --------------------------------------------------
    # Basic terrain properties
    
    terrain_scale: FloatVectorProperty(
            name="Scale",
            description="Scale terrain",
            size=3,
            min=0.0, max=10.0,
            default=(7.0, 7.0, 2.0),
            )
            
    sub_level: IntProperty(
            name = "Subdivision count",
            description="A number of subdivisions applied on the terrain",
            min = 1, max = 5,
            default = 5,
            )
    
    # --------------------------------------------------
    # Terrain deformation
     
    prop_smooth_up: IntProperty(
            name = "Count",
            min = 0, max = 20,
            default = 10,
            description = "Number of times a random vertex is moved up on Z-Axis (Prop. edit Smooth)"
            )
            
    prop_smooth_down: IntProperty(
            name = "Count",
            min = 0, max = 20,
            default = 5,
            description = "Number of times a random vertex is moved down on Z-Axis (Prop. edit Smooth)"
            )
            
    prop_random_up: IntProperty(
            name = "Count",
            min = 0, max = 20,
            default = 10,
            description = "Number of times a random vertex is moved up on Z-Axis (Prop. edit Random)"
            )
            
    prop_random_down: IntProperty(
            name = "Count",
            min = 0, max = 20,
            default = 5,
            description = "Number of times a random vertex is moved down on Z-Axis (Prop. edit Random)"
            )
            
    size_smooth_up: FloatProperty(
            name = "Size",
            min = 0.01, max = 10.0,
            default = 5.0,
            description = "Terrain height"
            )
            
    size_smooth_down: FloatProperty(
            name = "Size",
            min = 0.01, max = 10.0,
            default = 5.0,
            description = "Terrain height"
            )
            
    size_random_up: FloatProperty(
            name = "Size",
            min = 0.01, max = 10.0,
            default = 5.0,
            description = "Terrain height"
            )
            
    size_random_down: FloatProperty(
            name = "Size",
            min = 0.01, max = 10.0,
            default = 5.0,
            description = "Terrain height"
            )
    
    def execute(self, context):
        keywords = self.as_keywords()

        main(context, **keywords)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        col = box.column()
        col.label(text="Basic Terrain Properties")
        rowsub = col.row()
        rowsub.prop(self, "terrain_scale")
        rowsub = col.row()
        rowsub.prop(self, "sub_level")
        
        box = layout.box()
        col = box.column()
        col.label(text="Terrain Deformation via Proportional edit (Z-axis only)")
        rowsub = col.row(align=True)
        rowsub.label(text="Smooth Falloff Up")
        rowsub.prop(self, "prop_smooth_up")
        rowsub.prop(self, "size_smooth_up")
        rowsub = col.row(align=True)
        rowsub.label(text="Smooth Falloff Down")
        rowsub.prop(self, "prop_smooth_down")
        rowsub.prop(self, "size_smooth_down")  
        rowsub = col.row(align=True)
        rowsub.label(text="Random Falloff Up")
        rowsub.prop(self, "prop_random_up")
        rowsub.prop(self, "size_random_up")      
        rowsub = col.row(align=True)
        rowsub.label(text="Random Falloff Down")
        rowsub.prop(self, "prop_random_down")      
        rowsub.prop(self, "size_random_down")
        
# ----------------------------------------------------------------------------------------------------
    
def menu_func(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("add.add_lowpoly_terrain_object", text="Low Poly Terrain", icon="MOD_OCEAN")
    
def register():
    bpy.utils.register_class(LowpolyTer)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)
    
def unregister():
    bpy.utils.unregister_class(LowpolyTer)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)

    del bpy.types.Scene.lowpolyter

if __name__ == "__main__":
    register()