/**
 * Entity loading infrastructure exports
 */

// Core
export { EntityHandler } from "./EntityHandler";
export { EntityRegistry, entityRegistry } from "./EntityRegistry";

// Types
export type {
  EntityResult,
  EntityCreationContext,
  NPCData,
  InteractiveData,
  StaticData,
} from "./types";

// Handlers
export { StaticHandler, NPCHandler, InteractiveHandler } from "./handlers";

import { entityRegistry } from "./EntityRegistry";
import { StaticHandler } from "./handlers/StaticHandler";
import { NPCHandler } from "./handlers/NPCHandler";
import { InteractiveHandler } from "./handlers/InteractiveHandler";

/**
 * Register all default handlers with the global registry
 */
export function registerDefaultHandlers(): void {
  entityRegistry.register(new StaticHandler());
  entityRegistry.register(new NPCHandler());
  entityRegistry.register(new InteractiveHandler());
}
