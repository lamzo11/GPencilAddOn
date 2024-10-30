import bpy

bl_info = {
    "name": "2D Animation Setup",
    "author": "Djambar",
    "version": (1, 0),
    "blender": (4, 0, 2),
    "location": "Scene > 2D Animation Setup",
    "description": "Sets up a basic 2D animation scene in Blender",
    "category": "Animation"
}

class OBJECT_OT_setup_2d_animation_scene(bpy.types.Operator):
    """Setup a basic 2D animation scene"""
    bl_idname = "scene.setup_2d_animation_scene"
    bl_label = "2D Animation Setup"

    def execute(self, context):
        # Check if necessary objects exist
        if not bpy.data.objects.get('Cube') or not bpy.context.scene.camera or not bpy.data.objects.get('Light'):
            self.report({'ERROR'}, "Cannot find necessary objects (Cube, Camera, or Light). Make sure they exist.")
            return {'CANCELLED'}

        # Check if we're in the default scene
        if bpy.context.scene.name != 'Scene':
            self.report({'ERROR'}, "You're not allowed to overwrite the current scene.")
            return {'CANCELLED'}

        # Delete the default cube
        bpy.data.objects['Cube'].select_set(True)
        bpy.ops.object.delete()

        # Set the default camera as the active camera
        active_camera = bpy.context.scene.camera
        if active_camera:
            bpy.context.view_layer.objects.active = active_camera
            # Reset camera rotation and location
            active_camera.rotation_euler = (1.5708, 0, 0)  # Rotate 90 degrees around X-axis
            active_camera.location = (0, -8, 1)  # Move to (0, -8y, 1z)

            # Create a new collection for the camera if it doesn't exist
            cam_collection = bpy.data.collections.get("Cam")
            if not cam_collection:
                cam_collection = bpy.data.collections.new("Cam")
                bpy.context.scene.collection.children.link(cam_collection)
            cam_collection.objects.link(active_camera)

        # Move the default light object to a new collection named "Lights"
        default_light = bpy.context.scene.objects.get('Light')
        if default_light:
            lights_collection = bpy.data.collections.get("Lights")
            if not lights_collection:
                lights_collection = bpy.data.collections.new("Lights")
                bpy.context.scene.collection.children.link(lights_collection)
            lights_collection.objects.link(default_light)

        # Remove camera and light objects from the default collection
        default_collection = bpy.data.collections.get("Collection")
        if default_collection:
            if active_camera:
                default_collection.objects.unlink(active_camera)
            if default_light:
                default_collection.objects.unlink(default_light)
            # Delete the default collection if it's empty
            if not default_collection.objects:
                bpy.data.collections.remove(default_collection)

        # Create a grease pencil object and move it to a collection named "greasePencilobject"
        bpy.ops.object.gpencil_add(align='WORLD', location=(0, 0, 0))
        bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name="greasePencilobject")

        # Set render settings
        bpy.context.scene.render.film_transparent = True
        bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
        bpy.context.scene.render.ffmpeg.format = 'MPEG4'
        bpy.context.scene.view_settings.view_transform = 'Standard'

        # Compositing setup
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        links = tree.links

        # Clear existing nodes
        for node in tree.nodes:
            tree.nodes.remove(node)

        # Add nodes
        rl = tree.nodes.new(type='CompositorNodeRLayers')
        alpha_over = tree.nodes.new(type='CompositorNodeAlphaOver')
        composite = tree.nodes.new(type='CompositorNodeComposite')
        viewer = tree.nodes.new(type='CompositorNodeViewer')

        # Link nodes

        links.new(rl.outputs[0], alpha_over.inputs[2])
        links.new(alpha_over.outputs[0], composite.inputs[0])
        links.new(alpha_over.outputs[0], viewer.inputs[0])
        
        
        # Enable Z pass
        bpy.context.scene.view_layers["ViewLayer"].use_pass_z = True


        self.report({'INFO'}, "2D animation setup complete!")
        return {'FINISHED'}
    
    
#drawing the button in the "Scene" Tab
    
class SCENE_PT_layout(bpy.types.Panel):
    bl_label = "2D Animation Setup"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_setup_2d_animation_scene.bl_idname)

def register():
    bpy.utils.register_class(OBJECT_OT_setup_2d_animation_scene)
    bpy.utils.register_class(SCENE_PT_layout)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_setup_2d_animation_scene)
    bpy.utils.unregister_class(SCENE_PT_layout)

if __name__ == "__main__":
    register()
