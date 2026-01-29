"""Utility functions for Trivesta Level extension.

This module provides utility functions for transforms, naming, file handling,
island detection, and collection tree traversal.

All coordinates are output in Three.js format (Y-up) unless noted otherwise.
"""

from blender_extension.utils.collections import (
    build_collection_tree,
    find_parent_collection,
    get_collection_objects_recursive,
    get_collection_path,
)
from blender_extension.utils.files import (
    ensure_directory,
    get_export_subdir,
    get_relative_path,
    resolve_path,
)
from blender_extension.utils.islands import (
    assign_instances_to_islands,
    calculate_collection_bounds,
    convert_instances_to_local,
    detect_islands,
    find_island_for_object,
    get_collection_origin,
    to_local_coords,
)
from blender_extension.utils.naming import (
    generate_asset_key,
    generate_instance_id,
    sanitize_name,
)
from blender_extension.utils.raycast import (
    get_view3d_region,
    raycast_from_mouse,
)
from blender_extension.utils.transforms import (
    get_bounding_box,
    get_custom_properties,
    get_library_source,
    get_object_transform,
)

__all__ = [
    # transforms
    "get_object_transform",
    "get_bounding_box",
    "get_custom_properties",
    "get_library_source",
    # naming
    "sanitize_name",
    "generate_asset_key",
    "generate_instance_id",
    # files
    "ensure_directory",
    "resolve_path",
    "get_relative_path",
    "get_export_subdir",
    # islands
    "detect_islands",
    "get_collection_origin",
    "to_local_coords",
    "calculate_collection_bounds",
    "find_island_for_object",
    "assign_instances_to_islands",
    "convert_instances_to_local",
    # collections
    "get_collection_objects_recursive",
    "build_collection_tree",
    "get_collection_path",
    "find_parent_collection",
    # raycast
    "get_view3d_region",
    "raycast_from_mouse",
]
