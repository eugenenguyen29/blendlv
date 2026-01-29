"""Island detection and coordinate utilities.

This module provides functions for detecting island collections in Blender
scenes and computing their bounds and origins for export to Three.js.

Islands are identified by convention: top-level collections starting with
"Island_" are treated as separate island chunks in the game world.

Manual Test Checklist (Blender Python Console):
-----------------------------------------------
1. Test detect_islands (requires Island_* collections in scene):
   >>> from blender_extension.utils.islands import detect_islands
   >>> import bpy
   >>> islands = detect_islands(bpy.context.scene)
   >>> print(f"Found {len(islands)} islands")
   >>> for island_id, island in islands.items():
   ...     print(f"  {island_id}: {len(island.instances)} objects")

2. Test get_collection_origin:
   >>> from blender_extension.utils.islands import get_collection_origin
   >>> import bpy
   >>> col = bpy.data.collections.get("Island_01")
   >>> if col:
   ...     origin = get_collection_origin(col)
   ...     print(f"Origin: {origin}")

3. Test calculate_collection_bounds:
   >>> from blender_extension.utils.islands import calculate_collection_bounds
   >>> import bpy
   >>> col = bpy.data.collections.get("Island_01")
   >>> if col:
   ...     bounds = calculate_collection_bounds(col)
   ...     print(f"Bounds: {bounds}")

4. Test to_local_coords:
   >>> from blender_extension.utils.islands import to_local_coords, detect_islands
   >>> import bpy
   >>> islands = detect_islands(bpy.context.scene)
   >>> if islands:
   ...     island = list(islands.values())[0]
   ...     local = to_local_coords((10.0, 5.0, -3.0), island)
   ...     print(f"Local coords: {local}")
"""

import bpy
from mathutils import Vector

from blender_extension.core.data import BoundingBox, Island
from blender_extension.utils.collections import get_collection_objects_recursive
from blender_extension.utils.naming import sanitize_name


def detect_islands(scene: bpy.types.Scene) -> dict[str, Island]:
    """Detect islands from Blender collections.

    Convention: Top-level collections starting with 'Island_' are islands.
    Each island represents a self-contained chunk of the game world.

    Args:
        scene: Blender scene to scan.

    Returns:
        Dict mapping island_id to Island dataclass.

    Example:
        >>> import bpy
        >>> islands = detect_islands(bpy.context.scene)
        >>> for island_id, island in islands.items():
        ...     print(f"{island_id}: {island.name}")
    """
    islands = {}

    for collection in scene.collection.children:
        if not collection.name.startswith("Island_"):
            continue

        island_id = sanitize_name(collection.name)
        origin = get_collection_origin(collection)
        bounds = calculate_collection_bounds(collection)

        island = Island(
            id=island_id,
            name=collection.name,
            world_position=origin,
            world_rotation=(0.0, 0.0, 0.0, 1.0),  # Identity quaternion
            bounds=bounds,
            instances=[],
            terrain_objects=[],
            collision_mesh=None,
        )

        # Collect instance IDs
        for obj in get_collection_objects_recursive(collection):
            if obj.type == "MESH":
                island.instances.append(obj.name)

        islands[island_id] = island

    return islands


def get_collection_origin(
    collection: bpy.types.Collection,
) -> tuple[float, float, float]:
    """Get island origin from collection.

    Detection order:
    1. Empty object named '{collection.name}_Origin' or ending with '_Origin'
    2. Center of bounding box of all mesh objects

    Args:
        collection: Blender collection to find origin for.

    Returns:
        Origin position as (x, y, z) tuple in Three.js coordinates.
    """
    # Look for explicit origin marker
    for obj in collection.objects:
        if obj.type == "EMPTY" and obj.name.endswith("_Origin"):
            loc = obj.matrix_world.to_translation()
            return (loc.x, loc.z, -loc.y)  # Convert to Three.js coords

    # Fallback: calculate center of bounds
    all_objects = list(get_collection_objects_recursive(collection))
    if not all_objects:
        return (0.0, 0.0, 0.0)

    min_pos = Vector((float("inf"), float("inf"), float("inf")))
    max_pos = Vector((float("-inf"), float("-inf"), float("-inf")))

    has_mesh = False
    for obj in all_objects:
        if obj.type != "MESH":
            continue
        has_mesh = True
        loc = obj.matrix_world.to_translation()
        min_pos.x = min(min_pos.x, loc.x)
        min_pos.y = min(min_pos.y, loc.y)
        min_pos.z = min(min_pos.z, loc.z)
        max_pos.x = max(max_pos.x, loc.x)
        max_pos.y = max(max_pos.y, loc.y)
        max_pos.z = max(max_pos.z, loc.z)

    if not has_mesh:
        return (0.0, 0.0, 0.0)

    center = (min_pos + max_pos) / 2
    return (center.x, center.z, -center.y)


