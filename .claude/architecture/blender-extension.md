# Blender Extension Architecture

## Overview

Location: `blender_extension/`

A Blender add-on for level design pipeline exporting to Three.js-compatible formats. Version 2.0 with clean domain-driven architecture.

## Structure

```
blender_extension/
├── __init__.py              # Entry point only (~51 lines)
├── blender_manifest.toml    # Blender extension manifest
├── core/                    # Domain models & configuration
│   ├── __init__.py
│   ├── constants.py         # Enums, version info
│   ├── data.py              # Dataclasses (Instance, Island, ExportData)
│   ├── properties.py        # Scene + Object PropertyGroups
│   └── registry.py          # Class registration helpers
├── entities/                # Entity extractors (Strategy pattern)
│   ├── __init__.py          # extract_all(), register_extractors()
│   ├── base.py              # EntityExtractor ABC
│   ├── static.py            # StaticMeshExtractor
│   ├── terrain.py           # TerrainExtractor
│   └── collision.py         # CollisionExtractor
├── exporters/               # Export modules
│   ├── __init__.py          # export_world() orchestrator
│   ├── base.py              # ExportResult, shared types
│   ├── glb.py               # GLB export helper
│   ├── assets.py            # Asset separation export (deduplicated)
│   ├── islands.py           # Per-island terrain export
│   ├── collision.py         # Per-island collision export
│   └── manifest.py          # ManifestSerializer (v2.0)
├── operators/
│   ├── export.py            # TRIVESTA_OT_export (unified)
│   ├── placement.py         # Asset placement operators
│   └── dialog.py            # NPC dialog operators + UIList
├── panels/                  # Split UI panels
│   ├── __init__.py
│   ├── scene.py             # Main panel + World Settings
│   ├── export.py            # Export controls
│   ├── assets.py            # Linked assets list
│   └── object.py            # Object properties
└── utils/                   # Utility modules
    ├── __init__.py          # Re-exports all utilities
    ├── transforms.py        # Coordinate conversion
    ├── naming.py            # Asset key generation
    ├── files.py             # Path handling
    ├── islands.py           # Island detection
    └── collections.py       # Collection tree traversal
```

## Entry Point (`__init__.py`)

Minimal entry point using registry pattern:

```python
from blender_extension.core.registry import collect_classes
from blender_extension.core.properties import register_properties, unregister_properties
from blender_extension.entities import register_extractors

def register():
    for cls in collect_classes():
        bpy.utils.register_class(cls)
    register_properties()
    register_extractors()

def unregister():
    unregister_properties()
    for cls in reversed(collect_classes()):
        bpy.utils.unregister_class(cls)
```

## Component Relationships

```
__init__.py
    ├── core/
    │   ├── registry.py      → Collects all classes
    │   ├── properties.py    → PropertyGroups
    │   └── data.py          → Shared dataclasses
    ├── entities/
    │   └── *.py             → Extract scene data
    ├── exporters/
    │   ├── __init__.py      → export_world() main entry
    │   └── *.py             → Focused export modules
    ├── operators/
    │   └── export.py        → UI trigger → exporters/
    ├── panels/
    │   └── *.py             → UI → operators, properties
    └── utils/
        └── *.py             → Shared utilities
```

## Architecture Patterns

| Pattern | Implementation |
|---------|----------------|
| **Strategy** | Entity extractors (static, terrain, collision) |
| **Registry** | Class collection, extractor registration |
| **Composition** | Export composed of focused modules |
| **Dataclass** | Immutable data transfer objects |

## Data Flow

```
Scene Objects
    ↓
entities/ (extract)
    ↓
ExportData (instances, terrain, collision)
    ↓
utils/islands.py (detect + group)
    ↓
exporters/ (GLB + manifest)
    ↓
Output files
```

## Coordinate System

Blender (Z-up) → Three.js (Y-up):
- Position: `(x, y, z)` → `(x, z, -y)`
- Rotation: `(x, y, z, w)` → `(x, z, -y, w)`
- Scale: `(x, y, z)` → `(x, z, y)`

## Key Features

1. **Asset Deduplication**: 100 trees → 1 tree.glb (unique assets only)
2. **Island-Based Structure**: Per-island terrain and collision
3. **Instancing**: Multiple instances reference shared assets
4. **Manifest v2.0**: Islands, collections, statistics (no world.glb)
5. **Local Coordinates**: Instance positions relative to island origin
6. **Linked Asset Tracking**: External .blend dependencies tracked
7. **NPC Dialog System**: Per-object dialog lines with popup editor
8. **Interactive Scripting**: script_id reference for game engine handlers

## Export Output

```
exports/
├── manifest.json           # Level data (instances, positions, dialog, etc.)
├── assets/                 # Unique assets (deduplicated)
│   ├── tree_oak.glb
│   ├── npc_merchant.glb
│   └── rock_large.glb
├── islands/                # Terrain meshes per island
│   └── island_01.glb
└── collision/              # Collision meshes per island
    └── island_01.glb
```

**Note**: `world.glb` is not exported. Assets are managed separately.

## Version Info

- Blender: 4.2.0 - 6.0.0
- Python: 3.11+
- Extension ID: `trivesta_level`
- Extension Version: 2.0.0
