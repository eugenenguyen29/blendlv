import { describe, it, expect, vi, beforeEach } from "vitest";
import { Group, Mesh, BoxGeometry, MeshBasicMaterial, Matrix4 } from "three";
import type { Island } from "../../src/types/manifest";

// Control mock behavior via module-level flag
let shouldFailLoad = false;
let mockMeshPosition = { x: 0, y: 0, z: 0 };

// Mock GLTFLoader
vi.mock("three/addons/loaders/GLTFLoader.js", () => {
  return {
    GLTFLoader: class MockGLTFLoader {
      load(
        _path: string,
        onLoad: (gltf: { scene: Group }) => void,
        _onProgress?: unknown,
        onError?: (error: Error) => void
      ) {
        if (shouldFailLoad) {
          // Simulate load failure
          if (onError) {
            onError(new Error("File not found"));
          }
          return;
        }
        // Create mock GLTF result with parent node (simulates real GLB structure)
        const scene = new Group();
        const parentNode = new Group();
        parentNode.position.set(mockMeshPosition.x, mockMeshPosition.y, mockMeshPosition.z);
        const mesh = new Mesh(
          new BoxGeometry(1, 1, 1),
          new MeshBasicMaterial()
        );
        mesh.name = "terrain_mesh";
        // Mesh local position is 0,0,0 - world position comes from parent
        parentNode.add(mesh);
        scene.add(parentNode);
        // Update world matrices
        scene.updateMatrixWorld(true);
        onLoad({ scene });
      }
    },
  };
});

describe("TerrainLoader", () => {
  let TerrainLoader: typeof import("../../src/loaders/TerrainLoader").TerrainLoader;
  let setConfig: typeof import("../../src/config").setConfig;
  let resetConfig: typeof import("../../src/config").resetConfig;

  const mockIsland: Island = {
    id: "test_island",
    name: "Test Island",
    world_position: [0, 0, 0],
    world_rotation: [0, 0, 0, 1],
    bounds: { min: [0, 0, 0], max: [10, 10, 10], radius: 10 },
    instances: [],
    terrain_objects: [],
    terrain: {
      chunks: ["islands/test_island/terrain/chunk_a.glb"],
      merged: null,
    },
  };

  beforeEach(async () => {
    // Reset mock flags
    shouldFailLoad = false;
    mockMeshPosition = { x: 0, y: 0, z: 0 };

    vi.resetModules();
    const configModule = await import("../../src/config");
    setConfig = configModule.setConfig;
    resetConfig = configModule.resetConfig;
    resetConfig();

    const loaderModule = await import("../../src/loaders/TerrainLoader");
    TerrainLoader = loaderModule.TerrainLoader;
  });

  it("should create instance with base path", () => {
    const loader = new TerrainLoader("/levels/demo");
    expect(loader).toBeDefined();
  });

  it("should load merged terrain when merged path exists", async () => {
    const islandWithMerged: Island = {
      ...mockIsland,
      terrain: {
        chunks: [],
        merged: "islands/test_island/terrain/merged.glb",
      },
    };

    setConfig({ terrainMode: "merged" });
    const loader = new TerrainLoader("/levels/demo");
    const result = await loader.loadIslandTerrain(islandWithMerged);

    expect(result.mode).toBe("merged");
    expect(result.root).toBeDefined();
  });

  it("should create Group in group mode", async () => {
    setConfig({ terrainMode: "group" });
    const loader = new TerrainLoader("/levels/demo");
    const result = await loader.loadIslandTerrain(mockIsland);

    expect(result.mode).toBe("group");
    expect(result.root).toBeInstanceOf(Group);
  });

  it("should return mesh count", async () => {
    setConfig({ terrainMode: "group" });
    const loader = new TerrainLoader("/levels/demo");
    const result = await loader.loadIslandTerrain(mockIsland);

    expect(result.meshCount).toBeGreaterThanOrEqual(0);
  });

  it("should return vertex count", async () => {
    setConfig({ terrainMode: "group" });
    const loader = new TerrainLoader("/levels/demo");
    const result = await loader.loadIslandTerrain(mockIsland);

    expect(typeof result.vertexCount).toBe("number");
  });

  it("should handle empty terrain gracefully", async () => {
    const emptyIsland: Island = {
      ...mockIsland,
      terrain: {
        chunks: [],
        merged: null,
      },
    };

    const loader = new TerrainLoader("/levels/demo");
    const result = await loader.loadIslandTerrain(emptyIsland);

    expect(result.meshCount).toBe(0);
    expect(result.root).toBeInstanceOf(Group);
  });

  it("should respect mode override parameter", async () => {
    setConfig({ terrainMode: "merged" });
    const loader = new TerrainLoader("/levels/demo");
    const result = await loader.loadIslandTerrain(mockIsland, "group");

    expect(result.mode).toBe("group");
  });

  it("should handle GLTF load failure gracefully", async () => {
    // Enable failure mode
    shouldFailLoad = true;

    const islandWithChunks: Island = {
      ...mockIsland,
      terrain: {
        chunks: ["islands/test_island/terrain/missing_chunk.glb"],
        merged: null,
      },
    };

    const loader = new TerrainLoader("/levels/demo");
    const result = await loader.loadIslandTerrain(islandWithChunks);

    // Should return empty result instead of throwing
    expect(result.root).toBeInstanceOf(Group);
    expect(result.meshCount).toBe(0);
    expect(result.vertexCount).toBe(0);
  });

  it("should preserve world position when cloning meshes in group mode", async () => {
    // Set mock mesh position (simulates mesh nested under a positioned parent node)
    mockMeshPosition = { x: -4.82, y: 0, z: 0.55 };

    setConfig({ terrainMode: "group" });
    const loader = new TerrainLoader("/levels/demo");
    const result = await loader.loadIslandTerrain(mockIsland);

    expect(result.root).toBeInstanceOf(Group);
    const group = result.root as Group;
    expect(group.children.length).toBe(1);

    const clonedMesh = group.children[0] as Mesh;
    // Verify world position was applied to the clone (not 0,0,0)
    expect(clonedMesh.position.x).toBeCloseTo(-4.82, 2);
    expect(clonedMesh.position.y).toBeCloseTo(0, 2);
    expect(clonedMesh.position.z).toBeCloseTo(0.55, 2);
  });
});
