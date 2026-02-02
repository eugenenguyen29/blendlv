"""Tests for blender_extension/exporters/manifest.py.

Tests the ManifestSerializer class and write_manifest function.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from blender_extension.core.data import (
    AssetDefinition,
    BoundingBox,
    CollectionNode,
    ExportData,
    Instance,
    Island,
)


def make_bounding_box() -> BoundingBox:
    """Create a test bounding box."""
    return {"min": [0.0, 0.0, 0.0], "max": [1.0, 1.0, 1.0], "radius": 0.87}


def make_test_instance(
    id: str = "test-1",
    name: str = "TestObj",
    entity_type: str = "static",
    asset_id: str | None = None,
    custom_properties: dict[str, object] | None = None,
) -> Instance:
    """Create a test Instance."""
    return Instance(
        id=id,
        name=name,
        entity_type=entity_type,
        asset_id=asset_id,
        position=(1.0, 2.0, 3.0),
        rotation=(0.0, 0.0, 0.0, 1.0),
        scale=(1.0, 1.0, 1.0),
        bounding_box=make_bounding_box(),
        collection_path=["/Scene", "Objects"],
        custom_properties=custom_properties or {},
    )


def make_test_asset_definition(
    id: str = "asset-1",
    file: str = "assets/asset-1.glb",
    source: str | None = None,
) -> AssetDefinition:
    """Create a test AssetDefinition."""
    return AssetDefinition(id=id, file=file, source=source)


def make_test_island(
    id: str = "island-1",
    name: str = "TestIsland",
    collision_mesh: str | None = None,
    terrain_chunks: list[str] | None = None,
    terrain_merged: str | None = None,
) -> Island:
    """Create a test Island."""
    return Island(
        id=id,
        name=name,
        world_position=(100.0, 0.0, 200.0),
        world_rotation=(0.0, 0.0, 0.0, 1.0),
        bounds=make_bounding_box(),
        instances=["inst-1", "inst-2"],
        terrain_objects=["terrain-1"],
        collision_mesh=collision_mesh,
        terrain_chunks=terrain_chunks or [],
        terrain_merged=terrain_merged,
    )


def make_mock_context() -> MagicMock:
    """Create a mock Blender context with trivesta settings."""
    mock_ctx = MagicMock()
    mock_ctx.scene.trivesta.world_size_x = 1024.0
    mock_ctx.scene.trivesta.world_size_z = 1024.0
    mock_ctx.scene.trivesta.water_level = 0.0
    return mock_ctx


class TestManifestSerializerSerialize:
    """Tests for ManifestSerializer.serialize()."""

    def test_serialize_returns_dict_with_required_keys(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """serialize() returns dict with all required top-level keys."""
        from blender_extension.exporters.manifest import ManifestSerializer

        mock_bpy_module.data.filepath = "/path/to/file.blend"

        serializer = ManifestSerializer()
        data = ExportData()
        mock_ctx = make_mock_context()

        result = serializer.serialize(data, mock_ctx)

        assert "_generated" in result
        assert "version" in result
        assert "exported_at" in result
        assert "blender_file" in result
        assert "asset_definitions" in result
        assert "instances" in result
        assert "terrain_objects" in result
        assert "collections" in result
        assert "islands" in result
        assert "world" in result
        assert "statistics" in result

    def test_serialize_uses_manifest_version(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """serialize() uses MANIFEST_VERSION from constants."""
        from blender_extension.core.constants import MANIFEST_VERSION
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        data = ExportData()
        mock_ctx = make_mock_context()

        result = serializer.serialize(data, mock_ctx)

        assert result["version"] == MANIFEST_VERSION

    def test_serialize_includes_blender_filepath(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """serialize() includes bpy.data.filepath."""
        from blender_extension.exporters.manifest import ManifestSerializer

        mock_bpy_module.data.filepath = "/projects/game/level.blend"

        serializer = ManifestSerializer()
        data = ExportData()
        mock_ctx = make_mock_context()

        result = serializer.serialize(data, mock_ctx)

        assert result["blender_file"] == "/projects/game/level.blend"

    def test_serialize_unsaved_file(self, mock_bpy_module: MagicMock) -> None:
        """serialize() returns 'unsaved' for empty filepath."""
        from blender_extension.exporters.manifest import ManifestSerializer

        mock_bpy_module.data.filepath = ""

        serializer = ManifestSerializer()
        data = ExportData()
        mock_ctx = make_mock_context()

        result = serializer.serialize(data, mock_ctx)

        assert result["blender_file"] == "unsaved"

    def test_serialize_exported_at_is_iso_format(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """serialize() includes ISO format timestamp."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        data = ExportData()
        mock_ctx = make_mock_context()

        result = serializer.serialize(data, mock_ctx)

        # ISO format should contain 'T' separator and '+' or 'Z' for timezone
        assert "T" in result["exported_at"]


