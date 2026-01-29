"""Blender operators for Trivesta Level extension.

This module provides the operators that execute export actions. All operators
are thin wrappers that delegate to the exporters module.

Operators:
    TRIVESTA_OT_export: Unified export operator for GLB and manifest.
    TRIVESTA_OT_place_asset: Click-to-place asset operator.
    TRIVESTA_OT_drag_asset: Drag-and-drop asset placement operator.

Manual Test Checklist (Blender Python Console):
-----------------------------------------------
1. Verify operator registration:
   >>> import bpy
   >>> hasattr(bpy.ops.trivesta, 'export')
   True
   >>> hasattr(bpy.ops.trivesta, 'place_asset')
   True
   >>> hasattr(bpy.ops.trivesta, 'drag_asset')
   True

2. Test export invocation:
   >>> bpy.ops.trivesta.export(export_glb=True, export_manifest=True)
"""

from .export import TRIVESTA_OT_export
from .placement import TRIVESTA_OT_drag_asset, TRIVESTA_OT_place_asset

__all__ = [
    "TRIVESTA_OT_export",
    "TRIVESTA_OT_place_asset",
    "TRIVESTA_OT_drag_asset",
]
