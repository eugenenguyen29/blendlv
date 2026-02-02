/**
 * Handler for NPC entities
 * Extracts dialog data from instance custom properties
 */

import type { EntityType, Instance, DialogLine } from "../../../types/manifest";
import { EntityHandler } from "../EntityHandler";
import type { EntityResult, EntityCreationContext, NPCData } from "../types";

export class NPCHandler extends EntityHandler<NPCData> {
  readonly entityTypes: readonly EntityType[] = ["npc"];

  create(context: EntityCreationContext): EntityResult<NPCData> {
    const { instance, asset } = context;
    const object = this.createGroup(instance, asset);
    const dialog = this.extractDialog(instance);

    return {
      object,
      instance,
      data: { dialog },
    };
  }

  /**
   * Extract dialog lines from an NPC instance
   */
  private extractDialog(instance: Instance): DialogLine[] {
    const props = instance.custom_properties;
    if (!props) return [];

    if (Array.isArray(props.dialog)) {
      return props.dialog as DialogLine[];
    }

    return [];
  }
}