class TestSerializeAssetDefinitions:
    """Tests for ManifestSerializer._serialize_asset_definitions()."""

    def test_serialize_empty_definitions(self, mock_bpy_module: MagicMock) -> None:
        """_serialize_asset_definitions() returns empty dict for no assets."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        result = serializer._serialize_asset_definitions({})

        assert result == {}

    def test_serialize_single_asset(self, mock_bpy_module: MagicMock) -> None:
        """_serialize_asset_definitions() serializes asset with id and file."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        asset = make_test_asset_definition(id="cube-1", file="assets/cube.glb")

        result = serializer._serialize_asset_definitions({"cube-1": asset})

        assert "cube-1" in result
        assert result["cube-1"]["id"] == "cube-1"
        assert result["cube-1"]["file"] == "assets/cube.glb"
        assert "source" not in result["cube-1"]

    def test_serialize_asset_with_source(self, mock_bpy_module: MagicMock) -> None:
        """_serialize_asset_definitions() includes optional source field."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        asset = make_test_asset_definition(
            id="linked-1",
            file="assets/linked.glb",
            source="/lib/meshes.blend",
        )

        result = serializer._serialize_asset_definitions({"linked-1": asset})

        assert result["linked-1"]["source"] == "/lib/meshes.blend"

    def test_serialize_multiple_assets(self, mock_bpy_module: MagicMock) -> None:
        """_serialize_asset_definitions() handles multiple assets."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        assets = {
            "asset-1": make_test_asset_definition(id="asset-1", file="a.glb"),
            "asset-2": make_test_asset_definition(id="asset-2", file="b.glb"),
        }

        result = serializer._serialize_asset_definitions(assets)

        assert len(result) == 2
        assert "asset-1" in result
        assert "asset-2" in result


