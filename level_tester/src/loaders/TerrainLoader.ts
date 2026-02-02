/**
 * TerrainLoader - Loads and optimizes terrain meshes
 *
 * Supports three render modes:
 * - merged: BufferGeometryUtils.mergeGeometries (production)
 * - batched: Three.js BatchedMesh (dev, single draw call)
 * - group: Simple Group with individual meshes (dev, full debug)
 */

import {
  Group,
  Mesh,
  BufferGeometry,
  Material,
  MeshStandardMaterial,
  BatchedMesh,
  Object3D,
} from "three";
import * as BufferGeometryUtils from "three/addons/utils/BufferGeometryUtils.js";
import { GLTFLoader, type GLTF } from "three/addons/loaders/GLTFLoader.js";
import type { Island } from "../types/manifest";
import { config, devOnly, type TerrainRenderMode } from "../config";

export interface TerrainLoadResult {
  /** Root object containing terrain */
  root: Object3D;
  /** Render mode used */
  mode: TerrainRenderMode;
  /** Number of source meshes */
  meshCount: number;
  /** Total vertex count */
  vertexCount: number;
}

export class TerrainLoader {
  private gltfLoader: GLTFLoader;
  private basePath: string;

  constructor(basePath: string) {
    this.basePath = basePath;
    this.gltfLoader = new GLTFLoader();
  }

  /**
   * Load terrain for an island with appropriate render mode
   */
  async loadIslandTerrain(
    island: Island,
    modeOverride?: TerrainRenderMode
  ): Promise<TerrainLoadResult> {
    const mode = modeOverride ?? config.terrainMode;
    const terrain = island.terrain;

    // If merged file exists and mode is "merged", use it directly
    if (mode === "merged" && terrain.merged) {
      return this.loadMergedTerrain(terrain.merged, island, mode);
    }

    // Load individual chunks
    if (terrain.chunks.length > 0) {
      return this.loadChunks(terrain.chunks, island, mode);
    }

    // Fallback: try merged file regardless of mode
    if (terrain.merged) {
      return this.loadMergedTerrain(terrain.merged, island, mode);
    }

    // No terrain available
    return {
      root: new Group(),
      mode,
      meshCount: 0,
      vertexCount: 0,
    };
  }

  /**
   * Load pre-merged terrain GLB
   */
  private async loadMergedTerrain(
    path: string,
    island: Island,
    mode: TerrainRenderMode
  ): Promise<TerrainLoadResult> {
    try {
      const gltf = await this.loadGLTF(`${this.basePath}/${path}`);
      const root = new Group();
      root.name = `${island.name}_terrain_merged`;

      let meshCount = 0;
      let vertexCount = 0;

      gltf.scene.traverse((child) => {
        if (child instanceof Mesh) {
          meshCount++;
          vertexCount += child.geometry.attributes.position?.count ?? 0;
        }
      });

      while (gltf.scene.children.length > 0) {
        root.add(gltf.scene.children[0]);
      }

      return { root, mode, meshCount, vertexCount };
    } catch (error) {
      devOnly(() =>
        console.warn(
          `Failed to load merged terrain for ${island.id}: ${path}`,
          error
        )
      );
      return {
        root: new Group(),
        mode,
        meshCount: 0,
        vertexCount: 0,
      };
    }
  }

