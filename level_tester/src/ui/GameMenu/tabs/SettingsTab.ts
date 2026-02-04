import type { TabContent } from "../TabContainer";

export class SettingsTab implements TabContent {
  render(): HTMLElement {
    const container = document.createElement("div");

    const header = document.createElement("h3");
    header.textContent = "Settings";
    header.style.cssText = `
      margin: 0 0 16px 0;
      font-size: 16px;
      font-weight: 600;
      color: rgba(255, 255, 255, 0.9);
    `;
    container.appendChild(header);

    const placeholder = document.createElement("p");
    placeholder.textContent = "Settings options will appear here.";
    placeholder.style.cssText = `
      color: rgba(255, 255, 255, 0.6);
      font-size: 14px;
    `;
    container.appendChild(placeholder);

    return container;
  }

  dispose(): void {}
}
