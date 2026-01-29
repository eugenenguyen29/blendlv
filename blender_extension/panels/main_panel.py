import bpy
from bpy.types import Panel

from ..utils.transforms import get_library_source


class TRIVESTA_PT_main_panel(Panel):
    bl_label = "Trivesta Level"
    bl_idname = "TRIVESTA_PT_main_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.trivesta_level

        layout.prop(settings, "export_path")


class TRIVESTA_PT_export_panel(Panel):
    bl_label = "Export"
    bl_idname = "TRIVESTA_PT_export_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "TRIVESTA_PT_main_panel"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("trivesta.export_world", text="Export World GLB", icon='EXPORT')
        col.operator("trivesta.export_manifest", text="Export Manifest JSON", icon='FILE_TEXT')

        layout.separator()

        row = layout.row()
        row.operator("trivesta.export_world", text="Export Both").export_manifest = True


class TRIVESTA_PT_assets_panel(Panel):
    bl_label = "Linked Assets"
    bl_idname = "TRIVESTA_PT_assets_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "TRIVESTA_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        # Find all linked objects
        linked_objects = []
        for obj in context.scene.objects:
            source = get_library_source(obj)
            if source:
                linked_objects.append((obj, source))

        if not linked_objects:
            layout.label(text="No linked assets found", icon='INFO')
            return

        layout.label(text=f"{len(linked_objects)} linked asset(s):", icon='LINKED')

        box = layout.box()
        for obj, source in linked_objects[:10]:  # Limit display
            row = box.row()
            row.label(text=obj.name, icon='OBJECT_DATA')
            # Show truncated path
            short_path = source if len(source) < 30 else "..." + source[-27:]
            row.label(text=short_path)

        if len(linked_objects) > 10:
            layout.label(text=f"... and {len(linked_objects) - 10} more")
