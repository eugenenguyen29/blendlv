/**
 * WorldLoader - Loads world geometry (terrain, islands) into Three.js
 * Handles coordinate system (already Y-up from Blender export)
 */

import {
  Group,
  Mesh,
  Object3D,
  Vector3,
  Box3,
} from "three";
import { GLTFLoader, type GLTF } from "three/addons/loaders/GLTFLoader.js";
import { ManifestLoader } from "../loaders/ManifestLoader";
import { TerrainLoader } from "../loaders/TerrainLoader";
import { devOnly } from "../config";
import type {
  Island,
  TerrainObject,
  Quaternion,
  Vec3,
} from "../types/manifest";

export interface WorldLoadResult {
  /** Root group containing all world geometry */
  root: Group;
  /** Individual island groups indexed by island ID */
  islands: Map<string, Group>;
  /** Terrain meshes indexed by terrain object ID */
  terrainMeshes: Map<string, Object3D>;
  /** World bounds */
  bounds: Box3;
}

export interface WorldLoaderOptions {
  /** Load collision meshes (default: false) */
  loadCollision?: boolean;
  /** Only load specific islands by ID */
  islandFilter?: string[];
  /** Callback for load progress */
  onProgress?: (loaded: number, total: number) => void;
}

export class WorldLoader {
  private gltfLoader: GLTFLoader;
  private manifestLoader: ManifestLoader;
  private terrainLoader: TerrainLoader;

  constructor(manifestLoader: ManifestLoader) {
    this.manifestLoader = manifestLoader;
    this.gltfLoader = new GLTFLoader();
    this.terrainLoader = new TerrainLoader(manifestLoader.getBasePath());
  }

  /**
   * Load the entire world (all islands and terrain)
   */
  async load(options: WorldLoaderOptions = {}): Promise<WorldLoadResult> {
    const manifest = this.manifestLoader.getManifest();
    const root = new Group();
    root.name = "World";

    const islands = new Map<string, Group>();
    const terrainMeshes = new Map<string, Object3D>();
    const bounds = new Box3();

    // Get islands to load
    const islandIds = options.islandFilter ?? Object.keys(manifest.islands);
    const totalItems = islandIds.length;
    let loadedItems = 0;

    // Load each island
    for (const islandId of islandIds) {
      const island = manifest.islands[islandId];
      if (!island) continue;

      const islandGroup = await this.loadIsland(island, options);
      islands.set(islandId, islandGroup);
      root.add(islandGroup);

      // Expand world bounds
      const islandBounds = new Box3().setFromObject(islandGroup);
      bounds.union(islandBounds);

      loadedItems++;
      options.onProgress?.(loadedItems, totalItems);
    }

    // Also load any terrain objects not associated with islands
    for (const terrain of manifest.terrain_objects) {
      const islandId = terrain.custom_properties?.island_id as
        | string
        | undefined;
      if (!islandId || !islands.has(islandId)) {
        // Standalone terrain - load directly into root
        // Note: terrain files might be in different locations
        // For now, we just track them in the map
        terrainMeshes.set(terrain.id, new Group()); // Placeholder
      }
    }

    return { root, islands, terrainMeshes, bounds };
  }

  /**
   * Load a single island with its terrain
   */
  async loadIsland(
    island: Island,
    options: WorldLoaderOptions = {}
  ): Promise<Group> {
    const group = new Group();
    group.name = island.name;
    group.userData.islandId = island.id;
    group.userData.island = island;

    // NOTE: We do NOT apply world_position/rotation to the island group.
    // The terrain GLB files already contain geometry in world space coordinates.
    // The island's world_position is stored in userData for reference (camera focus, etc.)
    // but should not be used as a transform since it would double-transform the terrain.

    // Load terrain using TerrainLoader
    try {
      const terrainResult = await this.terrainLoader.loadIslandTerrain(island);
      terrainResult.root.name = `${island.name}_terrain`;
      group.add(terrainResult.root);

      devOnly(() => {
        console.log(
          `[WorldLoader] Loaded terrain for ${island.id}: ` +
            `mode=${terrainResult.mode}, meshes=${terrainResult.meshCount}, ` +
            `vertices=${terrainResult.vertexCount}`
        );
      });
    } catch (error) {
      console.warn(`Failed to load terrain for island ${island.id}:`, error);
    }

    // Optionally load collision mesh
    if (options.loadCollision && island.collision_mesh) {
      const collisionPath = this.manifestLoader.resolveCollisionPath(island.id);
      try {
        const collisionGltf = await this.loadGLTF(collisionPath);
        const collisionGroup = new Group();
        collisionGroup.name = `${island.name}_collision`;
        collisionGroup.visible = false; // Hidden by default
        collisionGroup.userData.isCollision = true;

        while (collisionGltf.scene.children.length > 0) {
          const child = collisionGltf.scene.children[0];
          child.visible = false;
          collisionGroup.add(child);
        }

        group.add(collisionGroup);
      } catch (error) {
        console.warn(
          `Failed to load collision for island ${island.id}:`,
          error
        );
      }
    }

    return group;
  }

  /**
   * Load a single terrain object
   */
  async loadTerrainObject(terrain: TerrainObject): Promise<Object3D> {
    const group = new Group();
    group.name = terrain.name;
    group.userData.terrainId = terrain.id;
    group.userData.terrain = terrain;

    this.applyTransform(group, terrain.position, terrain.rotation, terrain.scale);

    return group;
  }

  /**
   * Apply position, rotation, scale to an Object3D
   */
  private applyTransform(
    object: Object3D,
    position: Vec3,
    rotation: Quaternion,
    scale?: Vec3
  ): void {
    // Position (already in Three.js Y-up coordinates)
    object.position.set(position[0], position[1], position[2]);

    // Rotation (quaternion: x, y, z, w)
    object.quaternion.set(rotation[0], rotation[1], rotation[2], rotation[3]);

    // Scale
    if (scale) {
      object.scale.set(scale[0], scale[1], scale[2]);
    }
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
   * Get all meshes from an Object3D hierarchy
   */
  static getMeshes(object: Object3D): Mesh[] {
    const meshes: Mesh[] = [];
    object.traverse((child) => {
      if (child instanceof Mesh) {
        meshes.push(child);
      }
    });
    return meshes;
  }

  /**
   * Create a bounding box helper from island bounds data
   */
  static createBoundsFromIsland(island: Island): Box3 {
    const min = new Vector3(...island.bounds.min);
    const max = new Vector3(...island.bounds.max);
    return new Box3(min, max);
  }
}
