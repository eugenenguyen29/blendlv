"""Base types and helpers for export operations.

This module provides shared data structures and utility functions
used across all exporter modules.

Manual Test Checklist (Blender Python Console):
-----------------------------------------------
1. Test ExportResult creation:
   >>> from blender_extension.exporters.base import ExportResult
   >>> result = ExportResult(success=True, message="Test", files_created=["test.glb"])
   >>> print(f"Success: {result.success}, Files: {result.files_created}")

2. Test selection save/restore:
   >>> from blender_extension.exporters.base import save_selection, restore_selection
   >>> import bpy
   >>> saved = save_selection(bpy.context)
   >>> print(f"Saved {len(saved.selected)} objects")
   >>> restore_selection(bpy.context, saved)
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import bpy

    from blender_extension.core.data import ExportData


@dataclass
class ExportResult:
    """Result of an export operation.

    Attributes:
        success: Whether the export completed successfully.
        message: Human-readable status message.
        files_created: List of absolute paths to created files.
        export_data: The ExportData used for the export (optional).
        errors: List of error messages if any.
    """

    success: bool
    message: str
    files_created: list[str] = field(default_factory=list)
    export_data: ExportData | None = None
    errors: list[str] = field(default_factory=list)


@dataclass
class SelectionState:
    """Captured selection state for restoration.

    Attributes:
        selected: List of selected objects.
        active: The active object (may be None).
    """

    selected: list[bpy.types.Object]
    active: bpy.types.Object | None


def save_selection(context: bpy.types.Context) -> SelectionState:
    """Save current selection state.

    Captures the currently selected objects and active object
    for later restoration.

    Args:
        context: Blender context.

    Returns:
        SelectionState with captured selection.
    """
    return SelectionState(
        selected=list(context.selected_objects),
        active=context.view_layer.objects.active,
    )


def restore_selection(context: bpy.types.Context, state: SelectionState) -> None:
    """Restore previously saved selection state.

    Deselects all objects, then re-selects the saved objects
    and restores the active object.

    Args:
        context: Blender context.
        state: Previously saved SelectionState.
    """
    import bpy

    bpy.ops.object.select_all(action="DESELECT")
    for obj in state.selected:
        try:
            obj.select_set(True)
        except ReferenceError:
            # Object may have been deleted
            pass
    context.view_layer.objects.active = state.active
