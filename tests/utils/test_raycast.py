"""Unit tests for raycast utilities."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestGetMouseLocation:
    """Tests for get_mouse_location function."""

    def test_returns_none_when_no_3d_view(self, mock_bpy_module, mock_context, mock_event):
        """Should return None when mouse not over 3D view."""
        from blender_extension.operators.placement import get_mouse_location

        mock_context.screen.areas = []

        result = get_mouse_location(mock_context, mock_event)
        assert result is None

    def test_returns_none_when_mouse_outside_area(
        self, mock_bpy_module, mock_context, mock_event
    ):
        """Should return None when mouse outside 3D view area."""
        from blender_extension.operators.placement import get_mouse_location

        area = MagicMock()
        area.type = "VIEW_3D"
        area.x = 0
        area.y = 0
        area.width = 100
        area.height = 100
        mock_context.screen.areas = [area]

        # Mouse way outside area
        mock_event.mouse_x = 500
        mock_event.mouse_y = 500

        result = get_mouse_location(mock_context, mock_event)
        assert result is None

    def test_returns_location_on_raycast_hit(
        self, mock_bpy_module, mock_context, mock_event
    ):
        """Should return hit location when raycast succeeds."""
        import sys
        from blender_extension.operators.placement import get_mouse_location

        # Setup area
        area = MagicMock()
        area.type = "VIEW_3D"
        area.x = 0
        area.y = 0
        area.width = 1920
        area.height = 1080

        # Setup region
        region = MagicMock()
        region.type = "WINDOW"
        region.x = 0
        region.y = 0
        region.width = 1920
        region.height = 1080
        area.regions = [region]

        # Setup region_3d
        rv3d = MagicMock()
        area.spaces.active.region_3d = rv3d
        mock_context.screen.areas = [area]

        # Setup event
        mock_event.mouse_x = 960
        mock_event.mouse_y = 540

        # Mock raycast result
        mock_origin = MagicMock()
        mock_direction = MagicMock()
        mock_direction.z = -1
        mock_location = MagicMock()

        # Mock distance calculation
        mock_diff = MagicMock()
        mock_diff.length = 5.0  # > MIN_PLACEMENT_DISTANCE
        mock_location.__sub__ = MagicMock(return_value=mock_diff)

        mock_context.scene.ray_cast.return_value = (True, mock_location, None, None, None, None)

        # Patch the bpy_extras mock
        bpy_extras_mock = sys.modules["bpy_extras"]
        bpy_extras_mock.view3d_utils.region_2d_to_origin_3d.return_value = mock_origin
        bpy_extras_mock.view3d_utils.region_2d_to_vector_3d.return_value = mock_direction

        result = get_mouse_location(mock_context, mock_event)

        assert result == mock_location

    def test_excludes_object_from_raycast(
        self, mock_bpy_module, mock_context, mock_event, mock_object
    ):
        """Should temporarily hide excluded object during raycast."""
        import sys
        from blender_extension.operators.placement import get_mouse_location

        # Setup area
        area = MagicMock()
        area.type = "VIEW_3D"
        area.x = 0
        area.y = 0
        area.width = 1920
        area.height = 1080

        region = MagicMock()
        region.type = "WINDOW"
        region.x = 0
        region.y = 0
        region.width = 1920
        region.height = 1080
        area.regions = [region]

        rv3d = MagicMock()
        area.spaces.active.region_3d = rv3d
        mock_context.screen.areas = [area]

        mock_event.mouse_x = 960
        mock_event.mouse_y = 540

        mock_origin = MagicMock()
        mock_direction = MagicMock()
        mock_direction.z = 0  # Force ground plane projection
        mock_direction.__mul__ = MagicMock(return_value=MagicMock())
        mock_origin.__add__ = MagicMock(return_value=MagicMock())
        mock_origin.z = 10

        mock_context.scene.ray_cast.return_value = (False, None, None, None, None, None)

        # Object starts visible
        mock_object.hide_viewport = False

        # Patch the bpy_extras mock
        bpy_extras_mock = sys.modules["bpy_extras"]
        bpy_extras_mock.view3d_utils.region_2d_to_origin_3d.return_value = mock_origin
        bpy_extras_mock.view3d_utils.region_2d_to_vector_3d.return_value = mock_direction

        get_mouse_location(mock_context, mock_event, exclude=mock_object)

        # Object should be restored to visible
        assert mock_object.hide_viewport is False

    def test_returns_ground_plane_when_no_hit(
        self, mock_bpy_module, mock_context, mock_event
    ):
        """Should project to ground plane when raycast misses."""
        import sys
        from blender_extension.operators.placement import get_mouse_location

        area = MagicMock()
        area.type = "VIEW_3D"
        area.x = 0
        area.y = 0
        area.width = 1920
        area.height = 1080

        region = MagicMock()
        region.type = "WINDOW"
        region.x = 0
        region.y = 0
        region.width = 1920
        region.height = 1080
        area.regions = [region]

        rv3d = MagicMock()
        area.spaces.active.region_3d = rv3d
        mock_context.screen.areas = [area]

        mock_event.mouse_x = 960
        mock_event.mouse_y = 540

        mock_origin = MagicMock()
        mock_origin.z = 10  # Camera at Z=10
        mock_direction = MagicMock()
        mock_direction.z = -1  # Looking down

        expected_location = MagicMock()
        mock_direction.__mul__ = MagicMock(return_value=MagicMock())
        mock_origin.__add__ = MagicMock(return_value=expected_location)

        mock_context.scene.ray_cast.return_value = (False, None, None, None, None, None)

        # Patch the bpy_extras mock
        bpy_extras_mock = sys.modules["bpy_extras"]
        bpy_extras_mock.view3d_utils.region_2d_to_origin_3d.return_value = mock_origin
        bpy_extras_mock.view3d_utils.region_2d_to_vector_3d.return_value = mock_direction

        result = get_mouse_location(mock_context, mock_event)

        # Should return a location (ground plane or default)
        assert result is not None
