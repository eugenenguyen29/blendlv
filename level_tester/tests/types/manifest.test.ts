import { describe, it, expect } from "vitest";
import type { IslandTerrain, Island } from "../../src/types/manifest";

describe("IslandTerrain type", () => {
  it("should have chunks and merged fields", () => {
    const terrain: IslandTerrain = {
      chunks: [],
      merged: null,
    };
    expect(terrain.chunks).toEqual([]);
    expect(terrain.merged).toBeNull();
  });

  it("should accept chunk paths", () => {
    const terrain: IslandTerrain = {
      chunks: ["islands/test/terrain/chunk_a.glb"],
      merged: null,
    };
    expect(terrain.chunks).toHaveLength(1);
  });

  it("should accept merged path", () => {
    const terrain: IslandTerrain = {
      chunks: [],
      merged: "islands/test/terrain/merged.glb",
    };
    expect(terrain.merged).toBe("islands/test/terrain/merged.glb");
  });
});

describe("Island type", () => {
  it("should include terrain field", () => {
    const island: Island = {
      id: "test",
      name: "Test Island",
      world_position: [0, 0, 0],
      world_rotation: [0, 0, 0, 1],
      bounds: { min: [0, 0, 0], max: [1, 1, 1], radius: 1 },
      instances: [],
      terrain_objects: [],
      terrain: {
        chunks: [],
        merged: null,
      },
    };
    expect(island.terrain).toBeDefined();
  });
});
