/**
 * Keyboard movement controller for OrbitControls debugging
 * DEV-ONLY: This module is dynamically imported only in development
 */

import { Vector3, type PerspectiveCamera } from "three";
import type { OrbitControls } from "three/addons/controls/OrbitControls.js";

export class KeyboardMovement {
  private keysPressed = new Set<string>();
  private moveDirection = new Vector3();
  private forward = new Vector3();
  private right = new Vector3();
  private readonly up = new Vector3(0, 1, 0);

  constructor(
    private camera: PerspectiveCamera,
    private controls: OrbitControls,
    private speed = 50
  ) {
    window.addEventListener("keydown", this.onKeyDown);
    window.addEventListener("keyup", this.onKeyUp);
  }

  private onKeyDown = (e: KeyboardEvent): void => {
    this.keysPressed.add(e.code);
  };

  private onKeyUp = (e: KeyboardEvent): void => {
    this.keysPressed.delete(e.code);
  };

  update(delta: number): void {
    if (this.keysPressed.size === 0) return;

    this.moveDirection.set(0, 0, 0);

    // Get camera forward/right vectors (horizontal plane)
    this.camera.getWorldDirection(this.forward);
    this.forward.y = 0;
    this.forward.normalize();
    this.right.crossVectors(this.forward, this.up).normalize();

    // WASD + QE movement
    if (this.keysPressed.has("KeyW")) this.moveDirection.add(this.forward);
    if (this.keysPressed.has("KeyS")) this.moveDirection.sub(this.forward);
    if (this.keysPressed.has("KeyA")) this.moveDirection.sub(this.right);
    if (this.keysPressed.has("KeyD")) this.moveDirection.add(this.right);
    if (this.keysPressed.has("KeyQ")) this.moveDirection.y -= 1;
    if (this.keysPressed.has("KeyE")) this.moveDirection.y += 1;

    if (this.moveDirection.lengthSq() === 0) return;

    this.moveDirection.normalize();

    const actualSpeed = this.keysPressed.has("ShiftLeft") || this.keysPressed.has("ShiftRight")
      ? this.speed * 3
      : this.speed;

    const movement = this.moveDirection.multiplyScalar(actualSpeed * delta);

    this.camera.position.add(movement);
    this.controls.target.add(movement);
  }

  dispose(): void {
    window.removeEventListener("keydown", this.onKeyDown);
    window.removeEventListener("keyup", this.onKeyUp);
  }
}
