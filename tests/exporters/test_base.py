"""Tests for blender_extension/exporters/base.py.

Tests the ExportResult and SelectionState dataclasses along with
save_selection and restore_selection functions.
"""

from __future__ import annotations

from unittest.mock import MagicMock


class TestExportResult:
    """Tests for ExportResult dataclass."""

    def test_create_success_result(self) -> None:
        """ExportResult with success=True and message."""
        from blender_extension.exporters.base import ExportResult

        result = ExportResult(success=True, message="Export completed")

        assert result.success is True
        assert result.message == "Export completed"
        assert result.files_created == []
        assert result.errors == []
        assert result.export_data is None

    def test_create_failure_result_with_errors(self) -> None:
        """ExportResult with success=False and error list."""
        from blender_extension.exporters.base import ExportResult

        errors = ["File not found", "Permission denied"]
        result = ExportResult(
            success=False,
            message="Export failed",
            errors=errors,
        )

        assert result.success is False
        assert result.message == "Export failed"
        assert result.errors == errors
        assert len(result.errors) == 2

    def test_default_files_created_is_empty_list(self) -> None:
        """files_created defaults to empty list."""
        from blender_extension.exporters.base import ExportResult

        result = ExportResult(success=True, message="Done")

        assert result.files_created == []
        assert isinstance(result.files_created, list)

    def test_default_errors_is_empty_list(self) -> None:
        """errors defaults to empty list."""
        from blender_extension.exporters.base import ExportResult

        result = ExportResult(success=True, message="Done")

        assert result.errors == []
        assert isinstance(result.errors, list)

    def test_files_created_with_paths(self) -> None:
        """ExportResult stores file paths correctly."""
        from blender_extension.exporters.base import ExportResult

        files = ["/path/to/export.glb", "/path/to/manifest.json"]
        result = ExportResult(
            success=True,
            message="Exported 2 files",
            files_created=files,
        )

        assert result.files_created == files
        assert len(result.files_created) == 2

    def test_mutable_default_isolation(self) -> None:
        """Each instance has independent default lists (no shared state)."""
        from blender_extension.exporters.base import ExportResult

        result1 = ExportResult(success=True, message="First")
        result2 = ExportResult(success=True, message="Second")

        result1.files_created.append("/file1.glb")
        result1.errors.append("error1")

        # result2 should not be affected
        assert result2.files_created == []
        assert result2.errors == []


class TestSelectionState:
    """Tests for SelectionState dataclass."""

    def test_create_with_empty_selection(self) -> None:
        """SelectionState with no selected objects."""
        from blender_extension.exporters.base import SelectionState

        state = SelectionState(selected=[], active=None)

        assert state.selected == []
        assert state.active is None

    def test_create_with_selected_objects(self) -> None:
        """SelectionState with mock objects."""
        from blender_extension.exporters.base import SelectionState

        obj1 = MagicMock(name="Cube")
        obj2 = MagicMock(name="Sphere")

        state = SelectionState(selected=[obj1, obj2], active=obj1)

        assert len(state.selected) == 2
        assert obj1 in state.selected
        assert obj2 in state.selected
        assert state.active is obj1


class TestSaveSelection:
    """Tests for save_selection function."""

    def test_save_empty_selection(self, mock_context: MagicMock) -> None:
        """save_selection with no objects selected."""
        from blender_extension.exporters.base import save_selection

        mock_context.selected_objects = []
        mock_context.view_layer.objects.active = None

        state = save_selection(mock_context)

        assert state.selected == []
        assert state.active is None

    def test_save_single_selection(self, mock_context: MagicMock) -> None:
        """save_selection with one object selected and active."""
        from blender_extension.exporters.base import save_selection

        obj = MagicMock(name="Cube")
        mock_context.selected_objects = [obj]
        mock_context.view_layer.objects.active = obj

        state = save_selection(mock_context)

        assert len(state.selected) == 1
        assert obj in state.selected
        assert state.active is obj

    def test_save_multiple_selection(self, mock_context: MagicMock) -> None:
        """save_selection with multiple objects selected."""
        from blender_extension.exporters.base import save_selection

        obj1 = MagicMock(name="Cube")
        obj2 = MagicMock(name="Sphere")
        obj3 = MagicMock(name="Cylinder")
        mock_context.selected_objects = [obj1, obj2, obj3]
        mock_context.view_layer.objects.active = obj2

        state = save_selection(mock_context)

        assert len(state.selected) == 3
        assert state.active is obj2

    def test_save_creates_copy_of_list(self, mock_context: MagicMock) -> None:
        """save_selection creates a copy, not a reference."""
        from blender_extension.exporters.base import save_selection

        obj = MagicMock(name="Cube")
        original_list = [obj]
        mock_context.selected_objects = original_list
        mock_context.view_layer.objects.active = obj

        state = save_selection(mock_context)

        # Modify original list
        original_list.append(MagicMock(name="NewObj"))

        # State should be unaffected
        assert len(state.selected) == 1


