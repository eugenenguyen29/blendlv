from __future__ import annotations

import bpy
from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d
from mathutils import Vector


def get_view3d_region(
    context: bpy.types.Context,
) -> tuple[bpy.types.Region, bpy.types.RegionView3D] | None:
    """Find the main 3D View region and region_data.

    When called from contexts like Asset Shelf, context.region_data is None.
    This function manually searches for the 3D View region.

    Returns:
        Tuple of (region, region_data) or None if not found.
    """
    # Try context first (works in normal 3D View context)
    if context.region and context.region.type == "WINDOW" and context.region_data:
        return context.region, context.region_data

    # Search for 3D View in screen areas
    for area in context.screen.areas:
        if area.type == "VIEW_3D":
            for region in area.regions:
                if region.type == "WINDOW":
                    # Get region_data from space_data
                    space = area.spaces.active
                    if space and hasattr(space, "region_3d"):
                        return region, space.region_3d
    return None


def raycast_from_mouse(
    context: bpy.types.Context,
    event: bpy.types.Event,
    terrain_only: bool = False,
) -> tuple[bool, Vector | None, Vector | None, bpy.types.Object | None]:
    """Cast ray from mouse position to scene surfaces.

    Args:
        context: Blender context.
        event: Mouse event with position data.
        terrain_only: If True, only hit objects with entity_type='TERRAIN'.

    Returns:
        Tuple of (hit, location, normal, object).
        If no hit, returns (False, None, None, None).
    """
    view3d = get_view3d_region(context)
    if view3d is None:
        return False, None, None, None

    region, region_data = view3d

    # Calculate mouse coordinates relative to region
    mouse_pos = (event.mouse_x - region.x, event.mouse_y - region.y)

    # Get ray origin and direction
    ray_origin = region_2d_to_origin_3d(region, region_data, mouse_pos)
    ray_direction = region_2d_to_vector_3d(region, region_data, mouse_pos)

    if ray_origin is None or ray_direction is None:
        return False, None, None, None

    # Get depsgraph for evaluated scene
    depsgraph = context.evaluated_depsgraph_get()

    # Perform raycast
    hit, location, normal, _, obj, _ = context.scene.ray_cast(
        depsgraph, ray_origin, ray_direction
    )

    if not hit:
        return False, None, None, None

    # Filter for terrain if requested
    if terrain_only and obj is not None:
        # Get the original (non-evaluated) object for property access
        original_obj = obj.original if hasattr(obj, "original") else obj
        entity_type = getattr(original_obj, "trivesta_entity_type", None)
        if entity_type != "TERRAIN":
            return False, None, None, None

    return hit, location, normal, obj
