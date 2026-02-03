/**
 * Level Tester - Three.js viewer for Blender level exports
 */

import {
  Scene,
  PerspectiveCamera,
  WebGLRenderer,
  AmbientLight,
  DirectionalLight,
  GridHelper,
  AxesHelper,
  Color,
  Vector3,
  Box3,
} from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { ManifestLoader, EntityLoader, registerDefaultHandlers, type LoadedNPC } from "./loaders";
import { WorldLoader } from "./world";
import { LoadingScreen, SettingsPanel } from "./ui";
import { setConfig, config } from "./config";

// Register entity handlers before loading
registerDefaultHandlers();

// Configuration
const LEVEL_PATH = "/levels/demo"; // Change to your exported level path

class LevelTester {
  private scene: Scene;
  private camera: PerspectiveCamera;
  private renderer: WebGLRenderer;
  private controls: OrbitControls;
  private loadingScreen: LoadingScreen;
  private settingsPanel: SettingsPanel;
  private manifestLoader: ManifestLoader | null = null;
  private worldLoader: WorldLoader | null = null;
  private entityLoader: EntityLoader | null = null;
  private npcs: Map<string, LoadedNPC> = new Map();

  // Dev-only keyboard movement (dynamically loaded)
  private keyboardMovement: { update(delta: number): void } | null = null;
  private lastTime = 0;

  constructor() {
    // Loading screen (must be first)
    this.loadingScreen = new LoadingScreen();

    // Settings panel for terrain mode
    this.settingsPanel = new SettingsPanel((mode) => {
      setConfig({ terrainMode: mode });
      if (confirm(`Terrain mode changed to "${mode}". Reload page to apply?`)) {
        window.location.reload();
      }
    });
    this.settingsPanel.setTerrainMode(config.terrainMode);
    this.settingsPanel.mount(document.body);
    this.loadingScreen.setPhases([
      { name: "Initializing", weight: 1 },
      { name: "Loading manifest", weight: 1 },
      { name: "Loading world", weight: 3 },
      { name: "Loading entities", weight: 3 },
      { name: "Finalizing", weight: 1 },
    ]);

    // Scene
    this.scene = new Scene();
    this.scene.background = new Color(0x87ceeb); // Sky blue

    // Camera
    this.camera = new PerspectiveCamera(
      60,
      window.innerWidth / window.innerHeight,
      0.1,
      10000
    );
    this.camera.position.set(50, 50, 50);

    // Renderer
    this.renderer = new WebGLRenderer({ antialias: true });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    document.getElementById("app")!.appendChild(this.renderer.domElement);

    // Camera controls (OrbitControls for landscape debugging)
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;

    // Lights
    this.setupLights();

    // Helpers
    this.setupHelpers();

    // Events
    window.addEventListener("resize", this.onResize.bind(this));

    // Dev-only keyboard movement (WASD + QE)
    if (import.meta.env.DEV) {
      import("./dev/KeyboardMovement").then(({ KeyboardMovement }) => {
        this.keyboardMovement = new KeyboardMovement(this.camera, this.controls);
      });
    }

    // Mark initialization complete
    this.loadingScreen.startPhase("Initializing");
    this.loadingScreen.setPhaseProgress(1);

    // Start render loop
    this.animate();
  }

  private setupLights(): void {
    // Ambient light
    const ambient = new AmbientLight(0xffffff, 0.4);
    this.scene.add(ambient);

    // Directional light (sun)
    const sun = new DirectionalLight(0xffffff, 1.0);
    sun.position.set(100, 100, 50);
    sun.castShadow = true;
    this.scene.add(sun);
  }

  private setupHelpers(): void {
    // Grid
    const grid = new GridHelper(100, 100, 0x444444, 0x888888);
    this.scene.add(grid);

    // Axes
    const axes = new AxesHelper(10);
    this.scene.add(axes);
  }