class TestRestoreSelection:
    """Tests for restore_selection function."""

    def test_restore_empty_selection(
        self,
        mock_bpy_module: MagicMock,
        mock_context: MagicMock,
    ) -> None:
        """restore_selection with empty state."""
        from blender_extension.exporters.base import SelectionState, restore_selection

        mock_bpy_module.ops.object.select_all.reset_mock()
        state = SelectionState(selected=[], active=None)

        restore_selection(mock_context, state)

        mock_bpy_module.ops.object.select_all.assert_called_once_with(action="DESELECT")
        assert mock_context.view_layer.objects.active is None

    def test_restore_single_selection(
        self,
        mock_bpy_module: MagicMock,
        mock_context: MagicMock,
    ) -> None:
        """restore_selection with one object."""
        from blender_extension.exporters.base import SelectionState, restore_selection

        mock_bpy_module.ops.object.select_all.reset_mock()
        obj = MagicMock(name="Cube")
        state = SelectionState(selected=[obj], active=obj)

        restore_selection(mock_context, state)

        mock_bpy_module.ops.object.select_all.assert_called_once_with(action="DESELECT")
        obj.select_set.assert_called_once_with(True)
        assert mock_context.view_layer.objects.active is obj

    def test_restore_multiple_selection(
        self,
        mock_bpy_module: MagicMock,
        mock_context: MagicMock,
    ) -> None:
        """restore_selection with multiple objects."""
        from blender_extension.exporters.base import SelectionState, restore_selection

        mock_bpy_module.ops.object.select_all.reset_mock()
        obj1 = MagicMock(name="Cube")
        obj2 = MagicMock(name="Sphere")
        obj3 = MagicMock(name="Cylinder")
        state = SelectionState(selected=[obj1, obj2, obj3], active=obj2)

        restore_selection(mock_context, state)

        mock_bpy_module.ops.object.select_all.assert_called_once_with(action="DESELECT")
        obj1.select_set.assert_called_once_with(True)
        obj2.select_set.assert_called_once_with(True)
        obj3.select_set.assert_called_once_with(True)
        assert mock_context.view_layer.objects.active is obj2

    def test_restore_handles_deleted_object(
        self,
        mock_bpy_module: MagicMock,
        mock_context: MagicMock,
    ) -> None:
        """restore_selection handles ReferenceError for deleted objects."""
        from blender_extension.exporters.base import SelectionState, restore_selection

        mock_bpy_module.ops.object.select_all.reset_mock()
        valid_obj = MagicMock(name="ValidCube")
        deleted_obj = MagicMock(name="DeletedCube")
        deleted_obj.select_set.side_effect = ReferenceError("Object deleted")

        state = SelectionState(selected=[valid_obj, deleted_obj], active=valid_obj)

        # Should not raise
        restore_selection(mock_context, state)

        valid_obj.select_set.assert_called_once_with(True)
        deleted_obj.select_set.assert_called_once_with(True)
        assert mock_context.view_layer.objects.active is valid_obj

    def test_restore_with_none_active(
        self,
        mock_bpy_module: MagicMock,
        mock_context: MagicMock,
    ) -> None:
        """restore_selection with selected objects but no active."""
        from blender_extension.exporters.base import SelectionState, restore_selection

        mock_bpy_module.ops.object.select_all.reset_mock()
        obj = MagicMock(name="Cube")
        state = SelectionState(selected=[obj], active=None)

        restore_selection(mock_context, state)

        mock_bpy_module.ops.object.select_all.assert_called_once_with(action="DESELECT")
        obj.select_set.assert_called_once_with(True)
        assert mock_context.view_layer.objects.active is None
