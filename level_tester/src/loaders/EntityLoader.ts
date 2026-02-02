/**
 * EntityLoader - Loads entity instances (static, NPC, interactive, etc.)
 * Handles asset loading, instancing, and delegates to handlers via registry
 */

import { Group, Object3D, Vector3 } from "three";
import { GLTFLoader, type GLTF } from "three/addons/loaders/GLTFLoader.js";
import { ManifestLoader } from "./ManifestLoader";
import { entityRegistry } from "./entities";
import type { EntityResult, NPCData, InteractiveData } from "./entities";
import type {
  Instance,
  EntityType,
  Vec3,
  Quaternion,
  DialogLine,
} from "../types/manifest";

/**
 * Loaded NPC with dialog data accessible
 * @deprecated Use EntityResult<NPCData> from handlers
 */
export interface LoadedNPC {
  object: Object3D;
  instance: Instance;
  dialog: DialogLine[];
}

/**
 * Loaded interactive object with script reference
 * @deprecated Use EntityResult<InteractiveData> from handlers
 */
export interface LoadedInteractive {
  object: Object3D;
  instance: Instance;
  scriptId: string;
}

/**
 * Generic loaded entity
 */
export interface LoadedEntity {
  object: Object3D;
  instance: Instance;
}

export interface EntityLoadResult {
  /** Root group containing all entities */
  root: Group;
  /** All loaded entities by ID */
  entities: Map<string, LoadedEntity>;
  /** NPCs with dialog data */
  npcs: Map<string, LoadedNPC>;
  /** Interactive objects with script IDs */
  interactives: Map<string, LoadedInteractive>;
  /** Entities grouped by type */
  byType: Map<EntityType, LoadedEntity[]>;
}

export interface EntityLoaderOptions {
  /** Entity types to load (default: all) */
  entityTypes?: EntityType[];
  /** Only load entities in specific islands */
  islandFilter?: string[];
  /** Progress callback */
  onProgress?: (loaded: number, total: number, assetId: string) => void;
}

export class EntityLoader {
  private gltfLoader: GLTFLoader;
  private manifestLoader: ManifestLoader;
  private assetCache: Map<string, GLTF> = new Map();

  constructor(manifestLoader: ManifestLoader) {
    this.manifestLoader = manifestLoader;
    this.gltfLoader = new GLTFLoader();
  }

  /**
   * Load all entity instances
   */
  async load(options: EntityLoaderOptions = {}): Promise<EntityLoadResult> {
    const manifest = this.manifestLoader.getManifest();
    const root = new Group();
    root.name = "Entities";

    const entities = new Map<string, LoadedEntity>();
    const npcs = new Map<string, LoadedNPC>();
    const interactives = new Map<string, LoadedInteractive>();
    const byType = new Map<EntityType, LoadedEntity[]>();

    // Filter instances
    let instances = manifest.instances;

    if (options.entityTypes) {
      instances = instances.filter((i) =>
        options.entityTypes!.includes(i.entity_type)
      );
    }

    if (options.islandFilter) {
      instances = instances.filter((i) => {
        const islandId = i.custom_properties?.island_id as string | undefined;
        return islandId && options.islandFilter!.includes(islandId);
      });
    }

    // Pre-load all required assets
    const assetIds = new Set<string>();
    for (const instance of instances) {
      if (instance.asset_id) {
        assetIds.add(instance.asset_id);
      }
    }

    let loadedAssets = 0;
    const totalAssets = assetIds.size;

    for (const assetId of assetIds) {
      await this.preloadAsset(assetId);
      loadedAssets++;
      options.onProgress?.(loadedAssets, totalAssets, assetId);
    }

    // Create instances using handlers
    console.log(`[EntityLoader] Creating ${instances.length} entity instances`);
    for (const instance of instances) {
      console.log(`[EntityLoader] Processing instance: ${instance.name} (${instance.id}) at position:`, instance.position);
      const result = this.createEntity(instance);
      if (!result) {
        console.warn(`[EntityLoader] Failed to create entity for ${instance.name}`);
        continue;
      }

      const loaded: LoadedEntity = {
        object: result.object,
        instance: result.instance,
      };

      console.log(`[EntityLoader] Added ${instance.name} to scene. Object position:`, result.object.position.toArray());
      entities.set(instance.id, loaded);
      root.add(result.object);

      // Group by type
      const typeList = byType.get(instance.entity_type) ?? [];
      typeList.push(loaded);
      byType.set(instance.entity_type, typeList);

      // Handle NPCs with dialog
      if (instance.entity_type === "npc") {
        const npcResult = result as EntityResult<NPCData>;
        npcs.set(instance.id, {
          object: result.object,
          instance,
          dialog: npcResult.data.dialog,
        });
      }

      // Handle interactive objects
      if (instance.entity_type === "interactive") {
        const interactiveResult = result as EntityResult<InteractiveData>;
        if (interactiveResult.data.scriptId) {
          interactives.set(instance.id, {
            object: result.object,
            instance,
            scriptId: interactiveResult.data.scriptId,
          });
        }
      }
    }

    // Debug: Log final entity positions
    console.log(`[EntityLoader] Final entity summary:`);
    console.log(`  - Total entities: ${entities.size}`);
    console.log(`  - NPCs: ${npcs.size}`);
    console.log(`  - Interactives: ${interactives.size}`);
    for (const entity of entities.values()) {
      const pos = entity.object.position;
      const worldPos = new Vector3();
      entity.object.getWorldPosition(worldPos);
      console.log(`  - ${entity.instance.name}: local=${pos.toArray()}, world=${worldPos.toArray()}`);
    }

    return { root, entities, npcs, interactives, byType };
  }

