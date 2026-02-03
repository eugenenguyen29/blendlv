/**
 * Integration tests for ThirdPersonCamera
 * @vitest-environment jsdom
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { Scene, PerspectiveCamera, Object3D, Group } from "three";
import { ThirdPersonCamera } from "../../src/camera";

/**
 * Phase 5: Integration Tests
 *
 * These tests verify the integration patterns used in main.ts.
 * Since main.ts is excluded from coverage, we test the integration
 * patterns in isolation to ensure they work correctly.
 */
describe("ThirdPersonCamera - Phase 5 (Integration)", () => {
  let scene: Scene;
  let camera: PerspectiveCamera;
  let domElement: HTMLElement;
  let cameraController: ThirdPersonCamera;

  beforeEach(() => {
    scene = new Scene();
    camera = new PerspectiveCamera(60, 1, 0.1, 10000);
    domElement = document.createElement("div");
  });

  afterEach(() => {
    cameraController?.dispose();
  });

  describe("Camera controller creation", () => {
    it("should create ThirdPersonCamera with scene, camera, and domElement", () => {
      cameraController = new ThirdPersonCamera(camera, domElement, scene, {
        enableCollision: true,
        initialDistance: -5,
        verticalUpLimit: 1.5,
        verticalDownLimit: -1.3,
      });

      expect(cameraController).toBeDefined();
      expect(cameraController.isCollisionEnabled()).toBe(true);
      expect(cameraController.getCurrentDistance()).toBe(-5);
    });
  });

  describe("Delta time tracking pattern", () => {
    it("should accept delta time in update method", () => {
      cameraController = new ThirdPersonCamera(camera, domElement, scene);

      const target = new Object3D();
      target.position.set(0, 0, 0);
      scene.add(target);
      cameraController.setTarget(target);

      const delta = 0.016;
      expect(() => cameraController.update(delta)).not.toThrow();
    });

    it("should handle zero delta gracefully", () => {
      cameraController = new ThirdPersonCamera(camera, domElement, scene);

      const target = new Object3D();
      scene.add(target);
      cameraController.setTarget(target);

      expect(() => cameraController.update(0)).not.toThrow();
    });

    it("should handle large delta gracefully", () => {
      cameraController = new ThirdPersonCamera(camera, domElement, scene);

      const target = new Object3D();
      scene.add(target);
      cameraController.setTarget(target);

      expect(() => cameraController.update(1.0)).not.toThrow();
    });
  });

  describe("Target selection", () => {
    it("should set target from entity map", () => {
      cameraController = new ThirdPersonCamera(camera, domElement, scene);

      const entities = new Map<string, { object: Object3D }>();
      const entity1 = new Group();
      entity1.name = "FirstEntity";
      entity1.position.set(10, 0, 10);
      scene.add(entity1);

      const entity2 = new Group();
      entity2.name = "SecondEntity";
      entity2.position.set(20, 0, 20);
      scene.add(entity2);

      entities.set("entity-1", { object: entity1 });
      entities.set("entity-2", { object: entity2 });

      const firstEntity = entities.values().next().value;
      if (firstEntity) {
        cameraController.setTarget(firstEntity.object);
      }

      cameraController.update(0.016);

      const pivotPos = cameraController.getPivotPosition();
      expect(pivotPos.x).toBeGreaterThan(0);
    });

    it("should handle empty entity map gracefully", () => {
      cameraController = new ThirdPersonCamera(camera, domElement, scene);

      const entities = new Map<string, { object: Object3D }>();
      const firstEntity = entities.values().next().value;

      expect(firstEntity).toBeUndefined();
      expect(() => cameraController.update(0.016)).not.toThrow();
    });
  });

  describe("Collision exclusion", () => {
    it("should exclude objects with camExcludeCollision flag from collision detection", () => {
      cameraController = new ThirdPersonCamera(camera, domElement, scene, {
        enableCollision: true,
      });

      const excludedObject = new Group();
      excludedObject.userData.camExcludeCollision = true;
      scene.add(excludedObject);

      const collisionObjects = cameraController.getCollisionObjects();
      const hasExcluded = collisionObjects.some(
        (obj) => obj.uuid === excludedObject.uuid
      );
      expect(hasExcluded).toBe(false);
    });

    it("should respect camExcludeCollision flag on multiple objects", () => {
      const excludedObjects: Object3D[] = [];

      const obj1 = new Group();
      obj1.userData.camExcludeCollision = true;
      excludedObjects.push(obj1);

      const obj2 = new Group();
      obj2.userData.camExcludeCollision = true;
      excludedObjects.push(obj2);

      cameraController = new ThirdPersonCamera(camera, domElement, scene, {
        enableCollision: true,
      });

      for (const obj of excludedObjects) {
        scene.add(obj);
      }

      const collisionObjects = cameraController.getCollisionObjects();
      for (const obj of excludedObjects) {
        const found = collisionObjects.some((o) => o.uuid === obj.uuid);
        expect(found).toBe(false);
      }
    });
  });

  describe("Cleanup/disposal", () => {
    it("should properly dispose camera controller", () => {
      cameraController = new ThirdPersonCamera(camera, domElement, scene);

      const pivotInSceneBefore = scene.children.some(
        (child) => child.name === "ThirdPersonCamera_Pivot"
      );
      expect(pivotInSceneBefore).toBe(true);

      cameraController.dispose();

      const pivotInSceneAfter = scene.children.some(
        (child) => child.name === "ThirdPersonCamera_Pivot"
      );
      expect(pivotInSceneAfter).toBe(false);
    });

    it("should remove event listeners on dispose", () => {
      const removeEventListenerSpy = vi.spyOn(domElement, "removeEventListener");

      cameraController = new ThirdPersonCamera(camera, domElement, scene);
      cameraController.dispose();

      expect(removeEventListenerSpy).toHaveBeenCalledWith(
        "mousedown",
        expect.any(Function)
      );
      expect(removeEventListenerSpy).toHaveBeenCalledWith(
        "mouseup",
        expect.any(Function)
      );
      expect(removeEventListenerSpy).toHaveBeenCalledWith(
        "mousemove",
        expect.any(Function)
      );
      expect(removeEventListenerSpy).toHaveBeenCalledWith(
        "wheel",
        expect.any(Function)
      );

      removeEventListenerSpy.mockRestore();
    });
  });

  describe("Animation loop integration pattern", () => {
    it("should work with performance.now() delta calculation pattern", () => {
      cameraController = new ThirdPersonCamera(camera, domElement, scene);

      const target = new Object3D();
      target.position.set(5, 0, 5);
      scene.add(target);
      cameraController.setTarget(target);

      let lastTime = performance.now();

      const simulateFrame = () => {
        const now = performance.now();
        const delta = (now - lastTime) / 1000;
        lastTime = now;
        cameraController.update(delta);
      };

      expect(() => simulateFrame()).not.toThrow();
      expect(() => simulateFrame()).not.toThrow();
      expect(() => simulateFrame()).not.toThrow();
    });
  });
});
