"""Class registration helpers for Blender add-on.

This module provides utilities to collect all registrable Blender classes
in the correct dependency order. PropertyGroups must be registered before
classes that reference them.
"""

from __future__ import annotations


def collect_classes() -> list[type]:
    """Collect all registrable Blender classes in correct order.

    Returns classes in dependency order:
    1. PropertyGroups first (no dependencies)
    2. Operators (may depend on properties)
    3. UI Lists (used by panels)
    4. Panels and Asset Shelves (depend on operators)

    Returns:
        List of Blender class types ready for registration.

    Note:
        This function uses delayed imports to avoid circular dependencies.
    """
    from ..operators.dialog import (
        TRIVESTA_OT_add_dialog_line,
        TRIVESTA_OT_edit_dialog,
        TRIVESTA_OT_move_dialog_line,
        TRIVESTA_OT_remove_dialog_line,
        TRIVESTA_UL_dialog_list,
    )
    from ..operators.export import TRIVESTA_OT_export
    from ..operators.placement import TRIVESTA_OT_drag_asset, TRIVESTA_OT_place_asset
    from ..panels.asset_browser import (
        AssetItem,
        TRIVESTA_OT_place_scene_asset,
        TRIVESTA_OT_refresh_assets,
        TRIVESTA_PT_asset_browser,
        TRIVESTA_UL_asset_list,
    )
    from ..panels.asset_shelf import TRIVESTA_AST_level_assets
    from ..panels.assets import TRIVESTA_PT_assets_panel
    from ..panels.export import TRIVESTA_PT_export_panel
    from ..panels.object import TRIVESTA_PT_object_panel
    from ..panels.scene import TRIVESTA_PT_scene_panel
    from .properties import DialogLine, TrivestaObjectSettings, TrivestaSceneSettings

    # Classes in dependency order
    classes: list[type] = [
        # PropertyGroups first (no dependencies)
        DialogLine,  # Must be before TrivestaObjectSettings (referenced by CollectionProperty)
        TrivestaSceneSettings,
        TrivestaObjectSettings,
        AssetItem,  # For asset browser list
        # Operators (may depend on properties)
        TRIVESTA_OT_add_dialog_line,
        TRIVESTA_OT_remove_dialog_line,
        TRIVESTA_OT_move_dialog_line,
        TRIVESTA_OT_edit_dialog,
        TRIVESTA_OT_export,
        TRIVESTA_OT_place_asset,
        TRIVESTA_OT_drag_asset,
        TRIVESTA_OT_refresh_assets,
        TRIVESTA_OT_place_scene_asset,
        # UI Lists
        TRIVESTA_UL_dialog_list,
        TRIVESTA_UL_asset_list,
        # Panels (depend on operators, parent panels before children)
        TRIVESTA_PT_scene_panel,
        TRIVESTA_PT_export_panel,
        TRIVESTA_PT_assets_panel,
        TRIVESTA_PT_object_panel,
        TRIVESTA_PT_asset_browser,  # N-panel in 3D View
        # Asset Shelf (requires Blender 4.2+)
        TRIVESTA_AST_level_assets,
    ]

    return classes
