"""Scene asset browser panel for Trivesta level design.

This module provides an N-panel (sidebar) in the 3D View that displays
linked assets from the current scene, allowing quick duplication and placement.
This is simpler than the Asset Shelf and doesn't require Asset Library setup.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import bpy
from bpy.props import StringProperty
from bpy.types import Operator, Panel, UIList

if TYPE_CHECKING:
    from bpy.types import Context, Event

from ..utils.naming import generate_asset_key
from ..utils.transforms import get_library_source


class TRIVESTA_UL_asset_list(UIList):
    """UI List for displaying scene assets."""

    bl_idname = "TRIVESTA_UL_asset_list"

    def draw_item(
        self,
        context: Context,
        layout: bpy.types.UILayout,
        data: object,
        item: bpy.types.PropertyGroup,
        icon: int,
        active_data: object,
        active_property: str,
        index: int = 0,
        flt_flag: int = 0,
    ) -> None:
        """Draw a single asset item in the list."""
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row(align=True)
            row.label(text=item.name, icon="OBJECT_DATA")
            row.label(text=f"({item.count})")
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text="", icon="OBJECT_DATA")


class AssetItem(bpy.types.PropertyGroup):
    """Property group for storing asset information."""

    name: StringProperty(name="Asset Name")  # type: ignore[valid-type]
    asset_key: StringProperty(name="Asset Key")  # type: ignore[valid-type]
    source_object: StringProperty(name="Source Object Name")  # type: ignore[valid-type]
    count: bpy.props.IntProperty(name="Instance Count", default=1)  # type: ignore[valid-type]


class TRIVESTA_OT_refresh_assets(Operator):
    """Refresh the asset list from scene objects."""

    bl_idname = "trivesta.refresh_assets"
    bl_label = "Refresh Assets"
    bl_description = "Scan scene for linked assets"

    def execute(self, context: Context) -> set[str]:
        """Scan scene and populate asset list."""
        scene = context.scene
        scene.trivesta_assets.clear()

        # Group objects by asset key
        asset_map: dict[str, dict] = {}

        for obj in scene.objects:
            if obj.type != "MESH":
                continue

            source = get_library_source(obj)
            if source is None:
                continue  # Skip local objects

            asset_key = generate_asset_key(obj)
            if asset_key not in asset_map:
                asset_map[asset_key] = {
                    "name": obj.name.rsplit(".", 1)[0],  # Remove .001 suffix
                    "key": asset_key,
                    "source_obj": obj.name,
                    "count": 0,
                }
            asset_map[asset_key]["count"] += 1

        # Populate the list
        for asset_data in sorted(asset_map.values(), key=lambda x: x["name"]):
            item = scene.trivesta_assets.add()
            item.name = asset_data["name"]
            item.asset_key = asset_data["key"]
            item.source_object = asset_data["source_obj"]
            item.count = asset_data["count"]

        self.report({"INFO"}, f"Found {len(asset_map)} unique assets")
        return {"FINISHED"}


class TRIVESTA_OT_place_scene_asset(Operator):
    """Place a copy of the selected asset at the 3D cursor."""

    bl_idname = "trivesta.place_scene_asset"
    bl_label = "Place Asset"
    bl_description = "Duplicate selected asset at 3D cursor or click location"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        """Check if an asset is selected."""
        return context.scene.trivesta_assets and 0 <= context.scene.trivesta_asset_index < len(
            context.scene.trivesta_assets
        )

    def execute(self, context: Context) -> set[str]:
        """Duplicate the asset at 3D cursor."""
        scene = context.scene
        asset_item = scene.trivesta_assets[scene.trivesta_asset_index]

        # Find source object
        source_obj = bpy.data.objects.get(asset_item.source_object)
        if source_obj is None:
            self.report({"ERROR"}, f"Source object not found: {asset_item.source_object}")
            return {"CANCELLED"}

        # Create linked duplicate
        new_obj = source_obj.copy()
        context.collection.objects.link(new_obj)

        # Position at 3D cursor
        new_obj.location = scene.cursor.location.copy()

        # Select new object
        bpy.ops.object.select_all(action="DESELECT")
        new_obj.select_set(True)
        context.view_layer.objects.active = new_obj

        self.report({"INFO"}, f"Placed: {asset_item.name}")
        return {"FINISHED"}

    def invoke(self, context: Context, event: Event) -> set[str]:
        """Place at mouse position if possible."""
        # Try raycast placement
        from ..utils.raycast import raycast_from_mouse

        hit, location, _normal, _obj = raycast_from_mouse(context, event)
        if hit and location:
            context.scene.cursor.location = location

        return self.execute(context)


class TRIVESTA_PT_asset_browser(Panel):
    """Panel for browsing and placing scene assets."""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Trivesta"
    bl_idname = "TRIVESTA_PT_asset_browser"
    bl_label = "Asset Browser"

    def draw(self, context: Context) -> None:
        """Draw the panel UI."""
        layout = self.layout
        scene = context.scene

        # Refresh button
        row = layout.row()
        row.operator("trivesta.refresh_assets", icon="FILE_REFRESH")

        # Asset list
        row = layout.row()
        row.template_list(
            "TRIVESTA_UL_asset_list",
            "",
            scene,
            "trivesta_assets",
            scene,
            "trivesta_asset_index",
            rows=8,
        )

        # Place button
        row = layout.row()
        row.scale_y = 1.5
        row.operator("trivesta.place_scene_asset", icon="ADD", text="Place Selected")

        # Info about selected asset
        if scene.trivesta_assets and 0 <= scene.trivesta_asset_index < len(scene.trivesta_assets):
            asset = scene.trivesta_assets[scene.trivesta_asset_index]
            box = layout.box()
            box.label(text=f"Key: {asset.asset_key}")
            box.label(text=f"Instances: {asset.count}")


def register_asset_browser_properties() -> None:
    """Register asset browser properties on Scene."""
    bpy.types.Scene.trivesta_assets = bpy.props.CollectionProperty(type=AssetItem)
    bpy.types.Scene.trivesta_asset_index = bpy.props.IntProperty(name="Asset Index")


def unregister_asset_browser_properties() -> None:
    """Unregister asset browser properties."""
    del bpy.types.Scene.trivesta_asset_index
    del bpy.types.Scene.trivesta_assets


__all__ = [
    "AssetItem",
    "TRIVESTA_UL_asset_list",
    "TRIVESTA_OT_refresh_assets",
    "TRIVESTA_OT_place_scene_asset",
    "TRIVESTA_PT_asset_browser",
    "register_asset_browser_properties",
    "unregister_asset_browser_properties",
]
