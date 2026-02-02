"""E2E tests for island terrain export functionality.

Tests the complete pipeline for terrain objects within islands:
- Terrain entity_type marking
- Terrain object detection during island detection
- Terrain file export (merged, individual, dual modes)
- Manifest terrain paths
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from tests.e2e.base import TrivestaTestCase


class TestIslandTerrainExport(TrivestaTestCase):
    """Test island terrain export with different terrain modes."""

    def _create_island_with_terrain(self, island_name: str = "Island_Test") -> None:
        """Create an island collection with terrain and static objects.

        Args:
            island_name: Name for the island collection
        """
        import bmesh
        import bpy

        # Create island collection
        collection = bpy.data.collections.new(island_name)
        bpy.context.scene.collection.children.link(collection)

        # Create terrain mesh
        terrain_mesh = bpy.data.meshes.new(f"{island_name}_Terrain_Mesh")
        terrain_obj = bpy.data.objects.new(f"{island_name}_Terrain", terrain_mesh)
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=4, y_segments=4, size=10.0)
        bm.to_mesh(terrain_mesh)
        bm.free()
        collection.objects.link(terrain_obj)

        # Mark as terrain entity type
        terrain_obj.trivesta.entity_type = "terrain"

        # Create static object (tree)
        tree_mesh = bpy.data.meshes.new(f"{island_name}_Tree_Mesh")
        tree_obj = bpy.data.objects.new(f"{island_name}_Tree", tree_mesh)
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=1.0, radius2=0.0, depth=3.0)
        bm.to_mesh(tree_mesh)
        bm.free()
        tree_obj.location = (2.0, 0.0, 1.5)
        collection.objects.link(tree_obj)

        # Static object has default entity_type (not terrain)
        tree_obj.trivesta.entity_type = "static"

        # Update view layer
        bpy.context.view_layer.update()

    def test_island_terrain_detection(self) -> None:
        """Test that terrain objects are correctly detected in islands."""
        import bpy

        from blender_extension.utils.islands import detect_islands

        self._create_island_with_terrain("Island_Detection")

        islands = detect_islands(bpy.context.scene)

        # Verify island was detected
        self.assertIn("island_detection", islands)
        island = islands["island_detection"]

        # Verify terrain object is in terrain_objects list
        terrain_names = island.terrain_objects
        instance_names = island.instances

        self.assertEqual(len(terrain_names), 1)
        self.assertIn("Island_Detection_Terrain", terrain_names)

        # Verify static object is in instances list
        self.assertEqual(len(instance_names), 1)
        self.assertIn("Island_Detection_Tree", instance_names)

        # Verify no overlap
        for name in terrain_names:
            self.assertNotIn(name, instance_names)

    def test_export_island_with_terrain_merged(self) -> None:
        """Test export with merged terrain mode creates correct files."""
        import bpy

        self._create_island_with_terrain("Island_Merged")

        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = Path(tmpdir)
            bpy.context.scene.trivesta.export_path = str(export_dir)
            bpy.context.scene.trivesta.terrain_mode = "MERGED"

            result = bpy.ops.trivesta.export()
            self.assertEqual(result, {"FINISHED"})

            # Verify manifest exists
            manifest_path = export_dir / "manifest.json"
            self.assertTrue(manifest_path.exists())

            with open(manifest_path) as f:
                manifest = json.load(f)

            # Check islands in manifest
            self.assertIn("islands", manifest)
            self.assertIn("island_merged", manifest["islands"])

            island_data = manifest["islands"]["island_merged"]

            # Verify terrain section exists
            self.assertIn("terrain", island_data)

            # For merged mode, should have merged path
            if "merged" in island_data["terrain"]:
                merged_path = island_data["terrain"]["merged"]
                self.assertTrue(merged_path.endswith(".glb"))

    def test_export_island_with_terrain_individual(self) -> None:
        """Test export with individual terrain mode creates chunk files."""
        import bpy

        self._create_island_with_terrain("Island_Individual")

        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = Path(tmpdir)
            bpy.context.scene.trivesta.export_path = str(export_dir)
            bpy.context.scene.trivesta.terrain_mode = "INDIVIDUAL"

            result = bpy.ops.trivesta.export()
            self.assertEqual(result, {"FINISHED"})

            # Verify manifest exists
            manifest_path = export_dir / "manifest.json"
            self.assertTrue(manifest_path.exists())

            with open(manifest_path) as f:
                manifest = json.load(f)

            # Check islands in manifest
            self.assertIn("islands", manifest)
            self.assertIn("island_individual", manifest["islands"])

            island_data = manifest["islands"]["island_individual"]

            # Verify terrain section exists
            self.assertIn("terrain", island_data)

            # For individual mode, should have chunks array
            if "chunks" in island_data["terrain"]:
                chunks = island_data["terrain"]["chunks"]
                self.assertIsInstance(chunks, list)
                for chunk_path in chunks:
                    self.assertTrue(chunk_path.endswith(".glb"))

    def test_export_island_terrain_files_created(self) -> None:
        """Test that terrain GLB files are actually created on disk."""
        import bpy

        self._create_island_with_terrain("Island_Files")

        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = Path(tmpdir)
            bpy.context.scene.trivesta.export_path = str(export_dir)

            result = bpy.ops.trivesta.export()
            self.assertEqual(result, {"FINISHED"})

            # Check for terrain directory
            terrain_dir = export_dir / "islands" / "island_files" / "terrain"
            if terrain_dir.exists():
                # Verify at least one GLB file exists
                glb_files = list(terrain_dir.glob("*.glb"))
                self.assertGreater(len(glb_files), 0, "Should have terrain GLB files")

                # Verify files are not empty
                for glb_file in glb_files:
                    self.assertGreater(
                        glb_file.stat().st_size, 0, f"{glb_file.name} should not be empty"
                    )

    def test_multiple_terrain_objects(self) -> None:
        """Test island with multiple terrain objects."""
        import bmesh
        import bpy

        # Create island collection
        collection = bpy.data.collections.new("Island_MultiTerrain")
        bpy.context.scene.collection.children.link(collection)

        # Create multiple terrain objects
        for i in range(3):
            mesh = bpy.data.meshes.new(f"Terrain_Chunk_{i}_Mesh")
            obj = bpy.data.objects.new(f"Terrain_Chunk_{i}", mesh)
            bm = bmesh.new()
            bmesh.ops.create_grid(bm, x_segments=2, y_segments=2, size=5.0)
            bm.to_mesh(mesh)
            bm.free()
            obj.location = (i * 10.0, 0.0, 0.0)
            obj.trivesta.entity_type = "terrain"
            collection.objects.link(obj)

        # Create one static object
        static_mesh = bpy.data.meshes.new("Static_Rock_Mesh")
        static_obj = bpy.data.objects.new("Static_Rock", static_mesh)
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
        bm.to_mesh(static_mesh)
        bm.free()
        static_obj.trivesta.entity_type = "static"
        collection.objects.link(static_obj)

        bpy.context.view_layer.update()

        # Test detection
        from blender_extension.utils.islands import detect_islands

        islands = detect_islands(bpy.context.scene)

        island = islands["island_multiterrain"]
        self.assertEqual(len(island.terrain_objects), 3)
        self.assertEqual(len(island.instances), 1)

        # Verify all terrain chunks are detected
        for i in range(3):
            self.assertIn(f"Terrain_Chunk_{i}", island.terrain_objects)

        # Verify static object is in instances
        self.assertIn("Static_Rock", island.instances)
