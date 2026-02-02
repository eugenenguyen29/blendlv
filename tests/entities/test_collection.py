"""Tests for CollectionExtractor in blender_extension.entities.collection.

Tests verify that collection instances (EMPTY objects with instance_type='COLLECTION')
are correctly identified and extracted with proper asset keys and bounding boxes.
"""

from __future__ import annotations

import math
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_transforms():
    """Mock transform utility functions for isolated testing."""
    with (
        patch("blender_extension.entities.collection.get_object_transform") as mock_transform,
        patch("blender_extension.entities.collection.get_custom_properties") as mock_custom_props,
    ):
        mock_transform.return_value = {
            "position": [0.0, 0.0, 0.0],
            "rotation": [0.0, 0.0, 0.0, 1.0],
            "scale": [1.0, 1.0, 1.0],
        }
        mock_custom_props.return_value = {}
        yield {
            "transform": mock_transform,
            "custom_props": mock_custom_props,
        }


@pytest.fixture
def mock_collection_instance(mock_object: MagicMock) -> MagicMock:
    """Create a mock collection instance object (EMPTY with COLLECTION)."""
    mock_object.type = "EMPTY"
    mock_object.instance_type = "COLLECTION"

    # Mock the instanced collection
    mock_collection = MagicMock()
    mock_collection.name = "Palm_Tree"
    mock_collection.library = None  # Local collection
    mock_collection.all_objects = []

    mock_object.instance_collection = mock_collection

    # Remove trivesta attribute for basic tests
    if hasattr(mock_object, "trivesta"):
        delattr(mock_object, "trivesta")

    return mock_object


@pytest.fixture
def mock_linked_collection_instance(mock_collection_instance: MagicMock) -> MagicMock:
    """Create a mock linked collection instance with external library."""
    mock_library = MagicMock()
    mock_library.filepath = "//assets/vegetation.blend"
    mock_collection_instance.instance_collection.library = mock_library
    return mock_collection_instance


@pytest.fixture
def mock_mesh_object_with_bbox() -> MagicMock:
    """Create a mock mesh object with bounding box data."""
    mesh_obj = MagicMock()
    mesh_obj.type = "MESH"
    mesh_obj.data = MagicMock()

    # Simple 1x1x1 cube at origin in Blender coords
    # bound_box is 8 corners: [x, y, z]
    mesh_obj.bound_box = [
        [-0.5, -0.5, -0.5],
        [-0.5, -0.5, 0.5],
        [-0.5, 0.5, 0.5],
        [-0.5, 0.5, -0.5],
        [0.5, -0.5, -0.5],
        [0.5, -0.5, 0.5],
        [0.5, 0.5, 0.5],
        [0.5, 0.5, -0.5],
    ]

    # Identity matrix for world transform
    from mathutils import Matrix

    mesh_obj.matrix_world = Matrix.Identity(4)

    return mesh_obj


class TestCollectionExtractorMatching:
    """Tests for CollectionExtractor.matches()."""

    def test_matches_empty_with_collection(
        self,
        mock_bpy_module: MagicMock,
        mock_collection_instance: MagicMock,
    ) -> None:
        """Should match EMPTY objects with instance_type='COLLECTION'."""
        from blender_extension.entities.collection import CollectionExtractor

        extractor = CollectionExtractor()
        assert extractor.matches(mock_collection_instance) is True

    def test_rejects_mesh_objects(
        self,
        mock_bpy_module: MagicMock,
        mock_object: MagicMock,
    ) -> None:
        """Should reject regular MESH objects."""
        from blender_extension.entities.collection import CollectionExtractor

        mock_object.type = "MESH"
        extractor = CollectionExtractor()
        assert extractor.matches(mock_object) is False

    def test_rejects_empty_without_collection(
        self,
        mock_bpy_module: MagicMock,
        mock_object: MagicMock,
    ) -> None:
        """Should reject EMPTY objects without collection instance."""
        from blender_extension.entities.collection import CollectionExtractor

        mock_object.type = "EMPTY"
        mock_object.instance_type = "NONE"
        mock_object.instance_collection = None

        extractor = CollectionExtractor()
        assert extractor.matches(mock_object) is False


