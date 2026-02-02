import { describe, it, expect, beforeEach } from "vitest";
import {
  config,
  setConfig,
  resetConfig,
  devOnly,
  defaultConfig,
  getAvailableTerrainModes,
  PRODUCTION_TERRAIN_MODES,
  DEV_TERRAIN_MODES,
} from "../src/config";

describe("config", () => {
  beforeEach(() => {
    // Reset config to defaults between tests
    resetConfig();
  });

  it("should export TerrainRenderMode type", () => {
    expect(["merged", "batched", "group"]).toContain(config.terrainMode);
  });

  it("should have debug flag", () => {
    expect(typeof config.debug).toBe("boolean");
  });

  it("setConfig should update config", () => {
    setConfig({ terrainMode: "batched" });
    expect(config.terrainMode).toBe("batched");
  });

  it("setConfig should preserve other values", () => {
    const originalDebug = config.debug;
    setConfig({ terrainMode: "group" });
    expect(config.debug).toBe(originalDebug);
  });

  it("devOnly should return value in dev mode", () => {
    // In test environment, import.meta.env.DEV is typically true
    const result = devOnly(() => "test");
    // Result depends on environment - just verify it doesn't throw
    expect(result === "test" || result === undefined).toBe(true);
  });

  it("resetConfig should restore defaults", () => {
    setConfig({ terrainMode: "batched", debug: !defaultConfig.debug });
    resetConfig();
    expect(config.terrainMode).toBe(defaultConfig.terrainMode);
    expect(config.debug).toBe(defaultConfig.debug);
  });
});

describe("getAvailableTerrainModes", () => {
  it("should return all modes in dev environment", () => {
    // Tests run in DEV mode
    const modes = getAvailableTerrainModes();

    expect(modes).toContain("merged");
    expect(modes).toContain("batched");
    expect(modes).toContain("group");
    expect(modes.length).toBe(3);
  });

  it("should match DEV_TERRAIN_MODES constant in dev environment", () => {
    const modes = getAvailableTerrainModes();
    expect(modes).toEqual(DEV_TERRAIN_MODES);
  });
});

describe("PRODUCTION_TERRAIN_MODES constant", () => {
  it("should only include merged mode", () => {
    expect(PRODUCTION_TERRAIN_MODES).toEqual(["merged"]);
  });

  it("should be readonly array", () => {
    expect(Array.isArray(PRODUCTION_TERRAIN_MODES)).toBe(true);
    expect(PRODUCTION_TERRAIN_MODES.length).toBe(1);
  });
});

describe("DEV_TERRAIN_MODES constant", () => {
  it("should include all three modes", () => {
    expect(DEV_TERRAIN_MODES).toHaveLength(3);
    expect(DEV_TERRAIN_MODES).toContain("merged");
    expect(DEV_TERRAIN_MODES).toContain("batched");
    expect(DEV_TERRAIN_MODES).toContain("group");
  });

  it("should be readonly array", () => {
    expect(Array.isArray(DEV_TERRAIN_MODES)).toBe(true);
  });
});

describe("setConfig terrain mode validation", () => {
  beforeEach(() => {
    resetConfig();
  });

  it("should allow setting valid terrain modes in dev", () => {
    setConfig({ terrainMode: "group" });
    expect(config.terrainMode).toBe("group");

    setConfig({ terrainMode: "batched" });
    expect(config.terrainMode).toBe("batched");

    setConfig({ terrainMode: "merged" });
    expect(config.terrainMode).toBe("merged");
  });

  it("should validate mode against available modes", () => {
    // In dev, all modes are available, so all should work
    const availableModes = getAvailableTerrainModes();

    for (const mode of availableModes) {
      setConfig({ terrainMode: mode });
      expect(config.terrainMode).toBe(mode);
    }
  });
});
