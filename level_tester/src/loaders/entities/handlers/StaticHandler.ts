/**
 * Handler for static entities (static, trigger, audio)
 * These entities have no special data extraction
 */

import type { EntityType } from "../../../types/manifest";
import { EntityHandler } from "../EntityHandler";
import type { EntityResult, EntityCreationContext, StaticData } from "../types";

export class StaticHandler extends EntityHandler<StaticData> {
  readonly entityTypes: readonly EntityType[] = ["static", "trigger", "audio"];

  create(context: EntityCreationContext): EntityResult<StaticData> {
    const { instance, asset } = context;
    const object = this.createGroup(instance, asset);

    return {
      object,
      instance,
      data: undefined,
    };
  }
}
