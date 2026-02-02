"""Tests for blender_extension.utils.transforms module."""

from __future__ import annotations

import math
from unittest.mock import MagicMock


class TestGetObjectTransform:
    """Tests for get_object_transform function."""

    def test_coordinate_conversion_position(self, mock_bpy_module: MagicMock) -> None:
        """Test Blender Z-up to Three.js Y-up position conversion."""
        from blender_extension.utils.transforms import get_object_transform

        mock_obj = MagicMock()
        mock_matrix = MagicMock()
        mock_obj.matrix_world = mock_matrix

        # Blender: (x=1, y=2, z=3)
        mock_loc = MagicMock()
        mock_loc.x, mock_loc.y, mock_loc.z = 1.0, 2.0, 3.0
        mock_matrix.to_translation.return_value = mock_loc

        mock_rot = MagicMock()
        mock_rot.x, mock_rot.y, mock_rot.z, mock_rot.w = 0.0, 0.0, 0.0, 1.0
        mock_matrix.to_quaternion.return_value = mock_rot

        mock_scale = MagicMock()
        mock_scale.x, mock_scale.y, mock_scale.z = 1.0, 1.0, 1.0
        mock_matrix.to_scale.return_value = mock_scale

        result = get_object_transform(mock_obj)

        # Three.js: [x, z, -y] -> [1, 3, -2]
        assert result["position"] == [1.0, 3.0, -2.0]

    def test_coordinate_conversion_rotation(self, mock_bpy_module: MagicMock) -> None:
        """Test quaternion conversion to Three.js order."""
        from blender_extension.utils.transforms import get_object_transform

        mock_obj = MagicMock()
        mock_matrix = MagicMock()
        mock_obj.matrix_world = mock_matrix

        mock_loc = MagicMock()
        mock_loc.x, mock_loc.y, mock_loc.z = 0.0, 0.0, 0.0
        mock_matrix.to_translation.return_value = mock_loc

        # Blender quaternion: (x=0.1, y=0.2, z=0.3, w=0.9)
        mock_rot = MagicMock()
        mock_rot.x, mock_rot.y, mock_rot.z, mock_rot.w = 0.1, 0.2, 0.3, 0.9
        mock_matrix.to_quaternion.return_value = mock_rot

        mock_scale = MagicMock()
        mock_scale.x, mock_scale.y, mock_scale.z = 1.0, 1.0, 1.0
        mock_matrix.to_scale.return_value = mock_scale

        result = get_object_transform(mock_obj)

        # Three.js: [x, z, -y, w] -> [0.1, 0.3, -0.2, 0.9]
        assert result["rotation"] == [0.1, 0.3, -0.2, 0.9]

    def test_coordinate_conversion_scale(self, mock_bpy_module: MagicMock) -> None:
        """Test scale conversion (swap Y and Z)."""
        from blender_extension.utils.transforms import get_object_transform

        mock_obj = MagicMock()
        mock_matrix = MagicMock()
        mock_obj.matrix_world = mock_matrix

        mock_loc = MagicMock()
        mock_loc.x, mock_loc.y, mock_loc.z = 0.0, 0.0, 0.0
        mock_matrix.to_translation.return_value = mock_loc

        mock_rot = MagicMock()
        mock_rot.x, mock_rot.y, mock_rot.z, mock_rot.w = 0.0, 0.0, 0.0, 1.0
        mock_matrix.to_quaternion.return_value = mock_rot

        # Blender scale: (x=2, y=3, z=4)
        mock_scale = MagicMock()
        mock_scale.x, mock_scale.y, mock_scale.z = 2.0, 3.0, 4.0
        mock_matrix.to_scale.return_value = mock_scale

        result = get_object_transform(mock_obj)

        # Three.js: [x, z, y] -> [2, 4, 3]
        assert result["scale"] == [2.0, 4.0, 3.0]


