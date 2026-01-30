"""Unit tests for placement operators."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestGetLibraryPath:
    """Tests for get_library_path function."""

    def test_returns_path_when_library_exists(self, mock_bpy_module):
        """Should return library path when library name matches."""
        from blender_extension.operators.placement import get_library_path

        lib = MagicMock()
        lib.name = "TestLibrary"
        lib.path = "/path/to/library"
        mock_bpy_module.context.preferences.filepaths.asset_libraries = [lib]

        result = get_library_path("TestLibrary")
        assert result == "/path/to/library"

    def test_returns_none_when_library_not_found(self, mock_bpy_module):
        """Should return None when library name doesn't exist."""
        from blender_extension.operators.placement import get_library_path

        mock_bpy_module.context.preferences.filepaths.asset_libraries = []
        result = get_library_path("NonExistent")
        assert result is None


class TestPlaceAsset:
    """Tests for place_asset function."""

    def test_returns_error_for_invalid_path_format(self, mock_bpy_module, mock_context):
        """Should return error if path has fewer than 3 parts."""
        from blender_extension.operators.placement import PlacementError, place_asset

        result = place_asset(mock_context, "lib", "invalid/path", MagicMock())
        assert result.success is False
        assert result.error == PlacementError.INVALID_PATH

    def test_returns_error_for_unsupported_id_type(self, mock_bpy_module, mock_context):
        """Should return error for non-Object id types."""
        from blender_extension.operators.placement import PlacementError, place_asset

        result = place_asset(
            mock_context,
            "TestLib",
            "file.blend/Collection/MyCollection",
            MagicMock(),
        )
        assert result.success is False
        assert result.error == PlacementError.UNSUPPORTED_TYPE

    def test_returns_error_when_library_not_found(self, mock_bpy_module, mock_context):
        """Should return error when library doesn't exist."""
        from blender_extension.operators.placement import PlacementError, place_asset

        mock_bpy_module.context.preferences.filepaths.asset_libraries = []

        result = place_asset(
            mock_context,
            "NonExistent",
            "file.blend/Object/Cube",
            MagicMock(),
        )
        assert result.success is False
        assert result.error == PlacementError.LIBRARY_NOT_FOUND


