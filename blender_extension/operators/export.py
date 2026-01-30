"""Unified export operator for Trivesta Level extension.

This module provides a single operator that handles all export operations,
delegating to the appropriate exporter based on scene settings.
"""

from __future__ import annotations

import bpy
from bpy.types import Operator

from ..exporters import ExportResult, export_world


class TRIVESTA_OT_export(Operator):
    """Export Trivesta Level data.

    Unified operator that exports world geometry and manifest JSON.
    Exports both GLB files and manifest in a single operation.
    """

    bl_idname = "trivesta.export"
    bl_label = "Export Trivesta Level"
    bl_description = "Export world geometry and manifest JSON"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> set[str]:
        """Execute the export operation.

        Args:
            context: Blender context.

        Returns:
            {'FINISHED'} on success, {'CANCELLED'} on failure.
        """
        settings = context.scene.trivesta
        export_path = bpy.path.abspath(settings.export_path)

        # Validate export path
        if not export_path:
            self.report({'ERROR'}, "Export path not set")
            return {'CANCELLED'}

        # Execute export with exception handling
        try:
            result = export_world(context, export_path)
        except Exception as e:
            self.report({'ERROR'}, f"Export failed with exception: {e}")
            return {'CANCELLED'}

        # Report results
        self._report_result(result)

        return {'FINISHED'} if result.success else {'CANCELLED'}

    def _report_result(self, result: ExportResult) -> None:
        """Report export results to the user.

        Args:
            result: Export result with success status and file list.
        """
        if result.success:
            self.report({'INFO'}, f"Export complete: {result.message}")

            # Log created files (limit to avoid spam)
            file_count = len(result.files_created)
            if file_count <= 5:
                for file_path in result.files_created:
                    self.report({'INFO'}, f"  Created: {file_path}")
            else:
                for file_path in result.files_created[:3]:
                    self.report({'INFO'}, f"  Created: {file_path}")
                self.report({'INFO'}, f"  ... and {file_count - 3} more files")
        else:
            self.report({'ERROR'}, f"Export failed: {result.message}")
            for error in result.errors:
                self.report({'ERROR'}, f"  {error}")

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        """Invoke the operator, showing confirmation for large scenes.

        Shows a confirmation dialog when exporting scenes with more than
        100 mesh objects to prevent accidental long exports.

        Args:
            context: Blender context.
            event: Blender event.

        Returns:
            Result of execute() or confirmation dialog invoke.
        """
        # Count visible mesh objects
        mesh_count = sum(
            1 for obj in context.scene.objects
            if obj.type == 'MESH' and obj.visible_get()
        )

        # Show confirmation for large scenes
        if mesh_count > 100:
            return context.window_manager.invoke_confirm(self, event)

        return self.execute(context)


__all__ = ["TRIVESTA_OT_export"]
