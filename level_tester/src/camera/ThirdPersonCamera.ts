import {
  type Event as ThreeEvent,
  Mesh,
  Object3D,
  PerspectiveCamera,
  Raycaster,
  Scene,
  Vector3,
} from "three";

export interface ThirdPersonCameraOptions {
  initialDistance?: number;
  maxDistance?: number;
  minDistance?: number;
  verticalUpLimit?: number;
  verticalDownLimit?: number;
  initialDirection?: { x: number; y: number };
  rotationSpeed?: number;
  zoomSpeed?: number;
  enableCollision?: boolean;
  collisionOffset?: number;
  collisionLerpSpeed?: number;
  cameraLerpSpeed?: number;
  pivotFollowSpeed?: number;
}

const DEFAULT_OPTIONS: Required<ThirdPersonCameraOptions> = {
  initialDistance: -5,
  maxDistance: -7,
  minDistance: -0.7,
  verticalUpLimit: 1.5,
  verticalDownLimit: -1.3,
  initialDirection: { x: 0, y: 0 },
  rotationSpeed: 1,
  zoomSpeed: 1,
  enableCollision: true,
  collisionOffset: 0.7,
  collisionLerpSpeed: 4,
  cameraLerpSpeed: 2,
  pivotFollowSpeed: 5,
};

export class ThirdPersonCamera {
  private camera: PerspectiveCamera;
  private domElement: HTMLElement;
  private scene: Scene;
  private options: Required<ThirdPersonCameraOptions>;

  private pivot: Object3D;
  private followCam: Object3D;
  private target: Object3D | null = null;
  private enabled = true;

  private tempVector = new Vector3();
  private followCamWorldPosition = new Vector3();

  private isMouseDown = false;
  private originZDis: number;

  private intersectObjects: Object3D[] = [];
  private raycaster: Raycaster;
  private cameraRayOrigin = new Vector3();
  private cameraRayDir = new Vector3();
  private cameraPosition = new Vector3();
  private camLerpingPoint = new Vector3();
  private smallestDistance: number;

  private boundOnObjectAdded: (
    e: ThreeEvent<"childadded", Scene> & { child: Object3D }
  ) => void;
  private boundOnObjectRemoved: (
    e: ThreeEvent<"childremoved", Scene> & { child: Object3D }
  ) => void;

  private boundOnMouseDown: (e: MouseEvent) => void;
  private boundOnMouseUp: (e: MouseEvent) => void;
  private boundOnMouseMove: (e: MouseEvent) => void;
  private boundOnMouseWheel: (e: WheelEvent) => void;

  constructor(
    camera: PerspectiveCamera,
    domElement: HTMLElement,
    scene: Scene,
    options: ThirdPersonCameraOptions = {}
  ) {
    this.camera = camera;
    this.domElement = domElement;
    this.scene = scene;
    this.options = { ...DEFAULT_OPTIONS, ...options };

    this.originZDis = this.options.initialDistance;
    this.smallestDistance = this.originZDis;

    this.raycaster = new Raycaster(
      new Vector3(),
      new Vector3(),
      0,
      Math.abs(this.options.maxDistance)
    );

    this.pivot = new Object3D();
    this.pivot.name = "ThirdPersonCamera_Pivot";

    this.followCam = new Object3D();
    this.followCam.name = "ThirdPersonCamera_FollowCam";

    this.initializeFollowCamPosition();

    this.pivot.add(this.followCam);
    this.scene.add(this.pivot);

    this.boundOnMouseDown = this.onMouseDown.bind(this);
    this.boundOnMouseUp = this.onMouseUp.bind(this);
    this.boundOnMouseMove = this.onMouseMove.bind(this);
    this.boundOnMouseWheel = this.onMouseWheel.bind(this);
    this.boundOnObjectAdded = this.onObjectAdded.bind(this);
    this.boundOnObjectRemoved = this.onObjectRemoved.bind(this);

    this.setupEventListeners();
    this.setupSceneListeners();
    this.buildCollisionObjects();
  }

  private initializeFollowCamPosition(): void {
    const { initialDistance, initialDirection } = this.options;
    const verticalAngle = initialDirection.x;

    this.followCam.position.set(
      0,
      initialDistance * Math.sin(-verticalAngle),
      initialDistance * Math.cos(-verticalAngle)
    );

    this.followCam.rotation.x = verticalAngle;
    this.pivot.rotation.y = initialDirection.y;
  }

  setTarget(target: Object3D): void {
    this.target = target;
  }

  update(delta: number): void {
    if (!this.enabled || !this.target) {
      return;
    }

    this.updatePivotPosition(delta);
    this.cameraCollisionDetect(delta);
    this.updateCameraPosition(delta);
    this.updateCameraLookAt();
  }

  private updatePivotPosition(delta: number): void {
    if (!this.target) return;

    this.target.getWorldPosition(this.tempVector);
    const lerpFactor = 1 - Math.exp(-this.options.pivotFollowSpeed * delta);
    this.pivot.position.lerp(this.tempVector, lerpFactor);
  }

  private updateCameraPosition(delta: number): void {
    this.followCam.getWorldPosition(this.followCamWorldPosition);
    const lerpFactor = 1 - Math.exp(-this.options.cameraLerpSpeed * delta);
    this.camera.position.lerp(this.followCamWorldPosition, lerpFactor);
  }

  private updateCameraLookAt(): void {
    this.camera.lookAt(this.pivot.position);
  }

  setEnabled(enabled: boolean): void {
    this.enabled = enabled;
  }

  dispose(): void {
    this.removeEventListeners();
    this.removeSceneListeners();
    this.scene.remove(this.pivot);
  }