  /**
   * Load a level from the given path
   */
  async loadLevel(levelPath: string): Promise<void> {
    if (import.meta.env.DEV) {
      console.log(`Loading level from: ${levelPath}`);
    }

    try {
      // Phase 1: Load manifest
      this.loadingScreen.startPhase("Loading manifest");
      this.manifestLoader = new ManifestLoader(levelPath);
      const manifest = await this.manifestLoader.load();
      this.loadingScreen.setPhaseProgress(1);

      if (import.meta.env.DEV) {
        console.log("Manifest loaded:", manifest);
        console.log(`  - ${manifest.statistics.total_instances} instances`);
        console.log(
          `  - ${manifest.statistics.total_terrain ?? manifest.terrain_objects.length} terrain objects`
        );
        console.log(`  - ${Object.keys(manifest.islands).length} islands`);
      }

      // Phase 2: Load world geometry
      this.loadingScreen.startPhase("Loading world");
      this.worldLoader = new WorldLoader(this.manifestLoader);

      const worldResult = await this.worldLoader.load({
        loadCollision: false,
        onProgress: (loaded, total) => {
          this.loadingScreen.setPhaseProgress(loaded / total);
          this.loadingScreen.setStatus(
            `Loading islands: ${loaded}/${total}`
          );
        },
      });

      this.scene.add(worldResult.root);
      this.loadingScreen.setPhaseProgress(1);

      // Phase 3: Load entities
      this.loadingScreen.startPhase("Loading entities");
      this.entityLoader = new EntityLoader(this.manifestLoader);

      const entityResult = await this.entityLoader.load({
        onProgress: (loaded, total, assetId) => {
          this.loadingScreen.setPhaseProgress(loaded / total);
          this.loadingScreen.setStatus(`Loading asset: ${assetId}`);
        },
      });

      this.scene.add(entityResult.root);
      this.loadingScreen.setPhaseProgress(1);

      // Store NPCs for interaction
      this.npcs = entityResult.npcs;

      // Log NPC dialog info
      if (import.meta.env.DEV && this.npcs.size > 0) {
        console.log(`Loaded ${this.npcs.size} NPCs with dialog:`);
        for (const [id, npc] of this.npcs) {
          console.log(
            `  - ${npc.instance.name} (${id}): ${npc.dialog.length} dialog lines`
          );
          for (const line of npc.dialog) {
            console.log(`      [${line.speaker}]: "${line.text}"`);
          }
        }
      }

      // Log interactive objects
      if (import.meta.env.DEV && entityResult.interactives.size > 0) {
        console.log(
          `Loaded ${entityResult.interactives.size} interactive objects:`
        );
        for (const interactive of entityResult.interactives.values()) {
          console.log(
            `  - ${interactive.instance.name}: script="${interactive.scriptId}"`
          );
        }
      }

      // Phase 4: Finalize
      this.loadingScreen.startPhase("Finalizing");
      this.focusOnBounds(worldResult.bounds);
      this.loadingScreen.setPhaseProgress(1);

      if (import.meta.env.DEV) {
        console.log("Level loaded successfully!");
      }
      this.loadingScreen.complete();
    } catch (error) {
      console.error("Failed to load level:", error);
      this.loadingScreen.showError(`${error}`);
    }
  }

  /**
   * Focus camera on the given bounds
   */
  private focusOnBounds(bounds: Box3): void {
    if (bounds.isEmpty()) return;

    const center = new Vector3();
    bounds.getCenter(center);

    const size = new Vector3();
    bounds.getSize(size);
    const maxDim = Math.max(size.x, size.y, size.z);

    const distance = maxDim * 1.5;
    this.camera.position.set(
      center.x + distance,
      center.y + distance * 0.5,
      center.z + distance
    );
    this.controls.target.copy(center);
    this.controls.update();
  }

  private onResize(): void {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }

  private animate(): void {
    const now = performance.now();
    const delta = (now - this.lastTime) / 1000;
    this.lastTime = now;

    requestAnimationFrame(this.animate.bind(this));
    this.keyboardMovement?.update(delta);
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
}

// Initialize
const app = new LevelTester();

// Load the demo level
app.loadLevel(LEVEL_PATH);
