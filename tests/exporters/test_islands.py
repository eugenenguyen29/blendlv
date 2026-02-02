"""Tests for island terrain export functionality.

Tests the dual-mode terrain export system supporting both individual
chunk exports and merged terrain exports.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch


class TestExportIslandTerrainIndividualMode:
    """Tests for individual terrain chunk export mode."""

    def test_export_individual_creates_separate_glb_per_terrain_object(
        self, mock_bpy_module, mock_context
    ):
        """Individual mode should export separate GLB per terrain object."""
        from blender_extension.core.data import Island
        from blender_extension.exporters.islands import export_island_terrain

        island = Island(
            id="test_island",
            name="Test Island",
            world_position=(0, 0, 0),
            world_rotation=(0, 0, 0, 1),
            bounds={"min": [0, 0, 0], "max": [10, 10, 10], "radius": 10.0},
            terrain_objects=["terrain_chunk_a", "terrain_chunk_b"],
        )

        mock_obj_a = MagicMock()
        mock_obj_a.name = "terrain_chunk_a"
        mock_obj_a.type = "MESH"
        mock_obj_b = MagicMock()
        mock_obj_b.name = "terrain_chunk_b"
        mock_obj_b.type = "MESH"

        mock_context.scene.objects.get.side_effect = lambda name: {
            "terrain_chunk_a": mock_obj_a,
            "terrain_chunk_b": mock_obj_b,
        }.get(name)

        with patch(
            "blender_extension.exporters.islands.export_objects_to_glb"
        ) as mock_export:
            with patch(
                "blender_extension.exporters.islands.get_export_subdir"
            ) as mock_subdir:
                mock_export.return_value = True
                mock_subdir.return_value = "/tmp/exports/islands/test_island/terrain"

                chunks, merged = export_island_terrain(
                    island, "/tmp/exports", mock_context, export_mode="individual"
                )

        assert len(chunks) == 2
        assert "islands/test_island/terrain/terrain_chunk_a.glb" in chunks
        assert "islands/test_island/terrain/terrain_chunk_b.glb" in chunks
        assert merged is None

    def test_export_individual_returns_empty_when_no_terrain(
        self, mock_bpy_module, mock_context
    ):
        """Individual mode should return empty lists when no terrain objects."""
        from blender_extension.core.data import Island
        from blender_extension.exporters.islands import export_island_terrain

        island = Island(
            id="test_island",
            name="Test Island",
            world_position=(0, 0, 0),
            world_rotation=(0, 0, 0, 1),
            bounds={"min": [0, 0, 0], "max": [10, 10, 10], "radius": 10.0},
            terrain_objects=[],
        )

        chunks, merged = export_island_terrain(
            island, "/tmp/exports", mock_context, export_mode="individual"
        )

        assert chunks == []
        assert merged is None

    def test_export_individual_calls_export_per_object(
        self, mock_bpy_module, mock_context
    ):
        """Individual mode should call export_objects_to_glb once per object."""
        from blender_extension.core.data import Island
        from blender_extension.exporters.islands import export_island_terrain

        island = Island(
            id="test_island",
            name="Test Island",
            world_position=(0, 0, 0),
            world_rotation=(0, 0, 0, 1),
            bounds={"min": [0, 0, 0], "max": [10, 10, 10], "radius": 10.0},
            terrain_objects=["chunk_1", "chunk_2", "chunk_3"],
        )

        mock_objs = {}
        for name in ["chunk_1", "chunk_2", "chunk_3"]:
            mock_obj = MagicMock()
            mock_obj.name = name
            mock_obj.type = "MESH"
            mock_objs[name] = mock_obj

        mock_context.scene.objects.get.side_effect = lambda name: mock_objs.get(name)

        with patch(
            "blender_extension.exporters.islands.export_objects_to_glb"
        ) as mock_export:
            with patch(
                "blender_extension.exporters.islands.get_export_subdir"
            ) as mock_subdir:
                mock_export.return_value = True
                mock_subdir.return_value = "/tmp/exports/islands/test_island/terrain"

                export_island_terrain(
                    island, "/tmp/exports", mock_context, export_mode="individual"
                )

        assert mock_export.call_count == 3


class TestExportIslandTerrainMergedMode:
    """Tests for merged terrain export mode."""

    def test_export_merged_creates_single_glb(self, mock_bpy_module, mock_context):
        """Merged mode should export single GLB for all terrain."""
        from blender_extension.core.data import Island
        from blender_extension.exporters.islands import export_island_terrain

        island = Island(
            id="test_island",
            name="Test Island",
            world_position=(0, 0, 0),
            world_rotation=(0, 0, 0, 1),
            bounds={"min": [0, 0, 0], "max": [10, 10, 10], "radius": 10.0},
            terrain_objects=["terrain_chunk_a", "terrain_chunk_b"],
        )

        mock_obj_a = MagicMock()
        mock_obj_a.name = "terrain_chunk_a"
        mock_obj_a.type = "MESH"
        mock_obj_b = MagicMock()
        mock_obj_b.name = "terrain_chunk_b"
        mock_obj_b.type = "MESH"

        mock_context.scene.objects.get.side_effect = lambda name: {
            "terrain_chunk_a": mock_obj_a,
            "terrain_chunk_b": mock_obj_b,
        }.get(name)

        with patch(
            "blender_extension.exporters.islands.export_objects_to_glb"
        ) as mock_export:
            with patch(
                "blender_extension.exporters.islands.get_export_subdir"
            ) as mock_subdir:
                mock_export.return_value = True
                mock_subdir.return_value = "/tmp/exports/islands/test_island/terrain"

                chunks, merged = export_island_terrain(
                    island, "/tmp/exports", mock_context, export_mode="merged"
                )

        assert chunks == []
        assert merged == "islands/test_island/terrain/merged.glb"

    def test_export_merged_is_default_mode(self, mock_bpy_module, mock_context):
        """Merged mode should be the default when no mode specified."""
        from blender_extension.core.data import Island
        from blender_extension.exporters.islands import export_island_terrain

        island = Island(
            id="test_island",
            name="Test Island",
            world_position=(0, 0, 0),
            world_rotation=(0, 0, 0, 1),
            bounds={"min": [0, 0, 0], "max": [10, 10, 10], "radius": 10.0},
            terrain_objects=["terrain_chunk_a"],
        )

        mock_obj_a = MagicMock()
        mock_obj_a.name = "terrain_chunk_a"
        mock_obj_a.type = "MESH"

        mock_context.scene.objects.get.side_effect = lambda name: {
            "terrain_chunk_a": mock_obj_a
        }.get(name)

        with patch(
            "blender_extension.exporters.islands.export_objects_to_glb"
        ) as mock_export:
            with patch(
                "blender_extension.exporters.islands.get_export_subdir"
            ) as mock_subdir:
                mock_export.return_value = True
                mock_subdir.return_value = "/tmp/exports/islands/test_island/terrain"

                # Call without export_mode parameter
                chunks, merged = export_island_terrain(
                    island, "/tmp/exports", mock_context
                )

        assert chunks == []
        assert merged == "islands/test_island/terrain/merged.glb"

    def test_export_merged_returns_none_when_no_terrain(
        self, mock_bpy_module, mock_context
    ):
        """Merged mode should return empty lists when no terrain objects."""
        from blender_extension.core.data import Island
        from blender_extension.exporters.islands import export_island_terrain

        island = Island(
            id="test_island",
            name="Test Island",
            world_position=(0, 0, 0),
            world_rotation=(0, 0, 0, 1),
            bounds={"min": [0, 0, 0], "max": [10, 10, 10], "radius": 10.0},
            terrain_objects=[],
        )

        chunks, merged = export_island_terrain(
            island, "/tmp/exports", mock_context, export_mode="merged"
        )

        assert chunks == []
        assert merged is None

    def test_export_merged_calls_export_once_with_all_objects(
        self, mock_bpy_module, mock_context
    ):
        """Merged mode should call export_objects_to_glb once with all objects."""
        from blender_extension.core.data import Island
        from blender_extension.exporters.islands import export_island_terrain

        island = Island(
            id="test_island",
            name="Test Island",
            world_position=(0, 0, 0),
            world_rotation=(0, 0, 0, 1),
            bounds={"min": [0, 0, 0], "max": [10, 10, 10], "radius": 10.0},
            terrain_objects=["chunk_1", "chunk_2", "chunk_3"],
        )

        mock_objs = {}
        for name in ["chunk_1", "chunk_2", "chunk_3"]:
            mock_obj = MagicMock()
            mock_obj.name = name
            mock_obj.type = "MESH"
            mock_objs[name] = mock_obj

        mock_context.scene.objects.get.side_effect = lambda name: mock_objs.get(name)

        with patch(
            "blender_extension.exporters.islands.export_objects_to_glb"
        ) as mock_export:
            with patch(
                "blender_extension.exporters.islands.get_export_subdir"
            ) as mock_subdir:
                mock_export.return_value = True
                mock_subdir.return_value = "/tmp/exports/islands/test_island/terrain"

                export_island_terrain(
                    island, "/tmp/exports", mock_context, export_mode="merged"
                )

        assert mock_export.call_count == 1
        # Verify all 3 objects were passed
        call_args = mock_export.call_args[0]
        assert len(call_args[0]) == 3


class TestExportIslandTerrainEdgeCases:
    """Tests for edge cases in terrain export."""

    def test_export_skips_missing_objects(self, mock_bpy_module, mock_context):
        """Should skip terrain objects that don't exist in scene."""
        from blender_extension.core.data import Island
        from blender_extension.exporters.islands import export_island_terrain

        island = Island(
            id="test_island",
            name="Test Island",
            world_position=(0, 0, 0),
            world_rotation=(0, 0, 0, 1),
            bounds={"min": [0, 0, 0], "max": [10, 10, 10], "radius": 10.0},
            terrain_objects=["exists", "missing"],
        )

        mock_obj = MagicMock()
        mock_obj.name = "exists"
        mock_obj.type = "MESH"

        mock_context.scene.objects.get.side_effect = lambda name: (
            mock_obj if name == "exists" else None
        )

        with patch(
            "blender_extension.exporters.islands.export_objects_to_glb"
        ) as mock_export:
            with patch(
                "blender_extension.exporters.islands.get_export_subdir"
            ) as mock_subdir:
                mock_export.return_value = True
                mock_subdir.return_value = "/tmp/exports/islands/test_island/terrain"

                chunks, merged = export_island_terrain(
                    island, "/tmp/exports", mock_context, export_mode="individual"
                )

        # Should only export the one that exists
        assert len(chunks) == 1
        assert "islands/test_island/terrain/exists.glb" in chunks

    def test_export_returns_none_when_export_fails(self, mock_bpy_module, mock_context):
        """Should return None for merged when export fails."""
        from blender_extension.core.data import Island
        from blender_extension.exporters.islands import export_island_terrain

        island = Island(
            id="test_island",
            name="Test Island",
            world_position=(0, 0, 0),
            world_rotation=(0, 0, 0, 1),
            bounds={"min": [0, 0, 0], "max": [10, 10, 10], "radius": 10.0},
            terrain_objects=["terrain_chunk"],
        )

        mock_obj = MagicMock()
        mock_obj.name = "terrain_chunk"
        mock_obj.type = "MESH"

        mock_context.scene.objects.get.side_effect = lambda name: (
            mock_obj if name == "terrain_chunk" else None
        )

        with patch(
            "blender_extension.exporters.islands.export_objects_to_glb"
        ) as mock_export:
            with patch(
                "blender_extension.exporters.islands.get_export_subdir"
            ) as mock_subdir:
                mock_export.return_value = False  # Export fails
                mock_subdir.return_value = "/tmp/exports/islands/test_island/terrain"

                chunks, merged = export_island_terrain(
                    island, "/tmp/exports", mock_context, export_mode="merged"
                )

        assert chunks == []
        assert merged is None