class TestCollectionExtractorAssetKey:
    """Tests for asset key generation in CollectionExtractor."""

    def test_extract_local_collection_asset_key(
        self,
        mock_bpy_module: MagicMock,
        mock_collection_instance: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Should generate asset_id from local collection name."""
        from blender_extension.entities.collection import CollectionExtractor

        extractor = CollectionExtractor()
        instance = extractor.extract(mock_collection_instance)

        # Palm_Tree -> palm_tree (sanitized)
        assert instance.asset_id == "palm_tree"

    def test_extract_linked_collection_asset_key(
        self,
        mock_bpy_module: MagicMock,
        mock_linked_collection_instance: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Should include library name in asset_id for linked collections."""
        from blender_extension.entities.collection import CollectionExtractor

        extractor = CollectionExtractor()
        instance = extractor.extract(mock_linked_collection_instance)

        # vegetation.blend + Palm_Tree -> vegetation_palm_tree
        assert instance.asset_id == "vegetation_palm_tree"

    def test_extract_linked_collection_with_empty_filepath(
        self,
        mock_bpy_module: MagicMock,
        mock_collection_instance: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Should fallback to collection name when library filepath is empty."""
        from blender_extension.entities.collection import CollectionExtractor

        # Setup linked collection with empty filepath
        mock_library = MagicMock()
        mock_library.filepath = ""  # Empty filepath
        mock_collection_instance.instance_collection.library = mock_library

        extractor = CollectionExtractor()
        instance = extractor.extract(mock_collection_instance)

        # Should fallback to collection name only (Palm_Tree -> palm_tree)
        assert instance.asset_id == "palm_tree"


class TestCollectionExtractorBoundingBox:
    """Tests for bounding box calculation in CollectionExtractor."""

    def test_bounding_box_single_mesh(
        self,
        mock_bpy_module: MagicMock,
        mock_collection_instance: MagicMock,
        mock_mesh_object_with_bbox: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Should calculate bbox from single mesh in collection."""
        from blender_extension.entities.collection import CollectionExtractor

        # Add mesh to collection
        mock_collection_instance.instance_collection.all_objects = [mock_mesh_object_with_bbox]

        extractor = CollectionExtractor()
        instance = extractor.extract(mock_collection_instance)

        bbox = instance.bounding_box

        # Verify min/max in Three.js Y-up coords
        # Blender: X right, Y forward, Z up
        # Three.js: X right, Y up, Z back
        # Conversion: x->x, z->y, -y->z
        # Original Blender box: [-0.5, -0.5, -0.5] to [0.5, 0.5, 0.5]
        # Three.js: x: [-0.5, 0.5], y: [-0.5, 0.5] (from z), z: [-0.5, 0.5] (from -y)
        assert bbox["min"][0] == pytest.approx(-0.5)  # x
        assert bbox["min"][1] == pytest.approx(-0.5)  # y (from z)
        assert bbox["min"][2] == pytest.approx(-0.5)  # z (from -y)
        assert bbox["max"][0] == pytest.approx(0.5)
        assert bbox["max"][1] == pytest.approx(0.5)
        assert bbox["max"][2] == pytest.approx(0.5)

        # Radius should be half-diagonal
        expected_radius = math.sqrt(0.5**2 + 0.5**2 + 0.5**2)
        assert bbox["radius"] == pytest.approx(expected_radius)

    def test_bounding_box_multiple_meshes(
        self,
        mock_bpy_module: MagicMock,
        mock_collection_instance: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Should calculate combined bbox from multiple meshes."""
        from mathutils import Matrix

        from blender_extension.entities.collection import CollectionExtractor

        # Create two mesh objects at different positions
        mesh1 = MagicMock()
        mesh1.type = "MESH"
        mesh1.data = MagicMock()
        mesh1.bound_box = [
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 1.0, 1.0],
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0],
            [1.0, 1.0, 0.0],
        ]
        mesh1.matrix_world = Matrix.Identity(4)

        mesh2 = MagicMock()
        mesh2.type = "MESH"
        mesh2.data = MagicMock()
        mesh2.bound_box = [
            [2.0, 0.0, 0.0],
            [2.0, 0.0, 1.0],
            [2.0, 1.0, 1.0],
            [2.0, 1.0, 0.0],
            [3.0, 0.0, 0.0],
            [3.0, 0.0, 1.0],
            [3.0, 1.0, 1.0],
            [3.0, 1.0, 0.0],
        ]
        mesh2.matrix_world = Matrix.Identity(4)

        mock_collection_instance.instance_collection.all_objects = [mesh1, mesh2]

        extractor = CollectionExtractor()
        instance = extractor.extract(mock_collection_instance)

        bbox = instance.bounding_box

        # Combined bounds in Blender: x=[0,3], y=[0,1], z=[0,1]
        # Three.js conversion: x=[0,3], y=[0,1] (from z), z=[-1,0] (from -y)
        assert bbox["min"][0] == pytest.approx(0.0)
        assert bbox["min"][1] == pytest.approx(0.0)  # from z=0
        assert bbox["min"][2] == pytest.approx(-1.0)  # from -y=-1
        assert bbox["max"][0] == pytest.approx(3.0)
        assert bbox["max"][1] == pytest.approx(1.0)  # from z=1
        assert bbox["max"][2] == pytest.approx(0.0)  # from -y=0

    def test_empty_collection_bounding_box(
        self,
        mock_bpy_module: MagicMock,
        mock_collection_instance: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Should return zero-size bbox for empty collection."""
        from blender_extension.entities.collection import CollectionExtractor

        # Collection with no objects
        mock_collection_instance.instance_collection.all_objects = []

        extractor = CollectionExtractor()
        instance = extractor.extract(mock_collection_instance)

        bbox = instance.bounding_box
        assert bbox["min"] == [0, 0, 0]
        assert bbox["max"] == [0, 0, 0]
        assert bbox["radius"] == 0.0


class TestCollectionExtractorEntityType:
    """Tests for entity type handling in CollectionExtractor."""

    def test_extract_respects_entity_type_override(
        self,
        mock_bpy_module: MagicMock,
        mock_collection_instance: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Should use trivesta.entity_type if set."""
        from blender_extension.entities.collection import CollectionExtractor

        # Add trivesta settings with custom entity type
        mock_settings = MagicMock()
        mock_settings.entity_type = "prop"
        mock_collection_instance.trivesta = mock_settings

        extractor = CollectionExtractor()
        instance = extractor.extract(mock_collection_instance)

        assert instance.entity_type == "prop"

    def test_extract_defaults_to_static_entity_type(
        self,
        mock_bpy_module: MagicMock,
        mock_collection_instance: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Should default to 'static' entity type when trivesta not set."""
        from blender_extension.entities.collection import CollectionExtractor

        # Ensure trivesta is not set
        if hasattr(mock_collection_instance, "trivesta"):
            delattr(mock_collection_instance, "trivesta")

        extractor = CollectionExtractor()
        instance = extractor.extract(mock_collection_instance)

        assert instance.entity_type == "static"


class TestCollectionExtractorDialogSerialization:
    """Tests for NPC dialog and Interactive script_id serialization."""

    def test_extract_npc_with_dialog_lines(
        self,
        mock_bpy_module: MagicMock,
        mock_collection_instance: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Should serialize dialog_lines into custom_properties['dialog'] for NPC entities."""
        from blender_extension.entities.collection import CollectionExtractor

        # Setup NPC entity with dialog lines
        mock_settings = MagicMock()
        mock_settings.entity_type = "npc"

        # Create mock dialog lines as list
        mock_line1 = MagicMock()
        mock_line1.speaker = "Guard"
        mock_line1.text = "Halt! Who goes there?"
        mock_line2 = MagicMock()
        mock_line2.speaker = "Guard"
        mock_line2.text = "Show me your papers."

        mock_settings.dialog_lines = [mock_line1, mock_line2]

        mock_collection_instance.trivesta = mock_settings

        extractor = CollectionExtractor()
        instance = extractor.extract(mock_collection_instance)

        # Verify dialog was serialized
        assert "dialog" in instance.custom_properties
        dialog_data = cast(list[dict[str, Any]], instance.custom_properties["dialog"])
        assert len(dialog_data) == 2
        assert dialog_data[0] == {"speaker": "Guard", "text": "Halt! Who goes there?"}
        assert dialog_data[1] == {"speaker": "Guard", "text": "Show me your papers."}

    def test_extract_npc_without_dialog_lines(
        self,
        mock_bpy_module: MagicMock,
        mock_collection_instance: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Should not add dialog key when dialog_lines is empty."""
        from blender_extension.entities.collection import CollectionExtractor

        mock_settings = MagicMock()
        mock_settings.entity_type = "npc"
        mock_settings.dialog_lines = []

        mock_collection_instance.trivesta = mock_settings

        extractor = CollectionExtractor()
        instance = extractor.extract(mock_collection_instance)

        assert "dialog" not in instance.custom_properties

    def test_extract_interactive_with_script_id(
        self,
        mock_bpy_module: MagicMock,
        mock_collection_instance: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Should serialize script_id for Interactive entities."""
        from blender_extension.entities.collection import CollectionExtractor

        mock_settings = MagicMock()
        mock_settings.entity_type = "interactive"
        mock_settings.script_id = "door_interaction"

        mock_collection_instance.trivesta = mock_settings

        extractor = CollectionExtractor()
        instance = extractor.extract(mock_collection_instance)

        assert "script_id" in instance.custom_properties
        assert instance.custom_properties["script_id"] == "door_interaction"

    def test_extract_interactive_without_script_id(
        self,
        mock_bpy_module: MagicMock,
        mock_collection_instance: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Should not add script_id key when script_id is empty."""
        from blender_extension.entities.collection import CollectionExtractor

        mock_settings = MagicMock()
        mock_settings.entity_type = "interactive"
        mock_settings.script_id = ""

        mock_collection_instance.trivesta = mock_settings

        extractor = CollectionExtractor()
        instance = extractor.extract(mock_collection_instance)

        assert "script_id" not in instance.custom_properties

    def test_extract_static_no_dialog_serialization(
        self,
        mock_bpy_module: MagicMock,
        mock_collection_instance: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Should not serialize dialog or script_id for static entities."""
        from blender_extension.entities.collection import CollectionExtractor

        mock_settings = MagicMock()
        mock_settings.entity_type = "static"

        # Even if these exist, they shouldn't be serialized for static
        mock_line = MagicMock()
        mock_line.speaker = "Someone"
        mock_line.text = "Should not appear"
        mock_settings.dialog_lines = [mock_line]
        mock_settings.script_id = "should_not_serialize"

        mock_collection_instance.trivesta = mock_settings

        extractor = CollectionExtractor()
        instance = extractor.extract(mock_collection_instance)

        assert "dialog" not in instance.custom_properties
        assert "script_id" not in instance.custom_properties
