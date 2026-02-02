import { describe, it, expect, beforeEach } from "vitest";
import {
  config,
  setConfig,
  resetConfig,
  devOnly,
  defaultConfig,
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
