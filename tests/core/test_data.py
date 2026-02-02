"""Tests for blender_extension.core.data module.

These are pure Python dataclasses with no Blender dependencies.
"""

from __future__ import annotations

import pytest

from blender_extension.core.data import (
    AssetDefinition,
    BoundingBox,
    CollectionNode,
    ExportData,
    Instance,
    Island,
    WorldMap,
)

# --- Fixtures ---


@pytest.fixture
def sample_bounding_box() -> BoundingBox:
    """Create a sample bounding box."""
    return {"min": [0.0, 0.0, 0.0], "max": [1.0, 2.0, 3.0], "radius": 1.87}


@pytest.fixture
def sample_instance(sample_bounding_box: BoundingBox) -> Instance:
    """Create a sample instance with all fields."""
    return Instance(
        id="inst_001",
        name="TestObject",
        asset_id="asset_rock_01",
        entity_type="static",
        position=(10.0, 5.0, 20.0),
        rotation=(0.0, 0.707, 0.0, 0.707),
        scale=(1.0, 1.0, 1.0),
        bounding_box=sample_bounding_box,
        collection_path=["Scene", "Props", "Rocks"],
        custom_properties={"lod_level": 0, "visible": True},
    )


@pytest.fixture
def sample_instance_no_asset(sample_bounding_box: BoundingBox) -> Instance:
    """Create an instance without asset_id (terrain/unique object)."""
    return Instance(
        id="terrain_001",
        name="TerrainChunk",
        asset_id=None,
        entity_type="terrain",
        position=(0.0, 0.0, 0.0),
        rotation=(0.0, 0.0, 0.0, 1.0),
        scale=(1.0, 1.0, 1.0),
        bounding_box=sample_bounding_box,
        collection_path=["Scene", "Terrain"],
    )


# --- BoundingBox Tests ---


class TestBoundingBox:
    """Tests for BoundingBox TypedDict."""

    def test_creation(self) -> None:
        bbox: BoundingBox = {
            "min": [-1.0, -2.0, -3.0],
            "max": [1.0, 2.0, 3.0],
            "radius": 3.74,
        }
        assert bbox["min"] == [-1.0, -2.0, -3.0]
        assert bbox["max"] == [1.0, 2.0, 3.0]
        assert bbox["radius"] == 3.74

    def test_access_individual_coordinates(self) -> None:
        bbox: BoundingBox = {
            "min": [0.0, 1.0, 2.0],
            "max": [3.0, 4.0, 5.0],
            "radius": 2.5,
        }
        assert bbox["min"][0] == 0.0
        assert bbox["max"][2] == 5.0


# --- Instance Tests ---


class TestInstance:
    """Tests for Instance dataclass."""

    def test_creation_with_all_fields(
        self, sample_instance: Instance, sample_bounding_box: BoundingBox
    ) -> None:
        assert sample_instance.id == "inst_001"
        assert sample_instance.name == "TestObject"
        assert sample_instance.asset_id == "asset_rock_01"
        assert sample_instance.entity_type == "static"
        assert sample_instance.position == (10.0, 5.0, 20.0)
        assert sample_instance.rotation == (0.0, 0.707, 0.0, 0.707)
        assert sample_instance.scale == (1.0, 1.0, 1.0)
        assert sample_instance.bounding_box == sample_bounding_box
        assert sample_instance.collection_path == ["Scene", "Props", "Rocks"]
        assert sample_instance.custom_properties == {"lod_level": 0, "visible": True}

    def test_creation_with_none_asset_id(self, sample_instance_no_asset: Instance) -> None:
        assert sample_instance_no_asset.asset_id is None
        assert sample_instance_no_asset.entity_type == "terrain"

    def test_default_custom_properties(self, sample_bounding_box: BoundingBox) -> None:
        inst = Instance(
            id="test",
            name="Test",
            asset_id="asset_01",
            entity_type="static",
            position=(0.0, 0.0, 0.0),
            rotation=(0.0, 0.0, 0.0, 1.0),
            scale=(1.0, 1.0, 1.0),
            bounding_box=sample_bounding_box,
            collection_path=["Scene"],
        )
        assert inst.custom_properties == {}

    def test_bounding_box_access(self, sample_instance: Instance) -> None:
        assert sample_instance.bounding_box["min"] == [0.0, 0.0, 0.0]
        assert sample_instance.bounding_box["max"] == [1.0, 2.0, 3.0]
        assert sample_instance.bounding_box["radius"] == 1.87


