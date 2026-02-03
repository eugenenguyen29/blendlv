/**
 * Tests for ThirdPersonCamera
 * @vitest-environment jsdom
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import {
  PerspectiveCamera,
  Object3D,
  Scene,
  Vector3,
  Mesh,
  BoxGeometry,
  MeshBasicMaterial,
  Raycaster,
} from "three";
import { ThirdPersonCamera } from "../../src/camera/ThirdPersonCamera";

describe("ThirdPersonCamera - Phase 1", () => {
  let camera: PerspectiveCamera;
  let scene: Scene;
  let domElement: HTMLElement;
  let controller: ThirdPersonCamera;

  beforeEach(() => {
    camera = new PerspectiveCamera(60, 1, 0.1, 1000);
    scene = new Scene();
    domElement = document.createElement("div");
  });

  describe("constructor", () => {
    it("should create pivot and followCam objects", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene);

      expect(controller.getPivotPosition).toBeDefined();
      expect(controller.getFollowCamPosition).toBeDefined();

      const pivotPos = controller.getPivotPosition();
      expect(pivotPos).toBeInstanceOf(Vector3);

      const followCamPos = controller.getFollowCamPosition();
      expect(followCamPos).toBeInstanceOf(Vector3);
    });

    it("should apply default options", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene);

      const followCamPos = controller.getFollowCamPosition();
      expect(followCamPos.z).toBeCloseTo(-5, 1);
      expect(followCamPos.x).toBeCloseTo(0, 5);
    });

    it("should apply custom options", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene, {
        initialDistance: -10,
      });

      const followCamPos = controller.getFollowCamPosition();
      expect(followCamPos.z).toBeCloseTo(-10, 1);
    });

    it("should position followCam based on initialDirection", () => {
      const verticalAngle = Math.PI / 6;
      controller = new ThirdPersonCamera(camera, domElement, scene, {
        initialDistance: -5,
        initialDirection: { x: verticalAngle, y: 0 },
      });

      const followCamPos = controller.getFollowCamPosition();
      const expectedY = -5 * Math.sin(-verticalAngle);
      const expectedZ = -5 * Math.cos(-verticalAngle);

      expect(followCamPos.y).toBeCloseTo(expectedY, 2);
      expect(followCamPos.z).toBeCloseTo(expectedZ, 2);
    });
  });

  describe("setTarget", () => {
    it("should store target reference and update pivot on next update", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene);
      const target = new Object3D();
      target.position.set(10, 5, 20);

      controller.setTarget(target);

      for (let i = 0; i < 100; i++) {
        controller.update(0.016);
      }

      const pivotPos = controller.getPivotPosition();
      expect(pivotPos.x).toBeCloseTo(10, 0.5);
      expect(pivotPos.y).toBeCloseTo(5, 0.5);
      expect(pivotPos.z).toBeCloseTo(20, 0.5);
    });
  });

  describe("update", () => {
    it("should move camera toward followCam world position", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene);
      const target = new Object3D();
      controller.setTarget(target);

      const initialCameraPos = camera.position.clone();
      controller.update(0.016);

      expect(camera.position.equals(initialCameraPos)).toBe(false);
    });

    it("should make camera look at pivot", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene);
      const target = new Object3D();
      target.position.set(10, 5, 20);
      controller.setTarget(target);

      const initialQuaternion = camera.quaternion.clone();
      for (let i = 0; i < 10; i++) {
        controller.update(0.016);
      }

      expect(camera.quaternion.equals(initialQuaternion)).toBe(false);
    });

    it("should not update when no target is set", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene);
      const initialCameraPos = camera.position.clone();

      controller.update(0.016);

      expect(camera.position).toEqual(initialCameraPos);
    });
  });

  describe("setEnabled", () => {
    it("should prevent updates when disabled", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene);
      const target = new Object3D();
      target.position.set(10, 5, 20);
      controller.setTarget(target);

      controller.setEnabled(false);
      const pivotBefore = controller.getPivotPosition().clone();
      const cameraBefore = camera.position.clone();

      controller.update(0.016);

      const pivotAfter = controller.getPivotPosition();
      expect(pivotAfter.x).toBeCloseTo(pivotBefore.x, 5);
      expect(pivotAfter.y).toBeCloseTo(pivotBefore.y, 5);
      expect(pivotAfter.z).toBeCloseTo(pivotBefore.z, 5);
      expect(camera.position).toEqual(cameraBefore);
    });
  });

  describe("dispose", () => {
    it("should not throw when called", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene);
      expect(() => controller.dispose()).not.toThrow();
    });
  });
});

describe("ThirdPersonCamera - Phase 2 (Input Handlers)", () => {
  let camera: PerspectiveCamera;
  let scene: Scene;
  let domElement: HTMLElement;
  let controller: ThirdPersonCamera;

  beforeEach(() => {
    camera = new PerspectiveCamera(60, 1, 0.1, 1000);
    scene = new Scene();
    domElement = document.createElement("div");
    controller = new ThirdPersonCamera(camera, domElement, scene);
  });

  describe("mouse drag rotation", () => {
    it("should enable drag mode on mousedown", () => {
      const event = new MouseEvent("mousedown");
      domElement.dispatchEvent(event);

      const pivotRotationBefore = controller.getPivotRotation();
      const moveEvent = new MouseEvent("mousemove", {
        movementX: 100,
        movementY: 0,
      });
      domElement.dispatchEvent(moveEvent);

      const pivotRotationAfter = controller.getPivotRotation();
      expect(pivotRotationAfter).not.toBeCloseTo(pivotRotationBefore);
    });

    it("should disable drag mode on mouseup", () => {
      domElement.dispatchEvent(new MouseEvent("mousedown"));
      domElement.dispatchEvent(new MouseEvent("mouseup"));

      const pivotRotationBefore = controller.getPivotRotation();
      domElement.dispatchEvent(
        new MouseEvent("mousemove", { movementX: 100 })
      );
      const pivotRotationAfter = controller.getPivotRotation();

      expect(pivotRotationAfter).toBeCloseTo(pivotRotationBefore);
    });

    it("should rotate pivot horizontally on mousemove with drag", () => {
      domElement.dispatchEvent(new MouseEvent("mousedown"));

      const pivotRotationBefore = controller.getPivotRotation();
      domElement.dispatchEvent(
        new MouseEvent("mousemove", {
          movementX: 100,
          movementY: 0,
        })
      );

      const pivotRotationAfter = controller.getPivotRotation();
      expect(pivotRotationAfter).not.toBeCloseTo(pivotRotationBefore);
    });

    it("should rotate followCam vertically on mousemove with drag", () => {
      domElement.dispatchEvent(new MouseEvent("mousedown"));

      const followCamRotationBefore = controller.getFollowCamRotation();
      domElement.dispatchEvent(
        new MouseEvent("mousemove", {
          movementX: 0,
          movementY: 100,
        })
      );

      const followCamRotationAfter = controller.getFollowCamRotation();
      expect(followCamRotationAfter.x).not.toBeCloseTo(
        followCamRotationBefore.x
      );
    });

    it("should clamp vertical rotation to limits", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene, {
        verticalUpLimit: 1.5,
        verticalDownLimit: -1.3,
      });
      domElement.dispatchEvent(new MouseEvent("mousedown"));

      domElement.dispatchEvent(
        new MouseEvent("mousemove", {
          movementX: 0,
          movementY: -10000,
        })
      );

      const rotation = controller.getFollowCamRotation();
      expect(rotation.x).toBeLessThanOrEqual(1.5);

      domElement.dispatchEvent(
        new MouseEvent("mousemove", {
          movementX: 0,
          movementY: 10000,
        })
      );

      const rotation2 = controller.getFollowCamRotation();
      expect(rotation2.x).toBeGreaterThanOrEqual(-1.3);
    });

    it("should update followCam position when rotating vertically", () => {
      domElement.dispatchEvent(new MouseEvent("mousedown"));

      const positionBefore = controller.getFollowCamPosition().clone();
      domElement.dispatchEvent(
        new MouseEvent("mousemove", {
          movementX: 0,
          movementY: 100,
        })
      );

      const positionAfter = controller.getFollowCamPosition();
      expect(positionAfter.y).not.toBeCloseTo(positionBefore.y);
      expect(positionAfter.z).not.toBeCloseTo(positionBefore.z);
    });

    it("should not rotate without drag mode", () => {
      const pivotRotationBefore = controller.getPivotRotation();
      domElement.dispatchEvent(
        new MouseEvent("mousemove", { movementX: 100 })
      );

      const pivotRotationAfter = controller.getPivotRotation();
      expect(pivotRotationAfter).toBeCloseTo(pivotRotationBefore);
    });
  });

  describe("mouse wheel zoom", () => {
    it("should zoom in on negative deltaY", () => {
      const distanceBefore = controller.getCurrentDistance();
      domElement.dispatchEvent(new WheelEvent("wheel", { deltaY: -100 }));

      const distanceAfter = controller.getCurrentDistance();
      expect(Math.abs(distanceAfter)).toBeLessThan(Math.abs(distanceBefore));
    });

    it("should zoom out on positive deltaY", () => {
      const distanceBefore = controller.getCurrentDistance();
      domElement.dispatchEvent(new WheelEvent("wheel", { deltaY: 100 }));

      const distanceAfter = controller.getCurrentDistance();
      expect(Math.abs(distanceAfter)).toBeGreaterThan(Math.abs(distanceBefore));
    });

    it("should clamp zoom to distance limits", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene, {
        maxDistance: -7,
        minDistance: -0.7,
      });

      domElement.dispatchEvent(new WheelEvent("wheel", { deltaY: 10000 }));
      expect(controller.getCurrentDistance()).toBeGreaterThanOrEqual(-7);

      domElement.dispatchEvent(new WheelEvent("wheel", { deltaY: -10000 }));
      expect(controller.getCurrentDistance()).toBeLessThanOrEqual(-0.7);
    });

    it("should update followCam position after zoom", () => {
      const positionBefore = controller.getFollowCamPosition().clone();
      domElement.dispatchEvent(new WheelEvent("wheel", { deltaY: 100 }));

      const positionAfter = controller.getFollowCamPosition();
      expect(positionAfter.z).not.toBeCloseTo(positionBefore.z);
    });
  });

  describe("dispose", () => {
    it("should remove all event listeners", () => {
      const removeEventListenerSpy = vi.spyOn(domElement, "removeEventListener");
      controller.dispose();

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
    });
  });
});

describe("ThirdPersonCamera - Phase 3 (Collision Detection)", () => {
  let camera: PerspectiveCamera;
  let scene: Scene;
  let domElement: HTMLElement;
  let controller: ThirdPersonCamera;

  beforeEach(() => {
    camera = new PerspectiveCamera(60, 1, 0.1, 1000);
    scene = new Scene();
    domElement = document.createElement("div");
  });

  afterEach(() => {
    if (controller) {
      controller.dispose();
    }
  });

  describe("collision enabled/disabled", () => {
    it("should enable collision by default", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene);
      expect(controller.isCollisionEnabled()).toBe(true);
    });

    it("should disable collision when option set", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene, {
        enableCollision: false,
      });
      expect(controller.isCollisionEnabled()).toBe(false);
    });
  });

  describe("collision object list", () => {
    it("should build collision list from scene meshes", () => {
      const mesh = new Mesh(new BoxGeometry(1, 1, 1), new MeshBasicMaterial());
      scene.add(mesh);

      controller = new ThirdPersonCamera(camera, domElement, scene);

      const collisionObjects = controller.getCollisionObjects();
      expect(collisionObjects).toContain(mesh);
    });

    it("should exclude objects with camExcludeCollision flag", () => {
      const mesh = new Mesh(new BoxGeometry(1, 1, 1), new MeshBasicMaterial());
      mesh.userData.camExcludeCollision = true;
      scene.add(mesh);

      controller = new ThirdPersonCamera(camera, domElement, scene);

      const collisionObjects = controller.getCollisionObjects();
      expect(collisionObjects).not.toContain(mesh);
    });

    it("should exclude invisible meshes", () => {
      const mesh = new Mesh(new BoxGeometry(1, 1, 1), new MeshBasicMaterial());
      mesh.visible = false;
      scene.add(mesh);

      controller = new ThirdPersonCamera(camera, domElement, scene);

      const collisionObjects = controller.getCollisionObjects();
      expect(collisionObjects).not.toContain(mesh);
    });

    it("should add new meshes when childadded event fires", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene);

      const mesh = new Mesh(new BoxGeometry(1, 1, 1), new MeshBasicMaterial());
      scene.add(mesh);

      const collisionObjects = controller.getCollisionObjects();
      expect(collisionObjects).toContain(mesh);
    });

    it("should remove meshes when childremoved event fires", () => {
      const mesh = new Mesh(new BoxGeometry(1, 1, 1), new MeshBasicMaterial());
      scene.add(mesh);

      controller = new ThirdPersonCamera(camera, domElement, scene);
      scene.remove(mesh);

      const collisionObjects = controller.getCollisionObjects();
      expect(collisionObjects).not.toContain(mesh);
    });
  });

  describe("collision detection", () => {
    it("should raycast from pivot to camera", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene, {
        enableCollision: true,
      });
      const target = new Object3D();
      target.position.set(10, 5, 20);
      controller.setTarget(target);

      const raycasterSpy = vi.spyOn(Raycaster.prototype, "intersectObjects");

      controller.update(0.016);

      expect(raycasterSpy).toHaveBeenCalled();
      raycasterSpy.mockRestore();
    });

    it("should use full distance when no obstacles", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene, {
        initialDistance: -5,
        enableCollision: true,
        cameraLerpSpeed: 1000,
        pivotFollowSpeed: 1000,
      });
      const target = new Object3D();
      controller.setTarget(target);

      for (let i = 0; i < 100; i++) {
        controller.update(0.016);
      }

      const distance = camera.position.distanceTo(target.position);
      expect(distance).toBeCloseTo(5, 0);
    });

    it("should move camera closer when obstacle found", () => {
      const obstacle = new Mesh(
        new BoxGeometry(20, 20, 0.5),
        new MeshBasicMaterial()
      );
      obstacle.position.set(0, 0, -3);
      scene.add(obstacle);
      obstacle.updateMatrixWorld(true);

      controller = new ThirdPersonCamera(camera, domElement, scene, {
        initialDistance: -5,
        enableCollision: true,
        cameraLerpSpeed: 1000,
        pivotFollowSpeed: 1000,
        collisionLerpSpeed: 1000,
      });
      const target = new Object3D();
      target.position.set(0, 0, 0);
      controller.setTarget(target);

      for (let i = 0; i < 100; i++) {
        controller.update(0.016);
      }

      const distance = camera.position.distanceTo(target.position);
      expect(distance).toBeLessThan(5);
    });

    it("should respect min distance limit in collision", () => {
      const obstacle = new Mesh(
        new BoxGeometry(10, 10, 10),
        new MeshBasicMaterial()
      );
      obstacle.position.set(0, 0, -0.3);
      scene.add(obstacle);

      controller = new ThirdPersonCamera(camera, domElement, scene, {
        initialDistance: -5,
        minDistance: -1,
        enableCollision: true,
        collisionOffset: 0.1,
        cameraLerpSpeed: 1000,
        pivotFollowSpeed: 1000,
        collisionLerpSpeed: 1000,
      });
      const target = new Object3D();
      target.position.set(0, 0, 0);
      controller.setTarget(target);

      for (let i = 0; i < 100; i++) {
        controller.update(0.016);
      }

      const distance = camera.position.distanceTo(target.position);
      expect(distance).toBeGreaterThanOrEqual(0.9);
    });
  });

  describe("dispose", () => {
    it("should remove scene event listeners", () => {
      const removeEventListenerSpy = vi.spyOn(scene, "removeEventListener");
      controller = new ThirdPersonCamera(camera, domElement, scene);
      controller.dispose();

      expect(removeEventListenerSpy).toHaveBeenCalledWith(
        "childadded",
        expect.any(Function)
      );
      expect(removeEventListenerSpy).toHaveBeenCalledWith(
        "childremoved",
        expect.any(Function)
      );
    });
  });
});

describe("ThirdPersonCamera - Phase 4 (Smooth Lerping)", () => {
  let camera: PerspectiveCamera;
  let scene: Scene;
  let domElement: HTMLElement;
  let controller: ThirdPersonCamera;

  beforeEach(() => {
    camera = new PerspectiveCamera(60, 1, 0.1, 1000);
    scene = new Scene();
    domElement = document.createElement("div");
  });

  afterEach(() => {
    if (controller) {
      controller.dispose();
    }
  });

  describe("pivot lerping to target", () => {
    it("should lerp pivot to target position, not snap instantly", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene);
      const target = new Object3D();
      target.position.set(100, 50, 200);
      controller.setTarget(target);

      const pivotBefore = controller.getPivotPosition().clone();
      controller.update(0.016);
      const pivotAfter = controller.getPivotPosition();

      expect(pivotAfter.distanceTo(pivotBefore)).toBeGreaterThan(0);
      expect(pivotAfter.distanceTo(target.position)).toBeGreaterThan(0.1);
    });

    it("should use frame-rate independent lerping", () => {
      const target1 = new Object3D();
      target1.position.set(100, 0, 0);

      const controller1 = new ThirdPersonCamera(camera, domElement, scene);
      controller1.setTarget(target1);
      controller1.update(0.016);
      const pos1 = controller1.getPivotPosition();

      const camera2 = new PerspectiveCamera(60, 1, 0.1, 1000);
      const controller2 = new ThirdPersonCamera(camera2, domElement, scene);
      const target2 = new Object3D();
      target2.position.set(100, 0, 0);
      controller2.setTarget(target2);
      controller2.update(0.033);
      const pos2 = controller2.getPivotPosition();

      const distance1 = pos1.distanceTo(new Vector3(0, 0, 0));
      const distance2 = pos2.distanceTo(new Vector3(0, 0, 0));

      expect(distance2 / distance1).toBeCloseTo(2, 0);
    });

    it("should eventually reach target position", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene);
      const target = new Object3D();
      target.position.set(10, 5, 20);
      controller.setTarget(target);

      for (let i = 0; i < 100; i++) {
        controller.update(0.016);
      }

      const pivotPos = controller.getPivotPosition();
      expect(pivotPos.distanceTo(target.position)).toBeLessThan(0.1);
    });
  });

  describe("followCam lerping for collision", () => {
    it("should lerp followCam to collision point", () => {
      const obstacle = new Mesh(
        new BoxGeometry(20, 20, 0.5),
        new MeshBasicMaterial()
      );
      obstacle.position.set(0, 0, -3);
      scene.add(obstacle);
      obstacle.updateMatrixWorld(true);

      controller = new ThirdPersonCamera(camera, domElement, scene, {
        initialDistance: -5,
        enableCollision: true,
      });
      const target = new Object3D();
      controller.setTarget(target);

      const followCamBefore = controller.getFollowCamPosition().clone();
      controller.update(0.016);
      const followCamAfter = controller.getFollowCamPosition();

      expect(Math.abs(followCamAfter.z)).not.toBeCloseTo(
        Math.abs(followCamBefore.z),
        1
      );
    });

    it("should use collisionLerpSpeed option", () => {
      const obstacle = new Mesh(
        new BoxGeometry(20, 20, 0.5),
        new MeshBasicMaterial()
      );
      obstacle.position.set(0, 0, -3);
      scene.add(obstacle);
      obstacle.updateMatrixWorld(true);

      const cameraFast = new PerspectiveCamera(60, 1, 0.1, 1000);
      const controllerFast = new ThirdPersonCamera(
        cameraFast,
        domElement,
        scene,
        {
          initialDistance: -5,
          enableCollision: true,
          collisionLerpSpeed: 20,
        }
      );
      const target1 = new Object3D();
      controllerFast.setTarget(target1);
      controllerFast.update(0.016);
      const followCamFast = controllerFast.getFollowCamPosition();

      const cameraSlow = new PerspectiveCamera(60, 1, 0.1, 1000);
      const controllerSlow = new ThirdPersonCamera(
        cameraSlow,
        domElement,
        scene,
        {
          initialDistance: -5,
          enableCollision: true,
          collisionLerpSpeed: 1,
        }
      );
      const target2 = new Object3D();
      controllerSlow.setTarget(target2);
      controllerSlow.update(0.016);
      const followCamSlow = controllerSlow.getFollowCamPosition();

      expect(Math.abs(followCamFast.z)).toBeLessThan(Math.abs(followCamSlow.z));
    });

    it("should eventually reach collision point", () => {
      const obstacle = new Mesh(
        new BoxGeometry(20, 20, 0.5),
        new MeshBasicMaterial()
      );
      obstacle.position.set(0, 0, -3);
      scene.add(obstacle);
      obstacle.updateMatrixWorld(true);

      controller = new ThirdPersonCamera(camera, domElement, scene, {
        initialDistance: -5,
        enableCollision: true,
        collisionOffset: 0.7,
      });
      const target = new Object3D();
      controller.setTarget(target);

      for (let i = 0; i < 100; i++) {
        controller.update(0.016);
      }

      const followCamPos = controller.getFollowCamPosition();
      expect(Math.abs(followCamPos.z)).toBeLessThan(3.5);
    });
  });

  describe("camera lerping to followCam", () => {
    it("should lerp camera to followCam world position", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene);
      const target = new Object3D();
      target.position.set(10, 5, 20);
      controller.setTarget(target);

      const cameraBefore = camera.position.clone();
      controller.update(0.016);
      const cameraAfter = camera.position.clone();

      expect(cameraAfter.distanceTo(cameraBefore)).toBeGreaterThan(0);
    });

    it("should use frame-rate independent camera lerping", () => {
      const target1 = new Object3D();
      target1.position.set(100, 0, 0);

      const camera1 = new PerspectiveCamera(60, 1, 0.1, 1000);
      const controller1 = new ThirdPersonCamera(camera1, domElement, scene, {
        pivotFollowSpeed: 1000,
        collisionLerpSpeed: 1000,
      });
      controller1.setTarget(target1);
      controller1.update(0.016);
      const cameraPos1 = camera1.position.clone();

      const camera2 = new PerspectiveCamera(60, 1, 0.1, 1000);
      const controller2 = new ThirdPersonCamera(camera2, domElement, scene, {
        pivotFollowSpeed: 1000,
        collisionLerpSpeed: 1000,
      });
      const target2 = new Object3D();
      target2.position.set(100, 0, 0);
      controller2.setTarget(target2);
      controller2.update(0.033);
      const cameraPos2 = camera2.position.clone();

      const distance1 = cameraPos1.length();
      const distance2 = cameraPos2.length();

      expect(distance2 / distance1).toBeCloseTo(2, 0);
    });

    it("should handle moving target smoothly", () => {
      controller = new ThirdPersonCamera(camera, domElement, scene);
      const target = new Object3D();
      target.position.set(0, 0, 0);
      controller.setTarget(target);

      const positions: Vector3[] = [];
      for (let i = 0; i < 10; i++) {
        target.position.x += 1;
        controller.update(0.016);
        positions.push(camera.position.clone());
      }

      for (let i = 1; i < positions.length; i++) {
        const delta = positions[i].distanceTo(positions[i - 1]);
        expect(delta).toBeLessThan(5);
      }
    });
  });
});
