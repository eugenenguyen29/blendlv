"""Unit tests for island detection utilities."""

from __future__ import annotations

from unittest.mock import MagicMock, patch


class TestDetectIslandsTerrainObjects:
    """Tests for terrain object detection in detect_islands()."""

    def test_detect_islands_populates_terrain_objects(self, mock_bpy_module: MagicMock) -> None:
        """Objects with entity_type='terrain' go to terrain_objects list."""
        from blender_extension.utils.islands import detect_islands

        # Create terrain object with trivesta.entity_type = "terrain"
        terrain_obj = MagicMock()
        terrain_obj.name = "Terrain_Ground"
        terrain_obj.type = "MESH"
        terrain_obj.trivesta = MagicMock()
        terrain_obj.trivesta.entity_type = "terrain"

        # Create mock scene with island collection
        scene = MagicMock()
        island_collection = MagicMock()
        island_collection.name = "Island_Test"
        island_collection.objects = [terrain_obj]
        island_collection.children = []
        scene.collection.children = [island_collection]

        # Mock helper functions
        with (
            patch(
                "blender_extension.utils.islands.get_collection_origin",
                return_value=(0.0, 0.0, 0.0),
            ),
            patch(
                "blender_extension.utils.islands.calculate_collection_bounds",
                return_value={"min": [0, 0, 0], "max": [1, 1, 1], "radius": 1.0},
            ),
            patch(
                "blender_extension.utils.islands.get_collection_objects_recursive",
                return_value=[terrain_obj],
            ),
        ):
            islands = detect_islands(scene)

        # Verify terrain object is in terrain_objects list
        assert "island_test" in islands
        island = islands["island_test"]
        assert "Terrain_Ground" in island.terrain_objects
        assert "Terrain_Ground" not in island.instances

    def test_detect_islands_separates_terrain_from_instances(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """Terrain objects are NOT in instances list."""
        from blender_extension.utils.islands import detect_islands

        # Create terrain object
        terrain_obj = MagicMock()
        terrain_obj.name = "Ground_Mesh"
        terrain_obj.type = "MESH"
        terrain_obj.trivesta = MagicMock()
        terrain_obj.trivesta.entity_type = "terrain"

        # Create static object (no terrain entity_type)
        static_obj = MagicMock()
        static_obj.name = "Tree_01"
        static_obj.type = "MESH"
        static_obj.trivesta = MagicMock()
        static_obj.trivesta.entity_type = "static"

        # Create object without trivesta property
        plain_obj = MagicMock(spec=["name", "type"])
        plain_obj.name = "Rock_01"
        plain_obj.type = "MESH"

        # Create mock scene with island collection
        scene = MagicMock()
        island_collection = MagicMock()
        island_collection.name = "Island_Mixed"
        island_collection.objects = [terrain_obj, static_obj, plain_obj]
        island_collection.children = []
        scene.collection.children = [island_collection]

        # Mock helper functions
        with (
            patch(
                "blender_extension.utils.islands.get_collection_origin",
                return_value=(0.0, 0.0, 0.0),
            ),
            patch(
                "blender_extension.utils.islands.calculate_collection_bounds",
                return_value={"min": [0, 0, 0], "max": [10, 10, 10], "radius": 5.0},
            ),
            patch(
                "blender_extension.utils.islands.get_collection_objects_recursive",
                return_value=[terrain_obj, static_obj, plain_obj],
            ),
        ):
            islands = detect_islands(scene)

        # Verify separation
        island = islands["island_mixed"]
        assert "Ground_Mesh" in island.terrain_objects
        assert "Ground_Mesh" not in island.instances
        assert "Tree_01" in island.instances
        assert "Tree_01" not in island.terrain_objects
        assert "Rock_01" in island.instances
        assert "Rock_01" not in island.terrain_objects

    def test_detect_islands_handles_missing_trivesta_property(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """Objects without trivesta property go to instances list."""
        from blender_extension.utils.islands import detect_islands

        # Create object without trivesta attribute (using spec to exclude it)
        obj = MagicMock(spec=["name", "type"])
        obj.name = "Plain_Object"
        obj.type = "MESH"

        # Create mock scene with island collection
        scene = MagicMock()
        island_collection = MagicMock()
        island_collection.name = "Island_NoTrivesta"
        island_collection.objects = [obj]
        island_collection.children = []
        scene.collection.children = [island_collection]

        # Mock helper functions
        with (
            patch(
                "blender_extension.utils.islands.get_collection_origin",
                return_value=(0.0, 0.0, 0.0),
            ),
            patch(
                "blender_extension.utils.islands.calculate_collection_bounds",
                return_value={"min": [0, 0, 0], "max": [1, 1, 1], "radius": 1.0},
            ),
            patch(
                "blender_extension.utils.islands.get_collection_objects_recursive",
                return_value=[obj],
            ),
        ):
            islands = detect_islands(scene)

        # Verify object goes to instances (fallback behavior)
        island = islands["island_notrivesta"]
        assert "Plain_Object" in island.instances
        assert "Plain_Object" not in island.terrain_objects

    def test_detect_islands_non_mesh_objects_ignored(self, mock_bpy_module: MagicMock) -> None:
        """Non-MESH objects are not added to either list."""
        from blender_extension.utils.islands import detect_islands

        # Create an EMPTY object
        empty_obj = MagicMock()
        empty_obj.name = "Empty_Marker"
        empty_obj.type = "EMPTY"
        empty_obj.trivesta = MagicMock()
        empty_obj.trivesta.entity_type = "terrain"  # Even if marked as terrain

        # Create mock scene with island collection
        scene = MagicMock()
        island_collection = MagicMock()
        island_collection.name = "Island_Empty"
        island_collection.objects = [empty_obj]
        island_collection.children = []
        scene.collection.children = [island_collection]

        # Mock helper functions
        with (
            patch(
                "blender_extension.utils.islands.get_collection_origin",
                return_value=(0.0, 0.0, 0.0),
            ),
            patch(
                "blender_extension.utils.islands.calculate_collection_bounds",
                return_value={"min": [0, 0, 0], "max": [0, 0, 0], "radius": 0.0},
            ),
            patch(
                "blender_extension.utils.islands.get_collection_objects_recursive",
                return_value=[empty_obj],
            ),
        ):
            islands = detect_islands(scene)

        # Verify EMPTY is not in either list
        island = islands["island_empty"]
        assert len(island.terrain_objects) == 0
        assert len(island.instances) == 0


class TestDetectIslands:
    """General tests for detect_islands function."""

    def test_detect_islands_skips_non_island_collections(self, mock_bpy_module: MagicMock) -> None:
        """Collections not starting with 'Island_' are skipped."""
        from blender_extension.utils.islands import detect_islands

        scene = MagicMock()
        regular_collection = MagicMock()
        regular_collection.name = "Props"
        scene.collection.children = [regular_collection]

        islands = detect_islands(scene)

        assert len(islands) == 0

    def test_detect_islands_creates_island_dataclass(self, mock_bpy_module: MagicMock) -> None:
        """detect_islands returns Island dataclass instances."""
        from blender_extension.core.data import Island
        from blender_extension.utils.islands import detect_islands

        scene = MagicMock()
        island_collection = MagicMock()
        island_collection.name = "Island_Test"
        island_collection.objects = []
        island_collection.children = []
        scene.collection.children = [island_collection]

        # Mock helper functions
        with (
            patch(
                "blender_extension.utils.islands.get_collection_origin",
                return_value=(0.0, 0.0, 0.0),
            ),
            patch(
                "blender_extension.utils.islands.calculate_collection_bounds",
                return_value={"min": [0, 0, 0], "max": [0, 0, 0], "radius": 0.0},
            ),
            patch(
                "blender_extension.utils.islands.get_collection_objects_recursive",
                return_value=[],
            ),
        ):
            islands = detect_islands(scene)

        assert "island_test" in islands
        assert isinstance(islands["island_test"], Island)
        assert islands["island_test"].name == "Island_Test"
        assert islands["island_test"].id == "island_test"

    def test_detect_islands_multiple_islands(self, mock_bpy_module: MagicMock) -> None:
        """Multiple island collections are all detected."""
        from blender_extension.utils.islands import detect_islands

        scene = MagicMock()

        island1 = MagicMock()
        island1.name = "Island_Alpha"
        island1.objects = []
        island1.children = []

        island2 = MagicMock()
        island2.name = "Island_Beta"
        island2.objects = []
        island2.children = []

        scene.collection.children = [island1, island2]

        # Mock helper functions
        with (
            patch(
                "blender_extension.utils.islands.get_collection_origin",
                return_value=(0.0, 0.0, 0.0),
            ),
            patch(
                "blender_extension.utils.islands.calculate_collection_bounds",
                return_value={"min": [0, 0, 0], "max": [0, 0, 0], "radius": 0.0},
            ),
            patch(
                "blender_extension.utils.islands.get_collection_objects_recursive",
                return_value=[],
            ),
        ):
            islands = detect_islands(scene)

        assert len(islands) == 2
        assert "island_alpha" in islands
        assert "island_beta" in islands
