export { ManifestLoader } from "./ManifestLoader";
export type { ManifestIndices } from "./ManifestLoader";

export { EntityLoader } from "./EntityLoader";
export type {
  LoadedNPC,
  LoadedInteractive,
  LoadedEntity,
  EntityLoadResult,
  EntityLoaderOptions,
} from "./EntityLoader";

// Entity handler infrastructure
export {
  EntityHandler,
  EntityRegistry,
  entityRegistry,
  StaticHandler,
  NPCHandler,
  InteractiveHandler,
  registerDefaultHandlers,
} from "./entities";

export type {
  EntityResult,
  EntityCreationContext,
  NPCData,
  InteractiveData,
  StaticData,
} from "./entities";
