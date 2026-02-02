/**
 * Tests for EntityRegistry
 */
import { describe, it, expect, beforeEach, vi } from "vitest";
import { EntityRegistry } from "../../../src/loaders/entities/EntityRegistry";
import type { EntityHandler } from "../../../src/loaders/entities/EntityHandler";
import type { EntityType } from "../../../src/types/manifest";
import type { EntityResult, EntityCreationContext } from "../../../src/loaders/entities/types";

/**
 * Create a mock EntityHandler for testing
 */
function createMockHandler(types: readonly EntityType[]): EntityHandler {
  return {
    entityTypes: types,
    canHandle: (entityType: EntityType) => types.includes(entityType),
    create: vi.fn(() => ({} as EntityResult)),
  } as unknown as EntityHandler;
}

describe("EntityRegistry", () => {
  let registry: EntityRegistry;

  beforeEach(() => {
    registry = new EntityRegistry();
  });

  describe("register()", () => {
    it("registers handler for a single entity type", () => {
      const handler = createMockHandler(["static"]);

      registry.register(handler);

      expect(registry.hasHandler("static")).toBe(true);
      expect(registry.getHandler("static")).toBe(handler);
    });

    it("registers handler for multiple entity types", () => {
      const handler = createMockHandler(["static", "interactive"]);

      registry.register(handler);

      expect(registry.hasHandler("static")).toBe(true);
      expect(registry.hasHandler("interactive")).toBe(true);
      expect(registry.getHandler("static")).toBe(handler);
      expect(registry.getHandler("interactive")).toBe(handler);
    });

    it("registers multiple handlers for different types", () => {
      const staticHandler = createMockHandler(["static"]);
      const npcHandler = createMockHandler(["npc"]);

      registry.register(staticHandler);
      registry.register(npcHandler);

      expect(registry.getHandler("static")).toBe(staticHandler);
      expect(registry.getHandler("npc")).toBe(npcHandler);
    });
  });

  describe("getHandler()", () => {
    it("returns handler for registered type", () => {
      const handler = createMockHandler(["npc"]);
      registry.register(handler);

      const result = registry.getHandler("npc");

      expect(result).toBe(handler);
    });

    it("returns undefined for unregistered type", () => {
      const result = registry.getHandler("npc");

      expect(result).toBeUndefined();
    });
  });

  describe("hasHandler()", () => {
    it("returns true for registered type", () => {
      const handler = createMockHandler(["trigger"]);
      registry.register(handler);

      expect(registry.hasHandler("trigger")).toBe(true);
    });

    it("returns false for unregistered type", () => {
      expect(registry.hasHandler("trigger")).toBe(false);
    });
  });

  describe("getRegisteredTypes()", () => {
    it("returns empty array when no handlers registered", () => {
      const types = registry.getRegisteredTypes();

      expect(types).toEqual([]);
    });

    it("returns all registered entity types", () => {
      const handler1 = createMockHandler(["static", "interactive"]);
      const handler2 = createMockHandler(["npc"]);

      registry.register(handler1);
      registry.register(handler2);

      const types = registry.getRegisteredTypes();

      expect(types).toHaveLength(3);
      expect(types).toContain("static");
      expect(types).toContain("interactive");
      expect(types).toContain("npc");
    });

    it("returns array of types even when one handler handles multiple", () => {
      const handler = createMockHandler(["audio", "terrain"]);
      registry.register(handler);

      const types = registry.getRegisteredTypes();

      expect(types).toEqual(expect.arrayContaining(["audio", "terrain"]));
      expect(types).toHaveLength(2);
    });
  });

  describe("clear()", () => {
    it("removes all registered handlers", () => {
      const handler1 = createMockHandler(["static"]);
      const handler2 = createMockHandler(["npc"]);
      registry.register(handler1);
      registry.register(handler2);

      registry.clear();

      expect(registry.hasHandler("static")).toBe(false);
      expect(registry.hasHandler("npc")).toBe(false);
      expect(registry.getRegisteredTypes()).toEqual([]);
    });

    it("does nothing when registry is already empty", () => {
      registry.clear();

      expect(registry.getRegisteredTypes()).toEqual([]);
    });
  });

  describe("overwrite warning", () => {
    it("logs warning when overwriting existing handler", () => {
      const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});

      const handler1 = createMockHandler(["static"]);
      const handler2 = createMockHandler(["static"]);

      registry.register(handler1);
      registry.register(handler2);

      expect(warnSpy).toHaveBeenCalledTimes(1);
      expect(warnSpy).toHaveBeenCalledWith(
        "Overwriting handler for entity type: static"
      );

      warnSpy.mockRestore();
    });

    it("logs warning for each overlapping type", () => {
      const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});

      const handler1 = createMockHandler(["static", "interactive"]);
      const handler2 = createMockHandler(["interactive", "npc"]);

      registry.register(handler1);
      registry.register(handler2);

      // Only "interactive" overlaps
      expect(warnSpy).toHaveBeenCalledTimes(1);
      expect(warnSpy).toHaveBeenCalledWith(
        "Overwriting handler for entity type: interactive"
      );

      warnSpy.mockRestore();
    });

    it("does not log warning for non-overlapping types", () => {
      const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});

      const handler1 = createMockHandler(["static"]);
      const handler2 = createMockHandler(["npc"]);

      registry.register(handler1);
      registry.register(handler2);

      expect(warnSpy).not.toHaveBeenCalled();

      warnSpy.mockRestore();
    });

    it("overwrites handler even when warning is logged", () => {
      const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});

      const handler1 = createMockHandler(["static"]);
      const handler2 = createMockHandler(["static"]);

      registry.register(handler1);
      registry.register(handler2);

      expect(registry.getHandler("static")).toBe(handler2);

      warnSpy.mockRestore();
    });
  });
});
