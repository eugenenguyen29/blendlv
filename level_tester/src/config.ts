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

/**
 * Default configuration based on build mode
 */
export const defaultConfig: RuntimeConfig = {
  terrainMode: import.meta.env.PROD ? "merged" : "group",
  debug: import.meta.env.DEV,
};

/**
 * Runtime config (can be modified at runtime)
 */
export let config: RuntimeConfig = { ...defaultConfig };

/**
 * Update runtime config (merges with existing)
 */
export function setConfig(partial: Partial<RuntimeConfig>): void {
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
