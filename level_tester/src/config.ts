/**
 * Runtime configuration with environment-aware defaults
 */

export type TerrainRenderMode = "merged" | "batched" | "group";

export interface RuntimeConfig {
  /** Terrain rendering strategy */
  terrainMode: TerrainRenderMode;
  /** Enable debug helpers */
  debug: boolean;
}

/** Terrain modes available in production (performance-only) */
export const PRODUCTION_TERRAIN_MODES: readonly TerrainRenderMode[] = ["merged"];

/** Terrain modes available in development (all modes for debugging) */
export const DEV_TERRAIN_MODES: readonly TerrainRenderMode[] = [
  "merged",
  "batched",
  "group",
];

/**
 * Get available terrain modes based on environment.
 * Production: merged only (best performance)
 * Development: all modes (debugging + perf testing)
 */
export function getAvailableTerrainModes(): readonly TerrainRenderMode[] {
  return import.meta.env.PROD ? PRODUCTION_TERRAIN_MODES : DEV_TERRAIN_MODES;
}

/**
 * Read persisted terrain mode from localStorage
 */
function getPersistedTerrainMode(): TerrainRenderMode | null {
  if (typeof localStorage === "undefined") return null;
  const stored = localStorage.getItem("terrainMode");
  if (stored === "merged" || stored === "batched" || stored === "group") {
    return stored;
  }
  return null;
}

const persistedTerrainMode = getPersistedTerrainMode();

/**
 * Default configuration based on build mode
 */
export const defaultConfig: RuntimeConfig = {
  terrainMode: persistedTerrainMode ?? (import.meta.env.DEV ? "group" : "merged"),
  debug: import.meta.env.DEV,
};

/**
 * Runtime config (can be modified at runtime)
 */
export let config: RuntimeConfig = { ...defaultConfig };

/**
 * Update runtime config (merges with existing).
 * Validates terrain mode against available modes for current environment.
 */
export function setConfig(partial: Partial<RuntimeConfig>): void {
  // Validate terrain mode against available modes
  if (partial.terrainMode !== undefined) {
    const available = getAvailableTerrainModes();
    if (!available.includes(partial.terrainMode)) {
      devOnly(() =>
        console.warn(
          `Terrain mode "${partial.terrainMode}" not available in this environment. Falling back to "merged".`
        )
      );
      partial = { ...partial, terrainMode: "merged" };
    }
  }

  config = { ...config, ...partial };
}

/**
 * Reset config to defaults
 */
export function resetConfig(): void {
  config = { ...defaultConfig };
}

/**
 * DEV-ONLY: Tree-shakeable wrapper for dev code
 *
 * In production builds, esbuild will eliminate the entire call
 * when import.meta.env.DEV is false.
 *
 * @example
 * devOnly(() => console.log("debug info"));
 */
export function devOnly<T>(fn: () => T): T | undefined {
  if (import.meta.env.DEV) {
    return fn();
  }
  return undefined;
}