  /**
   * Load only NPC entities
   */
  async loadNPCs(): Promise<Map<string, LoadedNPC>> {
    const result = await this.load({ entityTypes: ["npc"] });
    return result.npcs;
  }

  /**
   * Load only interactive entities
   */
  async loadInteractives(): Promise<Map<string, LoadedInteractive>> {
    const result = await this.load({ entityTypes: ["interactive"] });
    return result.interactives;
  }

  /**
   * Pre-load an asset into cache
   */
  private async preloadAsset(assetId: string): Promise<GLTF | null> {
    if (this.assetCache.has(assetId)) {
      return this.assetCache.get(assetId)!;
    }

    const assetPath = this.manifestLoader.resolveAssetPath(assetId);
    if (!assetPath) {
      console.warn(`Asset not found: ${assetId}`);
      return null;
    }

    try {
      const gltf = await this.loadGLTF(assetPath);
      this.assetCache.set(assetId, gltf);
      return gltf;
    } catch (error) {
      console.warn(`Failed to load asset ${assetId}:`, error);
      return null;
    }
  }

  /**
   * Create an entity using the registered handler
   */
  private createEntity(instance: Instance): EntityResult | null {
    const handler = entityRegistry.getHandler(instance.entity_type);

    if (!handler) {
      // Fallback for unregistered types
      return this.createFallbackEntity(instance);
    }

    const asset = instance.asset_id
      ? this.assetCache.get(instance.asset_id) ?? null
      : null;

    return handler.create({ instance, asset });
  }

  /**
   * Fallback entity creation for unregistered entity types
   */
  private createFallbackEntity(instance: Instance): EntityResult {
    const group = new Group();
    group.name = instance.name;
    group.userData.instanceId = instance.id;
    group.userData.entityType = instance.entity_type;
    group.userData.instance = instance;

    this.applyTransform(group, instance.position, instance.rotation, instance.scale);

    if (instance.asset_id) {
      const gltf = this.assetCache.get(instance.asset_id);
      if (gltf) {
        const clone = gltf.scene.clone(true);
        group.add(clone);
      }
    }

    return { object: group, instance, data: undefined };
  }

  /**
   * Apply transform to an Object3D
   */
  private applyTransform(
    object: Object3D,
    position: Vec3,
    rotation: Quaternion,
    scale: Vec3
  ): void {
    object.position.set(position[0], position[1], position[2]);
    object.quaternion.set(rotation[0], rotation[1], rotation[2], rotation[3]);
    object.scale.set(scale[0], scale[1], scale[2]);
  }

  /**
   * Load a GLTF/GLB file
   */
  private loadGLTF(path: string): Promise<GLTF> {
    return new Promise((resolve, reject) => {
      this.gltfLoader.load(
        path,
        (gltf) => resolve(gltf),
        undefined,
        (error) => reject(error)
      );
    });
  }

  /**
   * Clear the asset cache
   */
  clearCache(): void {
    this.assetCache.clear();
  }

  /**
   * Get an NPC's dialog by instance ID
   */
  static getDialog(entity: LoadedEntity): DialogLine[] {
    const props = entity.instance.custom_properties;
    if (!props || !Array.isArray(props.dialog)) return [];
    return props.dialog as DialogLine[];
  }

  /**
   * Get an interactive's script ID
   */
  static getScriptId(entity: LoadedEntity): string | null {
    const props = entity.instance.custom_properties;
    if (!props || typeof props.script_id !== "string") return null;
    return props.script_id;
  }
}
