# Blender Extension Data Schemas

Location: `blender_extension/core/data.py`

## Core Dataclasses

### Instance

```python
@dataclass
class Instance:
    id: str                      # Unique ID (name + hash)
    name: str                    # Display name
    asset_id: str | None         # Reference to AssetDefinition (None for terrain/collision)
    entity_type: str             # "static", "npc", "interactive", "terrain", "collision", etc.
    position: tuple[float, float, float]    # Three.js Y-up coords
    rotation: tuple[float, float, float, float]  # Quaternion (x, y, z, w)
    scale: tuple[float, float, float]
    bounding_box: BoundingBox    # {min, max, radius}
    collection_path: list[str]   # Hierarchy path ["Scene", "Island_01", ...]
    custom_properties: dict      # User props, dialog, script_id
```

### AssetDefinition

```python
@dataclass
class AssetDefinition:
    id: str              # Asset identifier
    file: str            # Relative path to GLB
    source: str | None   # Linked library path (if linked)
```

### Island

```python
@dataclass
class Island:
    id: str                      # e.g., "island_01"
    name: str                    # e.g., "Island_01"
    world_position: tuple[float, float, float]
    world_rotation: tuple[float, float, float, float]
    bounds: BoundingBox
    instances: list[str]         # Instance names
    terrain_objects: list[str]
    terrain: IslandTerrain       # Terrain file paths (nested structure)
    collision_mesh: str | None   # Path to collision GLB

@dataclass
class IslandTerrain:
    chunks: list[str]            # Chunk paths (individual terrain GLBs)
    merged: str | None           # Merged terrain GLB path
```

### ExportData

```python
@dataclass
class ExportData:
    asset_definitions: dict[str, AssetDefinition]
    instances: list[Instance]
    terrain_objects: list[Instance]
    islands: dict[str, Island]
    collection_tree: CollectionNode | None
    by_asset_id: dict[str, list[Instance]]     # Computed index
    by_entity_type: dict[str, list[Instance]]  # Computed index

    def build_indices(self): ...  # Populate computed indices
```

### CollectionNode

```python
@dataclass
class CollectionNode:
    name: str
    children: dict[str, CollectionNode]
    instance_ids: list[str]
```

### BoundingBox (TypedDict)

```python
class BoundingBox(TypedDict):
    min: list[float]   # [x, y, z]
    max: list[float]   # [x, y, z]
    radius: float
```

## PropertyGroups

### TrivestaSceneSettings

Attached to `bpy.types.Scene.trivesta`:

| Property | Type | Default |
|----------|------|---------|
| `export_path` | str | `"//exports/"` |
| `separate_assets` | bool | `True` |
| `export_collision` | bool | `True` |
| `terrain_export_mode` | Enum | `"merged"` (merged, individual, dual) |
| `world_size_x` | float | `1024.0` |
| `world_size_z` | float | `1024.0` |
| `water_level` | float | `0.0` |

### TrivestaObjectSettings

Attached to `bpy.types.Object.trivesta`:

| Property | Type | Description |
|----------|------|-------------|
| `entity_type` | Enum | static, npc, interactive, trigger, audio, terrain |
| `is_terrain` | bool | Mark as terrain mesh |
| `is_collision` | bool | Mark as collision mesh |
| `dialog_lines` | Collection | NPC dialog (when entity_type="npc") |
| `dialog_line_index` | int | Active dialog selection |
| `script_id` | str | Interactive handler (when entity_type="interactive") |

### DialogLine

| Property | Type |
|----------|------|
| `speaker` | str |
| `text` | str |

## Manifest v2.0 Schema

```json
{
  "_generated": "AUTO-GENERATED FILE",
  "version": "2.0",
  "exported_at": "ISO timestamp",
  "blender_file": "path/to/file.blend",

  "asset_definitions": {
    "{asset_id}": {
      "id": "{asset_id}",
      "file": "assets/{asset_id}.glb",
      "source": "library/path" // or null
    }
  },

  "instances": [{
    "id": "unique_id",
    "name": "object_name",
    "asset_id": "{asset_id}",  // or null for terrain/collision
    "entity_type": "static|npc|interactive|terrain|collision",
    "position": [x, y, z],     // Three.js Y-up
    "rotation": [x, y, z, w],  // Quaternion
    "scale": [x, y, z],
    "bounding_box": {"min": [], "max": [], "radius": float},
    "collection_path": ["Path", "To", "Object"],
    "custom_properties": {
      "dialog": [{"speaker": "", "text": ""}],  // NPC
      "script_id": "handler_name"                // Interactive
    }
  }],

  "terrain_objects": [/* same as instances */],

  "collections": {
    "name": "Scene Collection",
    "children": { /* recursive */ },
    "instances": ["instance_ids"]
  },

  "islands": {
    "{island_id}": {
      "id": "{island_id}",
      "name": "Island_01",
      "world_position": [x, y, z],
      "world_rotation": [x, y, z, w],
      "bounds": {"min": [], "max": [], "radius": float},
      "instances": ["ids"],
      "terrain_objects": ["ids"],
      "terrain": {
        "chunks": ["terrain/chunk_*.glb"],
        "merged": "terrain/merged.glb"
      },
      "collision_mesh": "collision/{island_id}.glb"
    }
  },

  "world": {"size": [x, z], "water_level": float},
  "statistics": {"total_instances": int, "total_assets": int, ...}
}
```

## TypeScript Interfaces

```typescript
interface Manifest {
  version: "2.0";
  asset_definitions: Record<string, AssetDefinition>;
  instances: Instance[];
  terrain_objects: Instance[];
  collections: CollectionNode;
  islands: Record<string, Island>;
  world: { size: [number, number]; water_level: number };
  statistics: Statistics;
}

interface Instance {
  id: string;
  name: string;
  asset_id: string | null;
  entity_type: string;
  position: [number, number, number];
  rotation: [number, number, number, number];
  scale: [number, number, number];
  bounding_box: { min: number[]; max: number[]; radius: number };
  collection_path: string[];
  custom_properties: Record<string, unknown>;
}

interface AssetDefinition {
  id: string;
  file: string;
  source: string | null;
}

interface IslandTerrain {
  chunks: string[];
  merged: string | null;
}

interface Island {
  id: string;
  name: string;
  world_position: [number, number, number];
  world_rotation: [number, number, number, number];
  bounds: { min: number[]; max: number[]; radius: number };
  instances: string[];
  terrain_objects: string[];
  terrain: IslandTerrain;
  collision_mesh: string | null;
}

interface CollectionNode {
  name: string;
  children: Record<string, CollectionNode>;
  instances: string[];
}

// NPC custom_properties.dialog
type Dialog = Array<{ speaker: string; text: string }>;
```

## GLB Export Settings

```python
bpy.ops.export_scene.gltf(
    filepath="...",
    export_format="GLB",
    use_selection=True,
    export_apply=True,
    export_yup=True,  # Three.js coords
)
```
