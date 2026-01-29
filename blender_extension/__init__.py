bl_info = {
    "name": "Trivesta Level",
    "author": "Trivesta",
    "version": (0, 1, 0),
    "blender": (4, 2, 0),
    "location": "Properties > Scene",
    "description": "Level design pipeline for Three.js worlds",
    "category": "Import-Export",
}

import bpy
from bpy.props import StringProperty, PointerProperty
from bpy.types import PropertyGroup

from .operators import export_world, export_manifest
from .panels import main_panel


class TrivestaLevelSettings(PropertyGroup):
    export_path: StringProperty(
        name="Export Path",
        description="Directory for exported files",
        default="//exports/",
        subtype='DIR_PATH'
    )


classes = [
    TrivestaLevelSettings,
    export_world.TRIVESTA_OT_export_world,
    export_manifest.TRIVESTA_OT_export_manifest,
    main_panel.TRIVESTA_PT_main_panel,
    main_panel.TRIVESTA_PT_export_panel,
    main_panel.TRIVESTA_PT_assets_panel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.trivesta_level = PointerProperty(type=TrivestaLevelSettings)


def unregister():
    del bpy.types.Scene.trivesta_level

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
