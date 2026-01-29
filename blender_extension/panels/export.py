"""Export controls panel.

This module provides the Export child panel with action buttons for
exporting world geometry and manifest files.
"""

from __future__ import annotations

from bpy.types import Panel


class TRIVESTA_PT_export_panel(Panel):
    """Export action buttons panel.

    Child panel of TRIVESTA_PT_scene_panel that displays export mode
    indicator and provides buttons for GLB and manifest export.
    """

    bl_label = "Export"
    bl_idname = "TRIVESTA_PT_export_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "TRIVESTA_PT_scene_panel"

    def draw(self, context):
        """Draw the export controls panel."""
        layout = self.layout
        settings = context.scene.trivesta

        # Export mode indicator
        if settings.separate_assets:
            layout.label(text="Mode: Separated Assets", icon='OUTLINER_OB_GROUP_INSTANCE')
        else:
            layout.label(text="Mode: Combined GLB", icon='MESH_DATA')

        layout.separator()

        # Export button
        col = layout.column(align=True)
        col.operator("trivesta.export", text="Export All", icon='EXPORT')
