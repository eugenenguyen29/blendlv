"""Scene-level settings panel.

This module provides the main Trivesta Level panel in the Properties > Scene
context. It displays export path and mode settings, and serves as the parent
for the Export and Linked Assets child panels.
"""

from __future__ import annotations

from bpy.types import Panel


class TRIVESTA_PT_scene_panel(Panel):
    """Main panel for Trivesta Level settings.

    Displays in Properties > Scene as the top-level panel for the extension.
    Contains export path configuration and mode toggles.
    """

    bl_label = "Trivesta Level"
    bl_idname = "TRIVESTA_PT_scene_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        """Draw the scene settings panel."""
        layout = self.layout
        settings = context.scene.trivesta

        # Export path
        layout.prop(settings, "export_path")

        # Export mode toggle
        layout.separator()
        layout.prop(settings, "separate_assets")

        # Show collision option when in separated mode
        if settings.separate_assets:
            layout.prop(settings, "export_collision")

        # Terrain export mode
        layout.separator()
        layout.prop(settings, "terrain_export_mode")

        # World settings section
        layout.separator()
        box = layout.box()
        box.label(text="World Settings", icon="WORLD")

        row = box.row()
        row.prop(settings, "world_size_x")
        row.prop(settings, "world_size_z")

        box.prop(settings, "water_level")
