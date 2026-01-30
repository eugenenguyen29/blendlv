"""Unit tests for naming utilities."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


class TestSanitizeName:
    """Tests for sanitize_name function - pure Python, no mocks needed."""

    def test_basic_sanitization(self):
        """Basic name with dot and space becomes underscored lowercase."""
        from blender_extension.utils.naming import sanitize_name

        assert sanitize_name("My Object.001") == "my_object_001"

    def test_parentheses_removal(self):
        """Parentheses and their contents get cleaned up."""
        from blender_extension.utils.naming import sanitize_name

        assert sanitize_name("Tree (Oak)") == "tree_oak"

    def test_special_chars_only_returns_unnamed(self):
        """String with only special chars returns 'unnamed'."""
        from blender_extension.utils.naming import sanitize_name

        assert sanitize_name("!!!") == "unnamed"

    def test_empty_string_returns_unnamed(self):
        """Empty string returns 'unnamed'."""
        from blender_extension.utils.naming import sanitize_name

        assert sanitize_name("") == "unnamed"

    def test_unicode_normalization(self):
        """Unicode characters get normalized to ASCII equivalents."""
        from blender_extension.utils.naming import sanitize_name

        # e with acute accent -> e
        assert sanitize_name("cafe") == "cafe"
        # n with tilde -> n
        assert sanitize_name("canon") == "canon"
        # Combined diacritics
        assert sanitize_name("resume") == "resume"

    def test_unicode_with_diacritics(self):
        """Diacritical marks are stripped during normalization."""
        from blender_extension.utils.naming import sanitize_name

        # NFD normalization separates base char from combining marks
        # Then ASCII encoding drops the combining marks
        result = sanitize_name("caf\u00e9")  # cafe with e-acute
        assert result == "cafe"

    def test_multiple_underscores_collapse(self):
        """Multiple consecutive underscores collapse to single underscore."""
        from blender_extension.utils.naming import sanitize_name

        assert sanitize_name("foo___bar") == "foo_bar"
        assert sanitize_name("a  b") == "a_b"  # spaces become underscores, then collapse
        assert sanitize_name("x..y") == "x_y"  # dots become underscores, then collapse

    def test_leading_trailing_underscores_stripped(self):
        """Leading and trailing underscores are stripped."""
        from blender_extension.utils.naming import sanitize_name

        assert sanitize_name("_foo_") == "foo"
        assert sanitize_name("  bar  ") == "bar"
        assert sanitize_name("...test...") == "test"

    def test_hyphen_to_underscore(self):
        """Hyphens are converted to underscores."""
        from blender_extension.utils.naming import sanitize_name

        assert sanitize_name("my-asset-name") == "my_asset_name"

    def test_mixed_case_to_lowercase(self):
        """Mixed case is converted to lowercase."""
        from blender_extension.utils.naming import sanitize_name

        assert sanitize_name("MyAssetName") == "myassetname"
        assert sanitize_name("ALLCAPS") == "allcaps"

    def test_numbers_preserved(self):
        """Numbers are preserved in the output."""
        from blender_extension.utils.naming import sanitize_name

        assert sanitize_name("asset123") == "asset123"
        assert sanitize_name("123asset") == "123asset"

    def test_complex_blender_name(self):
        """Complex Blender-style names are properly sanitized."""
        from blender_extension.utils.naming import sanitize_name

        assert sanitize_name("Palm_Tree.Large (Variant-A).001") == "palm_tree_large_variant_a_001"

    def test_whitespace_only_returns_unnamed(self):
        """String with only whitespace returns 'unnamed'."""
        from blender_extension.utils.naming import sanitize_name

        assert sanitize_name("   ") == "unnamed"
        assert sanitize_name("\t\n") == "unnamed"


class TestGenerateAssetKey:
    """Tests for generate_asset_key function - requires bpy mock."""

    def test_linked_object_combines_library_and_mesh_name(self, mock_bpy_module):
        """Linked object key combines library filename and mesh name."""
        from blender_extension.utils.naming import generate_asset_key

        obj = MagicMock()
        obj.name = "Oak_Tree.001"
        obj.data = MagicMock()
        obj.data.name = "Oak_Tree"
        obj.data.library = MagicMock()
        obj.data.library.filepath = "/path/to/trees.blend"
        obj.library = None
        obj.override_library = None

        result = generate_asset_key(obj)
        assert result == "trees_oak_tree"

    def test_linked_object_with_object_library(self, mock_bpy_module):
        """Object-level library link is used for key generation."""
        from blender_extension.utils.naming import generate_asset_key

        obj = MagicMock()
        obj.name = "House.002"
        obj.data = MagicMock()
        obj.data.name = "House"
        obj.data.library = None
        obj.library = MagicMock()
        obj.library.filepath = "/assets/buildings.blend"
        obj.override_library = None

        result = generate_asset_key(obj)
        assert result == "buildings_house"

    def test_local_object_uses_name_without_suffix(self, mock_bpy_module):
        """Local object uses object name without numeric suffix."""
        from blender_extension.utils.naming import generate_asset_key

        obj = MagicMock()
        obj.name = "Cube.003"
        obj.data = MagicMock()
        obj.data.name = "Cube"
        obj.data.library = None
        obj.library = None
        obj.override_library = None

        result = generate_asset_key(obj)
        assert result == "cube"

    def test_local_object_without_data(self, mock_bpy_module):
        """Local object without data (e.g., empty) uses object name."""
        from blender_extension.utils.naming import generate_asset_key

        obj = MagicMock()
        obj.name = "Empty.001"
        obj.data = None
        obj.library = None
        obj.override_library = None

        result = generate_asset_key(obj)
        assert result == "empty"

    def test_override_library_reference(self, mock_bpy_module):
        """Library override uses reference library path."""
        from blender_extension.utils.naming import generate_asset_key

        obj = MagicMock()
        obj.name = "Character.001"
        obj.data = MagicMock()
        obj.data.name = "Character"
        obj.data.library = None
        obj.library = None
        obj.override_library = MagicMock()
        obj.override_library.reference = MagicMock()
        obj.override_library.reference.library = MagicMock()
        obj.override_library.reference.library.filepath = "/rigs/hero.blend"

        result = generate_asset_key(obj)
        assert result == "hero_character"


class TestGenerateInstanceId:
    """Tests for generate_instance_id function - requires bpy mock."""

    def test_instance_id_format(self, mock_bpy_module):
        """Instance ID has format {sanitized_name}_{hash}."""
        from blender_extension.utils.naming import generate_instance_id

        obj = MagicMock()
        obj.name = "Tree.001"

        result = generate_instance_id(obj)

        # Should start with sanitized name
        assert result.startswith("tree_001_")
        # Should end with 6-char hex hash
        parts = result.rsplit("_", 1)
        assert len(parts) == 2
        assert len(parts[1]) == 6
        # Hash should be valid hex
        int(parts[1], 16)  # Raises if not valid hex

    def test_unique_ids_for_same_name_objects(self, mock_bpy_module):
        """Different objects with same name get unique IDs."""
        from blender_extension.utils.naming import generate_instance_id

        obj1 = MagicMock()
        obj1.name = "Cube"

        obj2 = MagicMock()
        obj2.name = "Cube"

        id1 = generate_instance_id(obj1)
        id2 = generate_instance_id(obj2)

        # Same prefix but different hash
        assert id1.startswith("cube_")
        assert id2.startswith("cube_")
        assert id1 != id2

    def test_instance_id_with_special_chars(self, mock_bpy_module):
        """Instance ID properly sanitizes names with special characters."""
        from blender_extension.utils.naming import generate_instance_id

        obj = MagicMock()
        obj.name = "My Object (Large).001"

        result = generate_instance_id(obj)

        # Should start with sanitized version
        assert result.startswith("my_object_large_001_")
