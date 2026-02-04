import { getAvailableTerrainModes, type TerrainRenderMode } from "../../config";
import { applyStyles, STYLES } from "../../ui/GameMenu/styles";
import type { TabContent } from "../../ui/GameMenu/TabContainer";

interface TerrainModeOption {
  value: TerrainRenderMode;
  label: string;
  description: string;
}

const TERRAIN_MODE_OPTIONS: TerrainModeOption[] = [
  { value: "merged", label: "Merged", description: "Best performance" },
  { value: "batched", label: "Batched", description: "Single draw call" },
  { value: "group", label: "Group", description: "Debug mode" },
];

export class DevTab implements TabContent {
  private select: HTMLSelectElement | null = null;
  private readonly onTerrainModeChange: (mode: TerrainRenderMode) => void;
  private readonly initialMode: TerrainRenderMode;

  private handleChange = (): void => {
    if (this.select) {
      this.onTerrainModeChange(this.select.value as TerrainRenderMode);
    }
  };

  constructor(
    onTerrainModeChange: (mode: TerrainRenderMode) => void,
    initialMode: TerrainRenderMode
  ) {
    this.onTerrainModeChange = onTerrainModeChange;
    this.initialMode = initialMode;
  }

  render(): HTMLElement {
    const container = document.createElement("div");

    const sectionHeader = document.createElement("h3");
    sectionHeader.textContent = "Terrain Debug";
    sectionHeader.style.cssText = `
      margin: 0 0 16px 0;
      font-size: 16px;
      font-weight: 600;
      color: rgba(255, 255, 255, 0.9);
    `;
    container.appendChild(sectionHeader);

    const selectId = "dev-terrain-mode";

    const label = document.createElement("label");
    label.textContent = "Terrain Mode";
    label.htmlFor = selectId;
    applyStyles(label, STYLES.label);
    container.appendChild(label);

    const select = document.createElement("select");
    select.id = selectId;
    applyStyles(select, STYLES.select);

    const availableModes = getAvailableTerrainModes();
    const options = TERRAIN_MODE_OPTIONS.filter((opt) =>
      availableModes.includes(opt.value)
    );

    for (const opt of options) {
      const option = document.createElement("option");
      option.value = opt.value;
      option.textContent = `${opt.label} (${opt.description})`;
      applyStyles(option, STYLES.option);
      select.appendChild(option);
    }

    const validInitialMode = options.some((opt) => opt.value === this.initialMode)
      ? this.initialMode
      : options[0]?.value ?? "merged";

    select.value = validInitialMode;

    if (validInitialMode !== this.initialMode) {
      this.onTerrainModeChange(validInitialMode);
    }

    select.addEventListener("change", this.handleChange);
    container.appendChild(select);

    this.select = select;

    return container;
  }

  setTerrainMode(mode: TerrainRenderMode): void {
    if (this.select) {
      const availableModes = getAvailableTerrainModes();
      if (!availableModes.includes(mode)) return;
      this.select.value = mode;
    }
  }

  getTerrainMode(): TerrainRenderMode {
    return (this.select?.value as TerrainRenderMode) ?? this.initialMode;
  }

  dispose(): void {
    if (this.select) {
      this.select.removeEventListener("change", this.handleChange);
    }
    this.select = null;
  }
}
