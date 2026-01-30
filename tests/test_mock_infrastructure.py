"""Tests to verify the mock infrastructure works correctly."""

from __future__ import annotations

from unittest.mock import MagicMock


def test_bpy_mock_available(mock_bpy_module: MagicMock) -> None:
    """Verify bpy module is mocked and importable."""
    import bpy

    assert bpy is not None
    assert hasattr(bpy, "types")
    assert hasattr(bpy, "props")
    assert hasattr(bpy, "data")
    assert hasattr(bpy, "ops")


def test_bpy_types_available(mock_bpy_module: MagicMock) -> None:
    """Verify bpy.types has expected types."""
    import bpy

    assert hasattr(bpy.types, "Object")
    assert hasattr(bpy.types, "Operator")
    assert hasattr(bpy.types, "Context")
    assert hasattr(bpy.types, "Event")
    assert hasattr(bpy.types, "AssetShelf")


def test_bpy_props_return_tuples(mock_bpy_module: MagicMock) -> None:
    """Verify bpy.props functions return tuples."""
    import bpy

    result = bpy.props.IntProperty(name="Test", default=0)
    assert isinstance(result, tuple)
    assert result[0] == "IntProperty"


def test_mathutils_available(mock_bpy_module: MagicMock) -> None:
    """Verify mathutils module is mocked."""
    import mathutils

    vec = mathutils.Vector((1.0, 2.0, 3.0))
    assert vec.x == 1.0
    assert vec.y == 2.0
    assert vec.z == 3.0


def test_mathutils_vector_operations(mock_bpy_module: MagicMock) -> None:
    """Verify Vector math operations work."""
    import mathutils

    v1 = mathutils.Vector((1.0, 0.0, 0.0))
    v2 = mathutils.Vector((0.0, 1.0, 0.0))

    v3 = v1 + v2
    assert v3.x == 1.0
    assert v3.y == 1.0

    v4 = v1 * 2.0
    assert v4.x == 2.0


def test_context_mock_has_scene(mock_context: MagicMock) -> None:
    """Verify context mock has scene."""
    assert mock_context.scene is not None
    assert mock_context.scene.cursor is not None


def test_context_mock_has_3d_view(mock_context: MagicMock) -> None:
    """Verify context has 3D view area."""
    assert mock_context.screen.areas
    assert any(a.type == "VIEW_3D" for a in mock_context.screen.areas)


def test_context_mock_has_depsgraph(mock_context: MagicMock) -> None:
    """Verify context has depsgraph getter."""
    depsgraph = mock_context.evaluated_depsgraph_get()
    assert depsgraph is not None


def test_event_mock_has_position(mock_event: MagicMock) -> None:
    """Verify event mock has mouse position."""
    assert mock_event.mouse_x == 960
    assert mock_event.mouse_y == 540
    assert mock_event.type == "MOUSEMOVE"


def test_event_factory(mock_event_factory) -> None:
    """Verify event factory creates custom events."""
    event = mock_event_factory(
        event_type="LEFTMOUSE",
        value="PRESS",
        mouse_x=100,
        mouse_y=200,
    )
    assert event.type == "LEFTMOUSE"
    assert event.value == "PRESS"
    assert event.mouse_x == 100
    assert event.mouse_y == 200


def test_object_mock_has_properties(mock_object: MagicMock) -> None:
    """Verify object mock has expected properties."""
    assert mock_object.name == "MockObject"
    assert mock_object.location is not None
    assert mock_object.hide_viewport is False


def test_object_mock_copy(mock_object: MagicMock) -> None:
    """Verify object mock copy creates new object."""
    copy = mock_object.copy()
    assert copy is not None
    assert copy.name.endswith(".001")


def test_linked_object_has_library(mock_linked_object: MagicMock) -> None:
    """Verify linked object has library reference."""
    assert mock_linked_object.library is not None
    assert mock_linked_object.library.filepath == "/path/to/library.blend"


def test_context_with_asset_library(
    mock_context_with_asset_library: MagicMock,
) -> None:
    """Verify context with asset library has library configured."""
    libs = mock_context_with_asset_library.preferences.filepaths.asset_libraries
    assert len(libs) == 1
    assert libs[0].name == "Test Assets"
