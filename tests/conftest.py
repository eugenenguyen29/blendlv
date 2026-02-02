"""Pytest fixtures for Blender extension testing.

Provides fixtures that mock bpy module and related Blender APIs,
allowing unit tests to run without Blender runtime.
"""

from __future__ import annotations

import sys
from collections.abc import Generator
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

# Import mocks - these must be imported before any blender_extension imports
from tests.mocks.bpy_mock import (
    create_bpy_extras_mock,
    create_bpy_mock,
    create_mathutils_mock,
)
from tests.mocks.context_mock import create_context_mock
from tests.mocks.event_mock import create_event_mock

if TYPE_CHECKING:
    pass


# --- Early module patching via pytest hooks ---
# This runs before test collection, ensuring bpy is mocked before any imports

_bpy_mock = None
_mathutils_mock = None
_bpy_extras_mock = None


def pytest_configure(config):
    """Patch sys.modules with bpy mocks before test collection."""
    global _bpy_mock, _mathutils_mock, _bpy_extras_mock

    _bpy_mock = create_bpy_mock()
    _mathutils_mock = create_mathutils_mock()
    _bpy_extras_mock = create_bpy_extras_mock()

    # Patch bpy and all its submodules
    sys.modules["bpy"] = _bpy_mock
    sys.modules["bpy.types"] = _bpy_mock.types
    sys.modules["bpy.props"] = _bpy_mock.props
    sys.modules["bpy.data"] = _bpy_mock.data
    sys.modules["bpy.ops"] = _bpy_mock.ops
    sys.modules["bpy.context"] = _bpy_mock.context
    sys.modules["bpy.utils"] = _bpy_mock.utils
    sys.modules["bpy.app"] = _bpy_mock.app
    sys.modules["mathutils"] = _mathutils_mock
    sys.modules["bpy_extras"] = _bpy_extras_mock
    sys.modules["bpy_extras.view3d_utils"] = _bpy_extras_mock.view3d_utils


def pytest_unconfigure(config):
    """Clean up mocked modules after tests."""
    module_names = [
        "bpy",
        "bpy.types",
        "bpy.props",
        "bpy.data",
        "bpy.ops",
        "bpy.context",
        "bpy.utils",
        "bpy.app",
        "mathutils",
        "bpy_extras",
        "bpy_extras.view3d_utils",
    ]
    for mod_name in module_names:
        if mod_name in sys.modules:
            del sys.modules[mod_name]


@pytest.fixture(autouse=True)
def mock_bpy_module() -> Generator[MagicMock]:
    """Provide access to the bpy mock for test configuration.

    The actual sys.modules patching is done in pytest_configure hook
    so it happens before any imports. This fixture provides access
    to the mock for tests that need to configure it.

    Yields:
        The bpy mock object for additional configuration if needed.
    """
    global _bpy_mock
    assert _bpy_mock is not None  # Ensure mock was initialized in pytest_configure
    # Reset mocks between tests to ensure isolation
    _bpy_mock.context.preferences.filepaths.asset_libraries = []
    _bpy_mock.data.objects.__iter__ = MagicMock(return_value=iter([]))
    yield _bpy_mock


@pytest.fixture
def mock_context() -> MagicMock:
    """Create a default Blender context mock.

    Returns:
        Configured context mock in OBJECT mode with 3D view.
    """
    return create_context_mock(mode="OBJECT", has_3d_view=True, mouse_in_region=True)


@pytest.fixture
def mock_context_edit_mode() -> MagicMock:
    """Create a context mock in EDIT mode.

    Returns:
        Configured context mock in EDIT_MESH mode.
    """
    return create_context_mock(mode="EDIT_MESH", has_3d_view=True, mouse_in_region=True)


@pytest.fixture
def mock_context_no_3d_view() -> MagicMock:
    """Create a context mock without 3D view.

    Returns:
        Configured context mock without 3D view area.
    """
    return create_context_mock(mode="OBJECT", has_3d_view=False, mouse_in_region=False)


@pytest.fixture
def mock_event() -> MagicMock:
    """Create a default mouse move event mock.

    Returns:
        Configured event mock for MOUSEMOVE at screen center.
    """
    return create_event_mock(
        event_type="MOUSEMOVE",
        value="NOTHING",
        mouse_x=960,
        mouse_y=540,
    )


@pytest.fixture
def mock_event_factory():
    """Factory fixture for creating custom event mocks.

    Returns:
        The create_event_mock function for flexible event creation.
    """
    return create_event_mock


@pytest.fixture
def mock_object() -> MagicMock:
    """Create a mock Blender object.

    Returns:
        Configured MagicMock simulating bpy.types.Object with
        common properties like name, location, hide_viewport.
    """
    obj = MagicMock()
    obj.name = "MockObject"
    obj.type = "MESH"

    # Location as mock with xyz attributes
    obj.location = MagicMock()
    obj.location.x = 0.0
    obj.location.y = 0.0
    obj.location.z = 0.0
    obj.location.copy = MagicMock(return_value=MagicMock(x=0.0, y=0.0, z=0.0))

    # Rotation
    obj.rotation_euler = MagicMock()
    obj.rotation_euler.x = 0.0
    obj.rotation_euler.y = 0.0
    obj.rotation_euler.z = 0.0

    # Scale
    obj.scale = MagicMock()
    obj.scale.x = 1.0
    obj.scale.y = 1.0
    obj.scale.z = 1.0

    # Visibility
    obj.hide_viewport = False
    obj.hide_render = False
    obj.hide_select = False

    # Selection
    obj.select_set = MagicMock()
    obj.select_get = MagicMock(return_value=False)

    # Library link info
    obj.library = None

    # Copy method for instancing
    def copy_obj():
        new_obj = MagicMock()
        new_obj.name = f"{obj.name}.001"
        new_obj.type = obj.type
        new_obj.location = MagicMock()
        new_obj.location.x = obj.location.x
        new_obj.location.y = obj.location.y
        new_obj.location.z = obj.location.z
        new_obj.hide_viewport = obj.hide_viewport
        new_obj.select_set = MagicMock()
        new_obj.library = None
        return new_obj

    obj.copy = MagicMock(side_effect=copy_obj)

    # Data (mesh, curve, etc.)
    obj.data = MagicMock()
    obj.data.name = "MockMesh"

    # Custom properties
    obj.get = MagicMock(return_value=None)
    obj.__getitem__ = MagicMock(side_effect=KeyError)
    obj.__setitem__ = MagicMock()

    return obj


@pytest.fixture
def mock_linked_object(mock_object: MagicMock) -> MagicMock:
    """Create a mock linked (library) object.

    Args:
        mock_object: Base object mock to extend.

    Returns:
        Object mock with library reference set.
    """
    mock_object.library = MagicMock()
    mock_object.library.filepath = "/path/to/library.blend"
    mock_object.library.name = "library.blend"
    return mock_object


@pytest.fixture
def mock_asset_library() -> MagicMock:
    """Create a mock asset library entry.

    Returns:
        Mock asset library with name and path.
    """
    lib = MagicMock()
    lib.name = "Test Assets"
    lib.path = "/tmp/test_assets"
    return lib


@pytest.fixture
def mock_context_with_asset_library(
    mock_context: MagicMock,
    mock_asset_library: MagicMock,
) -> MagicMock:
    """Create a context mock with asset library configured.

    Args:
        mock_context: Base context mock.
        mock_asset_library: Asset library mock.

    Returns:
        Context with asset library in preferences.
    """
    mock_context.preferences.filepaths.asset_libraries = [mock_asset_library]
    return mock_context
