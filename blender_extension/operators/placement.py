"""Asset placement operators for Trivesta Level extension.

Simple asset placement from Asset Shelf to 3D viewport.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING

import bpy
from bpy.props import IntProperty, StringProperty
from bpy.types import Operator
from mathutils import Vector

if TYPE_CHECKING:
    from bpy.types import Context, Event


class PlacementError(Enum):
    """Types of placement errors."""

    INVALID_PATH = "invalid_path"
    UNSUPPORTED_TYPE = "unsupported_type"
    LIBRARY_NOT_FOUND = "library_not_found"
    FILE_NOT_FOUND = "file_not_found"
    ASSET_NOT_FOUND = "asset_not_found"
    LINK_FAILED = "link_failed"


@dataclass
class PlacementResult:
    """Result of a placement operation."""

    success: bool
    object: bpy.types.Object | None = None
    error: PlacementError | None = None
    message: str = ""


class DragState(Enum):
    """Drag operator states."""

    IDLE = auto()
    DRAGGING = auto()  # Modal active, no object yet
    OBJECT_CREATED = auto()  # Object exists, following mouse


DEBUG = True


def debug(msg: str) -> None:
    """Print debug message if DEBUG is enabled."""
    if DEBUG:
        print(f"[Trivesta] {msg}")


def get_library_path(library_name: str) -> str | None:
    """Get the filesystem path for a named asset library from Blender preferences."""
    for lib in bpy.context.preferences.filepaths.asset_libraries:
        if lib.name == library_name:
            return lib.path
    return None


def link_object_from_blend(blend_path: str, object_name: str) -> bpy.types.Object | None:
    """Link an object from an external blend file."""
    debug(f"Linking '{object_name}' from '{blend_path}'")

    if not os.path.exists(blend_path):
        debug(f"  File not found: {blend_path}")
        return None

    # Link the object
    with bpy.data.libraries.load(blend_path, link=True) as (data_from, data_to):
        if object_name in data_from.objects:
            data_to.objects = [object_name]
        else:
            debug(f"  Object '{object_name}' not found in {blend_path}")
            debug(f"  Available objects: {data_from.objects}")
            return None

    # Find the linked object (might have .001 suffix if name collision)
    for obj in bpy.data.objects:
        if obj.library and (obj.name == object_name or obj.name.startswith(f"{object_name}.")):
            debug(f"  Linked: {obj.name}")
            return obj

    return None


def place_asset(
    context: Context,
    library_name: str,
    relative_path: str,
    location: Vector,
) -> PlacementResult:
    """Place an asset at the specified location.

    Args:
        context: Blender context
        library_name: Name of asset library (from preferences)
        relative_path: Path like "file.blend/Object/Name"
        location: World location to place at

    Returns:
        PlacementResult with success status, object, and error details
    """
    debug(f"place_asset: library={library_name}, path={relative_path}")

    # Parse relative path: "cube2.blend/Object/Cube.001"
    parts = relative_path.split("/")
    if len(parts) < 3:
        msg = f"Invalid path format: {relative_path}"
        debug(f"  {msg}")
        return PlacementResult(success=False, error=PlacementError.INVALID_PATH, message=msg)

    asset_name = parts[-1]
    id_type = parts[-2]  # "Object", "Collection", etc.
    blend_file = "/".join(parts[:-2])

    debug(f"  Parsed: file={blend_file}, type={id_type}, name={asset_name}")

    # Only handle Objects for now
    if id_type != "Object":
        msg = f"Unsupported id_type: {id_type}"
        debug(f"  {msg}")
        return PlacementResult(success=False, error=PlacementError.UNSUPPORTED_TYPE, message=msg)

    # Get library path and build full blend file path
    library_path = get_library_path(library_name)
    if not library_path:
        msg = f"Library not found: {library_name}"
        debug(f"  {msg}")
        return PlacementResult(success=False, error=PlacementError.LIBRARY_NOT_FOUND, message=msg)

    full_blend_path = os.path.join(library_path, blend_file)
    debug(f"  Full path: {full_blend_path}")

    # Check file exists before linking
    if not os.path.exists(full_blend_path):
        msg = f"File not found: {full_blend_path}"
        debug(f"  {msg}")
        return PlacementResult(success=False, error=PlacementError.FILE_NOT_FOUND, message=msg)

    # Link the object
    try:
        linked_obj = link_object_from_blend(full_blend_path, asset_name)
    except Exception as e:
        msg = str(e)
        debug(f"  Link failed: {msg}")
        return PlacementResult(success=False, error=PlacementError.LINK_FAILED, message=msg)

    if not linked_obj:
        msg = f"Asset not found after linking: {asset_name}"
        debug(f"  {msg}")
        return PlacementResult(success=False, error=PlacementError.ASSET_NOT_FOUND, message=msg)

    # Create an instance (copy) of the linked object
    new_obj = linked_obj.copy()
    context.collection.objects.link(new_obj)
    new_obj.location = location

    # Select the new object
    bpy.ops.object.select_all(action="DESELECT")
    new_obj.select_set(True)
    context.view_layer.objects.active = new_obj

    debug(f"  Placed at {location}")
    return PlacementResult(success=True, object=new_obj)


MIN_PLACEMENT_DISTANCE = 1.0  # Minimum distance from camera to place objects
DEFAULT_PLACEMENT_DISTANCE = 10.0  # Default distance when ground plane projection fails


def get_mouse_location(
    context: Context,
    event: Event,
    exclude: bpy.types.Object | None = None,
) -> Vector | None:
    """Get world location from mouse via raycast. Returns None if not over 3D view.

    Args:
        context: Blender context
        event: Mouse event
        exclude: Object to exclude from raycast (e.g., the object being dragged)
    """
    # Find 3D view area that contains the mouse
    mouse_x, mouse_y = event.mouse_x, event.mouse_y

    for area in context.screen.areas:
        if area.type != "VIEW_3D":
            continue
        # Check if mouse is within this area
        if not (
            area.x <= mouse_x < area.x + area.width and area.y <= mouse_y < area.y + area.height
        ):
            continue

        # Find the WINDOW region within this area
        for region in area.regions:
            if region.type != "WINDOW":
                continue
            # Check if mouse is within this region
            if not (
                region.x <= mouse_x < region.x + region.width
                and region.y <= mouse_y < region.y + region.height
            ):
                continue

            rv3d = area.spaces.active.region_3d
            if not rv3d:
                continue

            from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d

            # Convert to region-local coordinates
            coord = (mouse_x - region.x, mouse_y - region.y)
            origin = region_2d_to_origin_3d(region, rv3d, coord)
            direction = region_2d_to_vector_3d(region, rv3d, coord)

            if origin and direction:
                # Temporarily hide excluded object from raycast
                was_hidden = False
                if exclude:
                    was_hidden = exclude.hide_viewport
                    exclude.hide_viewport = True

                depsgraph = context.evaluated_depsgraph_get()
                hit, location, *_ = context.scene.ray_cast(depsgraph, origin, direction)

                # Restore visibility
                if exclude:
                    exclude.hide_viewport = was_hidden

                if hit:
                    # Ensure hit point is not too close to camera
                    dist = (location - origin).length
                    if dist >= MIN_PLACEMENT_DISTANCE:
                        return location
                    # Hit point too close - use minimum distance along ray
                    return origin + direction * MIN_PLACEMENT_DISTANCE

                # No hit - project onto ground plane (Z=0)
                if direction.z != 0:
                    t = -origin.z / direction.z
                    # Ensure ground plane point is at reasonable distance
                    if t >= MIN_PLACEMENT_DISTANCE:
                        return origin + direction * t

                # Ground plane projection failed or too close - use default distance
                return origin + direction * DEFAULT_PLACEMENT_DISTANCE

    return None


class TRIVESTA_OT_place_asset(Operator):
    """Place an asset from Asset Shelf at click location."""

    bl_idname = "trivesta.place_asset"
    bl_label = "Place Asset"
    bl_options = {"REGISTER", "UNDO"}

    # Properties passed by Asset Shelf
    asset_library_type: IntProperty(options={"HIDDEN", "SKIP_SAVE"})  # type: ignore
    asset_library_identifier: StringProperty(options={"HIDDEN", "SKIP_SAVE"})  # type: ignore
    relative_asset_identifier: StringProperty(options={"HIDDEN", "SKIP_SAVE"})  # type: ignore

    def invoke(self, context: Context, event: Event) -> set[str]:
        debug(
            f"place_asset.invoke: lib={self.asset_library_identifier}, path={self.relative_asset_identifier}"
        )

        if not self.relative_asset_identifier:
            self.report({"WARNING"}, "No asset selected")
            return {"CANCELLED"}

        # Click is from Asset Shelf, so use 3D cursor for placement
        location = context.scene.cursor.location.copy()
        result = place_asset(
            context,
            self.asset_library_identifier,
            self.relative_asset_identifier,
            location,
        )

        if result.success:
            self.report({"INFO"}, f"Placed: {result.object.name}")
            return {"FINISHED"}

        self.report({"ERROR"}, result.message or "Failed to place asset")
        return {"CANCELLED"}


class TRIVESTA_OT_drag_asset(Operator):
    """Drag and drop asset from Asset Shelf into 3D view."""

    bl_idname = "trivesta.drag_asset"
    bl_label = "Drag Asset"
    bl_options = {"REGISTER", "UNDO"}

    # Properties passed by Asset Shelf
    asset_library_type: IntProperty(options={"HIDDEN", "SKIP_SAVE"})  # type: ignore
    asset_library_identifier: StringProperty(options={"HIDDEN", "SKIP_SAVE"})  # type: ignore
    relative_asset_identifier: StringProperty(options={"HIDDEN", "SKIP_SAVE"})  # type: ignore

    # State management
    _state: DragState = DragState.IDLE
    _obj: bpy.types.Object | None = None
    _library: str = ""
    _path: str = ""

    # Performance optimization
    _last_raycast_time: float = 0.0
    _raycast_interval: float = 0.016  # ~60fps (16ms between raycasts)
    _last_location: Vector | None = None
    _position_threshold: float = 0.01  # Minimum movement to trigger update

    def _should_raycast(self) -> bool:
        """Check if enough time has passed for a new raycast."""
        now = time.perf_counter()
        if now - self._last_raycast_time >= self._raycast_interval:
            self._last_raycast_time = now
            return True
        return False

    def _position_changed(self, new_loc: Vector) -> bool:
        """Check if position changed enough to warrant update."""
        if self._last_location is None:
            return True
        try:
            delta = (new_loc - self._last_location).length
            return delta > self._position_threshold
        except (TypeError, AttributeError):
            return True

    def invoke(self, context: Context, event: Event) -> set[str]:
        debug(
            f"drag_asset.invoke: lib={self.asset_library_identifier}, path={self.relative_asset_identifier}"
        )

        if not self.relative_asset_identifier:
            return {"CANCELLED"}

        # Initialize state
        self._state = DragState.DRAGGING
        self._library = self.asset_library_identifier
        self._path = self.relative_asset_identifier
        self._obj = None
        self._last_raycast_time = 0.0
        self._last_location = None

        context.window_manager.modal_handler_add(self)
        context.window.cursor_set("CROSSHAIR")
        return {"RUNNING_MODAL"}

    def modal(self, context: Context, event: Event) -> set[str]:
        """Handle modal events with state machine."""
        try:
            # Edge case: Mode changed during drag
            if context.mode != "OBJECT":
                debug(f"Mode changed to {context.mode}, cancelling drag")
                return self._cancel(context)

            # Edge case: Window focus lost
            if event.type == "WINDOW_DEACTIVATE":
                debug("Window deactivated during drag")
                return self._cancel(context)

            # Dispatch to state handler
            if self._state == DragState.DRAGGING:
                return self._handle_dragging(context, event)
            elif self._state == DragState.OBJECT_CREATED:
                return self._handle_object_created(context, event)

            return {"RUNNING_MODAL"}

        except Exception as e:
            debug(f"Modal error: {e}")
            self._cleanup(context)
            return {"CANCELLED"}

    def _handle_dragging(self, context: Context, event: Event) -> set[str]:
        """Handle events when no object exists yet."""
        loc = get_mouse_location(context, event, exclude=None)

        if event.type == "MOUSEMOVE" and loc:
            # Create object on first valid location
            result = place_asset(context, self._library, self._path, loc)
            if result.success:
                self._obj = result.object
                self._state = DragState.OBJECT_CREATED
                context.window.cursor_set("NONE")
                debug("Object created, transitioning to OBJECT_CREATED state")
            else:
                debug(f"Placement failed: {result.message}")
            return {"RUNNING_MODAL"}

        # Cancel events
        if event.type in {"RIGHTMOUSE", "ESC"}:
            return self._cancel(context)

        # Left release before object created = cancel
        if event.type == "LEFTMOUSE" and event.value == "RELEASE":
            return self._cancel(context)

        return {"RUNNING_MODAL"}

    def _handle_object_created(self, context: Context, event: Event) -> set[str]:
        """Handle events when object exists and follows mouse."""
        if event.type == "MOUSEMOVE":
            # Throttle raycasts for performance
            if self._should_raycast():
                loc = get_mouse_location(context, event, exclude=self._obj)
                if loc and self._obj:
                    # Only update if position changed significantly
                    if self._position_changed(loc):
                        self._obj.location = loc
                        self._last_location = loc
                        # Only redraw when position actually changes
                        if context.area:
                            context.area.tag_redraw()
            return {"RUNNING_MODAL"}

        if event.type == "LEFTMOUSE" and event.value == "RELEASE":
            return self._finish(context)

        if event.type in {"RIGHTMOUSE", "ESC"}:
            return self._cancel(context)

        return {"RUNNING_MODAL"}

    def _finish(self, context: Context) -> set[str]:
        """Complete placement successfully."""
        context.window.cursor_set("DEFAULT")
        if self._obj:
            debug(f"Placed at {self._obj.location}")
        self._reset_state()
        return {"FINISHED"}

    def _cancel(self, context: Context) -> set[str]:
        """Cancel placement and cleanup."""
        self._cleanup(context)
        return {"CANCELLED"}

    def _cleanup(self, context: Context) -> None:
        """Clean up operator state and remove preview object."""
        try:
            context.window.cursor_set("DEFAULT")
        except Exception:
            pass  # Window may be invalid

        if self._obj:
            try:
                bpy.data.objects.remove(self._obj, do_unlink=True)
                debug("Preview object removed")
            except Exception as e:
                debug(f"Cleanup warning: {e}")

        self._reset_state()

    def _reset_state(self) -> None:
        """Reset all state variables."""
        self._state = DragState.IDLE
        self._obj = None
        self._library = ""
        self._path = ""
        self._last_raycast_time = 0.0
        self._last_location = None


__all__ = ["TRIVESTA_OT_place_asset", "TRIVESTA_OT_drag_asset"]