class TestSerializeInstances:
    """Tests for ManifestSerializer._serialize_instances()."""

    def test_serialize_empty_instances(self, mock_bpy_module: MagicMock) -> None:
        """_serialize_instances() returns empty list for no instances."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        result = serializer._serialize_instances([])

        assert result == []

    def test_serialize_single_instance(self, mock_bpy_module: MagicMock) -> None:
        """_serialize_instances() serializes instance with all required fields."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        inst = make_test_instance(id="obj-1", name="Cube", entity_type="static")

        result = serializer._serialize_instances([inst])

        assert len(result) == 1
        assert result[0]["id"] == "obj-1"
        assert result[0]["name"] == "Cube"
        assert result[0]["entity_type"] == "static"
        assert result[0]["position"] == [1.0, 2.0, 3.0]
        assert result[0]["rotation"] == [0.0, 0.0, 0.0, 1.0]
        assert result[0]["scale"] == [1.0, 1.0, 1.0]
        assert "bounding_box" in result[0]
        assert result[0]["collection_path"] == ["/Scene", "Objects"]

    def test_serialize_instance_with_asset_id(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """_serialize_instances() includes optional asset_id."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        inst = make_test_instance(asset_id="cube-mesh")

        result = serializer._serialize_instances([inst])

        assert result[0]["asset_id"] == "cube-mesh"

    def test_serialize_instance_without_asset_id(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """_serialize_instances() omits asset_id when None."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        inst = make_test_instance(asset_id=None)

        result = serializer._serialize_instances([inst])

        assert "asset_id" not in result[0]

    def test_serialize_instance_with_custom_properties(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """_serialize_instances() includes custom_properties when present."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        props = {"health": 100, "faction": "neutral"}
        inst = make_test_instance(custom_properties=props)

        result = serializer._serialize_instances([inst])

        assert result[0]["custom_properties"] == props

    def test_serialize_instance_without_custom_properties(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """_serialize_instances() omits custom_properties when empty."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        inst = make_test_instance(custom_properties={})

        result = serializer._serialize_instances([inst])

        assert "custom_properties" not in result[0]

    def test_serialize_multiple_instances(self, mock_bpy_module: MagicMock) -> None:
        """_serialize_instances() handles multiple instances."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        instances = [
            make_test_instance(id="obj-1", name="Cube"),
            make_test_instance(id="obj-2", name="Sphere"),
            make_test_instance(id="obj-3", name="Cylinder"),
        ]

        result = serializer._serialize_instances(instances)

        assert len(result) == 3
        assert result[0]["id"] == "obj-1"
        assert result[1]["id"] == "obj-2"
        assert result[2]["id"] == "obj-3"


class TestSerializeIslands:
    """Tests for ManifestSerializer._serialize_islands()."""

    def test_serialize_empty_islands(self, mock_bpy_module: MagicMock) -> None:
        """_serialize_islands() returns empty dict for no islands."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        result = serializer._serialize_islands({})

        assert result == {}

    def test_serialize_single_island(self, mock_bpy_module: MagicMock) -> None:
        """_serialize_islands() serializes island with all required fields."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        island = make_test_island(id="island-1", name="Main Island")

        result = serializer._serialize_islands({"island-1": island})

        assert "island-1" in result
        assert result["island-1"]["id"] == "island-1"
        assert result["island-1"]["name"] == "Main Island"
        assert result["island-1"]["world_position"] == [100.0, 0.0, 200.0]
        assert result["island-1"]["world_rotation"] == [0.0, 0.0, 0.0, 1.0]
        assert "bounds" in result["island-1"]
        assert result["island-1"]["instances"] == ["inst-1", "inst-2"]
        assert result["island-1"]["terrain_objects"] == ["terrain-1"]

    def test_serialize_island_with_collision_mesh(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """_serialize_islands() includes optional collision_mesh."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        island = make_test_island(collision_mesh="collision/island-1.glb")

        result = serializer._serialize_islands({"island-1": island})

        assert result["island-1"]["collision_mesh"] == "collision/island-1.glb"

    def test_serialize_island_without_collision_mesh(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """_serialize_islands() omits collision_mesh when None."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        island = make_test_island(collision_mesh=None)

        result = serializer._serialize_islands({"island-1": island})

        assert "collision_mesh" not in result["island-1"]

    def test_serialize_island_with_terrain_chunks(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """_serialize_islands() includes terrain.chunks for individual mode."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        island = make_test_island(
            terrain_chunks=[
                "islands/island-1/terrain/chunk_a.glb",
                "islands/island-1/terrain/chunk_b.glb",
            ],
            terrain_merged=None,
        )

        result = serializer._serialize_islands({"island-1": island})

        assert "terrain" in result["island-1"]
        assert result["island-1"]["terrain"]["chunks"] == [
            "islands/island-1/terrain/chunk_a.glb",
            "islands/island-1/terrain/chunk_b.glb",
        ]
        assert result["island-1"]["terrain"]["merged"] is None

    def test_serialize_island_with_terrain_merged(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """_serialize_islands() includes terrain.merged for merged mode."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        island = make_test_island(
            terrain_chunks=[],
            terrain_merged="islands/island-1/terrain/merged.glb",
        )

        result = serializer._serialize_islands({"island-1": island})

        assert "terrain" in result["island-1"]
        assert result["island-1"]["terrain"]["chunks"] == []
        assert result["island-1"]["terrain"]["merged"] == "islands/island-1/terrain/merged.glb"

    def test_serialize_island_terrain_always_present(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """_serialize_islands() always includes terrain object."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        island = make_test_island()

        result = serializer._serialize_islands({"island-1": island})

        # terrain key should always be present
        assert "terrain" in result["island-1"]
        assert "chunks" in result["island-1"]["terrain"]
        assert "merged" in result["island-1"]["terrain"]

    def test_serialize_multiple_islands(self, mock_bpy_module: MagicMock) -> None:
        """_serialize_islands() handles multiple islands."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        islands = {
            "island-1": make_test_island(id="island-1", name="First"),
            "island-2": make_test_island(id="island-2", name="Second"),
        }

        result = serializer._serialize_islands(islands)

        assert len(result) == 2
        assert "island-1" in result
        assert "island-2" in result


class TestComputeStatistics:
    """Tests for ManifestSerializer._compute_statistics()."""

    def test_compute_empty_statistics(self, mock_bpy_module: MagicMock) -> None:
        """_compute_statistics() returns zeros for empty data."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        data = ExportData()

        result = serializer._compute_statistics(data)

        assert result["total_instances"] == 0
        assert result["total_terrain"] == 0
        assert result["total_assets"] == 0
        assert result["total_islands"] == 0

    def test_compute_statistics_with_data(self, mock_bpy_module: MagicMock) -> None:
        """_compute_statistics() counts all data correctly."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        data = ExportData(
            instances=[
                make_test_instance(id="i1"),
                make_test_instance(id="i2"),
                make_test_instance(id="i3"),
            ],
            terrain_objects=[
                make_test_instance(id="t1", entity_type="terrain"),
                make_test_instance(id="t2", entity_type="terrain"),
            ],
            asset_definitions={
                "a1": make_test_asset_definition(id="a1"),
                "a2": make_test_asset_definition(id="a2"),
            },
            islands={
                "island-1": make_test_island(id="island-1"),
            },
        )

        result = serializer._compute_statistics(data)

        assert result["total_instances"] == 3
        assert result["total_terrain"] == 2
        assert result["total_assets"] == 2
        assert result["total_islands"] == 1


class TestSerializeCollectionTree:
    """Tests for ManifestSerializer._serialize_collection_tree()."""

    def test_serialize_none_tree(self, mock_bpy_module: MagicMock) -> None:
        """_serialize_collection_tree() returns None for None input."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        result = serializer._serialize_collection_tree(None)

        assert result is None

    def test_serialize_simple_tree(self, mock_bpy_module: MagicMock) -> None:
        """_serialize_collection_tree() serializes tree using to_dict()."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        tree = CollectionNode(
            name="Scene",
            children={
                "Objects": CollectionNode(
                    name="Objects",
                    instance_ids=["obj-1", "obj-2"],
                )
            },
            instance_ids=[],
        )

        result = serializer._serialize_collection_tree(tree)

        assert result is not None
        assert result["name"] == "Scene"
        assert "Objects" in result["children"]
        assert result["children"]["Objects"]["instances"] == ["obj-1", "obj-2"]


class TestSerializeWorld:
    """Tests for ManifestSerializer._serialize_world()."""

    def test_serialize_world(self, mock_bpy_module: MagicMock) -> None:
        """_serialize_world() returns world size and water level."""
        from blender_extension.exporters.manifest import ManifestSerializer

        serializer = ManifestSerializer()
        mock_ctx = make_mock_context()
        mock_ctx.scene.trivesta.world_size_x = 2048.0
        mock_ctx.scene.trivesta.world_size_z = 1024.0
        mock_ctx.scene.trivesta.water_level = 5.0

        result = serializer._serialize_world(mock_ctx)

        assert result["size"] == [2048.0, 1024.0]
        assert result["water_level"] == 5.0


class TestWriteManifest:
    """Tests for write_manifest() function."""

    def test_write_manifest_success(
        self, mock_bpy_module: MagicMock, tmp_path: Any
    ) -> None:
        """write_manifest() writes JSON file and returns True."""
        from blender_extension.exporters.manifest import write_manifest

        mock_bpy_module.data.filepath = "/test.blend"
        data = ExportData()
        mock_ctx = make_mock_context()
        export_path = str(tmp_path)

        with patch(
            "blender_extension.exporters.manifest.ensure_directory",
            return_value=export_path,
        ):
            result = write_manifest(data, export_path, mock_ctx)

        assert result is True
        manifest_file = tmp_path / "manifest.json"
        assert manifest_file.exists()

    def test_write_manifest_creates_valid_json(
        self, mock_bpy_module: MagicMock, tmp_path: Any
    ) -> None:
        """write_manifest() creates valid JSON file."""
        import json

        from blender_extension.exporters.manifest import write_manifest

        mock_bpy_module.data.filepath = "/test.blend"
        data = ExportData(
            instances=[make_test_instance()],
            asset_definitions={"a1": make_test_asset_definition()},
        )
        mock_ctx = make_mock_context()
        export_path = str(tmp_path)

        with patch(
            "blender_extension.exporters.manifest.ensure_directory",
            return_value=export_path,
        ):
            write_manifest(data, export_path, mock_ctx)

        manifest_file = tmp_path / "manifest.json"
        with open(manifest_file) as f:
            parsed = json.load(f)

        assert parsed["version"] == "2.0"
        assert len(parsed["instances"]) == 1
        assert "a1" in parsed["asset_definitions"]

    def test_write_manifest_error_raises_runtime_error(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """write_manifest() raises RuntimeError on failure."""
        from blender_extension.exporters.manifest import write_manifest

        data = ExportData()
        mock_ctx = make_mock_context()

        with patch(
            "blender_extension.exporters.manifest.ensure_directory",
            side_effect=OSError("Permission denied"),
        ):
            with pytest.raises(RuntimeError, match="Failed to write manifest"):
                write_manifest(data, "/invalid/path", mock_ctx)
