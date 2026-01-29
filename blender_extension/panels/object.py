"""Object-level properties panel.

This module provides the Trivesta panel in the Properties > Object context
for configuring per-object entity type and flags.
"""

from __future__ import annotations

from bpy.types import Panel

from ..utils.naming import generate_asset_key
from ..utils.transforms import get_library_source


class TRIVESTA_PT_object_panel(Panel):
    """Object entity type and properties panel.

    Displays in Properties > Object for mesh objects only. Allows
    configuration of entity type, terrain/collision flags, and shows
    read-only asset information for linked objects.
    """

    bl_label = "Trivesta"
    bl_idname = "TRIVESTA_PT_object_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        """Only show panel for mesh objects."""
        return context.object is not None and context.object.type == 'MESH'

    def draw(self, context):
        """Draw the object properties panel."""
        layout = self.layout
        obj = context.object
        settings = obj.trivesta

        # Entity type dropdown
        layout.prop(settings, "entity_type")

        # Terrain/collision flags
        row = layout.row()
        row.prop(settings, "is_terrain")
        row.prop(settings, "is_collision")

        layout.separator()

        # Asset info (read-only)
        box = layout.box()
        box.label(text="Asset Info", icon='INFO')

        source = get_library_source(obj)
        if source:
            asset_key = generate_asset_key(obj)
            if asset_key:
                box.label(text=f"Key: {asset_key}")
            else:
                box.label(text="Key: (unable to generate)")
            # Truncate long paths for readability
            short_path = source if len(source) < 40 else "..." + source[-37:]
            box.label(text=f"Source: {short_path}")
        else:
            box.label(text="Local object (not linked)")