# --- AssetDefinition Tests ---


class TestAssetDefinition:
    """Tests for AssetDefinition dataclass."""

    def test_creation_with_source(self) -> None:
        asset = AssetDefinition(
            id="asset_rock_01",
            file="meshes/rocks/rock_01.glb",
            source="//library/rocks.blend",
        )
        assert asset.id == "asset_rock_01"
        assert asset.file == "meshes/rocks/rock_01.glb"
        assert asset.source == "//library/rocks.blend"

    def test_creation_without_source(self) -> None:
        asset = AssetDefinition(
            id="asset_unique_01",
            file="meshes/unique/statue.glb",
            source=None,
        )
        assert asset.source is None


# --- CollectionNode Tests ---


class TestCollectionNode:
    """Tests for CollectionNode dataclass."""

    def test_creation_minimal(self) -> None:
        node = CollectionNode(name="TestCollection")
        assert node.name == "TestCollection"
        assert node.children == {}
        assert node.instance_ids == []

    def test_creation_with_children(self) -> None:
        child = CollectionNode(name="Child", instance_ids=["inst_001"])
        parent = CollectionNode(
            name="Parent",
            children={"Child": child},
            instance_ids=["inst_002"],
        )
        assert "Child" in parent.children
        assert parent.children["Child"].name == "Child"
        assert parent.instance_ids == ["inst_002"]

    def test_to_dict_empty_node(self) -> None:
        node = CollectionNode(name="Empty")
        result = node.to_dict()

        assert result["name"] == "Empty"
        assert result["children"] == {}
        assert result["instances"] == []

    def test_to_dict_with_instances(self) -> None:
        node = CollectionNode(name="Props", instance_ids=["inst_001", "inst_002"])
        result = node.to_dict()

        assert result["name"] == "Props"
        assert result["instances"] == ["inst_001", "inst_002"]

    def test_to_dict_nested_hierarchy(self) -> None:
        # Build a hierarchy: Scene -> Environment -> Rocks
        rocks = CollectionNode(name="Rocks", instance_ids=["rock_001", "rock_002"])
        environment = CollectionNode(
            name="Environment",
            children={"Rocks": rocks},
            instance_ids=["tree_001"],
        )
        scene = CollectionNode(
            name="Scene",
            children={"Environment": environment},
        )

        result = scene.to_dict()

        # Check root level
        assert result["name"] == "Scene"
        assert "Environment" in result["children"]

        # Check nested level
        env_dict = result["children"]["Environment"]
        assert env_dict["name"] == "Environment"
        assert env_dict["instances"] == ["tree_001"]
        assert "Rocks" in env_dict["children"]

        # Check deepest level
        rocks_dict = env_dict["children"]["Rocks"]
        assert rocks_dict["name"] == "Rocks"
        assert rocks_dict["instances"] == ["rock_001", "rock_002"]
        assert rocks_dict["children"] == {}

    def test_to_dict_returns_correct_type(self) -> None:
        node = CollectionNode(name="Test")
        result = node.to_dict()

        # Verify it matches CollectionNodeDict structure
        assert isinstance(result, dict)
        assert "name" in result
        assert "children" in result
        assert "instances" in result


# --- Island Tests ---


