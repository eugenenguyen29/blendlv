"""Tests for PropertyGroup classes in blender_extension.core.properties.

Tests DialogLine PropertyGroup and TrivestaObjectSettings extensions
for NPC dialog and interactive scripting support.

Note: Due to `from __future__ import annotations` (PEP 563), annotations are
stored as strings. Tests verify the annotation strings contain expected content.
"""

from __future__ import annotations

from unittest.mock import MagicMock


class TestDialogLinePropertyGroup:
    """Tests for DialogLine PropertyGroup."""

    def test_dialog_line_creation(self, mock_bpy_module: MagicMock) -> None:
        """Should create DialogLine with speaker and text properties."""
        from blender_extension.core.properties import DialogLine

        # DialogLine should be a class
        assert DialogLine is not None

        # Check that speaker property is defined in annotations
        annotations = DialogLine.__annotations__
        assert "speaker" in annotations
        assert "text" in annotations

    def test_dialog_line_speaker_property(self, mock_bpy_module: MagicMock) -> None:
        """Speaker should be a StringProperty with correct metadata."""
        from blender_extension.core.properties import DialogLine

        speaker_annotation = DialogLine.__annotations__["speaker"]
        # Annotation is a string due to PEP 563
        assert "StringProperty" in speaker_annotation
        assert "name='Speaker'" in speaker_annotation or 'name="Speaker"' in speaker_annotation
        assert "default=''" in speaker_annotation or 'default=""' in speaker_annotation

    def test_dialog_line_text_property(self, mock_bpy_module: MagicMock) -> None:
        """Text should be a StringProperty with correct metadata."""
        from blender_extension.core.properties import DialogLine

        text_annotation = DialogLine.__annotations__["text"]
        assert "StringProperty" in text_annotation
        assert "name='Text'" in text_annotation or 'name="Text"' in text_annotation
        assert "default=''" in text_annotation or 'default=""' in text_annotation

    def test_dialog_line_has_descriptions(self, mock_bpy_module: MagicMock) -> None:
        """Should have meaningful descriptions for properties."""
        from blender_extension.core.properties import DialogLine

        speaker_annotation = DialogLine.__annotations__["speaker"]
        assert "description=" in speaker_annotation

        text_annotation = DialogLine.__annotations__["text"]
        assert "description=" in text_annotation


class TestTrivestaObjectSettingsDialogProperties:
    """Tests for dialog-related properties on TrivestaObjectSettings."""

    def test_trivesta_settings_has_dialog_lines(self, mock_bpy_module: MagicMock) -> None:
        """Should have dialog_lines CollectionProperty."""
        from blender_extension.core.properties import TrivestaObjectSettings

        annotations = TrivestaObjectSettings.__annotations__
        assert "dialog_lines" in annotations

        dialog_lines_annotation = annotations["dialog_lines"]
        assert "CollectionProperty" in dialog_lines_annotation
        assert "type=DialogLine" in dialog_lines_annotation

    def test_trivesta_settings_has_dialog_line_index(self, mock_bpy_module: MagicMock) -> None:
        """Should have dialog_line_index IntProperty for tracking selection."""
        from blender_extension.core.properties import TrivestaObjectSettings

        annotations = TrivestaObjectSettings.__annotations__
        assert "dialog_line_index" in annotations

        index_annotation = annotations["dialog_line_index"]
        assert "IntProperty" in index_annotation
        assert "default=0" in index_annotation
        assert "min=0" in index_annotation

    def test_trivesta_settings_has_script_id(self, mock_bpy_module: MagicMock) -> None:
        """Should have script_id StringProperty for game engine handler."""
        from blender_extension.core.properties import TrivestaObjectSettings

        annotations = TrivestaObjectSettings.__annotations__
        assert "script_id" in annotations

        script_annotation = annotations["script_id"]
        assert "StringProperty" in script_annotation
        assert "default=''" in script_annotation or 'default=""' in script_annotation

    def test_dialog_lines_collection_metadata(self, mock_bpy_module: MagicMock) -> None:
        """Should have proper name and description for dialog_lines."""
        from blender_extension.core.properties import TrivestaObjectSettings

        dialog_lines_annotation = TrivestaObjectSettings.__annotations__["dialog_lines"]
        assert "name=" in dialog_lines_annotation
        assert "description=" in dialog_lines_annotation

    def test_script_id_has_description(self, mock_bpy_module: MagicMock) -> None:
        """Should have description for script_id property."""
        from blender_extension.core.properties import TrivestaObjectSettings

        script_annotation = TrivestaObjectSettings.__annotations__["script_id"]
        assert "description=" in script_annotation


