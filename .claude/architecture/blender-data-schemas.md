# Blender Extension Data Schemas

## Overview

Data structures and JSON schemas used by the Blender extension v2.0.

## Core Dataclasses

Location: `blender_extension/core/data.py`

### Instance

Represents a placed object instance:
```python
@dataclass
class Instance:
    id: str                    # Unique instance ID
    name: str                  # Object name
    asset_id: str | None       # Reference to asset_definitions key
    position: tuple[float, float, float]  # Three.js coords
    rotation: tuple[float, float, float, float]  # Quaternion
    scale: tuple[float, float, float]
    bounding_box: dict         # {min: [...], max: [...]}
    custom_properties: dict
    island_id: str | None      # Parent island (if any)
```

### Island

Represents an island/zone in the world:
```python
@dataclass
class Island:
    id: str                    # e.g., "island_01"
    name: str                  # e.g., "Island_01"
    world_position: tuple[float, float, float]
    world_rotation: tuple[float, float, float, float]
    bounds: dict               # {min, max, center, radius}
    instances: list[str]       # Instance IDs in this island
    terrain_objects: list[str] # Terrain instance IDs
    collision_mesh: str | None # Path to collision GLB
```

### ExportData

Container for all export data:
```python
@dataclass
class ExportData:
    instances: list[Instance]
    terrain_objects: list[Instance]
    collision_objects: list[Instance]
    asset_definitions: dict[str, dict]
    islands: dict[str, Island]
    collections: dict          # Collection tree
```

## Scene Settings

**Class**: `TrivestaSceneSettings` (PropertyGroup)

**Location**: Attached to `bpy.types.Scene.trivesta`

```python
{
    "export_path": str,        # Default: "//exports/"
    "separate_assets": bool,   # Default: True
    "export_collision": bool,  # Default: True
    "export_islands": bool,    # Default: True
    "world_size_x": float,     # Default: 1024.0
    "world_size_z": float,     # Default: 1024.0
    "water_level": float,      # Default: 0.0
}
```

Access: `context.scene.trivesta.export_path`

## Object Settings

**Class**: `TrivestaObjectSettings` (PropertyGroup)

**Location**: Attached to `bpy.types.Object.trivesta`

```python
{
    "entity_type": str,        # Enum: static, npc, interactive, trigger, audio, terrain
    "is_terrain": bool,        # Mark as terrain mesh
    "is_collision": bool,      # Mark as collision mesh

    # NPC Dialog System (entity_type == "npc")
    "dialog_lines": CollectionProperty,  # List of DialogLine
    "dialog_line_index": int,            # Active selection index

    # Interactive Scripting (entity_type == "interactive")
    "script_id": str,          # Game engine handler reference
}
```

Access: `context.object.trivesta.entity_type`

### DialogLine PropertyGroup

```python
{
    "speaker": str,            # Character name (e.g., "Merchant")
    "text": str,               # Dialog content
}
```

### Entity Types

| Type | Description | Extra Properties |
|------|-------------|------------------|
| `static` | Merged for rendering | - |
| `npc` | Character with AI | `dialog_lines[]` |
| `interactive` | Player interaction | `script_id` |
| `trigger` | Invisible trigger zone | - |
| `audio` | Audio source | - |
| `terrain` | Ground/terrain mesh | - |

## Manifest v2.0 JSON Schema

**File**: `manifest.json`

```json
{
  "version": "2.0",
  "exported_at": "<ISO 8601 UTC timestamp>",
  "blender_file": "<absolute path to .blend>",

  "asset_definitions": {
    "<asset_id>": {
      "name": "<asset name>",
      "file": "assets/<asset_id>.glb",
      "source_library": "<source .blend path or null>",
      "bounding_box": {"min": [x,y,z], "max": [x,y,z]}
    }
  },

  "instances": [
    {
      "id": "<instance_id>",
      "name": "<object name>",
      "asset_id": "<references asset_definitions key>",
      "position": [x, y, z],
      "rotation": [x, y, z, w],
      "scale": [x, y, z],
      "bounding_box": {"min": [...], "max": [...]},
      "custom_properties": {},
      "island_id": "<island_id or null>"
    }
  ],

  "terrain_objects": [
    {
      "id": "<instance_id>",
      "name": "<terrain name>",
      "file": "islands/<island_id>.glb",
      "position": [x, y, z],
      "rotation": [x, y, z, w],
      "scale": [x, y, z],
      "island_id": "<island_id>"
    }
  ],

  "collections": {
    "name": "Scene Collection",
    "instances": ["<instance_ids>"],
    "children": {
      "<child_name>": { ... recursive ... }
    }
  },

  "islands": {
    "<island_id>": {
      "name": "<Island_Name>",
      "world_position": [x, y, z],
      "world_rotation": [x, y, z, w],
      "bounds": {
        "min": [x, y, z],
        "max": [x, y, z],
        "center": [x, y, z],
        "radius": <float>
      },
      "instances": ["<instance_ids in this island>"],
      "terrain_objects": ["<terrain_ids>"],
      "collision_mesh": "collision/<island_id>.glb"
    }
  },

  "world": {
    "size": [<world_size_x>, <world_size_z>],
    "water_level": <float>
  },

  "statistics": {
    "total_instances": <int>,
    "unique_assets": <int>,
    "terrain_objects": <int>,
    "islands": <int>,
    "files_created": <int>
  }
}
```

