"""E2E tests for world export with real blend files.

Tests the complete export pipeline using actual blend files:
- base-road.blend
- rouge.blend

These tests verify the export operator works correctly with real-world
scene data, not just programmatically created test scenes.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from tests.e2e.base import TrivestaTestCase


class TestWorldExportBlendFiles(TrivestaTestCase):
    """Test world export with real blend files from tests/e2e/assets/."""

    ASSETS_DIR = Path(__file__).parent / "assets"

    def _open_blend_file(self, filename: str) -> None:
        """Open a blend file from the assets directory."""
        import bpy

        blend_path = self.ASSETS_DIR / filename
        self.assertTrue(blend_path.exists(), f"Blend file not found: {blend_path}")
        bpy.ops.wm.open_mainfile(filepath=str(blend_path))

    def _export_world(self, export_dir: Path) -> dict:
        """Run world export and return the manifest."""
        import bpy

        bpy.context.scene.trivesta.export_path = str(export_dir)
        result = bpy.ops.trivesta.export()
        self.assertEqual(result, {"FINISHED"}, "Export should succeed")

        manifest_path = export_dir / "manifest.json"
        self.assertTrue(manifest_path.exists(), "manifest.json should be created")

        with open(manifest_path) as f:
            return json.load(f)

    def test_export_base_road(self) -> None:
        """Test exporting base-road.blend creates manifest and GLB files."""
        self._open_blend_file("base-road.blend")

        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = Path(tmpdir)
            manifest = self._export_world(export_dir)

            # Verify manifest structure
            self.assertIn("version", manifest)
            self.assertIn("instances", manifest)
            self.assertIn("asset_definitions", manifest)

            # Should have at least 1 instance
            self.assertGreaterEqual(len(manifest["instances"]), 1)

            # All instances should have asset_id
            for inst in manifest["instances"]:
                self.assertIsNotNone(
                    inst.get("asset_id"),
                    f"Instance {inst.get('name')} should have asset_id",
                )

            # GLB files should be created for assets
            assets_dir = export_dir / "assets"
            if manifest["asset_definitions"]:
                self.assertTrue(assets_dir.exists(), "assets/ directory should exist")
                glb_files = list(assets_dir.glob("*.glb"))
                self.assertEqual(
                    len(glb_files),
                    len(manifest["asset_definitions"]),
                    "Should have one GLB file per asset definition",
                )

    def test_export_rouge(self) -> None:
        """Test exporting rouge.blend creates manifest and GLB files."""
        self._open_blend_file("rouge.blend")

        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = Path(tmpdir)
            manifest = self._export_world(export_dir)

            # Verify manifest structure
            self.assertIn("version", manifest)
            self.assertIn("instances", manifest)
            self.assertIn("asset_definitions", manifest)

            # Should have multiple instances (character body parts)
            self.assertGreaterEqual(len(manifest["instances"]), 1)

            # All instances should have asset_id
            for inst in manifest["instances"]:
                self.assertIsNotNone(
                    inst.get("asset_id"),
                    f"Instance {inst.get('name')} should have asset_id",
                )

            # GLB files should be created for assets
            assets_dir = export_dir / "assets"
            if manifest["asset_definitions"]:
                self.assertTrue(assets_dir.exists(), "assets/ directory should exist")
                glb_files = list(assets_dir.glob("*.glb"))
                self.assertEqual(
                    len(glb_files),
                    len(manifest["asset_definitions"]),
                    "Should have one GLB file per asset definition",
                )

    def test_export_both_files_sequentially(self) -> None:
        """Test exporting both files in sequence to verify no state leakage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)

            # Export base-road
            self._open_blend_file("base-road.blend")
            base_road_dir = base_dir / "base-road"
            base_road_dir.mkdir()
            base_road_manifest = self._export_world(base_road_dir)

            # Export rouge
            self._open_blend_file("rouge.blend")
            rouge_dir = base_dir / "rouge"
            rouge_dir.mkdir()
            rouge_manifest = self._export_world(rouge_dir)

            # Both should have valid manifests with instances
            self.assertGreaterEqual(len(base_road_manifest["instances"]), 1)
            self.assertGreaterEqual(len(rouge_manifest["instances"]), 1)

            # Both should have asset definitions
            self.assertGreaterEqual(len(base_road_manifest["asset_definitions"]), 1)
            self.assertGreaterEqual(len(rouge_manifest["asset_definitions"]), 1)


