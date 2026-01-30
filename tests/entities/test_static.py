"""Tests for StaticExtractor dialog and script_id export in blender_extension.entities.static.

Tests verify that dialog_lines and script_id from TrivestaObjectSettings
are correctly serialized into Instance.custom_properties during extraction.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_transforms():
    """Mock transform utility functions for isolated testing."""
    with (
        patch("blender_extension.entities.static.get_object_transform") as mock_transform,
        patch("blender_extension.entities.static.get_bounding_box") as mock_bbox,
        patch("blender_extension.entities.static.get_custom_properties") as mock_custom_props,
    ):
        mock_transform.return_value = {
            "position": [0.0, 0.0, 0.0],
            "rotation": [0.0, 0.0, 0.0, 1.0],
            "scale": [1.0, 1.0, 1.0],
        }
        mock_bbox.return_value = {"min": [0, 0, 0], "max": [1, 1, 1], "radius": 1.0}
        mock_custom_props.return_value = {}
        yield {
            "transform": mock_transform,
            "bbox": mock_bbox,
            "custom_props": mock_custom_props,
        }


class TestStaticExtractorDialogExport:
    """Tests for dialog export in StaticExtractor."""

    def test_extract_npc_with_dialog_lines(
        self,
        mock_bpy_module: MagicMock,
        mock_object: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Should export dialog array in custom_properties for NPC."""
        from blender_extension.entities.static import StaticExtractor

        # Setup mock trivesta settings
        mock_settings = MagicMock()
        mock_settings.entity_type = "npc"
        mock_settings.is_terrain = False
        mock_settings.is_collision = False

        # Mock dialog lines
        line1 = MagicMock()
        line1.speaker = "Guard"
        line1.text = "Halt!"
        line2 = MagicMock()
        line2.speaker = "Guard"
        line2.text = "Who goes there?"

        mock_settings.dialog_lines = [line1, line2]
        mock_settings.script_id = ""
        mock_object.trivesta = mock_settings

        extractor = StaticExtractor()
        instance = extractor.extract(mock_object)

        assert "dialog" in instance.custom_properties
        assert len(instance.custom_properties["dialog"]) == 2
        assert instance.custom_properties["dialog"][0]["speaker"] == "Guard"
        assert instance.custom_properties["dialog"][0]["text"] == "Halt!"

    def test_extract_npc_with_empty_dialog(
        self,
        mock_bpy_module: MagicMock,
        mock_object: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Should omit dialog key when NPC has no dialog lines."""
        from blender_extension.entities.static import StaticExtractor

        mock_settings = MagicMock()
        mock_settings.entity_type = "npc"
        mock_settings.is_terrain = False
        mock_settings.is_collision = False
        mock_settings.dialog_lines = []  # Empty dialog
        mock_settings.script_id = ""
        mock_object.trivesta = mock_settings

        extractor = StaticExtractor()
        instance = extractor.extract(mock_object)

        assert "dialog" not in instance.custom_properties

    def test_extract_interactive_with_script_id(
        self,
        mock_bpy_module: MagicMock,
        mock_object: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Should export script_id in custom_properties for Interactive."""
        from blender_extension.entities.static import StaticExtractor

        mock_settings = MagicMock()
        mock_settings.entity_type = "interactive"
        mock_settings.is_terrain = False
        mock_settings.is_collision = False
        mock_settings.script_id = "chest_open_handler"
        mock_settings.dialog_lines = []
        mock_object.trivesta = mock_settings

        extractor = StaticExtractor()
        instance = extractor.extract(mock_object)

        assert "script_id" in instance.custom_properties
        assert instance.custom_properties["script_id"] == "chest_open_handler"

    def test_extract_interactive_with_empty_script_id(
        self,
        mock_bpy_module: MagicMock,
        mock_object: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Should omit script_id key when Interactive has empty script_id."""
        from blender_extension.entities.static import StaticExtractor

        mock_settings = MagicMock()
        mock_settings.entity_type = "interactive"
        mock_settings.is_terrain = False
        mock_settings.is_collision = False
        mock_settings.script_id = ""  # Empty script_id
        mock_settings.dialog_lines = []
        mock_object.trivesta = mock_settings

        extractor = StaticExtractor()
        instance = extractor.extract(mock_object)

        assert "script_id" not in instance.custom_properties

    def test_dialog_serializes_speaker_and_text(
        self,
        mock_bpy_module: MagicMock,
        mock_object: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Dialog lines should include both speaker and text fields."""
        from blender_extension.entities.static import StaticExtractor

        mock_settings = MagicMock()
        mock_settings.entity_type = "npc"
        mock_settings.is_terrain = False
        mock_settings.is_collision = False

        line = MagicMock()
        line.speaker = "Merchant"
        line.text = "Welcome to my shop!"

        mock_settings.dialog_lines = [line]
        mock_settings.script_id = ""
        mock_object.trivesta = mock_settings

        extractor = StaticExtractor()
        instance = extractor.extract(mock_object)

        dialog_line = instance.custom_properties["dialog"][0]
        assert "speaker" in dialog_line
        assert "text" in dialog_line
        assert dialog_line["speaker"] == "Merchant"
        assert dialog_line["text"] == "Welcome to my shop!"

    def test_dialog_preserves_order(
        self,
        mock_bpy_module: MagicMock,
        mock_object: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Dialog lines should be exported in correct order."""
        from blender_extension.entities.static import StaticExtractor

        mock_settings = MagicMock()
        mock_settings.entity_type = "npc"
        mock_settings.is_terrain = False
        mock_settings.is_collision = False

        lines = []
        for i in range(5):
            line = MagicMock()
            line.speaker = f"Speaker{i}"
            line.text = f"Line {i}"
            lines.append(line)

        mock_settings.dialog_lines = lines
        mock_settings.script_id = ""
        mock_object.trivesta = mock_settings

        extractor = StaticExtractor()
        instance = extractor.extract(mock_object)

        dialog = instance.custom_properties["dialog"]
        for i in range(5):
            assert dialog[i]["speaker"] == f"Speaker{i}"
            assert dialog[i]["text"] == f"Line {i}"

    def test_static_entity_no_dialog_or_script(
        self,
        mock_bpy_module: MagicMock,
        mock_object: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Static entity type should not have dialog or script_id keys."""
        from blender_extension.entities.static import StaticExtractor

        mock_settings = MagicMock()
        mock_settings.entity_type = "static"
        mock_settings.is_terrain = False
        mock_settings.is_collision = False
        mock_settings.dialog_lines = []
        mock_settings.script_id = ""
        mock_object.trivesta = mock_settings

        extractor = StaticExtractor()
        instance = extractor.extract(mock_object)

        assert "dialog" not in instance.custom_properties
        assert "script_id" not in instance.custom_properties


class TestStaticExtractorMixedProperties:
    """Tests for mixed custom properties with dialog/script_id."""

    def test_npc_with_dialog_preserves_other_custom_properties(
        self,
        mock_bpy_module: MagicMock,
        mock_object: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """NPC with dialog should also include other custom properties."""
        from blender_extension.entities.static import StaticExtractor

        mock_settings = MagicMock()
        mock_settings.entity_type = "npc"
        mock_settings.is_terrain = False
        mock_settings.is_collision = False

        line = MagicMock()
        line.speaker = "Shopkeeper"
        line.text = "Hello!"
        mock_settings.dialog_lines = [line]
        mock_settings.script_id = ""
        mock_object.trivesta = mock_settings

        # Mock get_custom_properties to return existing custom property
        mock_transforms["custom_props"].return_value = {"shop_type": "weapons"}

        extractor = StaticExtractor()
        instance = extractor.extract(mock_object)

        # Dialog should be present
        assert "dialog" in instance.custom_properties
        # Custom property should also be preserved
        assert "shop_type" in instance.custom_properties
        assert instance.custom_properties["shop_type"] == "weapons"

    def test_interactive_with_script_preserves_other_custom_properties(
        self,
        mock_bpy_module: MagicMock,
        mock_object: MagicMock,
        mock_transforms: dict,
    ) -> None:
        """Interactive with script_id should also include other custom properties."""
        from blender_extension.entities.static import StaticExtractor

        mock_settings = MagicMock()
        mock_settings.entity_type = "interactive"
        mock_settings.is_terrain = False
        mock_settings.is_collision = False
        mock_settings.script_id = "door_open"
        mock_settings.dialog_lines = []
        mock_object.trivesta = mock_settings

        # Mock get_custom_properties to return existing custom property
        mock_transforms["custom_props"].return_value = {"door_id": 42}

        extractor = StaticExtractor()
        instance = extractor.extract(mock_object)

        # script_id should be present
        assert "script_id" in instance.custom_properties
        assert instance.custom_properties["script_id"] == "door_open"
        # Custom property should also be preserved
        assert "door_id" in instance.custom_properties
        assert instance.custom_properties["door_id"] == 42
