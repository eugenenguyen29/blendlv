import bpy
from mathutils import Vector


def get_object_transform(obj: bpy.types.Object) -> dict:
    """Extract world transform from a Blender object."""
    loc = obj.matrix_world.to_translation()
    rot = obj.matrix_world.to_quaternion()
    scale = obj.matrix_world.to_scale()

    return {
        "position": [loc.x, loc.z, -loc.y],  # Convert to Three.js coordinate system
        "rotation": [rot.x, rot.z, -rot.y, rot.w],  # Quaternion in Three.js order
        "scale": [scale.x, scale.z, scale.y],
    }


def get_bounding_box(obj: bpy.types.Object) -> dict:
    """Get world-space bounding box of an object."""
    if obj.type != 'MESH' or obj.data is None:
        return {"min": [0, 0, 0], "max": [0, 0, 0]}

    # Get world-space bounding box corners
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

    min_corner = [
        min(c.x for c in bbox_corners),
        min(c.z for c in bbox_corners),  # Blender Z -> Three.js Y
        min(-c.y for c in bbox_corners),  # Blender -Y -> Three.js Z
    ]
    max_corner = [
        max(c.x for c in bbox_corners),
        max(c.z for c in bbox_corners),
        max(-c.y for c in bbox_corners),
    ]

    return {"min": min_corner, "max": max_corner}


def get_custom_properties(obj: bpy.types.Object) -> dict:
    """Extract custom properties from an object, excluding Blender internals."""
    props = {}
    for key in obj.keys():
        if key.startswith("_"):
            continue
        value = obj[key]
        # Convert to JSON-serializable types
        if hasattr(value, "to_list"):
            props[key] = value.to_list()
        elif isinstance(value, (int, float, str, bool)):
            props[key] = value
    return props


def get_library_source(obj: bpy.types.Object) -> str | None:
    """Get the source .blend file path for linked objects."""
    if obj.library:
        return obj.library.filepath
    if obj.data and obj.data.library:
        return obj.data.library.filepath
    # Check if it's an override
    if obj.override_library and obj.override_library.reference:
        ref = obj.override_library.reference
        if ref.library:
            return ref.library.filepath
    return None