def calculate_collection_bounds(collection: bpy.types.Collection) -> BoundingBox:
    """Calculate bounding box for all objects in a collection.

    Computes the axis-aligned bounding box that encompasses all mesh
    objects in the collection hierarchy.

    Args:
        collection: Blender collection to compute bounds for.

    Returns:
        Dict with 'min', 'max' (coordinate lists), and 'radius' (float)
        in Three.js coordinates.
    """
    all_objects = list(get_collection_objects_recursive(collection))

    if not all_objects:
        return {"min": [0, 0, 0], "max": [0, 0, 0], "radius": 0}

    min_corner = [float("inf"), float("inf"), float("inf")]
    max_corner = [float("-inf"), float("-inf"), float("-inf")]

    has_mesh = False
    for obj in all_objects:
        if obj.type != "MESH" or obj.data is None:
            continue

        has_mesh = True
        # Get world-space bbox
        for corner in obj.bound_box:
            world_corner = obj.matrix_world @ Vector(corner)
            # Convert to Three.js coordinates
            x, y, z = world_corner.x, world_corner.z, -world_corner.y

            min_corner[0] = min(min_corner[0], x)
            min_corner[1] = min(min_corner[1], y)
            min_corner[2] = min(min_corner[2], z)
            max_corner[0] = max(max_corner[0], x)
            max_corner[1] = max(max_corner[1], y)
            max_corner[2] = max(max_corner[2], z)

    if not has_mesh:
        return {"min": [0, 0, 0], "max": [0, 0, 0], "radius": 0}

    # Calculate radius (distance from center to corner)
    center = [(min_corner[i] + max_corner[i]) / 2 for i in range(3)]
    radius = (
        (max_corner[0] - center[0]) ** 2
        + (max_corner[1] - center[1]) ** 2
        + (max_corner[2] - center[2]) ** 2
    ) ** 0.5

    return {
        "min": min_corner,
        "max": max_corner,
        "radius": round(radius, 2),
    }


def to_local_coords(
    position: tuple[float, float, float],
    island: Island,
) -> tuple[float, float, float]:
    """Convert world position to island-local coordinates.

    Subtracts the island's world position from the given position
    to get coordinates relative to the island origin.

    Args:
        position: World position as (x, y, z) in Three.js coords.
        island: Island to transform relative to.

    Returns:
        Position relative to island origin as (x, y, z) tuple.
    """
    return (
        position[0] - island.world_position[0],
        position[1] - island.world_position[1],
        position[2] - island.world_position[2],
    )


def find_island_for_object(
    obj: bpy.types.Object,
    islands: dict[str, Island],
) -> str | None:
    """Find which island an object belongs to.

    Checks if the object's name is in any island's instance list.

    Args:
        obj: Blender object to find island for.
        islands: Dict of island_id to Island.

    Returns:
        Island ID if found, None otherwise.

    Example:
        >>> import bpy
        >>> from blender_extension.utils.islands import detect_islands, find_island_for_object
        >>> islands = detect_islands(bpy.context.scene)
        >>> obj = bpy.context.object
        >>> island_id = find_island_for_object(obj, islands)
        >>> print(f"Object belongs to: {island_id}")
    """
    for island_id, island in islands.items():
        if obj.name in island.instances:
            return island_id
    return None


def assign_instances_to_islands(
    instances: list,
    islands: dict[str, Island],
) -> dict[str, list]:
    """Assign instances to their parent islands.

    Groups instances by which island collection they belong to.
    Instances not in any island are grouped under a special 'global' key.

    Args:
        instances: List of Instance objects with 'name' attribute.
        islands: Dict of island_id to Island.

    Returns:
        Dict mapping island_id (or 'global') to list of instances.

    Example:
        >>> from blender_extension.utils.islands import detect_islands, assign_instances_to_islands
        >>> from blender_extension.entities import extract_all
        >>> import bpy
        >>> islands = detect_islands(bpy.context.scene)
        >>> instances, _, _ = extract_all(bpy.context)
        >>> grouped = assign_instances_to_islands(instances, islands)
        >>> for island_id, insts in grouped.items():
        ...     print(f"{island_id}: {len(insts)} instances")
    """
    groups: dict[str, list] = {"global": []}

    # Build lookup from object name to island
    name_to_island: dict[str, str] = {}
    for island_id, island in islands.items():
        for obj_name in island.instances:
            name_to_island[obj_name] = island_id

    for inst in instances:
        island_id = name_to_island.get(inst.name)
        if island_id:
            groups.setdefault(island_id, []).append(inst)
        else:
            groups["global"].append(inst)

    return groups


def convert_instances_to_local(
    instances: list,
    islands: dict[str, Island],
) -> list:
    """Convert instance positions to island-local coordinates.

    For each instance that belongs to an island, converts its world
    position to be relative to the island origin. Updates instances
    in-place and returns the modified list.

    Args:
        instances: List of Instance objects with position attribute.
        islands: Dict of island_id to Island.

    Returns:
        The same list with positions converted to local coordinates.

    Note:
        This modifies instances in-place. Make a copy first if you
        need to preserve original world positions.

    Example:
        >>> from blender_extension.utils.islands import convert_instances_to_local
        >>> # instances already have world positions
        >>> convert_instances_to_local(instances, islands)
        >>> # Now positions are relative to island origins
    """
    grouped = assign_instances_to_islands(instances, islands)

    for island_id, insts in grouped.items():
        if island_id == "global":
            continue

        island = islands[island_id]
        for inst in insts:
            inst.position = to_local_coords(inst.position, island)

    return instances
