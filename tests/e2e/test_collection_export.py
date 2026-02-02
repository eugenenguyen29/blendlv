"""E2E tests for collection instance export functionality.

Tests the complete pipeline from collection creation through entity extraction.
Validates that collection instances (EMPTY objects with instance_type='COLLECTION')
are correctly identified, extracted, and exported.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from tests.e2e.base import TrivestaTestCase
from tests.e2e.helpers import (
    create_collection_instance,
    create_collection_with_cube,
    create_empty_collection,
)


class TestCollectionInstanceCreation(TrivestaTestCase):
    """Test collection instance creation in Blender."""

    def test_create_collection_instance(self) -> None:
        """Test creating a collection instance in Blender."""
        import bmesh
        import bpy

        # Create collection with cube
        collection = bpy.data.collections.new("TestCollection")
        bpy.context.scene.collection.children.link(collection)

        # Add cube to collection using bmesh (more reliable than bpy.ops)
        mesh = bpy.data.meshes.new("TestCube_Mesh")
        cube = bpy.data.objects.new("TestCube", mesh)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bm.to_mesh(mesh)
        bm.free()
        collection.objects.link(cube)

        # Create collection instance
        empty = bpy.data.objects.new(name="TestInstance", object_data=None)
        empty.instance_type = "COLLECTION"
        empty.instance_collection = collection
        bpy.context.scene.collection.objects.link(empty)

        # Verify instance properties
        self.assertEqual(empty.type, "EMPTY")
        self.assertEqual(empty.instance_type, "COLLECTION")
        self.assertEqual(empty.instance_collection, collection)

    def test_create_instance_with_helper(self) -> None:
        """Test creating collection instance using helper functions."""
        collection = create_collection_with_cube("HelperTest")
        instance = create_collection_instance(collection, location=(5.0, 3.0, 1.0))

        self.assertEqual(instance.type, "EMPTY")
        self.assertEqual(instance.instance_type, "COLLECTION")
        self.assertEqual(instance.instance_collection, collection)
        self.assertEqual(tuple(instance.location), (5.0, 3.0, 1.0))


class TestCollectionExtractorMatching(TrivestaTestCase):
    """Test CollectionExtractor matching behavior."""

    def test_collection_extractor_matches(self) -> None:
        """Test that CollectionExtractor matches collection instances."""
        import bpy

        from blender_extension.entities.collection import CollectionExtractor

        # Create collection instance
        collection = bpy.data.collections.new("TestCollection")
        bpy.context.scene.collection.children.link(collection)

        empty = bpy.data.objects.new(name="TestInstance", object_data=None)
        empty.instance_type = "COLLECTION"
        empty.instance_collection = collection
        bpy.context.scene.collection.objects.link(empty)

        # Test extractor
        extractor = CollectionExtractor()
        self.assertTrue(extractor.matches(empty))

    def test_collection_extractor_rejects_mesh(self) -> None:
        """Test that CollectionExtractor rejects mesh objects."""
        import bmesh
        import bpy

        from blender_extension.entities.collection import CollectionExtractor

        # Create mesh object using bmesh
        mesh = bpy.data.meshes.new("TestMesh")
        cube = bpy.data.objects.new("TestCube", mesh)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bm.to_mesh(mesh)
        bm.free()
        bpy.context.scene.collection.objects.link(cube)

        # Test extractor
        extractor = CollectionExtractor()
        self.assertFalse(extractor.matches(cube))

    def test_collection_extractor_rejects_empty_without_collection(self) -> None:
        """Test that CollectionExtractor rejects EMPTY without collection."""
        import bpy

        from blender_extension.entities.collection import CollectionExtractor

        # Create plain empty (no collection instance)
        empty = bpy.data.objects.new(name="PlainEmpty", object_data=None)
        bpy.context.scene.collection.objects.link(empty)

        # Test extractor
        extractor = CollectionExtractor()
        self.assertFalse(extractor.matches(empty))


class TestCollectionExtraction(TrivestaTestCase):
    """Test collection instance data extraction."""

    def test_extract_collection_instance(self) -> None:
        """Test extracting data from collection instance."""
        import bmesh
        import bpy

        from blender_extension.entities.collection import CollectionExtractor

        # Create collection with cube using bmesh
        collection = bpy.data.collections.new("TestCollection")
        bpy.context.scene.collection.children.link(collection)

        mesh = bpy.data.meshes.new("ExtractTestCube_Mesh")
        cube = bpy.data.objects.new("ExtractTestCube", mesh)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bm.to_mesh(mesh)
        bm.free()
        collection.objects.link(cube)

        # Create instance at specific location
        empty = bpy.data.objects.new(name="TestInstance", object_data=None)
        empty.instance_type = "COLLECTION"
        empty.instance_collection = collection
        empty.location = (1.0, 2.0, 3.0)
        bpy.context.scene.collection.objects.link(empty)

        # Update view layer to sync transforms
        bpy.context.view_layer.update()

        # Extract
        extractor = CollectionExtractor()
        instance = extractor.extract(empty)

        # Verify instance data
        self.assertEqual(instance.name, "TestInstance")
        self.assertIsNotNone(instance.asset_id)
        # Position is converted to Three.js Y-up coords: (x, z, -y)
        # Blender (1.0, 2.0, 3.0) -> Three.js [1.0, 3.0, -2.0]
        self.assertEqual(instance.position[0], 1.0)  # x stays x
        self.assertEqual(instance.position[1], 3.0)  # z -> y
        self.assertEqual(instance.position[2], -2.0)  # -y -> z
        self.assertEqual(instance.entity_type, "static")

    def test_asset_key_generation_local_collection(self) -> None:
        """Test asset key generation for local collections."""
        import bpy

        from blender_extension.entities.collection import CollectionExtractor

        # Create local collection (use underscore in name for sanitization test)
        collection = bpy.data.collections.new("My_Collection")
        bpy.context.scene.collection.children.link(collection)

        empty = bpy.data.objects.new(name="Instance", object_data=None)
        empty.instance_type = "COLLECTION"
        empty.instance_collection = collection
        bpy.context.scene.collection.objects.link(empty)

        # Extract and verify asset_id
        extractor = CollectionExtractor()
        instance = extractor.extract(empty)

        # Local collection should use collection name (sanitized: lowercase, underscore kept)
        self.assertEqual(instance.asset_id, "my_collection")

    def test_multiple_instances_same_collection(self) -> None:
        """Test multiple instances of the same collection share asset_id."""
        import bpy

        from blender_extension.entities.collection import CollectionExtractor

        # Create collection
        collection = bpy.data.collections.new("SharedCollection")
        bpy.context.scene.collection.children.link(collection)

        # Create two instances
        empty1 = bpy.data.objects.new(name="Instance1", object_data=None)
        empty1.instance_type = "COLLECTION"
        empty1.instance_collection = collection
        empty1.location = (0, 0, 0)
        bpy.context.scene.collection.objects.link(empty1)

        empty2 = bpy.data.objects.new(name="Instance2", object_data=None)
        empty2.instance_type = "COLLECTION"
        empty2.instance_collection = collection
        empty2.location = (5, 0, 0)
        bpy.context.scene.collection.objects.link(empty2)

        # Extract both
        extractor = CollectionExtractor()
        instance1 = extractor.extract(empty1)
        instance2 = extractor.extract(empty2)

        # Verify same asset_id
        self.assertEqual(instance1.asset_id, instance2.asset_id)
        self.assertNotEqual(instance1.id, instance2.id)  # Different instance IDs


class TestBoundingBoxCalculation(TrivestaTestCase):
    """Test bounding box calculation for collection instances."""

    def test_bounding_box_calculation(self) -> None:
        """Test bounding box calculation for collection instances."""
        import bmesh
        import bpy

        from blender_extension.entities.collection import CollectionExtractor

        # Create collection with scaled cube using bmesh
        collection = bpy.data.collections.new("BBoxTest")
        bpy.context.scene.collection.children.link(collection)

        mesh = bpy.data.meshes.new("BBoxCube_Mesh")
        cube = bpy.data.objects.new("BBoxCube", mesh)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=2.0)  # Create 2x2x2 cube directly
        bm.to_mesh(mesh)
        bm.free()
        collection.objects.link(cube)

        # Create instance
        empty = bpy.data.objects.new(name="BBoxInstance", object_data=None)
        empty.instance_type = "COLLECTION"
        empty.instance_collection = collection
        bpy.context.scene.collection.objects.link(empty)

        # Extract and verify bounding box
        extractor = CollectionExtractor()
        instance = extractor.extract(empty)

        self.assertIsNotNone(instance.bounding_box)
        self.assertIn("min", instance.bounding_box)
        self.assertIn("max", instance.bounding_box)
        self.assertIn("radius", instance.bounding_box)
        # Verify radius is positive for non-empty collection
        self.assertGreater(instance.bounding_box["radius"], 0)

    def test_empty_collection_bounding_box(self) -> None:
        """Test bounding box for empty collection."""
        from blender_extension.entities.collection import CollectionExtractor

        # Create empty collection
        collection = create_empty_collection("EmptyBBoxTest")

        # Create instance
        instance_obj = create_collection_instance(collection, name="EmptyBBoxInstance")

        # Extract
        extractor = CollectionExtractor()
        instance = extractor.extract(instance_obj)

        # Empty collection should have zero-size bbox
        self.assertEqual(instance.bounding_box["min"], [0, 0, 0])
        self.assertEqual(instance.bounding_box["max"], [0, 0, 0])
        self.assertEqual(instance.bounding_box["radius"], 0.0)


class TestExtractAllWithCollections(TrivestaTestCase):
    """Test extract_all() includes collection instances."""

    def test_extract_all_includes_collection_instances(self) -> None:
        """Test that extract_all() processes collection instances."""
        import bpy

        from blender_extension.entities import extract_all, register_extractors

        # Register extractors
        register_extractors()

        # Create collection with cube
        collection = create_collection_with_cube("ExtractAllTest")

        # Create collection instance
        instance_obj = create_collection_instance(collection)
        instance_obj.hide_set(False)  # Ensure visible

        # Run extract_all
        instances, terrain, collision = extract_all(bpy.context)

        # Find our collection instance in results
        collection_instances = [inst for inst in instances if inst.name == instance_obj.name]

        self.assertEqual(
            len(collection_instances),
            1,
            f"Expected 1 collection instance, got {len(collection_instances)}. "
            f"All instances: {[i.name for i in instances]}",
        )

    def test_extract_all_mixed_scene(self) -> None:
        """Test extract_all() handles mixed scene with mesh and collection instances."""
        import bmesh
        import bpy

        from blender_extension.entities import extract_all, register_extractors

        # Register extractors
        register_extractors()

        # Create regular mesh object using bmesh (sphere via icosphere)
        mesh = bpy.data.meshes.new("RegularSphere_Mesh")
        sphere = bpy.data.objects.new("RegularSphere", mesh)
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
        bm.to_mesh(mesh)
        bm.free()
        bpy.context.scene.collection.objects.link(sphere)

        # Create collection instance
        collection = create_collection_with_cube("MixedTest")
        create_collection_instance(collection, name="MixedInstance")

        # Run extract_all
        instances, terrain, collision = extract_all(bpy.context)

        # Both should be extracted
        names = [inst.name for inst in instances]
        self.assertIn("RegularSphere", names, f"Sphere not found in: {names}")
        self.assertIn("MixedInstance", names, f"Collection instance not found in: {names}")


class TestEmptyCollectionHandling(TrivestaTestCase):
    """Test handling of empty collections."""

    def test_empty_collection_instance(self) -> None:
        """Test collection instance with no objects."""
        from blender_extension.entities.collection import CollectionExtractor

        # Create empty collection (use underscore for sanitization check)
        collection = create_empty_collection("Empty_Collection")

        # Create instance
        instance_obj = create_collection_instance(collection, name="EmptyInstance")

        # Extract
        extractor = CollectionExtractor()
        instance = extractor.extract(instance_obj)

        # Should still extract, but with minimal bounding box
        self.assertIsNotNone(instance.asset_id)
        self.assertEqual(instance.name, "EmptyInstance")
        # Sanitized: lowercase, underscore kept
        self.assertEqual(instance.asset_id, "empty_collection")


class TestCollectionExportPipeline(TrivestaTestCase):
    """Test full export pipeline with collection instances."""

    def test_export_collection_instance_to_glb(self) -> None:
        """Test full export pipeline with collection instance."""
        import bpy

        # Create collection with cube
        collection = create_collection_with_cube("ExportTest")

        # Create instance at specific location
        instance = create_collection_instance(collection, location=(2.0, 3.0, 4.0))

        # Export to temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = Path(tmpdir)

            # Set the export path on the scene (the operator reads from here)
            bpy.context.scene.trivesta.export_path = str(export_dir)

            # Run export operator (no filepath param - reads from scene)
            result = bpy.ops.trivesta.export()
            self.assertEqual(result, {"FINISHED"})

            # Verify manifest exists
            manifest_path = export_dir / "manifest.json"
            self.assertTrue(manifest_path.exists(), "manifest.json should exist")

            # Read and verify manifest structure
            with open(manifest_path) as f:
                manifest = json.load(f)

            self.assertIn("instances", manifest)
            self.assertIn("asset_definitions", manifest)

            # Find collection instance in manifest
            collection_instances = [
                inst for inst in manifest["instances"] if inst.get("name") == instance.name
            ]
            self.assertEqual(
                len(collection_instances),
                1,
                f"Expected 1 instance named '{instance.name}', found {len(collection_instances)}",
            )

            # Verify instance data
            inst_data = collection_instances[0]
            asset_id = inst_data.get("asset_id")
            self.assertIsNotNone(asset_id, "Instance must have asset_id")

            # Verify asset definition exists
            self.assertIn(asset_id, manifest["asset_definitions"])

            # Verify GLB file referenced
            asset_def = manifest["asset_definitions"][asset_id]
            self.assertIn("file", asset_def)
