/**
 * Manifest v2.0 TypeScript Types
 * Matches the Blender extension export schema
 */

// Tuple types for transforms
export type Vec3 = [number, number, number];
export type Vec2 = [number, number];
export type Quaternion = [number, number, number, number]; // [x, y, z, w]

// Entity types supported by the extension
export type EntityType =
  | "static"
  | "npc"
  | "interactive"
  | "trigger"
  | "audio"
  | "terrain";

export interface BoundingBox {
  min: Vec3;
  max: Vec3;
  radius?: number;
}

export interface AssetDefinition {
  id: string;
  file: string;
  source?: string | null;
  bounding_box?: BoundingBox;
}

export interface Instance {
  id: string;
  name: string;
  entity_type: EntityType;
  asset_id?: string | null;
  position: Vec3;
  rotation: Quaternion;
  scale: Vec3;
  bounding_box: BoundingBox;
  collection_path?: string[];
  custom_properties?: Record<string, unknown>;
}

export interface TerrainObject {
  id: string;
  name: string;
  entity_type: "terrain";
  position: Vec3;
  rotation: Quaternion;
  scale: Vec3;
  bounding_box: BoundingBox;
  collection_path?: string[];
  custom_properties?: Record<string, unknown>;
}

export interface CollectionNode {
  name: string;
  instances: string[];
  children: Record<string, CollectionNode>;
}

export interface IslandBounds {
  min: Vec3;
  max: Vec3;
  center?: Vec3;
  radius: number;
}

/**
 * Terrain file paths for an island
 */
export interface IslandTerrain {
  /** Individual chunk file paths (dev/individual mode) */
  chunks: string[];
  /** Merged terrain file path (prod/merged mode) */
  merged: string | null;
}

export interface Island {
  id: string;
  name: string;
  world_position: Vec3;
  world_rotation: Quaternion;
  bounds: IslandBounds;
  instances: string[];
  terrain_objects: string[];
  terrain: IslandTerrain;
  collision_mesh?: string | null;
}

export interface WorldSettings {
  size: Vec2;
  water_level: number;
}

export interface Statistics {
  total_instances: number;
  total_terrain?: number;
  total_assets?: number;
  total_islands?: number;
  unique_assets?: number;
  terrain_objects?: number;
  islands?: number;
  files_created?: number;
}

export interface Manifest {
  version: "2.0";
  exported_at: string;
  blender_file: string;
  asset_definitions: Record<string, AssetDefinition>;
  instances: Instance[];
  terrain_objects: TerrainObject[];
  collections?: CollectionNode;
  islands: Record<string, Island>;
  world: WorldSettings;
  statistics: Statistics;
}

// Custom property types for specific entity types
export interface DialogLine {
  speaker: string;
  text: string;
}

export interface NPCProperties extends Record<string, unknown> {
  dialog?: DialogLine[];
}

export interface InteractiveProperties extends Record<string, unknown> {
  script_id?: string;
}

// Type guards
export function isNPCInstance(instance: Instance): boolean {
  return instance.entity_type === "npc";
}

export function isInteractiveInstance(instance: Instance): boolean {
  return instance.entity_type === "interactive";
}

export function hasDialog(
  props: Record<string, unknown>
): props is NPCProperties {
  return Array.isArray(props.dialog);
}

export function hasScriptId(
  props: Record<string, unknown>
): props is InteractiveProperties {
  return typeof props.script_id === "string";
}