**Coordinate System**: Three.js (Y-up)

## TypeScript Interfaces (Consumer)

```typescript
interface Manifest {
  version: "2.0";
  exported_at: string;
  blender_file: string;
  asset_definitions: Record<string, AssetDefinition>;
  instances: Instance[];
  terrain_objects: TerrainObject[];
  collections: CollectionNode;
  islands: Record<string, Island>;
  world: WorldSettings;
  statistics: Statistics;
}

interface AssetDefinition {
  name: string;
  file: string;
  source_library: string | null;
  bounding_box: BoundingBox;
}

interface Instance {
  id: string;
  name: string;
  asset_id: string | null;
  position: [number, number, number];
  rotation: [number, number, number, number];
  scale: [number, number, number];
  bounding_box: BoundingBox;
  custom_properties: Record<string, unknown>;
  island_id: string | null;
}

interface TerrainObject {
  id: string;
  name: string;
  file: string;
  position: [number, number, number];
  rotation: [number, number, number, number];
  scale: [number, number, number];
  island_id: string;
}

interface CollectionNode {
  name: string;
  instances: string[];
  children: Record<string, CollectionNode>;
}

interface Island {
  name: string;
  world_position: [number, number, number];
  world_rotation: [number, number, number, number];
  bounds: {
    min: [number, number, number];
    max: [number, number, number];
    center: [number, number, number];
    radius: number;
  };
  instances: string[];
  terrain_objects: string[];
  collision_mesh: string | null;
}

interface WorldSettings {
  size: [number, number];
  water_level: number;
}

// NPC Dialog custom_properties
interface NPCCustomProperties {
  dialog: Array<{
    speaker: string;
    text: string;
  }>;
}

// Interactive custom_properties
interface InteractiveCustomProperties {
  script_id: string;
}

interface Statistics {
  total_instances: number;
  unique_assets: number;
  terrain_objects: number;
  islands: number;
  files_created: number;
}

interface BoundingBox {
  min: [number, number, number];
  max: [number, number, number];
}
```

## Custom Properties

Objects can have arbitrary custom properties accessible in manifest:

| Property | Type | Purpose |
|----------|------|---------|
| `trivesta_manifest_only` | bool | Exclude from GLB, include in manifest |
| `asset_type` | str | Asset classification |
| `*` | any | User-defined metadata |

### NPC Dialog Export (entity_type == "npc")

```json
{
  "id": "npc_merchant_001",
  "name": "Merchant",
  "entity_type": "npc",
  "asset_id": "npc_merchant",
  "position": [10.0, 0.0, 5.0],
  "custom_properties": {
    "dialog": [
      { "speaker": "Merchant", "text": "Welcome to my shop!" },
      { "speaker": "Merchant", "text": "What would you like?" }
    ]
  }
}
```

### Interactive Script Export (entity_type == "interactive")

```json
{
  "id": "interactive_chest_001",
  "name": "TreasureChest",
  "entity_type": "interactive",
  "asset_id": "chest_wooden",
  "position": [20.0, 0.0, 15.0],
  "custom_properties": {
    "script_id": "chest_open_handler"
  }
}
```

## GLB Export Settings

Settings passed to `bpy.ops.export_scene.gltf()`:

```python
{
    "filepath": "<path>/<file>.glb",
    "export_format": "GLB",
    "use_selection": True,
    "export_apply": True,         # Apply transforms
    "export_texcoords": True,
    "export_normals": True,
    "export_materials": "EXPORT",
    "export_yup": True,           # Three.js coordinate system
}
```