class TestIsland:
    """Tests for Island dataclass."""

    def test_creation_minimal(self) -> None:
        bounds: BoundingBox = {
            "min": [-50.0, 0.0, -50.0],
            "max": [50.0, 30.0, 50.0],
            "radius": 70.71,
        }
        island = Island(
            id="island_main",
            name="Main Island",
            world_position=(100.0, 0.0, 200.0),
            world_rotation=(0.0, 0.0, 0.0, 1.0),
            bounds=bounds,
        )

        assert island.id == "island_main"
        assert island.name == "Main Island"
        assert island.world_position == (100.0, 0.0, 200.0)
        assert island.world_rotation == (0.0, 0.0, 0.0, 1.0)
        assert island.bounds == bounds
        assert island.instances == []
        assert island.terrain_objects == []
        assert island.collision_mesh is None

    def test_creation_with_all_fields(self) -> None:
        bounds: BoundingBox = {
            "min": [-10.0, 0.0, -10.0],
            "max": [10.0, 5.0, 10.0],
            "radius": 15.0,
        }
        island = Island(
            id="island_001",
            name="TestIsland",
            world_position=(0.0, 0.0, 0.0),
            world_rotation=(0.0, 0.707, 0.0, 0.707),
            bounds=bounds,
            instances=["inst_001", "inst_002"],
            terrain_objects=["terrain_001"],
            collision_mesh="collision/island_001.glb",
        )

        assert island.instances == ["inst_001", "inst_002"]
        assert island.terrain_objects == ["terrain_001"]
        assert island.collision_mesh == "collision/island_001.glb"

    def test_bounds_access(self) -> None:
        bounds: BoundingBox = {
            "min": [-10.0, 0.0, -10.0],
            "max": [10.0, 5.0, 10.0],
            "radius": 11.18,
        }
        island = Island(
            id="test",
            name="Test",
            world_position=(0.0, 0.0, 0.0),
            world_rotation=(0.0, 0.0, 0.0, 1.0),
            bounds=bounds,
        )

        assert island.bounds["min"] == [-10.0, 0.0, -10.0]
        assert island.bounds["max"] == [10.0, 5.0, 10.0]
        assert island.bounds["radius"] == 11.18


# --- WorldMap Tests ---


class TestWorldMap:
    """Tests for WorldMap dataclass."""

    def test_creation_minimal(self) -> None:
        world = WorldMap(size=(1000.0, 1000.0))

        assert world.size == (1000.0, 1000.0)
        assert world.islands == {}
        assert world.water_level == 0.0

    def test_creation_with_islands(self) -> None:
        bounds: BoundingBox = {"min": [0.0, 0.0, 0.0], "max": [10.0, 5.0, 10.0], "radius": 10.0}
        island = Island(
            id="island_01",
            name="Island One",
            world_position=(100.0, 0.0, 100.0),
            world_rotation=(0.0, 0.0, 0.0, 1.0),
            bounds=bounds,
        )
        world = WorldMap(
            size=(2000.0, 2000.0),
            islands={"island_01": island},
            water_level=-5.0,
        )

        assert world.size == (2000.0, 2000.0)
        assert "island_01" in world.islands
        assert world.islands["island_01"].name == "Island One"
        assert world.water_level == -5.0


# --- ExportData Tests ---