class TestDragAssetOperator:
    """Tests for TRIVESTA_OT_drag_asset modal operator."""

    def test_invoke_cancels_without_asset_identifier(
        self, mock_bpy_module, mock_context, mock_event
    ):
        """Should return CANCELLED if no asset identifier provided."""
        from blender_extension.operators.placement import TRIVESTA_OT_drag_asset

        op = TRIVESTA_OT_drag_asset()
        op.relative_asset_identifier = ""
        op.asset_library_identifier = ""

        result = op.invoke(mock_context, mock_event)
        assert result == {"CANCELLED"}

    def test_invoke_starts_modal_with_valid_asset(
        self, mock_bpy_module, mock_context, mock_event
    ):
        """Should start modal operation with valid asset."""
        from blender_extension.operators.placement import TRIVESTA_OT_drag_asset

        op = TRIVESTA_OT_drag_asset()
        op.relative_asset_identifier = "file.blend/Object/Cube"
        op.asset_library_identifier = "MyLibrary"

        result = op.invoke(mock_context, mock_event)

        assert result == {"RUNNING_MODAL"}
        mock_context.window_manager.modal_handler_add.assert_called_once_with(op)
        mock_context.window.cursor_set.assert_called_with("CROSSHAIR")

    def test_modal_cancel_on_escape(self, mock_bpy_module, mock_context, mock_event):
        """Should cancel and cleanup on ESC key."""
        from blender_extension.operators.placement import TRIVESTA_OT_drag_asset, DragState

        op = TRIVESTA_OT_drag_asset()
        op._obj = MagicMock()
        op._state = DragState.OBJECT_CREATED
        mock_context.mode = "OBJECT"
        mock_event.type = "ESC"

        with patch(
            "blender_extension.operators.placement.get_mouse_location", return_value=None
        ):
            result = op.modal(mock_context, mock_event)

        assert result == {"CANCELLED"}
        mock_context.window.cursor_set.assert_called_with("DEFAULT")

    def test_modal_cancel_on_rightmouse(self, mock_bpy_module, mock_context, mock_event):
        """Should cancel on right mouse button."""
        from blender_extension.operators.placement import TRIVESTA_OT_drag_asset, DragState

        op = TRIVESTA_OT_drag_asset()
        op._obj = None
        op._state = DragState.DRAGGING
        mock_context.mode = "OBJECT"
        mock_event.type = "RIGHTMOUSE"

        with patch(
            "blender_extension.operators.placement.get_mouse_location", return_value=None
        ):
            result = op.modal(mock_context, mock_event)

        assert result == {"CANCELLED"}

    def test_modal_finish_on_left_release_with_object(
        self, mock_bpy_module, mock_context, mock_event, mock_object
    ):
        """Should finish when left mouse released with object placed."""
        from blender_extension.operators.placement import TRIVESTA_OT_drag_asset, DragState

        op = TRIVESTA_OT_drag_asset()
        op._obj = mock_object
        op._state = DragState.OBJECT_CREATED
        mock_context.mode = "OBJECT"
        mock_event.type = "LEFTMOUSE"
        mock_event.value = "RELEASE"

        with patch(
            "blender_extension.operators.placement.get_mouse_location",
            return_value=MagicMock(),
        ):
            result = op.modal(mock_context, mock_event)

        assert result == {"FINISHED"}

    def test_modal_cancel_on_left_release_without_object(
        self, mock_bpy_module, mock_context, mock_event
    ):
        """Should cancel when left mouse released outside 3D view."""
        from blender_extension.operators.placement import TRIVESTA_OT_drag_asset, DragState

        op = TRIVESTA_OT_drag_asset()
        op._obj = None
        op._state = DragState.DRAGGING
        mock_context.mode = "OBJECT"
        mock_event.type = "LEFTMOUSE"
        mock_event.value = "RELEASE"

        with patch(
            "blender_extension.operators.placement.get_mouse_location", return_value=None
        ):
            result = op.modal(mock_context, mock_event)

        assert result == {"CANCELLED"}

    def test_modal_creates_object_on_first_mousemove(
        self, mock_bpy_module, mock_context, mock_event, mock_object
    ):
        """Should create object on first MOUSEMOVE into 3D view."""
        from blender_extension.operators.placement import (
            TRIVESTA_OT_drag_asset,
            PlacementResult,
            DragState,
        )

        op = TRIVESTA_OT_drag_asset()
        op._obj = None
        op._state = DragState.DRAGGING
        op._library = "TestLib"
        op._path = "file.blend/Object/Cube"
        mock_context.mode = "OBJECT"
        mock_event.type = "MOUSEMOVE"

        mock_location = MagicMock()

        with patch(
            "blender_extension.operators.placement.get_mouse_location",
            return_value=mock_location,
        ):
            with patch(
                "blender_extension.operators.placement.place_asset",
                return_value=PlacementResult(success=True, object=mock_object),
            ):
                result = op.modal(mock_context, mock_event)

        assert result == {"RUNNING_MODAL"}
        assert op._obj == mock_object
        assert op._state == DragState.OBJECT_CREATED

    def test_modal_updates_position_on_mousemove(
        self, mock_bpy_module, mock_context, mock_event, mock_object
    ):
        """Should update object position on subsequent MOUSEMOVE."""
        from blender_extension.operators.placement import TRIVESTA_OT_drag_asset, DragState

        op = TRIVESTA_OT_drag_asset()
        op._obj = mock_object
        op._state = DragState.OBJECT_CREATED
        mock_context.mode = "OBJECT"
        mock_event.type = "MOUSEMOVE"

        mock_location = MagicMock()

        with patch(
            "blender_extension.operators.placement.get_mouse_location",
            return_value=mock_location,
        ):
            result = op.modal(mock_context, mock_event)

        assert result == {"RUNNING_MODAL"}
        assert mock_object.location == mock_location
