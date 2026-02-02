/**
 * Tests for StaticHandler
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { Group, Object3D } from "three";
import type { GLTF } from "three/addons/loaders/GLTFLoader.js";
import type { Instance, EntityType } from "../../../../src/types/manifest";
import { StaticHandler } from "../../../../src/loaders/entities/handlers/StaticHandler";

/**
 * Create a mock Instance for testing
 */
function createMockInstance(overrides: Partial<Instance> = {}): Instance {
  return {
    id: "test-instance-id",
    name: "TestInstance",
    entity_type: "static",
    asset_id: null,
    position: [1, 2, 3],
    rotation: [0, 0, 0, 1], // identity quaternion
    scale: [1, 1, 1],
    bounding_box: {
      min: [0, 0, 0],
      max: [1, 1, 1],
    },
    ...overrides,
  };
}

/**
 * Create a mock GLTF asset for testing
 */
function createMockAsset(): GLTF {
  const mockScene = new Group();
  mockScene.name = "MockAssetScene";

  // Add a child to verify cloning behavior
  const child = new Object3D();
  child.name = "ChildObject";
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

describe("StaticHandler", () => {
  let handler: StaticHandler;

  beforeEach(() => {
    handler = new StaticHandler();
  });

  describe("entityTypes", () => {
    it("includes 'static'", () => {
      expect(handler.entityTypes).toContain("static");
    });

    it("includes 'trigger'", () => {
      expect(handler.entityTypes).toContain("trigger");
    });

    it("includes 'audio'", () => {
      expect(handler.entityTypes).toContain("audio");
    });

    it("has exactly 3 entity types", () => {
      expect(handler.entityTypes).toHaveLength(3);
    });
  });

  describe("canHandle()", () => {
    it("returns true for 'static' type", () => {
      expect(handler.canHandle("static")).toBe(true);
    });

    it("returns true for 'trigger' type", () => {
      expect(handler.canHandle("trigger")).toBe(true);
    });

    it("returns true for 'audio' type", () => {
      expect(handler.canHandle("audio")).toBe(true);
    });

    it("returns false for 'npc' type", () => {
      expect(handler.canHandle("npc")).toBe(false);
    });

    it("returns false for 'interactive' type", () => {
      expect(handler.canHandle("interactive")).toBe(false);
    });

    it("returns false for 'terrain' type", () => {
      expect(handler.canHandle("terrain")).toBe(false);
    });
  });

  describe("create()", () => {
    it("returns EntityResult with object, instance, and data: undefined", () => {
      const instance = createMockInstance();
      const result = handler.create({ instance, asset: null });

      expect(result.object).toBeInstanceOf(Group);
      expect(result.instance).toBe(instance);
      expect(result.data).toBeUndefined();
    });

    it("applies correct position transform to the object", () => {
      const instance = createMockInstance({
        position: [10, 20, 30],
      });

      const result = handler.create({ instance, asset: null });

      expect(result.object.position.x).toBe(10);
      expect(result.object.position.y).toBe(20);
      expect(result.object.position.z).toBe(30);
    });

    it("applies correct rotation transform to the object", () => {
      const instance = createMockInstance({
        rotation: [0.5, 0.5, 0.5, 0.5], // normalized quaternion
      });

      const result = handler.create({ instance, asset: null });

      expect(result.object.quaternion.x).toBe(0.5);
      expect(result.object.quaternion.y).toBe(0.5);
      expect(result.object.quaternion.z).toBe(0.5);
      expect(result.object.quaternion.w).toBe(0.5);
    });

    it("applies correct scale transform to the object", () => {
      const instance = createMockInstance({
        scale: [2, 3, 4],
      });

      const result = handler.create({ instance, asset: null });

      expect(result.object.scale.x).toBe(2);
      expect(result.object.scale.y).toBe(3);
      expect(result.object.scale.z).toBe(4);
    });

    it("sets object name from instance", () => {
      const instance = createMockInstance({ name: "MyStaticObject" });

      const result = handler.create({ instance, asset: null });

      expect(result.object.name).toBe("MyStaticObject");
    });

    it("sets userData.instanceId from instance.id", () => {
      const instance = createMockInstance({ id: "unique-id-123" });

      const result = handler.create({ instance, asset: null });

      expect(result.object.userData.instanceId).toBe("unique-id-123");
    });

    it("sets userData.entityType from instance.entity_type", () => {
      const instance = createMockInstance({ entity_type: "trigger" });

      const result = handler.create({ instance, asset: null });

      expect(result.object.userData.entityType).toBe("trigger");
    });

    it("stores full instance in userData.instance", () => {
      const instance = createMockInstance();

      const result = handler.create({ instance, asset: null });

      expect(result.object.userData.instance).toBe(instance);
    });

    describe("with asset", () => {
      it("clones asset scene when asset is provided", () => {
        const instance = createMockInstance();
        const asset = createMockAsset();

        const result = handler.create({ instance, asset });

        // Should have one child (the cloned scene)
        expect(result.object.children).toHaveLength(1);
      });

      it("cloned scene is a separate object from the original", () => {
        const instance = createMockInstance();
        const asset = createMockAsset();

        const result = handler.create({ instance, asset });

        const clonedScene = result.object.children[0];
        expect(clonedScene).not.toBe(asset.scene);
      });

      it("cloned scene has same name as original", () => {
        const instance = createMockInstance();
        const asset = createMockAsset();

        const result = handler.create({ instance, asset });

        const clonedScene = result.object.children[0];
        expect(clonedScene.name).toBe("MockAssetScene");
      });

      it("cloned scene children are also cloned", () => {
        const instance = createMockInstance();
        const asset = createMockAsset();

        const result = handler.create({ instance, asset });

        const clonedScene = result.object.children[0];
        expect(clonedScene.children).toHaveLength(1);
        expect(clonedScene.children[0].name).toBe("ChildObject");
        expect(clonedScene.children[0]).not.toBe(asset.scene.children[0]);
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
