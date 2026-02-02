/**
 * Handler for interactive entities
 * Extracts script_id from instance custom properties
 */

import type { EntityType, Instance } from "../../../types/manifest";
import { EntityHandler } from "../EntityHandler";
import type { EntityResult, EntityCreationContext, InteractiveData } from "../types";

export class InteractiveHandler extends EntityHandler<InteractiveData> {
  readonly entityTypes: readonly EntityType[] = ["interactive"];

  create(context: EntityCreationContext): EntityResult<InteractiveData> {
    const { instance, asset } = context;
    const object = this.createGroup(instance, asset);
    const scriptId = this.extractScriptId(instance);

    return {
      object,
      instance,
      data: { scriptId },
    };
  }

  /**
   * Extract script ID from an interactive instance
   */
  private extractScriptId(instance: Instance): string | null {
    const props = instance.custom_properties;
    if (!props) return null;

    if (typeof props.script_id === "string") {
      return props.script_id;
    }

    return null;
  }
}