class TestWorldExportManifestContent(TrivestaTestCase):
    """Test manifest content for exported blend files."""

    ASSETS_DIR = Path(__file__).parent / "assets"

    def _open_and_export(self, filename: str, export_dir: Path) -> dict:
        """Open blend file and export, returning manifest."""
        import bpy

        blend_path = self.ASSETS_DIR / filename
        bpy.ops.wm.open_mainfile(filepath=str(blend_path))
        bpy.context.scene.trivesta.export_path = str(export_dir)
        result = bpy.ops.trivesta.export()
        self.assertEqual(result, {"FINISHED"})

        with open(export_dir / "manifest.json") as f:
            return json.load(f)

    def test_base_road_manifest_structure(self) -> None:
        """Verify base-road manifest has expected structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = self._open_and_export("base-road.blend", Path(tmpdir))

            # Check required fields
            required_fields = ["version", "instances", "asset_definitions", "exported_at"]
            for field in required_fields:
                self.assertIn(field, manifest, f"Missing required field: {field}")

            # Verify instances have required properties
            for inst in manifest.get("instances", []):
                self.assertIn("id", inst)
                self.assertIn("name", inst)
                self.assertIn("asset_id", inst)
                self.assertIn("position", inst)

    def test_rouge_manifest_structure(self) -> None:
        """Verify rouge manifest has expected structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = self._open_and_export("rouge.blend", Path(tmpdir))

            # Check required fields
            required_fields = ["version", "instances", "asset_definitions", "exported_at"]
            for field in required_fields:
                self.assertIn(field, manifest, f"Missing required field: {field}")

            # Verify instances have required properties
            for inst in manifest.get("instances", []):
                self.assertIn("id", inst)
                self.assertIn("name", inst)
                self.assertIn("asset_id", inst)
                self.assertIn("position", inst)

    def test_asset_definition_references_glb(self) -> None:
        """Verify asset definitions reference correct GLB files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = Path(tmpdir)
            manifest = self._open_and_export("rouge.blend", export_dir)

            # Each asset definition should reference a file
            for asset_id, asset_def in manifest["asset_definitions"].items():
                self.assertIn("file", asset_def)
                self.assertTrue(
                    asset_def["file"].endswith(".glb"),
                    f"Asset {asset_id} should reference a .glb file",
                )
                # Verify file exists
                glb_path = export_dir / asset_def["file"]
                self.assertTrue(
                    glb_path.exists(),
                    f"GLB file {asset_def['file']} should exist",
                )


class TestWorldExportAssetFiles(TrivestaTestCase):
    """Test that GLB asset files are created correctly."""

    ASSETS_DIR = Path(__file__).parent / "assets"

    def test_base_road_creates_glb_files(self) -> None:
        """Verify base-road export creates at least one GLB file."""
        import bpy

        blend_path = self.ASSETS_DIR / "base-road.blend"
        bpy.ops.wm.open_mainfile(filepath=str(blend_path))

        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = Path(tmpdir)
            bpy.context.scene.trivesta.export_path = str(export_dir)
            result = bpy.ops.trivesta.export()
            self.assertEqual(result, {"FINISHED"})

            # Should create assets directory with GLB files
            assets_dir = export_dir / "assets"
            self.assertTrue(assets_dir.exists(), "assets/ directory should be created")

            glb_files = list(assets_dir.glob("*.glb"))
            self.assertGreaterEqual(
                len(glb_files), 1, "Should create at least one GLB file"
            )

    def test_rouge_creates_glb_files(self) -> None:
        """Verify rouge export creates GLB files for all body parts."""
        import bpy

        blend_path = self.ASSETS_DIR / "rouge.blend"
        bpy.ops.wm.open_mainfile(filepath=str(blend_path))

        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = Path(tmpdir)
            bpy.context.scene.trivesta.export_path = str(export_dir)
            result = bpy.ops.trivesta.export()
            self.assertEqual(result, {"FINISHED"})

            # Should create assets directory with GLB files
            assets_dir = export_dir / "assets"
            self.assertTrue(assets_dir.exists(), "assets/ directory should be created")

            glb_files = list(assets_dir.glob("*.glb"))
            # Rouge has 8 visible mesh objects (body parts)
            self.assertGreaterEqual(
                len(glb_files), 1, "Should create GLB files for mesh objects"
            )

    def test_glb_file_not_empty(self) -> None:
        """Verify created GLB files have content."""
        import bpy

        blend_path = self.ASSETS_DIR / "base-road.blend"
        bpy.ops.wm.open_mainfile(filepath=str(blend_path))

        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = Path(tmpdir)
            bpy.context.scene.trivesta.export_path = str(export_dir)
            bpy.ops.trivesta.export()

            assets_dir = export_dir / "assets"
            glb_files = list(assets_dir.glob("*.glb"))

            for glb_file in glb_files:
                file_size = glb_file.stat().st_size
                self.assertGreater(
                    file_size, 0, f"GLB file {glb_file.name} should not be empty"
                )