  private setupEventListeners(): void {
    this.domElement.addEventListener("mousedown", this.boundOnMouseDown);
    this.domElement.addEventListener("mouseup", this.boundOnMouseUp);
    this.domElement.addEventListener("mousemove", this.boundOnMouseMove);
    this.domElement.addEventListener("wheel", this.boundOnMouseWheel);
  }

  private removeEventListeners(): void {
    this.domElement.removeEventListener("mousedown", this.boundOnMouseDown);
    this.domElement.removeEventListener("mouseup", this.boundOnMouseUp);
    this.domElement.removeEventListener("mousemove", this.boundOnMouseMove);
    this.domElement.removeEventListener("wheel", this.boundOnMouseWheel);
  }

  private setupSceneListeners(): void {
    this.scene.addEventListener("childadded", this.boundOnObjectAdded);
    this.scene.addEventListener("childremoved", this.boundOnObjectRemoved);
  }

  private removeSceneListeners(): void {
    this.scene.removeEventListener("childadded", this.boundOnObjectAdded);
    this.scene.removeEventListener("childremoved", this.boundOnObjectRemoved);
  }

  private buildCollisionObjects(): void {
    this.intersectObjects = [];
    this.scene.traverse((object) => {
      this.addToCollisionListIfMesh(object);
    });
  }

  private addToCollisionListIfMesh(object: Object3D): void {
    if (object.userData?.camExcludeCollision) return;
    if ((object as Mesh).isMesh && object.visible) {
      this.intersectObjects.push(object);
    }
  }

  private onObjectAdded(e: ThreeEvent<"childadded", Scene> & { child: Object3D }): void {
    this.traverseAdd(e.child);
  }

  private onObjectRemoved(e: ThreeEvent<"childremoved", Scene> & { child: Object3D }): void {
    this.traverseRemove(e.child);
  }

  private traverseAdd(object: Object3D): void {
    this.addToCollisionListIfMesh(object);
    object.children.forEach((child) => this.traverseAdd(child));
  }

  private traverseRemove(object: Object3D): void {
    this.intersectObjects = this.intersectObjects.filter(
      (item) => item.uuid !== object.uuid
    );
    object.children.forEach((child) => this.traverseRemove(child));
  }

  private cameraCollisionDetect(delta: number): void {
    if (!this.options.enableCollision) {
      this.camLerpingPoint.copy(this.followCam.position);
      return;
    }

    this.pivot.updateMatrixWorld(true);
    this.cameraRayOrigin.copy(this.pivot.position);
    this.followCam.getWorldPosition(this.cameraPosition);
    this.cameraRayDir.subVectors(this.cameraPosition, this.pivot.position);

    const rayLength = this.cameraRayDir.length();
    if (rayLength === 0) {
      this.camLerpingPoint.copy(this.followCam.position);
      return;
    }

    this.raycaster.set(this.cameraRayOrigin, this.cameraRayDir.normalize());
    this.raycaster.far = Math.abs(this.originZDis) + 1;

    const intersects = this.raycaster.intersectObjects(this.intersectObjects);

    if (intersects.length > 0 && intersects[0].distance <= Math.abs(this.originZDis)) {
      this.smallestDistance = Math.min(
        -intersects[0].distance * this.options.collisionOffset,
        this.options.minDistance
      );
    } else {
      this.smallestDistance = this.originZDis;
    }

    this.camLerpingPoint.set(
      this.followCam.position.x,
      this.smallestDistance * Math.sin(-this.followCam.rotation.x),
      this.smallestDistance * Math.cos(-this.followCam.rotation.x)
    );

    const lerpFactor = 1 - Math.exp(-this.options.collisionLerpSpeed * delta);
    this.followCam.position.lerp(this.camLerpingPoint, lerpFactor);
  }

  private onMouseDown(_e: MouseEvent): void {
    this.isMouseDown = true;
  }

  private onMouseUp(_e: MouseEvent): void {
    this.isMouseDown = false;
  }

  private onMouseMove(e: MouseEvent): void {
    if (!this.isMouseDown) return;

    this.pivot.rotation.y -= e.movementX * 0.002 * this.options.rotationSpeed;

    const newVerticalRotation =
      this.followCam.rotation.x + e.movementY * 0.002 * this.options.rotationSpeed;
    const distance = this.followCam.position.length();

    if (
      newVerticalRotation >= this.options.verticalDownLimit &&
      newVerticalRotation <= this.options.verticalUpLimit
    ) {
      this.followCam.rotation.x = newVerticalRotation;
      this.followCam.position.y = -distance * Math.sin(-newVerticalRotation);
      this.followCam.position.z = -distance * Math.cos(-newVerticalRotation);
    }
  }

  private onMouseWheel(e: WheelEvent): void {
    const newDistance =
      this.originZDis - e.deltaY * 0.002 * this.options.zoomSpeed;
    const verticalRotation = this.followCam.rotation.x;

    if (
      newDistance >= this.options.maxDistance &&
      newDistance <= this.options.minDistance
    ) {
      this.originZDis = newDistance;
      this.followCam.position.z = this.originZDis * Math.cos(-verticalRotation);
      this.followCam.position.y = this.originZDis * Math.sin(-verticalRotation);
    }
  }

  getPivotPosition(): Vector3 {
    return this.pivot.position.clone();
  }

  getFollowCamPosition(): Vector3 {
    return this.followCam.position.clone();
  }

  getPivotRotation(): number {
    return this.pivot.rotation.y;
  }

  getFollowCamRotation(): { x: number } {
    return { x: this.followCam.rotation.x };
  }

  getCurrentDistance(): number {
    return this.originZDis;
  }

  isCollisionEnabled(): boolean {
    return this.options.enableCollision;
  }

  getCollisionObjects(): Object3D[] {
    return this.intersectObjects;
  }
}
