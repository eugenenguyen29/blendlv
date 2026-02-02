/**
 * Registry for entity handlers
 * Maps entity types to their handlers for runtime lookup
 */

import type { EntityType } from "../../types/manifest";
import type { EntityHandler } from "./EntityHandler";

export class EntityRegistry {
  private handlers = new Map<EntityType, EntityHandler>();

  /**
   * Register a handler for its entity types
   */
  register(handler: EntityHandler): void {
    for (const entityType of handler.entityTypes) {
      if (this.handlers.has(entityType)) {
        console.warn(
          `Overwriting handler for entity type: ${entityType}`
        );
      }
      this.handlers.set(entityType, handler);
    }
  }

  /**
   * Get the handler for an entity type
   */
  getHandler(entityType: EntityType): EntityHandler | undefined {
    return this.handlers.get(entityType);
  }

  /**
   * Check if a handler is registered for an entity type
   */
  hasHandler(entityType: EntityType): boolean {
    return this.handlers.has(entityType);
  }

  /**
   * Get all registered entity types
   */
  getRegisteredTypes(): EntityType[] {
    return Array.from(this.handlers.keys());
  }

  /**
   * Clear all registered handlers
   */
  clear(): void {
    this.handlers.clear();
  }
}

/**
 * Global entity registry instance
 */
export const entityRegistry = new EntityRegistry();
