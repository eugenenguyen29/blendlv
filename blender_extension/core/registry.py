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
    3. Panels (depend on operators)

    Returns:
        List of Blender class types ready for registration.

    Note:
        This function uses delayed imports to avoid circular dependencies.
    """
    from ..operators.export import TRIVESTA_OT_export
    from ..panels.assets import TRIVESTA_PT_assets_panel
    from ..panels.export import TRIVESTA_PT_export_panel
    from ..panels.object import TRIVESTA_PT_object_panel
    from ..panels.scene import TRIVESTA_PT_scene_panel
    from .properties import TrivestaObjectSettings, TrivestaSceneSettings

    # Classes in dependency order
    classes: list[type] = [
        # PropertyGroups first (no dependencies)
        TrivestaSceneSettings,
        TrivestaObjectSettings,
        # Operators (may depend on properties)
        TRIVESTA_OT_export,
        # Panels (depend on operators, parent panels before children)
        TRIVESTA_PT_scene_panel,
        TRIVESTA_PT_export_panel,
        TRIVESTA_PT_assets_panel,
        TRIVESTA_PT_object_panel,
    ]

    return classes
