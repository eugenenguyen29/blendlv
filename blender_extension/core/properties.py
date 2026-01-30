"""Blender PropertyGroups for scene and object settings.

This module defines the PropertyGroup classes that store extension settings
on Blender Scene and Object data blocks. These are the primary interface
for users to configure export behavior.
"""

from __future__ import annotations

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

from .constants import DEFAULT_EXPORT_PATH, ENTITY_TYPES


class DialogLine(PropertyGroup):
    """Single dialog line entry for NPC conversations.

    Used as items in a CollectionProperty on TrivestaObjectSettings.
    Each line contains a speaker name and dialog text.

    Attributes:
        speaker: Character name who speaks this line.
        text: Dialog text content for this line.
    """

    speaker: StringProperty(
        name="Speaker",
        description="Character name who speaks this line",
        default="",
    )

    text: StringProperty(
        name="Text",
        description="Dialog text content for this line",
        default="",
    )


class TrivestaSceneSettings(PropertyGroup):
    """Scene-level export settings.

    Registered on bpy.types.Scene as 'trivesta'. Access via:
        context.scene.trivesta.export_path

    Attributes:
        export_path: Directory for exported files.
        separate_assets: Export instanced assets as separate GLB files.
        export_collision: Export collision meshes as separate files.
    """

    export_path: StringProperty(
        name="Export Path",
        description="Directory for exported files",
        default=DEFAULT_EXPORT_PATH,
        subtype="DIR_PATH",
    )

    separate_assets: BoolProperty(
        name="Separate Assets",
        description="Export instanced assets as separate GLB files",
        default=False,
    )

    export_collision: BoolProperty(
        name="Export Collision",
        description="Export collision meshes as separate files",
        default=True,
    )

    # World settings
    world_size_x: FloatProperty(
        name="World Size X",
        description="World extent in X direction (width)",
        default=1024.0,
        min=0.0,
        soft_max=8192.0,
        unit="LENGTH",
    )

    world_size_z: FloatProperty(
        name="World Size Z",
        description="World extent in Z direction (depth)",
        default=1024.0,
        min=0.0,
        soft_max=8192.0,
        unit="LENGTH",
    )

    water_level: FloatProperty(
        name="Water Level",
        description="Y coordinate of the water surface",
        default=0.0,
        soft_min=-100.0,
        soft_max=100.0,
        unit="LENGTH",
    )


class TrivestaObjectSettings(PropertyGroup):
    """Object-level entity settings.

    Registered on bpy.types.Object as 'trivesta'. Access via:
        context.object.trivesta.entity_type

    Attributes:
        entity_type: Type of game entity this object represents.
        is_terrain: Mark as terrain/ground mesh (not instanced).
        is_collision: Mark as collision-only mesh.
    """

    entity_type: EnumProperty(
        name="Entity Type",
        description="Type of game entity this object represents",
        items=ENTITY_TYPES,
        default="static",
    )

    is_terrain: BoolProperty(
        name="Is Terrain", description="Mark as terrain/ground mesh (not instanced)", default=False
    )

    is_collision: BoolProperty(
        name="Is Collision",
        description="Mark as collision-only mesh",
        default=False,
    )

    # NPC Dialog System
    dialog_lines: CollectionProperty(
        type=DialogLine,
        name="Dialog Lines",
        description="NPC dialog line entries",
    )

    dialog_line_index: IntProperty(
        name="Dialog Line Index",
        description="Active dialog line selection index",
        default=0,
        min=0,
    )

    # Interactive Scripting
    script_id: StringProperty(
        name="Script ID",
        description="Game engine handler reference for interactive behavior",
        default="",
    )


def register_properties() -> None:
    """Register property groups on Blender types.

    Must be called after registering the PropertyGroup classes.
    Creates 'trivesta' attribute on Scene and Object types.
    """
    bpy.types.Scene.trivesta = PointerProperty(type=TrivestaSceneSettings)
    bpy.types.Object.trivesta = PointerProperty(type=TrivestaObjectSettings)


def unregister_properties() -> None:
    """Unregister property groups from Blender types.

    Must be called before unregistering the PropertyGroup classes.
    Removes 'trivesta' attribute from Scene and Object types.
    """
    del bpy.types.Object.trivesta
    del bpy.types.Scene.trivesta
