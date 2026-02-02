# Blender Extension Architecture

## Overview

Location: `blender_extension/`

Blender add-on for Three.js level export. Version 2.0 with Strategy pattern entity extraction.

## Structure

```
blender_extension/
├── __init__.py              # Entry point, registration
├── blender_manifest.toml    # Blender extension manifest
├── core/
│   ├── constants.py         # ENTITY_TYPES, MANIFEST_VERSION
│   ├── data.py              # Dataclasses (Instance, AssetDefinition, Island, ExportData)
│   ├── properties.py        # Scene + Object PropertyGroups
│   └── registry.py          # Class registration in dependency order
├── entities/                # Entity extractors (Strategy pattern)
│   ├── __init__.py          # Registry + extract_all() orchestrator
│   ├── base.py              # EntityExtractor ABC
│   ├── collection.py        # CollectionExtractor (EMPTY with instance_type='COLLECTION')
│   ├── collision.py         # CollisionExtractor
│   ├── static.py            # StaticExtractor (default fallback)
│   └── terrain.py           # TerrainExtractor
├── exporters/
│   ├── __init__.py          # export_world() orchestrator
│   ├── base.py              # ExportResult, SelectionState
│   ├── glb.py               # GLB export wrapper
│   ├── assets.py            # Asset deduplication & export
│   ├── islands.py           # Per-island terrain export
│   ├── collision.py         # Per-island collision export
│   └── manifest.py          # v2.0 manifest serialization
├── operators/
│   ├── export.py            # TRIVESTA_OT_export
│   ├── dialog.py            # NPC dialog CRUD operators
│   └── placement.py         # Asset placement operators
├── panels/
│   ├── scene.py             # TRIVESTA_PT_scene_panel (main)
│   ├── export.py            # TRIVESTA_PT_export_panel
│   ├── object.py            # TRIVESTA_PT_object_panel (entity type, dialog)
│   ├── assets.py            # Linked assets list
│   ├── asset_browser.py     # Asset browser panel (N-panel)
│   └── asset_shelf.py       # Asset shelf (Blender 4.2+)
└── utils/
    ├── transforms.py        # Coordinate conversion (Z-up → Y-up)
    ├── naming.py            # Asset key generation, sanitization
    ├── files.py             # Path resolution
    ├── islands.py           # Island detection & local coords
    ├── collections.py       # Collection tree traversal
    ├── placement.py         # Asset placement helpers
    └── raycast.py           # Placement raycast
```

## Registration Order

```python
# core/registry.py - Dependency order
1. PropertyGroups (DialogLine, TrivestaSceneSettings, TrivestaObjectSettings)
2. Operators (TRIVESTA_OT_*)
3. UI Lists (TRIVESTA_UL_*)
4. Panels (TRIVESTA_PT_*)
5. Asset Shelf (TRIVESTA_AST_*)
```

## Entity Extraction (Strategy Pattern)

```
Scene Objects
    ↓ get_extractor(obj) - first match wins
CollectionExtractor → EMPTY with instance_type='COLLECTION' (NPC/Interactive)
CollisionExtractor  → name ends "_collision" OR is_collision=True
TerrainExtractor    → is_terrain=True OR entity_type='terrain'
StaticExtractor     → default fallback for MESH
    ↓
extract_all(context) → (instances, terrain_objects, collision_objects)
```

## Export Pipeline

```
export_world(context, export_path)
    ↓
1. register_extractors()
2. extract_all() → instances, terrain, collision
3. detect_islands() → Island_* collections
4. build_collection_tree()
5. ExportData() + build_indices()
6. convert_instances_to_local()
7. export_assets() → assets/*.glb
8. export_islands() → islands/*.glb
9. export_collision() → collision/*.glb
10. write_manifest() → manifest.json
```

## Coordinate Conversion

Blender (Z-up) → Three.js (Y-up):
- Position: `(x, y, z)` → `(x, z, -y)`
- Rotation: `(x, y, z, w)` → `(x, z, -y, w)`
- Scale: `(x, y, z)` → `(x, z, y)`

## Output Structure

```
exports/
├── manifest.json      # v2.0 metadata
├── assets/            # Deduplicated assets
├── islands/           # Per-island terrain
└── collision/         # Per-island collision
```

## Version

- Blender: 4.2.0+
- Manifest: v2.0
