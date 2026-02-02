/**
 * Shared types for entity handlers
 */

import type { Object3D } from "three";
import type { GLTF } from "three/addons/loaders/GLTFLoader.js";
import type { Instance, DialogLine } from "../../types/manifest";

/**
 * Result of creating an entity - generic data payload
 */
export interface EntityResult<TData = unknown> {
  object: Object3D;
  instance: Instance;
  data: TData;
}

/**
 * Context passed to entity handlers for creation
 */
export interface EntityCreationContext {
  instance: Instance;
  asset: GLTF | null;
}

/**
 * NPC-specific data extracted from instance
 */
export interface NPCData {
  dialog: DialogLine[];
}

/**
 * Interactive-specific data extracted from instance
 */
export interface InteractiveData {
  scriptId: string | null;
}

/**
 * Static entities have no special data
 */
export type StaticData = void;
