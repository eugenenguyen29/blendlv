"""Constants and enumerations for the Trivesta Level extension.

This module defines all constants, enums, and default values used throughout
the extension. No external dependencies required.
"""

# Entity type enum items for Blender EnumProperty
# Format: (identifier, name, description)
ENTITY_TYPES: list[tuple[str, str, str]] = [
    ('static', "Static", "Merged for rendering"),
    ('npc', "NPC", "Character with AI"),
    ('interactive', "Interactive", "Player interaction"),
    ('trigger', "Trigger", "Invisible trigger zone"),
    ('audio', "Audio", "Audio source"),
    ('terrain', "Terrain", "Ground/terrain mesh"),
]

# Manifest format versions
MANIFEST_VERSION: str = "2.0"
MANIFEST_VERSION_LEGACY: str = "1.0"

# Default export settings
DEFAULT_EXPORT_PATH: str = "//exports/"
DEFAULT_CHUNK_SIZE: float = 64.0

# Export modes
EXPORT_MODE_COMBINED: str = "combined"
EXPORT_MODE_SEPARATED: str = "separated"
