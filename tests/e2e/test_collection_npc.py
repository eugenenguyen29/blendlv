"""E2E tests for collection instances configured as NPCs.

These tests verify the complete pipeline:
1. Create collection instance (EMPTY with instance_type='COLLECTION')
2. Configure as NPC/Interactive via Trivesta panel
3. Add dialog lines or script_id
4. Export to JSON manifest
5. Verify data is correctly serialized
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from tests.e2e.base import TrivestaTestCase
from tests.e2e.helpers import (
    create_collection_instance,
    create_collection_with_cube,
)


class TestCollectionInstanceNPC(TrivestaTestCase):
    """E2E tests for collection instances as NPCs."""

    def test_collection_instance_npc_dialog_export(self) -> None:
        """Should export dialog lines for collection instance configured as NPC."""
        import bpy

        # Create a simple collection
        collection = create_collection_with_cube("NPC_Guard")

        # Create collection instance (EMPTY that instances the collection)
        empty = create_collection_instance(collection, name="Guard_Instance")

        # Configure as NPC with dialog
        empty.trivesta.entity_type = "npc"
        line1 = empty.trivesta.dialog_lines.add()
        line1.speaker = "Guard"
        line1.text = "Halt! State your business."
        line2 = empty.trivesta.dialog_lines.add()
        line2.speaker = "Guard"
        line2.text = "Very well, proceed."

        # Export to temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = Path(tmpdir)

            # Set the export path on the scene
            bpy.context.scene.trivesta.export_path = str(export_dir)

            # Run export operator
            result = bpy.ops.trivesta.export()
            self.assertEqual(result, {"FINISHED"})

            # Verify manifest exists
            manifest_path = export_dir / "manifest.json"
            self.assertTrue(manifest_path.exists(), "Manifest should be created")

            # Parse and verify
            with open(manifest_path) as f:
                data = json.load(f)

            # Find the guard instance
            guard = None
            for instance in data.get("instances", []):
                if instance["name"] == "Guard_Instance":
                    guard = instance
                    break

            self.assertIsNotNone(guard, "Guard instance should be in manifest")
            assert guard is not None  # Type narrowing
            self.assertEqual(guard["entity_type"], "npc")

            # Verify dialog was serialized
            self.assertIn("dialog", guard["custom_properties"])
            dialog = guard["custom_properties"]["dialog"]
            self.assertEqual(len(dialog), 2)
            self.assertEqual(dialog[0]["speaker"], "Guard")
            self.assertEqual(dialog[0]["text"], "Halt! State your business.")
            self.assertEqual(dialog[1]["speaker"], "Guard")
            self.assertEqual(dialog[1]["text"], "Very well, proceed.")

    def test_collection_instance_interactive_script_export(self) -> None:
        """Should export script_id for collection instance configured as Interactive."""
        import bpy

        # Create collection with object
        collection = create_collection_with_cube("Door")

        # Create collection instance
        empty = create_collection_instance(collection, name="Door_Instance")

        # Configure as Interactive with script_id
        empty.trivesta.entity_type = "interactive"
        empty.trivesta.script_id = "door_open_close"

        # Export to temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = Path(tmpdir)

            bpy.context.scene.trivesta.export_path = str(export_dir)

            result = bpy.ops.trivesta.export()
            self.assertEqual(result, {"FINISHED"})

            # Verify manifest
            manifest_path = export_dir / "manifest.json"
            self.assertTrue(manifest_path.exists(), "Manifest should be created")

            with open(manifest_path) as f:
                data = json.load(f)

            # Find door instance
            door = None
            for instance in data.get("instances", []):
                if instance["name"] == "Door_Instance":
                    door = instance
                    break

            self.assertIsNotNone(door, "Door instance should be in manifest")
            assert door is not None  # Type narrowing
            self.assertEqual(door["entity_type"], "interactive")
            self.assertIn("script_id", door["custom_properties"])
            self.assertEqual(door["custom_properties"]["script_id"], "door_open_close")

    def test_collection_instance_static_no_dialog(self) -> None:
        """Should not export dialog for collection instance with entity_type='static'."""
        import bpy

        # Create collection
        collection = create_collection_with_cube("StaticProp")

        # Create instance
        empty = create_collection_instance(collection, name="Prop_Instance")

        # Set as static explicitly and add dialog anyway (should be ignored)
        empty.trivesta.entity_type = "static"
        line = empty.trivesta.dialog_lines.add()
        line.speaker = "Test"
        line.text = "Should not export"

        # Export to temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = Path(tmpdir)

            bpy.context.scene.trivesta.export_path = str(export_dir)

            result = bpy.ops.trivesta.export()
            self.assertEqual(result, {"FINISHED"})

            # Verify manifest
            manifest_path = export_dir / "manifest.json"
            with open(manifest_path) as f:
                data = json.load(f)

            # Find prop instance
            prop = None
            for instance in data.get("instances", []):
                if instance["name"] == "Prop_Instance":
                    prop = instance
                    break

            self.assertIsNotNone(prop, "Prop instance should be in manifest")
            assert prop is not None  # Type narrowing
            self.assertEqual(prop["entity_type"], "static")
            # Dialog should NOT be in custom_properties
            self.assertNotIn("dialog", prop.get("custom_properties", {}))

    def test_panel_visible_for_collection_instance(self) -> None:
        """Verify Trivesta panel is accessible for collection instances."""
        import bpy

        # Create collection
        collection = create_collection_with_cube("TestCollection")

        # Create instance
        empty = create_collection_instance(collection, name="Test_Instance")

        # Select the empty
        bpy.context.view_layer.objects.active = empty
        empty.select_set(True)

        # Import panel class
        from blender_extension.panels.object import TRIVESTA_PT_object_panel

        # Test poll() - should return True
        self.assertTrue(
            TRIVESTA_PT_object_panel.poll(bpy.context),
            "Panel should be visible for collection instances",
        )

        # Verify trivesta properties are accessible
        self.assertTrue(hasattr(empty, "trivesta"))
        self.assertIsNotNone(empty.trivesta)


if __name__ == "__main__":
    import unittest

    unittest.main()
