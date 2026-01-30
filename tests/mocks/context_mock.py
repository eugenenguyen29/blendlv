"""Blender context mock factory for testing.

Provides configurable context mocks that simulate Blender's context
object with scene, view layer, 3D view areas, regions, and more.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    pass


def create_region_mock(
    region_type: str = "WINDOW",
    x: int = 0,
    y: int = 0,
    width: int = 1920,
    height: int = 1080,
) -> MagicMock:
    """Create a mock Region object.

    Args:
        region_type: Region type (WINDOW, HEADER, TOOLS, etc.)
        x: Region x position
        y: Region y position
        width: Region width
        height: Region height

    Returns:
        Configured MagicMock for bpy.types.Region
    """
    region = MagicMock()
    region.type = region_type
    region.x = x
    region.y = y
    region.width = width
    region.height = height
    return region


def create_region_view3d_mock(
    view_perspective: str = "PERSP",
    view_location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    view_distance: float = 10.0,
) -> MagicMock:
    """Create a mock RegionView3D object.

    Args:
        view_perspective: PERSP, ORTHO, or CAMERA
        view_location: 3D cursor location
        view_distance: View distance from pivot

    Returns:
        Configured MagicMock for bpy.types.RegionView3D
    """
    rv3d = MagicMock()
    rv3d.view_perspective = view_perspective
    rv3d.view_location = MagicMock()
    rv3d.view_location.x = view_location[0]
    rv3d.view_location.y = view_location[1]
    rv3d.view_location.z = view_location[2]
    rv3d.view_distance = view_distance
    rv3d.view_matrix = MagicMock()
    rv3d.perspective_matrix = MagicMock()
    return rv3d


def create_area_mock(
    area_type: str = "VIEW_3D",
    x: int = 0,
    y: int = 0,
    width: int = 1920,
    height: int = 1080,
    include_regions: bool = True,
) -> MagicMock:
    """Create a mock Area object.

    Args:
        area_type: Area type (VIEW_3D, PROPERTIES, OUTLINER, etc.)
        x: Area x position
        y: Area y position
        width: Area width
        height: Area height
        include_regions: Whether to include mock regions

    Returns:
        Configured MagicMock for bpy.types.Area
    """
    area = MagicMock()
    area.type = area_type
    area.x = x
    area.y = y
    area.width = width
    area.height = height
    area.tag_redraw = MagicMock()

    if include_regions:
        # Create standard regions for a 3D view
        window_region = create_region_mock(
            region_type="WINDOW",
            x=x + 50,  # Account for toolbar
            y=y + 30,  # Account for header
            width=width - 50,
            height=height - 60,
        )
        header_region = create_region_mock(
            region_type="HEADER",
            x=x,
            y=y + height - 30,
            width=width,
            height=30,
        )
        tools_region = create_region_mock(
            region_type="TOOLS",
            x=x,
            y=y + 30,
            width=50,
            height=height - 60,
        )
        area.regions = [header_region, tools_region, window_region]
    else:
        area.regions = []

    # SpaceView3D with region_3d
    space = MagicMock()
    space.type = area_type
    space.region_3d = create_region_view3d_mock()
    area.spaces = MagicMock()
    area.spaces.active = space

    return area


def create_scene_mock(name: str = "Scene") -> MagicMock:
    """Create a mock Scene object.

    Args:
        name: Scene name

    Returns:
        Configured MagicMock for bpy.types.Scene
    """
    scene = MagicMock()
    scene.name = name

    # 3D cursor
    scene.cursor = MagicMock()
    scene.cursor.location = MagicMock()
    scene.cursor.location.x = 0.0
    scene.cursor.location.y = 0.0
    scene.cursor.location.z = 0.0
    scene.cursor.location.copy = MagicMock(return_value=MagicMock(x=0.0, y=0.0, z=0.0))

    # Ray casting returns (hit, location, normal, face_index, object, matrix)
    scene.ray_cast = MagicMock(return_value=(False, None, None, -1, None, None))

    return scene


def create_collection_mock(name: str = "Collection") -> MagicMock:
    """Create a mock Collection object.

    Args:
        name: Collection name

    Returns:
        Configured MagicMock for bpy.types.Collection
    """
    collection = MagicMock()
    collection.name = name
    collection.objects = MagicMock()
    collection.objects.link = MagicMock()
    collection.objects.unlink = MagicMock()
    collection.children = MagicMock()
    return collection


def create_view_layer_mock(name: str = "ViewLayer") -> MagicMock:
    """Create a mock ViewLayer object.

    Args:
        name: View layer name

    Returns:
        Configured MagicMock for bpy.types.ViewLayer
    """
    view_layer = MagicMock()
    view_layer.name = name
    view_layer.objects = MagicMock()
    view_layer.objects.active = None
    view_layer.active_layer_collection = MagicMock()
    return view_layer


def create_window_mock() -> MagicMock:
    """Create a mock Window object.

    Returns:
        Configured MagicMock for bpy.types.Window
    """
    window = MagicMock()
    window.cursor_set = MagicMock()
    window.cursor_modal_set = MagicMock()
    window.cursor_modal_restore = MagicMock()
    return window


def create_window_manager_mock() -> MagicMock:
    """Create a mock WindowManager object.

    Returns:
        Configured MagicMock for bpy.types.WindowManager
    """
    wm = MagicMock()
    wm.modal_handler_add = MagicMock(return_value=True)
    wm.invoke_props_popup = MagicMock()
    wm.invoke_props_dialog = MagicMock()
    return wm


def create_screen_mock(has_3d_view: bool = True) -> MagicMock:
    """Create a mock Screen object.

    Args:
        has_3d_view: Whether to include a 3D view area

    Returns:
        Configured MagicMock for bpy.types.Screen
    """
    screen = MagicMock()

    areas = []
    if has_3d_view:
        areas.append(create_area_mock(area_type="VIEW_3D"))

    screen.areas = areas
    return screen


def create_context_mock(
    mode: str = "OBJECT",
    has_3d_view: bool = True,
    mouse_in_region: bool = True,
) -> MagicMock:
    """Create a fully configured Blender context mock.

    Args:
        mode: Blender mode (OBJECT, EDIT_MESH, SCULPT, etc.)
        has_3d_view: Whether to include a 3D view in screen.areas
        mouse_in_region: Whether mouse position is within 3D view region

    Returns:
        Configured MagicMock simulating bpy.types.Context
    """
    context = MagicMock()
    context.mode = mode

    # Scene
    context.scene = create_scene_mock()

    # Collection
    context.collection = create_collection_mock()

    # View layer
    context.view_layer = create_view_layer_mock()

    # Window
    context.window = create_window_mock()

    # Window manager
    context.window_manager = create_window_manager_mock()

    # Screen with areas
    context.screen = create_screen_mock(has_3d_view=has_3d_view)

    # Current area (may be 3D view or something else)
    if has_3d_view and context.screen.areas:
        context.area = context.screen.areas[0]
    else:
        context.area = create_area_mock(area_type="PROPERTIES")

    # Region within current area
    if context.area and context.area.regions:
        # Find WINDOW region
        for region in context.area.regions:
            if region.type == "WINDOW":
                context.region = region
                break
        else:
            context.region = context.area.regions[0]
    else:
        context.region = create_region_mock()

    # Region data (only valid in 3D view context)
    if has_3d_view:
        context.region_data = create_region_view3d_mock()
    else:
        context.region_data = None

    # Space data
    if context.area:
        context.space_data = context.area.spaces.active
    else:
        context.space_data = MagicMock()
        context.space_data.type = "VIEW_3D" if has_3d_view else "PROPERTIES"

    # Depsgraph
    depsgraph = MagicMock()
    context.evaluated_depsgraph_get = MagicMock(return_value=depsgraph)

    # Selected objects
    context.selected_objects = []
    context.active_object = None

    # Preferences
    context.preferences = MagicMock()
    context.preferences.filepaths = MagicMock()
    context.preferences.filepaths.asset_libraries = []

    return context
