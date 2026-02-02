/**
 * ManifestLoader - Fetches and parses manifest.json
 * Provides efficient lookup indices for instances
 */

import type {
  Manifest,
  Instance,
  TerrainObject,
  AssetDefinition,
  Island,
  EntityType,
} from "../types/manifest";

export interface ManifestIndices {
  byId: Map<string, Instance | TerrainObject>;
  byAssetId: Map<string, Instance[]>;
  byEntityType: Map<EntityType, Instance[]>;
  byIslandId: Map<string, Instance[]>;
}

export class ManifestLoader {
  private basePath: string;
  private manifest: Manifest | null = null;
  private indices: ManifestIndices | null = null;

  constructor(basePath: string) {
    // Normalize path (remove trailing slash)
    this.basePath = basePath.replace(/\/$/, "");
  }

  /**
   * Load and parse manifest.json
   */
  async load(): Promise<Manifest> {
    const url = `${this.basePath}/manifest.json`;
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Failed to load manifest: ${response.status} ${url}`);
    }

    this.manifest = (await response.json()) as Manifest;
    this.buildIndices();

    return this.manifest;
  }

  /**
   * Build lookup indices for efficient queries
   */
  private buildIndices(): void {
    if (!this.manifest) return;

    const byId = new Map<string, Instance | TerrainObject>();
    const byAssetId = new Map<string, Instance[]>();
    const byEntityType = new Map<EntityType, Instance[]>();
    const byIslandId = new Map<string, Instance[]>();

    // Index regular instances
    for (const instance of this.manifest.instances) {
      byId.set(instance.id, instance);

      // By asset_id
      if (instance.asset_id) {
        const list = byAssetId.get(instance.asset_id) ?? [];
        list.push(instance);
        byAssetId.set(instance.asset_id, list);
      }

      // By entity_type
      const typeList = byEntityType.get(instance.entity_type) ?? [];
      typeList.push(instance);
      byEntityType.set(instance.entity_type, typeList);

      // By island_id (from custom_properties if present)
      const islandId = instance.custom_properties?.island_id as
        | string
        | undefined;
      if (islandId) {
        const islandList = byIslandId.get(islandId) ?? [];
        islandList.push(instance);
        byIslandId.set(islandId, islandList);
      }
    }

    // Index terrain objects
    for (const terrain of this.manifest.terrain_objects) {
      byId.set(terrain.id, terrain);
    }

    this.indices = { byId, byAssetId, byEntityType, byIslandId };
  }

  /**
   * Get the loaded manifest (throws if not loaded)
   */
  getManifest(): Manifest {
    if (!this.manifest) {
      throw new Error("Manifest not loaded. Call load() first.");
    }
    return this.manifest;
  }

  /**
   * Get instance by ID
   */
  getInstance(id: string): Instance | TerrainObject | undefined {
    return this.indices?.byId.get(id);
  }

  /**
   * Get all instances using a specific asset
   */
  getInstancesByAsset(assetId: string): Instance[] {
    return this.indices?.byAssetId.get(assetId) ?? [];
  }

  /**
   * Get all instances of a specific entity type
   */
  getInstancesByType(entityType: EntityType): Instance[] {
    return this.indices?.byEntityType.get(entityType) ?? [];
  }

  /**
   * Get all instances in an island
   */
  getInstancesByIsland(islandId: string): Instance[] {
    return this.indices?.byIslandId.get(islandId) ?? [];
  }

  /**
   * Get asset definition by ID
   */
  getAsset(assetId: string): AssetDefinition | undefined {
    return this.manifest?.asset_definitions[assetId];
  }

  /**
   * Get island by ID
   */
  getIsland(islandId: string): Island | undefined {
    return this.manifest?.islands[islandId];
  }

  /**
   * Resolve full path to an asset file
   */
  resolveAssetPath(assetId: string): string | null {
    const asset = this.getAsset(assetId);
    if (!asset) return null;
    return `${this.basePath}/${asset.file}`;
  }

  /**
   * Resolve full path to island terrain GLB
   */
  resolveIslandPath(islandId: string): string {
    return `${this.basePath}/islands/${islandId}.glb`;
  }

  /**
   * Resolve full path to collision mesh
   */
  resolveCollisionPath(islandId: string): string {
    return `${this.basePath}/collision/${islandId}.glb`;
  }

  /**
   * Get base path for relative URL resolution
   */
  getBasePath(): string {
    return this.basePath;
  }
}
