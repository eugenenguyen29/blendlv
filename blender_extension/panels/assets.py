"""Linked assets panel.

This module provides the Linked Assets child panel that displays a summary
of linked objects from external .blend files, grouped by asset key.
"""

from __future__ import annotations

from bpy.types import Panel

from ..utils.naming import generate_asset_key
from ..utils.transforms import get_library_source


class TRIVESTA_PT_assets_panel(Panel):
    """Display linked assets from external .blend files.

    Child panel of TRIVESTA_PT_scene_panel that shows a summary of linked
    assets, including instance counts and unique asset counts. Collapsed
    by default to reduce visual clutter.
    """

    bl_label = "Linked Assets"
    bl_idname = "TRIVESTA_PT_assets_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "TRIVESTA_PT_scene_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        """Draw the linked assets panel."""
        layout = self.layout

        # Collect linked objects and group by asset key
        asset_counts: dict[str, int] = {}
        linked_objects: list[tuple] = []

        for obj in context.scene.objects:
            source = get_library_source(obj)
            if source:
                linked_objects.append((obj, source))
                key = generate_asset_key(obj)
                if key:  # Only count if key is valid
                    asset_counts[key] = asset_counts.get(key, 0) + 1

        if not linked_objects:
            layout.label(text="No linked assets found", icon='INFO')
            return

        # Summary line
        layout.label(
            text=f"{len(linked_objects)} instances, {len(asset_counts)} unique",
            icon='LINKED'
        )

        # Asset list grouped by key
        box = layout.box()
        for key, count in sorted(asset_counts.items())[:10]:
            row = box.row()
            row.label(text=key, icon='OBJECT_DATA')
            row.label(text=f"x{count}")

        if len(asset_counts) > 10:
            layout.label(text=f"... and {len(asset_counts) - 10} more unique assets")
