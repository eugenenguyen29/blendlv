/**
 * Tests for InteractiveHandler
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import type { Instance } from "../../../../src/types/manifest";
import type { EntityCreationContext } from "../../../../src/loaders/entities/types";

// Mock Three.js Group as a proper class
vi.mock("three", () => {
  class MockGroup {
    name = "";
    userData: Record<string, unknown> = {};
    position = { set: vi.fn() };
    quaternion = { set: vi.fn() };
    scale = { set: vi.fn() };
    add = vi.fn();
  }

  return {
    Group: MockGroup,
  };
});

/**
 * Create a mock Instance with optional custom_properties
 */
function createMockInstance(
  customProperties?: Record<string, unknown>
): Instance {
  return {
    id: "test-instance-id",
    name: "test-interactive",
    entity_type: "interactive",
    asset_id: "test-asset",
    position: [1, 2, 3],
    rotation: [0, 0, 0, 1],
    scale: [1, 1, 1],
    bounding_box: {
      min: [0, 0, 0],
      max: [1, 1, 1],
    },
    custom_properties: customProperties,
  };
}

/**
 * Create a mock GLTF asset
 */
function createMockAsset() {
  return {
    scene: {
      clone: vi.fn().mockReturnValue({ name: "cloned-scene" }),
    },
  };
}

describe("InteractiveHandler", () => {
  let InteractiveHandler: typeof import("../../../../src/loaders/entities/handlers/InteractiveHandler").InteractiveHandler;

  beforeEach(async () => {
    vi.clearAllMocks();
    // Dynamic import to ensure mocks are applied
    const module = await import(
      "../../../../src/loaders/entities/handlers/InteractiveHandler"
    );
    InteractiveHandler = module.InteractiveHandler;
  });

  describe("entityTypes", () => {
    it('should include "interactive"', () => {
      const handler = new InteractiveHandler();
      expect(handler.entityTypes).toContain("interactive");
    });

    it('should only contain "interactive"', () => {
      const handler = new InteractiveHandler();
      expect(handler.entityTypes).toEqual(["interactive"]);
    });
  });

  describe("canHandle()", () => {
    it('should return true for "interactive"', () => {
      const handler = new InteractiveHandler();
      expect(handler.canHandle("interactive")).toBe(true);
    });

    it('should return false for "static"', () => {
      const handler = new InteractiveHandler();
      expect(handler.canHandle("static")).toBe(false);
    });

    it('should return false for "npc"', () => {
      const handler = new InteractiveHandler();
      expect(handler.canHandle("npc")).toBe(false);
    });

    it('should return false for "trigger"', () => {
      const handler = new InteractiveHandler();
      expect(handler.canHandle("trigger")).toBe(false);
    });

    it('should return false for "audio"', () => {
      const handler = new InteractiveHandler();
      expect(handler.canHandle("audio")).toBe(false);
    });

    it('should return false for "terrain"', () => {
      const handler = new InteractiveHandler();
      expect(handler.canHandle("terrain")).toBe(false);
    });
  });

  describe("create()", () => {
    it("should extract script_id from instance.custom_properties.script_id", () => {
      const handler = new InteractiveHandler();
      const instance = createMockInstance({ script_id: "my-script-123" });
      const context: EntityCreationContext = {
        instance,
        asset: createMockAsset() as never,
      };

      const result = handler.create(context);

      expect(result.data.scriptId).toBe("my-script-123");
    });

    it("should return null scriptId when no custom_properties", () => {
      const handler = new InteractiveHandler();
      const instance = createMockInstance(undefined);
      const context: EntityCreationContext = {
        instance,
        asset: createMockAsset() as never,
      };

      const result = handler.create(context);

      expect(result.data.scriptId).toBeNull();
    });

    it("should return null scriptId when custom_properties is empty", () => {
      const handler = new InteractiveHandler();
      const instance = createMockInstance({});
      const context: EntityCreationContext = {
        instance,
        asset: createMockAsset() as never,
      };

      const result = handler.create(context);

      expect(result.data.scriptId).toBeNull();
    });

    it("should return null scriptId when script_id is not a string (number)", () => {
      const handler = new InteractiveHandler();
      const instance = createMockInstance({ script_id: 123 });
      const context: EntityCreationContext = {
        instance,
        asset: createMockAsset() as never,
      };

      const result = handler.create(context);

      expect(result.data.scriptId).toBeNull();
    });

    it("should return null scriptId when script_id is not a string (object)", () => {
      const handler = new InteractiveHandler();
      const instance = createMockInstance({ script_id: { id: "nested" } });
      const context: EntityCreationContext = {
        instance,
        asset: createMockAsset() as never,
      };

      const result = handler.create(context);

      expect(result.data.scriptId).toBeNull();
    });

    it("should return null scriptId when script_id is null", () => {
      const handler = new InteractiveHandler();
      const instance = createMockInstance({ script_id: null });
      const context: EntityCreationContext = {
        instance,
        asset: createMockAsset() as never,
      };

      const result = handler.create(context);

      expect(result.data.scriptId).toBeNull();
    });

    it("should return null scriptId when script_id is undefined", () => {
      const handler = new InteractiveHandler();
      const instance = createMockInstance({ script_id: undefined });
      const context: EntityCreationContext = {
        instance,
        asset: createMockAsset() as never,
      };

      const result = handler.create(context);

      expect(result.data.scriptId).toBeNull();
    });

    it("should return EntityResult with InteractiveData containing scriptId", () => {
      const handler = new InteractiveHandler();
      const instance = createMockInstance({ script_id: "door-open" });
      const context: EntityCreationContext = {
        instance,
        asset: createMockAsset() as never,
      };

      const result = handler.create(context);

      expect(result).toHaveProperty("object");
      expect(result).toHaveProperty("instance");
      expect(result).toHaveProperty("data");
      expect(result.instance).toBe(instance);
      expect(result.data).toEqual({ scriptId: "door-open" });
    });

    it("should return the same instance in the result", () => {
      const handler = new InteractiveHandler();
      const instance = createMockInstance({ script_id: "test" });
      const context: EntityCreationContext = {
        instance,
        asset: createMockAsset() as never,
      };

      const result = handler.create(context);

      expect(result.instance).toBe(instance);
    });

    it("should create an object with correct name from instance", () => {
      const handler = new InteractiveHandler();
      const instance = createMockInstance({ script_id: "test" });
      const context: EntityCreationContext = {
        instance,
        asset: createMockAsset() as never,
      };

      const result = handler.create(context);

      expect(result.object.name).toBe("test-interactive");
    });

    it("should work with null asset", () => {
      const handler = new InteractiveHandler();
      const instance = createMockInstance({ script_id: "test" });
      const context: EntityCreationContext = {
        instance,
        asset: null,
      };

      const result = handler.create(context);

      expect(result.data.scriptId).toBe("test");
      expect(result.object).toBeDefined();
    });
  });
});