  /**
   * Load individual chunks and combine based on mode
   */
  private async loadChunks(
    chunkPaths: string[],
    island: Island,
    mode: TerrainRenderMode
  ): Promise<TerrainLoadResult> {
    // Load all chunks in parallel, filtering out failures
    const results = await Promise.allSettled(
      chunkPaths.map((path) => this.loadGLTF(`${this.basePath}/${path}`))
    );

    const gltfs = results
      .filter(
        (result): result is PromiseFulfilledResult<Awaited<ReturnType<typeof this.loadGLTF>>> =>
          result.status === "fulfilled"
      )
      .map((result) => result.value);

    // Log any failures
    results.forEach((result, index) => {
      if (result.status === "rejected") {
        devOnly(() =>
          console.warn(
            `Failed to load terrain chunk ${chunkPaths[index]}:`,
            result.reason
          )
        );
      }
    });

    if (gltfs.length === 0) {
      return {
        root: new Group(),
        mode,
        meshCount: 0,
        vertexCount: 0,
      };
    }

    // Extract meshes from all chunks
    const meshes: Mesh[] = [];
    for (const gltf of gltfs) {
      gltf.scene.traverse((child) => {
        if (child instanceof Mesh) {
          child.updateMatrixWorld(true);
          meshes.push(child);
        }
      });
    }

    if (meshes.length === 0) {
      return {
        root: new Group(),
        mode,
        meshCount: 0,
        vertexCount: 0,
      };
    }

    let vertexCount = 0;
    meshes.forEach((m) => {
      vertexCount += m.geometry.attributes.position?.count ?? 0;
    });

    let root: Object3D;

    switch (mode) {
      case "merged":
        root = this.createMergedGeometry(meshes, island);
        break;
      case "batched":
        root = this.createBatchedMesh(meshes, island);
        break;
      case "group":
      default:
        root = this.createGroup(meshes, island);
        break;
    }

    return {
      root,
      mode,
      meshCount: meshes.length,
      vertexCount,
    };
  }

  /**
   * Mode: merged - Single merged geometry (best production performance)
   */
  private createMergedGeometry(meshes: Mesh[], island: Island): Object3D {
    const geometries: BufferGeometry[] = [];

    for (const mesh of meshes) {
      const geom = mesh.geometry.clone();
      geom.applyMatrix4(mesh.matrixWorld);
      geometries.push(geom);
    }

    const mergedGeometry = BufferGeometryUtils.mergeGeometries(geometries);

    // Dispose cloned geometries to prevent memory leak
    geometries.forEach((g) => g.dispose());

    if (!mergedGeometry) {
      devOnly(() =>
        console.warn(`Failed to merge terrain geometries for ${island.id}`)
      );
      return this.createGroup(meshes, island);
    }

    // Use first mesh's material or create default
    const material =
      (meshes[0]?.material as Material) ?? new MeshStandardMaterial();
    const mergedMesh = new Mesh(mergedGeometry, material);
    mergedMesh.name = `${island.name}_terrain_merged`;

    return mergedMesh;
  }

  /**
   * Mode: batched - BatchedMesh for single draw call with individual control
   */
  private createBatchedMesh(meshes: Mesh[], island: Island): Object3D {
    if (meshes.length === 0) return new Group();

    // Calculate total counts
    let totalVertices = 0;
    let totalIndices = 0;
    for (const mesh of meshes) {
      totalVertices += mesh.geometry.attributes.position?.count ?? 0;
      totalIndices += mesh.geometry.index?.count ?? 0;
    }

    // Use first mesh's material
    const material =
      (meshes[0]?.material as Material) ?? new MeshStandardMaterial();

    try {
      const batchedMesh = new BatchedMesh(
        meshes.length,
        totalVertices,
        totalIndices,
        material
      );
      batchedMesh.name = `${island.name}_terrain_batched`;

      // Add geometries and instances
      for (const mesh of meshes) {
        const geomId = batchedMesh.addGeometry(mesh.geometry);
        const instanceId = batchedMesh.addInstance(geomId);
        mesh.updateMatrixWorld();
        batchedMesh.setMatrixAt(instanceId, mesh.matrixWorld);
      }

      return batchedMesh;
    } catch (error) {
      devOnly(() =>
        console.warn(
          `BatchedMesh failed for ${island.id}, falling back to Group:`,
          error
        )
      );
      return this.createGroup(meshes, island);
    }
  }

  /**
   * Mode: group - Individual meshes in Group (full debug visibility)
   */
  private createGroup(meshes: Mesh[], island: Island): Object3D {
    const group = new Group();
    group.name = `${island.name}_terrain_group`;

    for (const mesh of meshes) {
      const clone = mesh.clone();
      clone.userData.terrainChunk = true;
      group.add(clone);
    }

    devOnly(() => {
      console.log(
        `[TerrainLoader] Created group with ${meshes.length} chunks for ${island.id}`
      );
    });

    return group;
  }

  private loadGLTF(path: string): Promise<GLTF> {
    return new Promise((resolve, reject) => {
      this.gltfLoader.load(path, resolve, undefined, reject);
    });
  }
}