class TestExportData:
    """Tests for ExportData dataclass."""

    def test_creation_empty(self) -> None:
        data = ExportData()

        assert data.asset_definitions == {}
        assert data.instances == []
        assert data.terrain_objects == []
        assert data.islands == {}
        assert data.collection_tree is None
        assert data.by_asset_id == {}
        assert data.by_entity_type == {}

    def test_build_indices_single_instance(self, sample_instance: Instance) -> None:
        data = ExportData()
        data.instances.append(sample_instance)
        data.build_indices()

        # Check by_asset_id index
        assert "asset_rock_01" in data.by_asset_id
        assert len(data.by_asset_id["asset_rock_01"]) == 1
        assert data.by_asset_id["asset_rock_01"][0] is sample_instance

        # Check by_entity_type index
        assert "static" in data.by_entity_type
        assert len(data.by_entity_type["static"]) == 1
        assert data.by_entity_type["static"][0] is sample_instance

    def test_build_indices_instance_without_asset_id(
        self, sample_instance_no_asset: Instance
    ) -> None:
        data = ExportData()
        data.instances.append(sample_instance_no_asset)
        data.build_indices()

        # Instance with None asset_id should not be in by_asset_id
        assert data.by_asset_id == {}

        # But should be in by_entity_type
        assert "terrain" in data.by_entity_type
        assert len(data.by_entity_type["terrain"]) == 1

    def test_build_indices_multiple_instances(self, sample_bounding_box: BoundingBox) -> None:
        data = ExportData()

        # Add multiple instances with same asset_id
        for i in range(3):
            inst = Instance(
                id=f"rock_{i:03d}",
                name=f"Rock_{i}",
                asset_id="asset_rock_01",
                entity_type="static",
                position=(float(i * 10), 0.0, 0.0),
                rotation=(0.0, 0.0, 0.0, 1.0),
                scale=(1.0, 1.0, 1.0),
                bounding_box=sample_bounding_box,
                collection_path=["Scene", "Rocks"],
            )
            data.instances.append(inst)

        # Add instances with different asset_id
        for i in range(2):
            inst = Instance(
                id=f"tree_{i:03d}",
                name=f"Tree_{i}",
                asset_id="asset_tree_01",
                entity_type="vegetation",
                position=(float(i * 20), 0.0, 0.0),
                rotation=(0.0, 0.0, 0.0, 1.0),
                scale=(1.0, 1.0, 1.0),
                bounding_box=sample_bounding_box,
                collection_path=["Scene", "Trees"],
            )
            data.instances.append(inst)

        data.build_indices()

        # Check by_asset_id
        assert len(data.by_asset_id["asset_rock_01"]) == 3
        assert len(data.by_asset_id["asset_tree_01"]) == 2

        # Check by_entity_type
        assert len(data.by_entity_type["static"]) == 3
        assert len(data.by_entity_type["vegetation"]) == 2

    def test_build_indices_clears_previous(
        self, sample_instance: Instance, sample_instance_no_asset: Instance
    ) -> None:
        data = ExportData()

        # First build
        data.instances.append(sample_instance)
        data.build_indices()
        assert len(data.by_asset_id) == 1

        # Modify instances and rebuild
        data.instances.clear()
        data.instances.append(sample_instance_no_asset)
        data.build_indices()

        # Old index should be cleared
        assert "asset_rock_01" not in data.by_asset_id
        assert data.by_asset_id == {}  # No asset_id on terrain instance
        assert "terrain" in data.by_entity_type

    def test_with_asset_definitions(self) -> None:
        data = ExportData()
        data.asset_definitions["asset_rock_01"] = AssetDefinition(
            id="asset_rock_01",
            file="meshes/rock_01.glb",
            source=None,
        )
        data.asset_definitions["asset_tree_01"] = AssetDefinition(
            id="asset_tree_01",
            file="meshes/tree_01.glb",
            source="//library/vegetation.blend",
        )

        assert len(data.asset_definitions) == 2
        assert data.asset_definitions["asset_rock_01"].file == "meshes/rock_01.glb"

    def test_with_collection_tree(self) -> None:
        data = ExportData()
        data.collection_tree = CollectionNode(
            name="Scene",
            children={
                "Props": CollectionNode(name="Props", instance_ids=["inst_001"]),
            },
        )

        assert data.collection_tree is not None
        assert data.collection_tree.name == "Scene"
        assert "Props" in data.collection_tree.children

    def test_full_export_data_workflow(self, sample_bounding_box: BoundingBox) -> None:
        """Integration test for typical export data workflow."""
        data = ExportData()

        # Add asset definitions
        data.asset_definitions["rock"] = AssetDefinition(id="rock", file="rock.glb", source=None)
        data.asset_definitions["tree"] = AssetDefinition(id="tree", file="tree.glb", source=None)

        # Add instances
        rock_inst = Instance(
            id="rock_001",
            name="Rock_001",
            asset_id="rock",
            entity_type="static",
            position=(0.0, 0.0, 0.0),
            rotation=(0.0, 0.0, 0.0, 1.0),
            scale=(1.0, 1.0, 1.0),
            bounding_box=sample_bounding_box,
            collection_path=["Scene", "Props"],
        )
        tree_inst = Instance(
            id="tree_001",
            name="Tree_001",
            asset_id="tree",
            entity_type="vegetation",
            position=(10.0, 0.0, 10.0),
            rotation=(0.0, 0.0, 0.0, 1.0),
            scale=(1.0, 1.0, 1.0),
            bounding_box=sample_bounding_box,
            collection_path=["Scene", "Vegetation"],
        )
        data.instances.extend([rock_inst, tree_inst])

        # Build collection tree
        data.collection_tree = CollectionNode(
            name="Scene",
            children={
                "Props": CollectionNode(name="Props", instance_ids=["rock_001"]),
                "Vegetation": CollectionNode(name="Vegetation", instance_ids=["tree_001"]),
            },
        )

        # Build indices
        data.build_indices()

        # Verify everything is set up correctly
        assert len(data.asset_definitions) == 2
        assert len(data.instances) == 2
        assert len(data.by_asset_id) == 2
        assert len(data.by_entity_type) == 2
        assert data.by_asset_id["rock"][0] is rock_inst
        assert data.by_entity_type["vegetation"][0] is tree_inst
        assert data.collection_tree is not None
        assert len(data.collection_tree.children) == 2


