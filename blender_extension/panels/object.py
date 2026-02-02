"""Object-level properties panel.

This module provides the Trivesta panel in the Properties > Object context
for configuring per-object entity type and flags.
"""

from __future__ import annotations

import bpy
from bpy.types import Panel

from ..utils.naming import generate_asset_key
from ..utils.transforms import get_library_source


class TRIVESTA_PT_object_panel(Panel):
    """Object entity type and properties panel.

    Displays in Properties > Object for:
    - Mesh objects
    - Collection instances (EMPTY with instance_type='COLLECTION')

    Allows configuration of entity type, terrain/collision flags, and shows
    read-only asset information for linked objects.
    """

    bl_label = "Trivesta"
    bl_idname = "TRIVESTA_PT_object_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        """Show panel for mesh objects and collection instances."""
        if context.object is None:
            return False

        # Support MESH objects
        if context.object.type == "MESH":
            return True

        # Support EMPTY objects that instance collections
        if context.object.type == "EMPTY" and context.object.instance_type == "COLLECTION":
            return True

        return False

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

        # NPC Dialog UI (conditional)
        if settings.entity_type == "npc":
            box = layout.box()
            box.label(text="NPC Dialog", icon="TEXT")

            row = box.row()
            row.template_list(
                "TRIVESTA_UL_dialog_list",
                "",
                settings,
                "dialog_lines",
                settings,
                "dialog_line_index",
                rows=4,
            )

            col = row.column(align=True)
            col.operator("trivesta.add_dialog_line", icon="ADD", text="")
            col.operator("trivesta.remove_dialog_line", icon="REMOVE", text="")
            col.separator()
            col.operator("trivesta.move_dialog_line", icon="TRIA_UP", text="").direction = "UP"
            col.operator("trivesta.move_dialog_line", icon="TRIA_DOWN", text="").direction = "DOWN"

            # Edit Dialog button
            box.operator("trivesta.edit_dialog", text="Edit Dialog", icon="GREASEPENCIL")

        # Interactive Script ID UI (conditional)
        elif settings.entity_type == "interactive":
            box = layout.box()
            box.label(text="Interactive Scripting", icon="SCRIPT")
            box.prop(settings, "script_id", text="Script ID")

        layout.separator()

        # Asset info (read-only)
        box = layout.box()
        box.label(text="Asset Info", icon="INFO")

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