class TestGetBoundingBox:
    """Tests for get_bounding_box function."""

    def test_non_mesh_returns_zeros(self, mock_bpy_module: MagicMock) -> None:
        """Test that non-MESH objects return zero bounding box."""
        from blender_extension.utils.transforms import get_bounding_box

        mock_obj = MagicMock()
        mock_obj.type = "EMPTY"
        mock_obj.data = None

        result = get_bounding_box(mock_obj)

        assert result["min"] == [0, 0, 0]
        assert result["max"] == [0, 0, 0]
        assert result["radius"] == 0.0

    def test_mesh_with_no_data_returns_zeros(self, mock_bpy_module: MagicMock) -> None:
        """Test MESH with no data returns zero bounding box."""
        from blender_extension.utils.transforms import get_bounding_box

        mock_obj = MagicMock()
        mock_obj.type = "MESH"
        mock_obj.data = None

        result = get_bounding_box(mock_obj)

        assert result["min"] == [0, 0, 0]
        assert result["max"] == [0, 0, 0]
        assert result["radius"] == 0.0

    def test_mesh_bounding_box_calculation(self, mock_bpy_module: MagicMock) -> None:
        """Test bounding box calculation with coordinate conversion."""
        from blender_extension.utils.transforms import get_bounding_box

        mock_obj = MagicMock()
        mock_obj.type = "MESH"
        mock_obj.data = MagicMock()

        # Unit cube bound_box corners in Blender coordinates
        # bound_box is 8 corners: (x, y, z) with x,y,z each being 0 or 1
        bound_box = [
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 1.0),
            (0.0, 1.0, 1.0),
            (0.0, 1.0, 0.0),
            (1.0, 0.0, 0.0),
            (1.0, 0.0, 1.0),
            (1.0, 1.0, 1.0),
            (1.0, 1.0, 0.0),
        ]
        mock_obj.bound_box = bound_box

        # Identity matrix_world - matmul returns Vector unchanged
        def matmul_identity(corner: tuple[float, float, float]) -> MagicMock:
            vec = MagicMock()
            vec.x, vec.y, vec.z = corner
            return vec

        mock_obj.matrix_world.__matmul__ = MagicMock(side_effect=matmul_identity)

        result = get_bounding_box(mock_obj)

        # Blender (0,0,0)-(1,1,1) -> Three.js min/max
        # min: [min_x, min_z, min(-y)] = [0, 0, -1]
        # max: [max_x, max_z, max(-y)] = [1, 1, 0]
        assert result["min"] == [0.0, 0.0, -1.0]
        assert result["max"] == [1.0, 1.0, 0.0]

    def test_radius_calculation(self, mock_bpy_module: MagicMock) -> None:
        """Test radius is distance from center to corner."""
        from blender_extension.utils.transforms import get_bounding_box

        mock_obj = MagicMock()
        mock_obj.type = "MESH"
        mock_obj.data = MagicMock()

        # Symmetric cube: Blender (-1,-1,-1) to (1,1,1)
        bound_box = [
            (-1.0, -1.0, -1.0),
            (-1.0, -1.0, 1.0),
            (-1.0, 1.0, 1.0),
            (-1.0, 1.0, -1.0),
            (1.0, -1.0, -1.0),
            (1.0, -1.0, 1.0),
            (1.0, 1.0, 1.0),
            (1.0, 1.0, -1.0),
        ]
        mock_obj.bound_box = bound_box

        def matmul_identity(corner: tuple[float, float, float]) -> MagicMock:
            vec = MagicMock()
            vec.x, vec.y, vec.z = corner
            return vec

        mock_obj.matrix_world.__matmul__ = MagicMock(side_effect=matmul_identity)

        result = get_bounding_box(mock_obj)

        # In Three.js coordinates: min=[-1,-1,-1], max=[1,1,1]
        # Center = [0,0,0], corner = [1,1,1]
        # Radius = sqrt(1+1+1) = sqrt(3)
        expected_radius = math.sqrt(3.0)
        assert abs(result["radius"] - expected_radius) < 1e-6


