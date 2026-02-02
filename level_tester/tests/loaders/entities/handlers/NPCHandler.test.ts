/**
 * Tests for NPCHandler
 */

import { describe, it, expect, beforeEach } from "vitest";
import { Group, Object3D } from "three";
import type { GLTF } from "three/addons/loaders/GLTFLoader.js";
import { NPCHandler } from "../../../../src/loaders/entities/handlers/NPCHandler";
import type { Instance, DialogLine } from "../../../../src/types/manifest";

/**
 * Create a mock Instance with optional overrides
 */
function createMockInstance(overrides: Partial<Instance> = {}): Instance {
  return {
    id: "test-npc-1",
    name: "TestNPC",
    entity_type: "npc",
    asset_id: "npc-asset",
    position: [1, 2, 3],
    rotation: [0, 0, 0, 1],
    scale: [1, 1, 1],
    bounding_box: {
      min: [-1, -1, -1],
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
  mockScene.name = "MockNPCAssetScene";

  const child = new Object3D();
  child.name = "NPCModel";
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

describe("NPCHandler", () => {
  let handler: NPCHandler;

  beforeEach(() => {
    handler = new NPCHandler();
  });

  describe("entityTypes", () => {
    it('includes "npc"', () => {
      expect(handler.entityTypes).toContain("npc");
    });

    it("only contains npc", () => {
      expect(handler.entityTypes).toHaveLength(1);
      expect(handler.entityTypes).toEqual(["npc"]);
    });
  });

  describe("canHandle", () => {
    it('returns true for "npc"', () => {
      expect(handler.canHandle("npc")).toBe(true);
    });

    it('returns false for "static"', () => {
      expect(handler.canHandle("static")).toBe(false);
    });

    it('returns false for "interactive"', () => {
      expect(handler.canHandle("interactive")).toBe(false);
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
    it("extracts dialog from instance.custom_properties.dialog", () => {
      const dialogLines: DialogLine[] = [
        { speaker: "NPC", text: "Hello adventurer!" },
        { speaker: "NPC", text: "How can I help you?" },
      ];

      const instance = createMockInstance({
        custom_properties: { dialog: dialogLines },
      });

      const result = handler.create({ instance, asset: null });

      expect(result.data.dialog).toEqual(dialogLines);
      expect(result.data.dialog).toHaveLength(2);
    });

    it("returns empty dialog array when no custom_properties", () => {
      const instance = createMockInstance({
        custom_properties: undefined,
      });

      const result = handler.create({ instance, asset: null });

      expect(result.data.dialog).toEqual([]);
    });

    it("returns empty dialog array when custom_properties is empty object", () => {
      const instance = createMockInstance({
        custom_properties: {},
      });

      const result = handler.create({ instance, asset: null });

      expect(result.data.dialog).toEqual([]);
    });

    it("returns empty dialog array when dialog is not an array", () => {
      const instance = createMockInstance({
        custom_properties: { dialog: "not an array" },
      });

      const result = handler.create({ instance, asset: null });

      expect(result.data.dialog).toEqual([]);
    });

    it("returns empty dialog array when dialog is null", () => {
      const instance = createMockInstance({
        custom_properties: { dialog: null },
      });

      const result = handler.create({ instance, asset: null });

      expect(result.data.dialog).toEqual([]);
    });

    it("returns empty dialog array when dialog is a number", () => {
      const instance = createMockInstance({
        custom_properties: { dialog: 123 },
      });

      const result = handler.create({ instance, asset: null });

      expect(result.data.dialog).toEqual([]);
    });

    it("returns EntityResult with NPCData containing dialog", () => {
      const dialogLines: DialogLine[] = [
        { speaker: "Merchant", text: "Welcome to my shop!" },
      ];

      const instance = createMockInstance({
        id: "merchant-1",
        name: "Merchant",
        custom_properties: { dialog: dialogLines },
      });

      const result = handler.create({ instance, asset: null });

      // Verify EntityResult structure
      expect(result).toHaveProperty("object");
      expect(result).toHaveProperty("instance");
      expect(result).toHaveProperty("data");

      // Verify instance is passed through
      expect(result.instance).toBe(instance);

      // Verify NPCData structure
      expect(result.data).toHaveProperty("dialog");
      expect(result.data.dialog).toEqual(dialogLines);
    });

    it("creates object with correct name and userData", () => {
      const instance = createMockInstance({
        id: "guard-1",
        name: "Guard",
        entity_type: "npc",
      });

      const result = handler.create({ instance, asset: null });

      expect(result.object.name).toBe("Guard");
      expect(result.object.userData.instanceId).toBe("guard-1");
      expect(result.object.userData.entityType).toBe("npc");
      expect(result.object.userData.instance).toBe(instance);
    });

    it("applies transform to the created object", () => {
      const instance = createMockInstance({
        position: [10, 20, 30],
        rotation: [0.1, 0.2, 0.3, 0.9],
        scale: [2, 2, 2],
      });

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

    it("handles dialog with multiple lines", () => {
      const dialogLines: DialogLine[] = [
        { speaker: "Villager", text: "Good morning!" },
        { speaker: "Player", text: "Hello there." },
        { speaker: "Villager", text: "Beautiful day, isn't it?" },
        { speaker: "Player", text: "Indeed it is." },
        { speaker: "Villager", text: "Safe travels!" },
      ];

      const instance = createMockInstance({
        custom_properties: { dialog: dialogLines },
      });

      const result = handler.create({ instance, asset: null });

      expect(result.data.dialog).toHaveLength(5);
      expect(result.data.dialog[0].speaker).toBe("Villager");
      expect(result.data.dialog[4].text).toBe("Safe travels!");
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
