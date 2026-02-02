import { describe, it, expect, vi, beforeEach } from "vitest";
import { Group } from "three";

// Control mock behavior via module-level flag
let shouldFailLoad = false;

// Mock TerrainLoader with proper class syntax
vi.mock("../../src/loaders/TerrainLoader", () => ({
  TerrainLoader: class MockTerrainLoader {
    loadIslandTerrain() {
      if (shouldFailLoad) {
        return Promise.reject(new Error("Load failed"));
      }
      return Promise.resolve({
        root: new Group(),
        mode: "group" as const,
        meshCount: 2,
        vertexCount: 1000,
      });
    }
  },
}));

// Mock GLTFLoader with proper class syntax
vi.mock("three/addons/loaders/GLTFLoader.js", () => ({
  GLTFLoader: class MockGLTFLoader {
    load(
      _path: string,
      onLoad: (gltf: { scene: Group }) => void,
      _onProgress?: unknown,
      onError?: (error: Error) => void
    ) {
      if (shouldFailLoad) {
        if (onError) {
          onError(new Error("File not found"));
        }
        return;
      }
      onLoad({ scene: new Group() });
    }
  },
}));

describe("WorldLoader terrain integration", () => {
  let WorldLoader: typeof import("../../src/world/WorldLoader").WorldLoader;
  let ManifestLoader: typeof import("../../src/loaders/ManifestLoader").ManifestLoader;

  beforeEach(async () => {
    shouldFailLoad = false;
    vi.resetModules();
    const worldModule = await import("../../src/world/WorldLoader");
    WorldLoader = worldModule.WorldLoader;

    const manifestModule = await import("../../src/loaders/ManifestLoader");
    ManifestLoader = manifestModule.ManifestLoader;
  });

  it("should use TerrainLoader for island terrain", async () => {
    const mockManifest = {
      version: "2.0" as const,
      exported_at: "2024-01-01T00:00:00Z",
      blender_file: "test.blend",
      instances: [],
      terrain_objects: [],
      islands: {
        test_island: {
          id: "test_island",
          name: "Test Island",
          world_position: [0, 0, 0] as [number, number, number],
          world_rotation: [0, 0, 0, 1] as [number, number, number, number],
          bounds: {
            min: [0, 0, 0] as [number, number, number],
            max: [10, 10, 10] as [number, number, number],
            radius: 10,
          },
          instances: [],
          terrain_objects: [],
          terrain: {
            chunks: ["islands/test_island/terrain/chunk.glb"],
            merged: null,
          },
        },
      },
      collections: undefined,
      asset_definitions: {},
      world: { size: [100, 100] as [number, number], water_level: 0 },
      statistics: { total_instances: 0 },
    };

    const manifestLoader = new ManifestLoader("/levels/demo");
    // @ts-expect-error - mock internal state for testing
    manifestLoader["manifest"] = mockManifest;

    const worldLoader = new WorldLoader(manifestLoader);
    const result = await worldLoader.load();

    expect(result.islands.has("test_island")).toBe(true);
    const islandGroup = result.islands.get("test_island");
    expect(islandGroup).toBeDefined();
    expect(islandGroup?.name).toBe("Test Island");
  });

  it("should handle terrain loading errors gracefully", async () => {
    shouldFailLoad = true;

    const mockManifest = {
      version: "2.0" as const,
      exported_at: "2024-01-01T00:00:00Z",
      blender_file: "test.blend",
      instances: [],
      terrain_objects: [],
      islands: {
        failing_island: {
          id: "failing_island",
          name: "Failing Island",
          world_position: [0, 0, 0] as [number, number, number],
          world_rotation: [0, 0, 0, 1] as [number, number, number, number],
          bounds: {
            min: [0, 0, 0] as [number, number, number],
            max: [10, 10, 10] as [number, number, number],
            radius: 10,
          },
          instances: [],
          terrain_objects: [],
          terrain: {
            chunks: ["islands/failing_island/terrain/missing.glb"],
            merged: null,
          },
        },
      },
      collections: undefined,
      asset_definitions: {},
      world: { size: [100, 100] as [number, number], water_level: 0 },
      statistics: { total_instances: 0 },
    };

    const manifestLoader = new ManifestLoader("/levels/demo");
    // @ts-expect-error - mock internal state for testing
    manifestLoader["manifest"] = mockManifest;

    const worldLoader = new WorldLoader(manifestLoader);

    // Should not throw even when terrain fails
    const result = await worldLoader.load();
    expect(result.islands.has("failing_island")).toBe(true);
  });
});
