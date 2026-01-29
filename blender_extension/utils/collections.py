"""Collection tree traversal utilities.

This module provides functions for traversing and querying Blender's
collection hierarchy, building tree representations, and finding
collection paths for objects.

Manual Test Checklist (Blender Python Console):
-----------------------------------------------
1. Test get_collection_objects_recursive:
   >>> from blender_extension.utils.collections import get_collection_objects_recursive
   >>> import bpy
   >>> col = bpy.context.scene.collection
   >>> objects = list(get_collection_objects_recursive(col))
   >>> print(f"Found {len(objects)} objects")

2. Test build_collection_tree:
   >>> from blender_extension.utils.collections import build_collection_tree
   >>> import bpy
   >>> tree = build_collection_tree(bpy.context.scene)
   >>> print(f"Root: {tree.name}")
   >>> print(f"Children: {list(tree.children.keys())}")

3. Test get_collection_path:
   >>> from blender_extension.utils.collections import get_collection_path
   >>> import bpy
   >>> obj = bpy.context.object
   >>> if obj:
   ...     path = get_collection_path(obj)
   ...     print(f"Collection path: {' > '.join(path)}")

4. Test find_parent_collection:
   >>> from blender_extension.utils.collections import find_parent_collection
   >>> import bpy
   >>> root = bpy.context.scene.collection
   >>> child = list(root.children)[0] if root.children else None
   >>> if child:
   ...     parent = find_parent_collection(root, child)
   ...     print(f"Parent of '{child.name}': {parent.name if parent else 'None'}")
"""

from __future__ import annotations

from collections.abc import Generator

import bpy

from blender_extension.core.data import CollectionNode


def get_collection_objects_recursive(
    collection: bpy.types.Collection,
) -> Generator[bpy.types.Object]:
    """Iterate all objects in a collection hierarchy.

    Recursively traverses the collection and all its child collections,
    yielding each object encountered.

    Args:
        collection: Root collection to traverse.

    Yields:
        All objects in the collection and its children.

    Example:
        >>> import bpy
        >>> col = bpy.context.scene.collection
        >>> for obj in get_collection_objects_recursive(col):
        ...     print(obj.name)
    """
    yield from collection.objects

    for child in collection.children:
        yield from get_collection_objects_recursive(child)


def build_collection_tree(scene: bpy.types.Scene) -> CollectionNode:
    """Build a CollectionNode tree from scene collections.

    Creates a tree structure mirroring Blender's collection hierarchy,
    with each node containing its direct mesh object references.

    Args:
        scene: Blender scene to build tree from.

    Returns:
        Root CollectionNode representing the scene collection.

    Example:
        >>> import bpy
        >>> tree = build_collection_tree(bpy.context.scene)
        >>> print(tree.to_dict())
    """

    def build_node(collection: bpy.types.Collection) -> CollectionNode:
        node = CollectionNode(
            name=collection.name,
            children={},
            instance_ids=[],
        )

        # Add direct object references
        for obj in collection.objects:
            if obj.type == "MESH":
                node.instance_ids.append(obj.name)

        # Recurse into children
        for child in collection.children:
            node.children[child.name] = build_node(child)

        return node

    return build_node(scene.collection)


def get_collection_path(obj: bpy.types.Object) -> list[str]:
    """Get the collection hierarchy path for an object.

    Returns the path from the root scene collection to the object's
    direct parent collection. If an object is in multiple collections,
    uses the first one.

    Args:
        obj: Blender object to find path for.

    Returns:
        List of collection names from root to direct parent.
        Empty list if object is not in any collection.

    Example:
        >>> import bpy
        >>> obj = bpy.context.object
        >>> path = get_collection_path(obj)
        >>> print(" > ".join(path))
        'Scene Collection > Island_01 > Vegetation > Trees'
    """
    if not obj.users_collection:
        return []

    # Use first collection (objects can be in multiple)
    collection = obj.users_collection[0]

    # Walk up the hierarchy
    path = [collection.name]
    current = collection

    # Find parent collections by searching through scenes
    for scene in bpy.data.scenes:
        parent = find_parent_collection(scene.collection, current)
        while parent:
            path.insert(0, parent.name)
            current = parent
            parent = find_parent_collection(scene.collection, current)
        if len(path) > 1:
            break

    return path


def find_parent_collection(
    root: bpy.types.Collection,
    target: bpy.types.Collection,
) -> bpy.types.Collection | None:
    """Find the parent of a collection in a hierarchy.

    Searches the collection tree starting from root to find which
    collection contains target as a direct child.

    Args:
        root: Root collection to search from.
        target: Collection to find parent of.

    Returns:
        Parent collection, or None if target is root or not found.

    Example:
        >>> import bpy
        >>> root = bpy.context.scene.collection
        >>> child = root.children[0]
        >>> parent = find_parent_collection(root, child)
        >>> print(parent.name)  # Should be same as root.name
    """
    for child in root.children:
        if child == target:
            return root
        result = find_parent_collection(child, target)
        if result:
            return result
    return None
