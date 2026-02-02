/**
 * Abstract base class for entity handlers
 * Each handler knows how to create entities of specific types
 */

import { Group, type Object3D, SkinnedMesh } from "three";
import { clone as cloneWithSkeleton } from "three/addons/utils/SkeletonUtils.js";
import type { GLTF } from "three/addons/loaders/GLTFLoader.js";
import type { Instance, EntityType, Vec3, Quaternion } from "../../types/manifest";
import type { EntityResult, EntityCreationContext } from "./types";

export abstract class EntityHandler<TData = unknown> {
  /**
   * Entity types this handler can process
   */
  abstract readonly entityTypes: readonly EntityType[];

  /**
   * Create an entity from an instance and optional asset
   */
  abstract create(context: EntityCreationContext): EntityResult<TData>;

  /**
   * Check if this handler can process the given entity type
   */
  canHandle(entityType: EntityType): boolean {
    return this.entityTypes.includes(entityType);
  }

  /**
   * Create a Group with standard setup (name, userData, transform)
   * Utility method for handlers to use
   */
  protected createGroup(instance: Instance, asset: GLTF | null): Object3D {
    const group = new Group();
    group.name = instance.name;
    group.userData.instanceId = instance.id;
    group.userData.entityType = instance.entity_type;
    group.userData.instance = instance;

    this.applyTransform(group, instance.position, instance.rotation, instance.scale);

    if (asset) {
      // Use SkeletonUtils.clone for skinned meshes (characters with skeletons)
      // Standard clone(true) doesn't properly clone skeletons
      const clone = this.hasSkinnedMesh(asset.scene)
        ? cloneWithSkeleton(asset.scene)
        : asset.scene.clone(true);
      group.add(clone);
    }

    return group;
  }

  /**
   * Check if an object contains any skinned meshes
   */
  private hasSkinnedMesh(object: Object3D): boolean {
    let found = false;
    object.traverse((child) => {
      if (child instanceof SkinnedMesh) {
        found = true;
      }
    });
    return found;
  }

  /**
   * Apply transform to an Object3D
   */
  protected applyTransform(
    object: Object3D,
    position: Vec3,
    rotation: Quaternion,
    scale: Vec3
  ): void {
    object.position.set(position[0], position[1], position[2]);
    object.quaternion.set(rotation[0], rotation[1], rotation[2], rotation[3]);
    object.scale.set(scale[0], scale[1], scale[2]);

    console.log(`[EntityHandler] Applied transform to "${object.name}":`, {
      position: object.position.toArray(),
      quaternion: object.quaternion.toArray(),
      scale: object.scale.toArray(),
    });
  }
}
