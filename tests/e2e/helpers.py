"""Helper functions for E2E tests.

Provides reusable utilities for creating test scenes, collections,
and verifying export results.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import bpy


def create_collection_with_cube(name: str = "TestCollection") -> bpy.types.Collection:
    """Create a collection containing a cube mesh.

    Args:
        name: Name for the collection

    Returns:
        The created collection
    """
    import bpy

    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)

    # Create cube mesh and object directly (more reliable than bpy.ops)
    mesh = bpy.data.meshes.new(f"{name}_Cube_Mesh")
    cube = bpy.data.objects.new(f"{name}_Cube", mesh)
    cube.name = f"{name}_Cube"

    # Create simple cube geometry
    import bmesh

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(mesh)
    bm.free()

    # Link cube to the collection (not scene collection)
    collection.objects.link(cube)

    return collection


def create_collection_instance(
    collection: bpy.types.Collection,
    name: str | None = None,
    location: tuple[float, float, float] = (0, 0, 0),
) -> bpy.types.Object:
    """Create an EMPTY that instances a collection.

    Args:
        collection: The collection to instance
        name: Name for the instance (defaults to collection name + "_Instance")
        location: World location for the instance

    Returns:
        The created instance object
    """
    import bpy

    if name is None:
        name = f"{collection.name}_Instance"

    empty = bpy.data.objects.new(name=name, object_data=None)
    empty.instance_type = "COLLECTION"
    empty.instance_collection = collection
    empty.location = location
    bpy.context.scene.collection.objects.link(empty)

    return empty


def create_empty_collection(name: str = "Empty_Collection") -> bpy.types.Collection:
    """Create an empty collection with no objects.

    Args:
        name: Name for the collection

    Returns:
        The created empty collection
    """
    import bpy

    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)

    return collection