class TestGetCustomProperties:
    """Tests for get_custom_properties function."""

    def test_filters_underscore_keys(self, mock_bpy_module: MagicMock) -> None:
        """Test that keys starting with underscore are filtered out."""
        from blender_extension.utils.transforms import get_custom_properties

        mock_obj = MagicMock()
        mock_obj.keys.return_value = ["_RNA_UI", "_private", "public_prop"]
        mock_obj.__getitem__ = MagicMock(return_value="value")

        result = get_custom_properties(mock_obj)

        assert "_RNA_UI" not in result
        assert "_private" not in result
        assert "public_prop" in result

    def test_converts_to_list_values(self, mock_bpy_module: MagicMock) -> None:
        """Test that values with to_list() method are converted."""
        from blender_extension.utils.transforms import get_custom_properties

        mock_obj = MagicMock()
        mock_obj.keys.return_value = ["vector_prop"]

        mock_vector = MagicMock()
        mock_vector.to_list.return_value = [1.0, 2.0, 3.0]

        def getitem(key: str) -> MagicMock:
            if key == "vector_prop":
                return mock_vector
            raise KeyError(key)

        mock_obj.__getitem__ = MagicMock(side_effect=getitem)

        result = get_custom_properties(mock_obj)

        assert result["vector_prop"] == [1.0, 2.0, 3.0]

    def test_basic_types_preserved(self, mock_bpy_module: MagicMock) -> None:
        """Test that int, float, str, bool values are preserved."""
        from blender_extension.utils.transforms import get_custom_properties

        mock_obj = MagicMock()
        mock_obj.keys.return_value = ["int_prop", "float_prop", "str_prop", "bool_prop"]

        values = {
            "int_prop": 42,
            "float_prop": 3.14,
            "str_prop": "hello",
            "bool_prop": True,
        }
        mock_obj.__getitem__ = MagicMock(side_effect=lambda k: values[k])

        result = get_custom_properties(mock_obj)

        assert result["int_prop"] == 42
        assert result["float_prop"] == 3.14
        assert result["str_prop"] == "hello"
        assert result["bool_prop"] is True

    def test_unsupported_types_skipped(self, mock_bpy_module: MagicMock) -> None:
        """Test that unsupported types are not included."""
        from blender_extension.utils.transforms import get_custom_properties

        mock_obj = MagicMock()
        mock_obj.keys.return_value = ["valid", "unsupported"]

        # Object without to_list that's not a basic type
        unsupported_value = MagicMock(spec=[])  # No to_list method

        def getitem(key: str) -> int | MagicMock:
            if key == "valid":
                return 123
            return unsupported_value

        mock_obj.__getitem__ = MagicMock(side_effect=getitem)

        result = get_custom_properties(mock_obj)

        assert result["valid"] == 123
        assert "unsupported" not in result


class TestGetLibrarySource:
    """Tests for get_library_source function."""

    def test_object_library(self, mock_bpy_module: MagicMock) -> None:
        """Test getting filepath from obj.library."""
        from blender_extension.utils.transforms import get_library_source

        mock_obj = MagicMock()
        mock_obj.library = MagicMock()
        mock_obj.library.filepath = "/path/to/linked.blend"
        mock_obj.data = None
        mock_obj.override_library = None

        result = get_library_source(mock_obj)

        assert result == "/path/to/linked.blend"

    def test_data_library(self, mock_bpy_module: MagicMock) -> None:
        """Test getting filepath from obj.data.library."""
        from blender_extension.utils.transforms import get_library_source

        mock_obj = MagicMock()
        mock_obj.library = None
        mock_obj.data = MagicMock()
        mock_obj.data.library = MagicMock()
        mock_obj.data.library.filepath = "/path/to/data.blend"
        mock_obj.override_library = None

        result = get_library_source(mock_obj)

        assert result == "/path/to/data.blend"

    def test_override_library_reference(self, mock_bpy_module: MagicMock) -> None:
        """Test getting filepath from override_library.reference."""
        from blender_extension.utils.transforms import get_library_source

        mock_obj = MagicMock()
        mock_obj.library = None
        mock_obj.data = MagicMock()
        mock_obj.data.library = None
        mock_obj.override_library = MagicMock()
        mock_obj.override_library.reference = MagicMock()
        mock_obj.override_library.reference.library = MagicMock()
        mock_obj.override_library.reference.library.filepath = "/path/to/override.blend"

        result = get_library_source(mock_obj)

        assert result == "/path/to/override.blend"

    def test_no_library_returns_none(self, mock_bpy_module: MagicMock) -> None:
        """Test that local objects return None."""
        from blender_extension.utils.transforms import get_library_source

        mock_obj = MagicMock()
        mock_obj.library = None
        mock_obj.data = MagicMock()
        mock_obj.data.library = None
        mock_obj.override_library = None

        result = get_library_source(mock_obj)

        assert result is None

    def test_override_without_reference_returns_none(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """Test override_library without reference returns None."""
        from blender_extension.utils.transforms import get_library_source

        mock_obj = MagicMock()
        mock_obj.library = None
        mock_obj.data = MagicMock()
        mock_obj.data.library = None
        mock_obj.override_library = MagicMock()
        mock_obj.override_library.reference = None

        result = get_library_source(mock_obj)

        assert result is None

    def test_override_reference_without_library_returns_none(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """Test override reference without library returns None."""
        from blender_extension.utils.transforms import get_library_source

        mock_obj = MagicMock()
        mock_obj.library = None
        mock_obj.data = MagicMock()
        mock_obj.data.library = None
        mock_obj.override_library = MagicMock()
        mock_obj.override_library.reference = MagicMock()
        mock_obj.override_library.reference.library = None

        result = get_library_source(mock_obj)

        assert result is None
