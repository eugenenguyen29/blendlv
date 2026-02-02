/**
 * Tests for InteractiveHandler
 */

import { describe, it, expect, beforeEach } from "vitest";
import { Group, Object3D } from "three";
import type { GLTF } from "three/addons/loaders/GLTFLoader.js";
import { InteractiveHandler } from "../../../../src/loaders/entities/handlers/InteractiveHandler";
import type { Instance } from "../../../../src/types/manifest";

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
 * Create a mock GLTF asset for testing
 */
function createMockAsset(): GLTF {
  const mockScene = new Group();
  mockScene.name = "MockInteractiveAssetScene";

  const child = new Object3D();
  child.name = "InteractiveModel";
  mockScene.add(child);

  return {
    scene: mockScene,
    scenes: [mockScene],
    animations: [],
    cameras: [],
    asset: {},
    parser: {} as GLTF["parser"],
    userData: {},
  };
}

describe("InteractiveHandler", () => {
  let handler: InteractiveHandler;

  beforeEach(() => {
    handler = new InteractiveHandler();
  });

  describe("entityTypes", () => {
    it('includes "interactive"', () => {
      expect(handler.entityTypes).toContain("interactive");
    });

    it("only contains interactive", () => {
      expect(handler.entityTypes).toHaveLength(1);
      expect(handler.entityTypes).toEqual(["interactive"]);
    });
  });

  describe("canHandle", () => {
    it('returns true for "interactive"', () => {
      expect(handler.canHandle("interactive")).toBe(true);
    });

    it('returns false for "static"', () => {
      expect(handler.canHandle("static")).toBe(false);
    });

    it('returns false for "npc"', () => {
      expect(handler.canHandle("npc")).toBe(false);
    });

    it('returns false for "trigger"', () => {
      expect(handler.canHandle("trigger")).toBe(false);
    });

    it('returns false for "audio"', () => {
      expect(handler.canHandle("audio")).toBe(false);
    });

    it('returns false for "terrain"', () => {
      expect(handler.canHandle("terrain")).toBe(false);
    });
  });

  describe("create", () => {
    it("extracts script_id from instance.custom_properties.script_id", () => {
      const instance = createMockInstance({ script_id: "my-script-123" });

      const result = handler.create({ instance, asset: createMockAsset() });

      expect(result.data.scriptId).toBe("my-script-123");
    });

    it("returns null scriptId when no custom_properties", () => {
      const instance = createMockInstance(undefined);

      const result = handler.create({ instance, asset: null });

      expect(result.data.scriptId).toBeNull();
    });

    it("returns null scriptId when custom_properties is empty object", () => {
      const instance = createMockInstance({});

      const result = handler.create({ instance, asset: null });

      expect(result.data.scriptId).toBeNull();
    });

    it("returns null scriptId when script_id is not a string (number)", () => {
      const instance = createMockInstance({ script_id: 123 });

      const result = handler.create({ instance, asset: null });

      expect(result.data.scriptId).toBeNull();
    });

    it("returns null scriptId when script_id is not a string (object)", () => {
      const instance = createMockInstance({ script_id: { id: "nested" } });

      const result = handler.create({ instance, asset: null });

      expect(result.data.scriptId).toBeNull();
    });

    it("returns null scriptId when script_id is null", () => {
      const instance = createMockInstance({ script_id: null });

      const result = handler.create({ instance, asset: null });

      expect(result.data.scriptId).toBeNull();
    });

    it("returns null scriptId when script_id is undefined", () => {
      const instance = createMockInstance({ script_id: undefined });

      const result = handler.create({ instance, asset: null });

      expect(result.data.scriptId).toBeNull();
    });

    it("returns EntityResult with InteractiveData containing scriptId", () => {
      const instance = createMockInstance({ script_id: "door-open" });

      const result = handler.create({ instance, asset: null });

      // Verify EntityResult structure
      expect(result).toHaveProperty("object");
      expect(result).toHaveProperty("instance");
      expect(result).toHaveProperty("data");

      // Verify instance is passed through
      expect(result.instance).toBe(instance);

      // Verify InteractiveData structure
      expect(result.data).toHaveProperty("scriptId");
      expect(result.data).toEqual({ scriptId: "door-open" });
    });

    it("returns the same instance in the result", () => {
      const instance = createMockInstance({ script_id: "test" });

      const result = handler.create({ instance, asset: null });

      expect(result.instance).toBe(instance);
    });

    it("creates object with correct name from instance", () => {
      const instance = createMockInstance({ script_id: "test" });

      const result = handler.create({ instance, asset: null });

      expect(result.object.name).toBe("test-interactive");
    });

    it("creates object with correct userData", () => {
      const instance = createMockInstance({ script_id: "test" });

      const result = handler.create({ instance, asset: null });

      expect(result.object.userData.instanceId).toBe("test-instance-id");
      expect(result.object.userData.entityType).toBe("interactive");
      expect(result.object.userData.instance).toBe(instance);
    });

    it("applies transform to the created object", () => {
      const instance = createMockInstance({ script_id: "test" });
      instance.position = [10, 20, 30];
      instance.rotation = [0.1, 0.2, 0.3, 0.9];
      instance.scale = [2, 2, 2];

      const result = handler.create({ instance, asset: null });

      expect(result.object.position.x).toBe(10);
      expect(result.object.position.y).toBe(20);
      expect(result.object.position.z).toBe(30);
      expect(result.object.quaternion.x).toBe(0.1);
      expect(result.object.quaternion.y).toBe(0.2);
      expect(result.object.quaternion.z).toBe(0.3);
      expect(result.object.quaternion.w).toBe(0.9);
      expect(result.object.scale.x).toBe(2);
      expect(result.object.scale.y).toBe(2);
      expect(result.object.scale.z).toBe(2);
    });

    it("returns object as instance of Group", () => {
      const instance = createMockInstance();

      const result = handler.create({ instance, asset: null });

      expect(result.object).toBeInstanceOf(Group);
    });

    describe("with asset", () => {
      it("clones asset scene when asset is provided", () => {
        const instance = createMockInstance();
        const asset = createMockAsset();

        const result = handler.create({ instance, asset });

        expect(result.object.children).toHaveLength(1);
      });

      it("cloned scene is a separate object from the original", () => {
        const instance = createMockInstance();
        const asset = createMockAsset();

        const result = handler.create({ instance, asset });

        const clonedScene = result.object.children[0];
        expect(clonedScene).not.toBe(asset.scene);
      });
    });

    describe("without asset", () => {
      it("creates empty group when asset is null", () => {
        const instance = createMockInstance();

        const result = handler.create({ instance, asset: null });

        expect(result.object.children).toHaveLength(0);
      });
    });
  });
});
