import os
import bpy
from bpy.types import Operator
from bpy.props import BoolProperty


class TRIVESTA_OT_export_world(Operator):
    bl_idname = "trivesta.export_world"
    bl_label = "Export World GLB"
    bl_description = "Export the world as a combined GLB file"
    bl_options = {'REGISTER', 'UNDO'}

    export_manifest: BoolProperty(
        name="Also Export Manifest",
        description="Export manifest JSON alongside the GLB",
        default=False
    )

    def execute(self, context):
        settings = context.scene.trivesta_level
        export_path = bpy.path.abspath(settings.export_path)

        # Ensure export directory exists
        os.makedirs(export_path, exist_ok=True)

        glb_path = os.path.join(export_path, "world.glb")

        # Store current selection
        original_selection = context.selected_objects.copy()
        original_active = context.view_layer.objects.active

        try:
            # Select all mesh objects for export
            bpy.ops.object.select_all(action='DESELECT')

            export_objects = []
            for obj in context.scene.objects:
                if obj.type == 'MESH' and obj.visible_get():
                    # Skip objects marked as manifest-only
                    if obj.get("trivesta_manifest_only", False):
                        continue
                    obj.select_set(True)
                    export_objects.append(obj)

            if not export_objects:
                self.report({'WARNING'}, "No visible mesh objects to export")
                return {'CANCELLED'}

            # Export using glTF exporter
            bpy.ops.export_scene.gltf(
                filepath=glb_path,
                use_selection=True,
                export_format='GLB',
                export_apply=True,
                export_texcoords=True,
                export_normals=True,
                export_materials='EXPORT',
                export_yup=True,  # Three.js uses Y-up
            )

            self.report({'INFO'}, f"Exported world to {glb_path}")

        finally:
            # Restore selection
            bpy.ops.object.select_all(action='DESELECT')
            for obj in original_selection:
                obj.select_set(True)
            context.view_layer.objects.active = original_active

        # Optionally export manifest too
        if self.export_manifest:
            bpy.ops.trivesta.export_manifest()

        return {'FINISHED'}
