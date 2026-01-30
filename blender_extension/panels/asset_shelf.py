"""Asset shelf for Trivesta level design.

This module provides an Asset Shelf in the 3D View for quick access to
level design assets. Requires Blender 4.2+.
"""

from __future__ import annotations

import bpy


class TRIVESTA_AST_level_assets(bpy.types.AssetShelf):
    """Asset shelf for Trivesta level design assets.

    Note: Asset names are hidden by default (Blender limitation - show_names
    cannot be set programmatically). Users can enable names via the shelf
    header menu (hamburger icon) -> "Show Names".
    """

    bl_space_type = "VIEW_3D"
    bl_idname = "VIEW3D_AST_trivesta_assets"
    bl_label = "Trivesta Assets"
    bl_options = {"DEFAULT_VISIBLE"}

    # Display settings - readable thumbnail size
    bl_default_preview_size = 96

    # Link to placement operators
    bl_activate_operator = "trivesta.place_asset"
    bl_drag_operator = "trivesta.drag_asset"

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        """Show shelf only in Object mode."""
        return (
            context.mode == "OBJECT"
            and context.space_data is not None
            and context.space_data.type == "VIEW_3D"
        )

    @classmethod
    def asset_poll(cls, asset: bpy.types.AssetRepresentation) -> bool:
        """Filter to Object and Collection assets only."""
        return asset.id_type in {"OBJECT", "COLLECTION"}
