"""Core bpy module mock for Blender testing.

Provides a configurable MagicMock that simulates bpy module structure
for unit testing Blender extension code without Blender runtime.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any
from unittest.mock import MagicMock


def _prop_factory(prop_name: str) -> Any:
    """Create a property function that returns a tuple annotation.

    Blender props return tuples containing property metadata when defined
    at class level. They become actual properties after registration.
    """

    def prop_func(**kwargs: Any) -> tuple[str, dict[str, Any]]:
        return (prop_name, kwargs)

    return prop_func


@contextmanager
def _libraries_load_context(blend_path: str, link: bool = False) -> Any:
    """Context manager for bpy.data.libraries.load()."""
    data_from = MagicMock()
    data_from.objects = ["Cube", "Sphere", "Cylinder"]
    data_from.collections = ["Characters", "Props", "Vehicles"]

    data_to = MagicMock()
    data_to.objects = []
    data_to.collections = []

    yield data_from, data_to


class MockOperator:
    """Mock base class for Blender operators."""

    bl_idname = ""
    bl_label = ""
    bl_options: set[str] = set()

    def report(self, level: set[str], message: str) -> None:
        """Mock report method."""
        pass


class MockPanel:
    """Mock base class for Blender panels."""

    bl_idname = ""
    bl_label = ""
    bl_space_type = ""
    bl_region_type = ""


class MockPropertyGroup:
    """Mock base class for Blender property groups."""

    pass


class MockAssetShelf:
    """Mock base class for Asset Shelf."""

    bl_idname = ""
    bl_space_type = ""


class MockUIList:
    """Mock base class for Blender UI lists."""

    bl_idname = ""
    layout_type = "DEFAULT"

    def draw_item(
        self,
        context,
        layout,
        data,
        item,
        icon,
        active_data,
        active_property,
        index=0,
        flt_flag=0,
    ):
        """Override in subclass to draw list items."""
        pass


def create_bpy_mock() -> MagicMock:
    """Create a comprehensive bpy module mock.

    Returns:
        MagicMock configured with bpy types, props, data, ops, and context.
    """
    bpy = MagicMock()

    # --- bpy.types ---
    # Use real classes for types that are subclassed
    bpy.types.Object = MagicMock(name="Object")
    bpy.types.Operator = MockOperator  # Real class for inheritance
    bpy.types.Context = MagicMock(name="Context")
    bpy.types.Event = MagicMock(name="Event")
    bpy.types.Region = MagicMock(name="Region")
    bpy.types.RegionView3D = MagicMock(name="RegionView3D")
    bpy.types.Area = MagicMock(name="Area")
    bpy.types.AssetShelf = MockAssetShelf  # Real class for inheritance
    bpy.types.Panel = MockPanel  # Real class for inheritance
    bpy.types.PropertyGroup = MockPropertyGroup  # Real class for inheritance
    bpy.types.Scene = MagicMock(name="Scene")
    bpy.types.Collection = MagicMock(name="Collection")
    bpy.types.ViewLayer = MagicMock(name="ViewLayer")
    bpy.types.Window = MagicMock(name="Window")
    bpy.types.WindowManager = MagicMock(name="WindowManager")
    bpy.types.Screen = MagicMock(name="Screen")
    bpy.types.SpaceView3D = MagicMock(name="SpaceView3D")
    bpy.types.AssetRepresentation = MagicMock(name="AssetRepresentation")
    bpy.types.UIList = MockUIList  # Real class for inheritance

    # --- bpy.props ---
    bpy.props.IntProperty = _prop_factory("IntProperty")
    bpy.props.StringProperty = _prop_factory("StringProperty")
    bpy.props.BoolProperty = _prop_factory("BoolProperty")
    bpy.props.FloatProperty = _prop_factory("FloatProperty")
    bpy.props.FloatVectorProperty = _prop_factory("FloatVectorProperty")
    bpy.props.EnumProperty = _prop_factory("EnumProperty")
    bpy.props.PointerProperty = _prop_factory("PointerProperty")
    bpy.props.CollectionProperty = _prop_factory("CollectionProperty")

    # --- bpy.data ---
    bpy.data.objects = MagicMock()
    bpy.data.objects.remove = MagicMock()
    bpy.data.objects.__iter__ = MagicMock(return_value=iter([]))

    bpy.data.collections = MagicMock()
    bpy.data.scenes = MagicMock()
    bpy.data.meshes = MagicMock()
    bpy.data.materials = MagicMock()

    # Configure libraries.load as context manager
    bpy.data.libraries = MagicMock()
    bpy.data.libraries.load = MagicMock(side_effect=_libraries_load_context)

    # --- bpy.ops ---
    bpy.ops.object = MagicMock()
    bpy.ops.object.select_all = MagicMock(return_value={"FINISHED"})
    bpy.ops.object.delete = MagicMock(return_value={"FINISHED"})
    bpy.ops.object.duplicate = MagicMock(return_value={"FINISHED"})
    bpy.ops.mesh = MagicMock()
    bpy.ops.export_scene = MagicMock()
    bpy.ops.wm = MagicMock()

    # --- bpy.context ---
    bpy.context = MagicMock()
    bpy.context.preferences = MagicMock()
    bpy.context.preferences.filepaths = MagicMock()
    bpy.context.preferences.filepaths.asset_libraries = []

    # --- bpy.utils ---
    bpy.utils.register_class = MagicMock()
    bpy.utils.unregister_class = MagicMock()

    # --- bpy.app ---
    bpy.app.version = (4, 2, 0)
    bpy.app.version_string = "4.2.0"

    return bpy


def create_mathutils_mock() -> MagicMock:
    """Create a mathutils module mock with Vector and Matrix support.

    Returns:
        MagicMock configured with Vector and Matrix classes.
    """
    mathutils = MagicMock()

    class MockVector:
        """Mock Vector class with basic operations."""

        def __init__(self, coords: tuple[float, ...] = (0.0, 0.0, 0.0)) -> None:
            self._coords = list(coords)

        @property
        def x(self) -> float:
            return self._coords[0]

        @x.setter
        def x(self, value: float) -> None:
            self._coords[0] = value

        @property
        def y(self) -> float:
            return self._coords[1]

        @y.setter
        def y(self, value: float) -> None:
            self._coords[1] = value

        @property
        def z(self) -> float:
            return self._coords[2] if len(self._coords) > 2 else 0.0

        @z.setter
        def z(self, value: float) -> None:
            if len(self._coords) > 2:
                self._coords[2] = value

        def copy(self) -> MockVector:
            return MockVector(tuple(self._coords))

        @property
        def length(self) -> float:
            return sum(c**2 for c in self._coords) ** 0.5

        def __add__(self, other: MockVector) -> MockVector:
            return MockVector(tuple(a + b for a, b in zip(self._coords, other._coords)))

        def __sub__(self, other: MockVector) -> MockVector:
            return MockVector(tuple(a - b for a, b in zip(self._coords, other._coords)))

        def __mul__(self, scalar: float) -> MockVector:
            return MockVector(tuple(c * scalar for c in self._coords))

        def __rmul__(self, scalar: float) -> MockVector:
            return self.__mul__(scalar)

        def __truediv__(self, scalar: float) -> MockVector:
            return MockVector(tuple(c / scalar for c in self._coords))

        def __repr__(self) -> str:
            return f"Vector({tuple(self._coords)})"

        def __iter__(self):
            return iter(self._coords)

        def __getitem__(self, idx: int) -> float:
            return self._coords[idx]

        def __setitem__(self, idx: int, value: float) -> None:
            self._coords[idx] = value

    class MockMatrix:
        """Mock Matrix class with basic operations."""

        def __init__(self, rows: list[list[float]] | None = None) -> None:
            if rows is None:
                # Default to 4x4 identity
                self._rows = [
                    [1.0, 0.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0, 0.0],
                    [0.0, 0.0, 1.0, 0.0],
                    [0.0, 0.0, 0.0, 1.0],
                ]
            else:
                self._rows = [list(row) for row in rows]

        @classmethod
        def Identity(cls, size: int) -> MockMatrix:
            """Create an identity matrix of given size."""
            rows = [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]
            return cls(rows)

        def __matmul__(self, other: MockVector) -> MockVector:
            """Matrix @ Vector multiplication (transform a vector)."""
            if isinstance(other, MockVector):
                # For 4x4 matrix and 3D vector, treat as homogeneous coords
                coords = list(other._coords)
                while len(coords) < 4:
                    coords.append(1.0 if len(coords) == 3 else 0.0)

                result = []
                for row in self._rows[:3]:  # Only first 3 rows for 3D result
                    val = sum(row[i] * coords[i] for i in range(len(row)))
                    result.append(val)

                return MockVector(tuple(result))
            return NotImplemented

        def __repr__(self) -> str:
            return f"Matrix({self._rows})"

    mathutils.Vector = MockVector
    mathutils.Matrix = MockMatrix
    return mathutils


def create_bpy_extras_mock() -> MagicMock:
    """Create a bpy_extras module mock.

    Returns:
        MagicMock with view3d_utils functions.
    """
    bpy_extras = MagicMock()

    # view3d_utils functions return mock vectors
    bpy_extras.view3d_utils.region_2d_to_origin_3d = MagicMock(
        return_value=MagicMock(x=0, y=0, z=10)
    )
    bpy_extras.view3d_utils.region_2d_to_vector_3d = MagicMock(
        return_value=MagicMock(x=0, y=0, z=-1)
    )

    return bpy_extras