# --- Island Terrain Fields Tests ---


class TestIslandTerrainFields:
    """Tests for Island terrain_chunks and terrain_merged fields."""

    def test_island_terrain_fields_defaults(self) -> None:
        """Island should have terrain_chunks and terrain_merged fields with defaults."""
        bounds: BoundingBox = {
            "min": [0.0, 0.0, 0.0],
            "max": [1.0, 1.0, 1.0],
            "radius": 1.0,
        }
        island = Island(
            id="test",
            name="Test",
            world_position=(0.0, 0.0, 0.0),
            world_rotation=(0.0, 0.0, 0.0, 1.0),
            bounds=bounds,
        )
        assert island.terrain_chunks == []
        assert island.terrain_merged is None

    def test_island_terrain_chunks_populated(self) -> None:
        """Island terrain_chunks should accept list of paths."""
        bounds: BoundingBox = {
            "min": [0.0, 0.0, 0.0],
            "max": [1.0, 1.0, 1.0],
            "radius": 1.0,
        }
        island = Island(
            id="test",
            name="Test",
            world_position=(0.0, 0.0, 0.0),
            world_rotation=(0.0, 0.0, 0.0, 1.0),
            bounds=bounds,
            terrain_chunks=["islands/test/terrain/chunk_a.glb", "islands/test/terrain/chunk_b.glb"],
            terrain_merged=None,
        )
        assert island.terrain_chunks == [
            "islands/test/terrain/chunk_a.glb",
            "islands/test/terrain/chunk_b.glb",
        ]

    def test_island_terrain_merged_populated(self) -> None:
        """Island terrain_merged should accept path string."""
        bounds: BoundingBox = {
            "min": [0.0, 0.0, 0.0],
            "max": [1.0, 1.0, 1.0],
            "radius": 1.0,
        }
        island = Island(
            id="test",
            name="Test",
            world_position=(0.0, 0.0, 0.0),
            world_rotation=(0.0, 0.0, 0.0, 1.0),
            bounds=bounds,
            terrain_chunks=[],
            terrain_merged="islands/test/terrain/merged.glb",
        )
        assert island.terrain_merged == "islands/test/terrain/merged.glb"
