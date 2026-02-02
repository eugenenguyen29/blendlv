import { describe, it, expect, beforeEach } from "vitest";

describe("ManifestLoader", () => {
  let ManifestLoader: typeof import("../../src/loaders/ManifestLoader").ManifestLoader;

  beforeEach(async () => {
    const module = await import("../../src/loaders/ManifestLoader");
    ManifestLoader = module.ManifestLoader;
  });

  describe("getBasePath", () => {
    it("should return the base path", () => {
      const loader = new ManifestLoader("/levels/demo");
      expect(loader.getBasePath()).toBe("/levels/demo");
    });

    it("should normalize trailing slashes", () => {
      const loader = new ManifestLoader("/levels/demo/");
      expect(loader.getBasePath()).toBe("/levels/demo");
    });
  });

  describe("terrain path resolution", () => {
    it("should resolve terrain chunk path", () => {
      const loader = new ManifestLoader("/levels/demo");
      const path = loader.resolveTerrainChunkPath("island_01", "chunk_a");
      expect(path).toBe("/levels/demo/islands/island_01/terrain/chunk_a.glb");
    });

    it("should resolve terrain merged path", () => {
      const loader = new ManifestLoader("/levels/demo");
      const path = loader.resolveTerrainMergedPath("island_01");
      expect(path).toBe("/levels/demo/islands/island_01/terrain/merged.glb");
    });

    it("should work with nested base paths", () => {
      const loader = new ManifestLoader("/assets/levels/world_01");
      const chunkPath = loader.resolveTerrainChunkPath("main_island", "grass");
      const mergedPath = loader.resolveTerrainMergedPath("main_island");

      expect(chunkPath).toBe(
        "/assets/levels/world_01/islands/main_island/terrain/grass.glb"
      );
      expect(mergedPath).toBe(
        "/assets/levels/world_01/islands/main_island/terrain/merged.glb"
      );
    });
  });
});
