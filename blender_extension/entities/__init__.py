"""Entity extractor registry and scene extraction.

This module provides the entity extraction system for the Trivesta Level
extension. It implements a registry of extractors that detect and extract
data from Blender objects based on their type.

Architecture:
    - Strategy Pattern: Each extractor is a strategy for handling a specific type
    - First Match Wins: Extractors are checked in priority order (collision > terrain > static)
    - Open/Closed: New entity types added by creating new extractor classes

Extractor Precedence:
    1. CollisionExtractor - Collision meshes (highest priority)
    2. TerrainExtractor - Terrain/ground meshes
    3. StaticExtractor - Default fallback for regular meshes

Manual Test Checklist (Blender Python Console):
-----------------------------------------------
1. Test extractor registration:
   >>> from blender_extension.entities import register_extractors, get_extractor
   >>> import bpy
   >>> register_extractors()
   >>> obj = bpy.context.object
   >>> ext = get_extractor(obj)
   >>> print(f"Matched: {ext.entity_type if ext else 'None'}")

2. Test collision takes precedence:
   >>> from blender_extension.entities import register_extractors, get_extractor
   >>> import bpy
   >>> register_extractors()
   >>> bpy.ops.mesh.primitive_cube_add()
   >>> obj = bpy.context.object
   >>> obj.name = "Wall_collision"
   >>> ext = get_extractor(obj)
   >>> print(f"Type: {ext.entity_type}")  # Should print "collision"

3. Test extract_all:
   >>> from blender_extension.entities import register_extractors, extract_all
   >>> import bpy
   >>> register_extractors()
   >>> instances, terrain, collision = extract_all(bpy.context)
   >>> print(f"Instances: {len(instances)}")
   >>> print(f"Terrain: {len(terrain)}")
   >>> print(f"Collision: {len(collision)}")

4. Test empty scene:
   >>> from blender_extension.entities import register_extractors, extract_all
   >>> import bpy
   >>> bpy.ops.object.select_all(action='SELECT')
   >>> bpy.ops.object.delete()
   >>> register_extractors()
   >>> instances, terrain, collision = extract_all(bpy.context)
   >>> print(len(instances) + len(terrain) + len(collision))  # Should print 0
"""

from __future__ import annotations

import bpy

from blender_extension.core.data import Instance
from blender_extension.entities.base import EntityExtractor
from blender_extension.entities.collision import CollisionExtractor
from blender_extension.entities.static import StaticExtractor
from blender_extension.entities.terrain import TerrainExtractor

# Registry of all extractors (order matters - first match wins)
_extractors: list[EntityExtractor] = []


def register_extractors() -> None:
    """Register default extractors in priority order.

    Must be called before using get_extractor() or extract_all().
    Typically called during extension initialization.

    Extractor Order (first match wins):
        1. CollisionExtractor - Check collision first (highest priority)
        2. TerrainExtractor - Then terrain
        3. StaticExtractor - Default fallback (lowest priority)
    """
    global _extractors
    _extractors = [
        CollisionExtractor(),  # Check collision first
        TerrainExtractor(),  # Then terrain
        StaticExtractor(),  # Default fallback
    ]


def get_extractor(obj: bpy.types.Object) -> EntityExtractor | None:
    """Get the first matching extractor for an object.

    Iterates through registered extractors in priority order,
    returning the first one that matches the object.

    Args:
        obj: Blender object to find extractor for.

    Returns:
        Matching EntityExtractor, or None if no extractor matches.

    Note:
        Call register_extractors() before using this function.
    """
    for extractor in _extractors:
        if extractor.matches(obj):
            return extractor
    return None


def extract_all(
    context: bpy.types.Context,
) -> tuple[list[Instance], list[Instance], list[Instance]]:
    """Extract all visible mesh objects from the scene.

    Iterates through all objects in the scene, finds matching extractors,
    and categorizes extracted instances by type.

    Args:
        context: Blender context with scene to extract from.

    Returns:
        Tuple of (instances, terrain_objects, collision_objects):
        - instances: Static mesh instances and other regular objects
        - terrain_objects: Objects marked as terrain
        - collision_objects: Objects marked as collision meshes

    Note:
        Only visible MESH objects are processed. Hidden objects and
        non-mesh objects (cameras, lights, etc.) are skipped.
    """
    instances: list[Instance] = []
    terrain_objects: list[Instance] = []
    collision_objects: list[Instance] = []

    for obj in context.scene.objects:
        # Skip non-mesh and hidden objects
        if obj.type != "MESH" or not obj.visible_get():
            continue

        extractor = get_extractor(obj)
        if extractor is None:
            continue

        data = extractor.extract(obj)

        # Categorize by entity type
        if extractor.entity_type == "collision":
            collision_objects.append(data)
        elif extractor.entity_type == "terrain":
            terrain_objects.append(data)
        else:
            instances.append(data)

    return instances, terrain_objects, collision_objects


__all__ = [
    # Base class
    "EntityExtractor",
    # Extractor implementations
    "StaticExtractor",
    "TerrainExtractor",
    "CollisionExtractor",
    # Registry functions
    "register_extractors",
    "get_extractor",
    "extract_all",
]
