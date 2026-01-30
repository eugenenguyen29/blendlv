"""Unit tests for file and path utilities."""

from __future__ import annotations

import os

import pytest


class TestGetRelativePath:
    """Tests for get_relative_path function (pure Python)."""

    def test_basic_subdirectory(self):
        """Should return relative path for file in subdirectory."""
        from blender_extension.utils.files import get_relative_path

        result = get_relative_path(
            "/home/user/exports/assets/tree.glb",
            "/home/user/exports",
        )
        assert result == os.path.join("assets", "tree.glb")

    def test_same_directory(self):
        """Should return filename when paths are in same directory."""
        from blender_extension.utils.files import get_relative_path

        result = get_relative_path(
            "/home/user/exports/model.glb",
            "/home/user/exports",
        )
        assert result == "model.glb"

    def test_deeply_nested_path(self):
        """Should handle deeply nested subdirectories."""
        from blender_extension.utils.files import get_relative_path

        result = get_relative_path(
            "/home/user/exports/assets/models/vegetation/tree.glb",
            "/home/user/exports",
        )
        expected = os.path.join("assets", "models", "vegetation", "tree.glb")
        assert result == expected

    def test_parent_directory_traversal(self):
        """Should handle paths requiring parent traversal."""
        from blender_extension.utils.files import get_relative_path

        result = get_relative_path(
            "/home/user/other/file.txt",
            "/home/user/exports",
        )
        expected = os.path.join("..", "other", "file.txt")
        assert result == expected


class TestResolvePath:
    """Tests for resolve_path function (bpy-dependent)."""

    def test_calls_bpy_abspath(self, mock_bpy_module):
        """Should delegate to bpy.path.abspath."""
        from blender_extension.utils.files import resolve_path

        mock_bpy_module.path.abspath.reset_mock()
        mock_bpy_module.path.abspath.return_value = "/home/user/project/exports/"

        result = resolve_path("//exports/")

        mock_bpy_module.path.abspath.assert_called_once_with("//exports/")
        assert result == "/home/user/project/exports/"

    def test_absolute_path_passthrough(self, mock_bpy_module):
        """Should pass absolute paths to bpy.path.abspath."""
        from blender_extension.utils.files import resolve_path

        mock_bpy_module.path.abspath.reset_mock()
        mock_bpy_module.path.abspath.return_value = "/absolute/path"

        result = resolve_path("/absolute/path")

        mock_bpy_module.path.abspath.assert_called_once_with("/absolute/path")
        assert result == "/absolute/path"


class TestEnsureDirectory:
    """Tests for ensure_directory function (bpy-dependent)."""

    def test_creates_directory(self, mock_bpy_module, tmp_path):
        """Should create directory if it does not exist."""
        from blender_extension.utils.files import ensure_directory

        test_dir = tmp_path / "new_directory"
        mock_bpy_module.path.abspath.return_value = str(test_dir)
        mock_bpy_module.data.filepath = "/some/file.blend"

        result = ensure_directory(str(test_dir))

        assert result == str(test_dir)
        assert test_dir.exists()

    def test_existing_directory(self, mock_bpy_module, tmp_path):
        """Should succeed when directory already exists."""
        from blender_extension.utils.files import ensure_directory

        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        mock_bpy_module.path.abspath.return_value = str(existing_dir)
        mock_bpy_module.data.filepath = "/some/file.blend"

        result = ensure_directory(str(existing_dir))

        assert result == str(existing_dir)
        assert existing_dir.exists()

    def test_raises_when_blend_not_saved(self, mock_bpy_module):
        """Should raise RuntimeError for // path when blend not saved."""
        from blender_extension.utils.files import ensure_directory

        mock_bpy_module.data.filepath = ""  # Not saved

        with pytest.raises(RuntimeError, match="Cannot resolve relative path"):
            ensure_directory("//exports/")

    def test_creates_nested_directories(self, mock_bpy_module, tmp_path):
        """Should create parent directories as needed."""
        from blender_extension.utils.files import ensure_directory

        nested_dir = tmp_path / "level1" / "level2" / "level3"
        mock_bpy_module.path.abspath.return_value = str(nested_dir)
        mock_bpy_module.data.filepath = "/some/file.blend"

        result = ensure_directory(str(nested_dir))

        assert result == str(nested_dir)
        assert nested_dir.exists()


class TestGetExportSubdir:
    """Tests for get_export_subdir function (bpy-dependent)."""

    def test_creates_subdirectory(self, mock_bpy_module, tmp_path):
        """Should create and return subdirectory path."""
        from blender_extension.utils.files import get_export_subdir

        base_dir = tmp_path / "exports"
        base_dir.mkdir()
        expected_subdir = base_dir / "assets"

        mock_bpy_module.path.abspath.return_value = str(base_dir)

        result = get_export_subdir(str(base_dir), "assets")

        assert result == str(expected_subdir)
        assert expected_subdir.exists()

    def test_returns_existing_subdirectory(self, mock_bpy_module, tmp_path):
        """Should return path when subdirectory already exists."""
        from blender_extension.utils.files import get_export_subdir

        base_dir = tmp_path / "exports"
        existing_subdir = base_dir / "islands"
        existing_subdir.mkdir(parents=True)

        mock_bpy_module.path.abspath.return_value = str(base_dir)

        result = get_export_subdir(str(base_dir), "islands")

        assert result == str(existing_subdir)
        assert existing_subdir.exists()

    def test_handles_blender_relative_path(self, mock_bpy_module, tmp_path):
        """Should resolve // paths before creating subdirectory."""
        from blender_extension.utils.files import get_export_subdir

        resolved_base = tmp_path / "project" / "exports"
        resolved_base.mkdir(parents=True)
        expected_subdir = resolved_base / "models"

        mock_bpy_module.path.abspath.return_value = str(resolved_base)

        result = get_export_subdir("//exports/", "models")

        mock_bpy_module.path.abspath.assert_called_with("//exports/")
        assert result == str(expected_subdir)
        assert expected_subdir.exists()