class TestDialogLineRegistration:
    """Tests for DialogLine registration order."""

    def test_dialog_line_in_classes_list(self, mock_bpy_module: MagicMock) -> None:
        """DialogLine should be in the classes list for registration."""
        from blender_extension.core.registry import collect_classes

        classes = collect_classes()
        # Filter to actual classes (not mocks)
        class_names = [cls.__name__ for cls in classes if hasattr(cls, "__name__")]
        assert "DialogLine" in class_names

    def test_dialog_line_registered_before_object_settings(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """DialogLine must be registered before TrivestaObjectSettings."""
        from blender_extension.core.registry import collect_classes

        classes = collect_classes()
        class_names = [cls.__name__ for cls in classes if hasattr(cls, "__name__")]

        dialog_line_idx = class_names.index("DialogLine")
        object_settings_idx = class_names.index("TrivestaObjectSettings")

        assert dialog_line_idx < object_settings_idx, (
            "DialogLine must be registered before TrivestaObjectSettings"
        )


class TestTrivestaSceneSettingsTerrainExportMode:
    """Tests for terrain_export_mode property on TrivestaSceneSettings."""

    def test_scene_terrain_export_mode_annotation(self, mock_bpy_module: MagicMock) -> None:
        """Scene should have terrain_export_mode property annotated."""
        from blender_extension.core.properties import TrivestaSceneSettings

        annotations = getattr(TrivestaSceneSettings, "__annotations__", {})
        assert "terrain_export_mode" in annotations

    def test_scene_terrain_export_mode_is_enum(self, mock_bpy_module: MagicMock) -> None:
        """terrain_export_mode should be an EnumProperty."""
        from blender_extension.core.properties import TrivestaSceneSettings

        annotations = TrivestaSceneSettings.__annotations__
        terrain_mode_annotation = annotations["terrain_export_mode"]
        assert "EnumProperty" in terrain_mode_annotation

    def test_scene_terrain_export_mode_has_items(self, mock_bpy_module: MagicMock) -> None:
        """terrain_export_mode should have merged and individual items."""
        from blender_extension.core.properties import TrivestaSceneSettings

        annotations = TrivestaSceneSettings.__annotations__
        terrain_mode_annotation = annotations["terrain_export_mode"]
        # Check for items tuple entries
        assert "merged" in terrain_mode_annotation
        assert "individual" in terrain_mode_annotation

    def test_scene_terrain_export_mode_default_merged(self, mock_bpy_module: MagicMock) -> None:
        """terrain_export_mode should default to merged."""
        from blender_extension.core.properties import TrivestaSceneSettings

        annotations = TrivestaSceneSettings.__annotations__
        terrain_mode_annotation = annotations["terrain_export_mode"]
        assert (
            "default='merged'" in terrain_mode_annotation
            or 'default="merged"' in terrain_mode_annotation
        )

    def test_scene_terrain_export_mode_has_dual_option(self, mock_bpy_module: MagicMock) -> None:
        """terrain_export_mode should include 'dual' option for exporting both."""
        from blender_extension.core.properties import TrivestaSceneSettings

        annotations = TrivestaSceneSettings.__annotations__
        terrain_mode_annotation = annotations["terrain_export_mode"]
        # Check for the enum identifier as a tuple first element: ('dual',
        assert "('dual'" in terrain_mode_annotation or '("dual"' in terrain_mode_annotation

    def test_scene_terrain_export_mode_dual_has_correct_metadata(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """dual option should have correct label and description mentioning 'both'."""
        from blender_extension.core.properties import TrivestaSceneSettings

        annotations = TrivestaSceneSettings.__annotations__
        terrain_mode_annotation = annotations["terrain_export_mode"]
        # Check that "Dual" label is present
        assert "Dual" in terrain_mode_annotation
        # Check that description mentions "both" (merged and individual)
        assert "both" in terrain_mode_annotation.lower() or "Both" in terrain_mode_annotation
