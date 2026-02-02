/**
 * SettingsPanel - UI controls for runtime configuration
 *
 * Provides dropdown for terrain render mode selection.
 * Positioned in top-right corner of viewport.
 */

import { getAvailableTerrainModes, type TerrainRenderMode } from "../config";

export type TerrainModeChangeCallback = (mode: TerrainRenderMode) => void;

export class SettingsPanel {
  private container: HTMLDivElement;
  private select: HTMLSelectElement;
  private onTerrainModeChange: TerrainModeChangeCallback;

  private handleChange = (): void => {
    this.onTerrainModeChange(this.select.value as TerrainRenderMode);
  };

  constructor(onTerrainModeChange: TerrainModeChangeCallback) {
    this.onTerrainModeChange = onTerrainModeChange;
    this.container = this.createContainer();
    this.select = this.container.querySelector("select") as HTMLSelectElement;
  }

  private createContainer(): HTMLDivElement {
    const container = document.createElement("div");
    container.className = "settings-panel";
    container.style.cssText = `
      position: fixed;
      top: 16px;
      right: 16px;
      background: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 12px 16px;
      border-radius: 8px;
      font-family: system-ui, -apple-system, sans-serif;
      font-size: 14px;
      z-index: 1000;
      min-width: 180px;
    `;

    const selectId = "terrain-mode-select";

    const label = document.createElement("label");
    label.textContent = "Terrain Mode";
    label.htmlFor = selectId;
    label.style.cssText = `
      display: block;
      margin-bottom: 8px;
      font-weight: 500;
      color: rgba(255, 255, 255, 0.7);
    `;

    const select = document.createElement("select");
    select.id = selectId;
    select.style.cssText = `
      width: 100%;
      padding: 8px;
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 4px;
      background: rgba(255, 255, 255, 0.1);
      color: white;
      font-size: 14px;
      cursor: pointer;
      outline: none;
    `;

    const allOptions: Array<{ value: TerrainRenderMode; label: string; description: string }> = [
      { value: "merged", label: "Merged", description: "Best performance" },
      { value: "batched", label: "Batched", description: "Single draw call" },
      { value: "group", label: "Group", description: "Debug mode" },
    ];

    // Filter by available modes (production: merged only, dev: all modes)
    const availableModes = getAvailableTerrainModes();
    const options = allOptions.filter((opt) => availableModes.includes(opt.value));

    for (const opt of options) {
      const option = document.createElement("option");
      option.value = opt.value;
      option.textContent = `${opt.label} (${opt.description})`;
      select.appendChild(option);
    }

    select.addEventListener("change", this.handleChange);

    container.appendChild(label);
    container.appendChild(select);

    return container;
  }

  /**
   * Get the panel DOM element
   */
  getElement(): HTMLDivElement {
    return this.container;
  }

  /**
   * Mount panel to a parent element
   */
  mount(parent: HTMLElement): void {
    parent.appendChild(this.container);
  }

  /**
   * Unmount panel from its parent
   */
  unmount(): void {
    this.container.remove();
  }

  /**
   * Clean up event listeners and unmount
   */
  destroy(): void {
    this.select.removeEventListener("change", this.handleChange);
    this.unmount();
  }

  /**
   * Set the terrain mode dropdown value (without triggering callback)
   */
  setTerrainMode(mode: TerrainRenderMode): void {
    this.select.value = mode;
  }

  /**
   * Get current terrain mode value
   */
  getTerrainMode(): TerrainRenderMode {
    return this.select.value as TerrainRenderMode;
  }

  /**
   * Show the panel
   */
  show(): void {
    this.container.style.display = "block";
  }

  /**
   * Hide the panel
   */
  hide(): void {
    this.container.style.display = "none";
  }
}
