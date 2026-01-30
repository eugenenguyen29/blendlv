"""Data models for export operations.

This module defines dataclasses that represent export data structures.
These are pure Python dataclasses with no Blender dependencies, making
them easy to test and serialize.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict


class BoundingBox(TypedDict):
    """Bounding box with min/max corners and radius.

    Attributes:
        min: Minimum corner coordinates [x, y, z] in Three.js Y-up space.
        max: Maximum corner coordinates [x, y, z] in Three.js Y-up space.
        radius: Distance from center to furthest corner.
    """

    min: list[float]
    max: list[float]
    radius: float


class CollectionNodeDict(TypedDict):
    """Dictionary representation of a CollectionNode.

    Attributes:
        name: Collection name.
        children: Nested child collection dictionaries.
        instances: List of instance IDs in this collection.
    """

    name: str
    children: dict[str, CollectionNodeDict]
    instances: list[str]


@dataclass
class Instance:
    """Single source of truth for each object instance.

    Attributes:
        id: Unique identifier for this instance.
        name: Display name from Blender object.
        asset_id: Reference to AssetDefinition (None for terrain/unique objects).
        entity_type: Type of game entity (static, npc, interactive, etc.).
        position: World position in Three.js coordinates (x, y, z).
        rotation: Rotation quaternion in Three.js coordinates (x, y, z, w).
        scale: Scale factors (x, y, z).
        bounding_box: Axis-aligned bounding box with min/max corners.
        collection_path: Hierarchy path from root collection.
        custom_properties: Additional user-defined properties.
    """

    id: str
    name: str
    asset_id: str | None
    entity_type: str
    position: tuple[float, float, float]
    rotation: tuple[float, float, float, float]
    scale: tuple[float, float, float]
    bounding_box: BoundingBox
    collection_path: list[str]
    custom_properties: dict[str, object] = field(default_factory=dict)


@dataclass
class AssetDefinition:
    """Unique asset type (geometry shared by instances).

    Attributes:
        id: Unique identifier for this asset.
        file: Relative path to GLB file.
        source: Optional linked library path.
    """

    id: str
    file: str
    source: str | None


@dataclass
class CollectionNode:
    """Tree node mirroring Blender collection hierarchy.

    Attributes:
        name: Collection name.
        children: Child collection nodes keyed by name.
        instance_ids: IDs of instances directly in this collection.
    """

    name: str
    children: dict[str, CollectionNode] = field(default_factory=dict)
    instance_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> CollectionNodeDict:
        """Convert to JSON-serializable dict.

        Returns:
            Dictionary representation with nested children.
        """
        return {
            "name": self.name,
            "children": {k: v.to_dict() for k, v in self.children.items()},
            "instances": self.instance_ids,
        }


@dataclass
class Island:
    """Self-contained island chunk with local coordinate system.

    Attributes:
        id: Unique identifier for this island.
        name: Display name.
        world_position: Position in world coordinates.
        world_rotation: Rotation quaternion in world coordinates.
        bounds: Bounding box of the island.
        instances: List of instance IDs belonging to this island.
        terrain_objects: List of terrain instance IDs.
        collision_mesh: Optional path to collision mesh file.
    """

    id: str
    name: str
    world_position: tuple[float, float, float]
    world_rotation: tuple[float, float, float, float]
    bounds: BoundingBox
    instances: list[str] = field(default_factory=list)
    terrain_objects: list[str] = field(default_factory=list)
    collision_mesh: str | None = None


@dataclass
class WorldMap:
    """Static world layout defining island placements.

    Attributes:
        size: World size (width, height).
        islands: Island definitions keyed by ID.
        water_level: Y coordinate of water surface.
    """

    size: tuple[float, float]
    islands: dict[str, Island] = field(default_factory=dict)
    water_level: float = 0.0


@dataclass
class ExportData:
    """Container for all export data with multiple indices.

    This is the main data structure passed through the export pipeline.
    It contains all instances, asset definitions, and computed indices
    for efficient lookup.

    Attributes:
        asset_definitions: Unique assets keyed by ID.
        instances: All object instances.
        terrain_objects: Instances marked as terrain.
        islands: Island chunks keyed by ID.
        collection_tree: Root of collection hierarchy.
        by_asset_id: Instances grouped by asset ID (computed index).
        by_entity_type: Instances grouped by entity type (computed index).
    """

    asset_definitions: dict[str, AssetDefinition] = field(default_factory=dict)
    instances: list[Instance] = field(default_factory=list)
    terrain_objects: list[Instance] = field(default_factory=list)
    islands: dict[str, Island] = field(default_factory=dict)
    collection_tree: CollectionNode | None = None

    # Computed indices
    by_asset_id: dict[str, list[Instance]] = field(default_factory=dict)
    by_entity_type: dict[str, list[Instance]] = field(default_factory=dict)

    def build_indices(self) -> None:
        """Build lookup indices from instances list.

        Call this after populating the instances list to create
        efficient lookup structures for asset_id and entity_type.
        """
        self.by_asset_id.clear()
        self.by_entity_type.clear()

        for inst in self.instances:
            if inst.asset_id:
                self.by_asset_id.setdefault(inst.asset_id, []).append(inst)
            self.by_entity_type.setdefault(inst.entity_type, []).append(inst)
