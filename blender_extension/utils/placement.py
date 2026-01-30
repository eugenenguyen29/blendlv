"""Entity type inference and asset linking utilities.

This module provides utilities for automatically detecting entity types
from asset names and applying trivesta settings to placed objects.
"""

from __future__ import annotations

import bpy

# Entity type detection prefixes
# Maps entity type to list of name prefixes that indicate that type
ENTITY_TYPE_PREFIXES: dict[str, list[str]] = {
    "static": ["Prop", "Static", "Decoration", "Deco"],
    "npc": ["Actor", "NPC", "Character", "Enemy"],
    "interactive": ["Interact", "Pickup", "Item", "Door"],
    "trigger": ["Trigger", "Zone", "Area"],
    "audio": ["Audio", "Sound", "Music"],
    "terrain": ["Terrain", "Ground", "Floor", "Landscape"],
}


def infer_entity_type(asset_name: str) -> str:
    """Detect entity type from asset name prefix.

    Checks the asset name against known prefixes to determine
    the appropriate entity type. Matching is case-insensitive.

    Args:
        asset_name: Name of the asset to analyze.

    Returns:
        Entity type string (e.g., 'static', 'npc', 'terrain').
        Defaults to 'static' if no prefix matches.

    Examples:
        >>> infer_entity_type("PropTree_Oak")
        'static'
        >>> infer_entity_type("NPC_Villager")
        'npc'
        >>> infer_entity_type("TerrainRock_Large")
        'terrain'
        >>> infer_entity_type("RandomObject")
        'static'
    """
    name_lower = asset_name.lower()

    for entity_type, prefixes in ENTITY_TYPE_PREFIXES.items():
        for prefix in prefixes:
            if name_lower.startswith(prefix.lower()):
                return entity_type

    return "static"


def apply_entity_settings(
    obj: bpy.types.Object,
    asset_name: str,
    auto_assign: bool = True,
) -> None:
    """Apply trivesta entity settings to a placed object.

    Sets the entity type based on the asset name and configures
    related properties like is_terrain flag.

    Args:
        obj: Blender object to configure.
        asset_name: Name of the asset (used for type inference).
        auto_assign: If True, automatically infer and set entity type.
            If False, only apply terrain flag if type is already 'terrain'.

    Note:
        Does nothing if the object lacks the trivesta property group.
    """
    if not hasattr(obj, "trivesta"):
        return

    if auto_assign:
        entity_type = infer_entity_type(asset_name)
        obj.trivesta.entity_type = entity_type

        if entity_type == "terrain":
            obj.trivesta.is_terrain = True
    else:
        # Only sync terrain flag if already set to terrain type
        if obj.trivesta.entity_type == "terrain":
            obj.trivesta.is_terrain = True
