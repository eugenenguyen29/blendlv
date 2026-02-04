import { STYLES, applyStyles, mergeStyles } from "./styles";
import { TabContainer, type TabDefinition } from "./TabContainer";
import { SettingsTab } from "./tabs/SettingsTab";

export interface GameMenuConfig {
  initialTabs?: TabDefinition[];
}

export class GameMenu {
  private backdrop: HTMLDivElement;
  private modal: HTMLDivElement;
  private tabContainer: TabContainer;
  private isOpen = false;
  private animating = false;

  private handleKeydown = (e: KeyboardEvent): void => {
    if (e.key === "Escape" && this.isOpen) {
      e.preventDefault();
      this.close();
    } else if (e.key === "`") {
      e.preventDefault();
      this.toggle();
    }
  };

  private handleBackdropClick = (e: MouseEvent): void => {
    if (e.target === this.backdrop) {
      this.close();
    }
  };

  constructor(config: GameMenuConfig = {}) {
    this.backdrop = document.createElement("div");
    applyStyles(this.backdrop, STYLES.backdrop.base);

    this.modal = document.createElement("div");
    applyStyles(this.modal, STYLES.modal.base);

    const settingsTab = new SettingsTab();

    const tabs: TabDefinition[] = config.initialTabs ?? [
      {
        id: "settings",
        label: "Settings",
        icon: "⚙️",
        content: settingsTab,
      },
    ];

    this.tabContainer = new TabContainer(tabs);
    this.modal.appendChild(this.tabContainer.getElement());
    this.backdrop.appendChild(this.modal);
  }

  mount(parent: HTMLElement): void {
    parent.appendChild(this.backdrop);
    document.addEventListener("keydown", this.handleKeydown);
    this.backdrop.addEventListener("click", this.handleBackdropClick);
  }

  unmount(): void {
    document.removeEventListener("keydown", this.handleKeydown);
    this.backdrop.removeEventListener("click", this.handleBackdropClick);
    this.backdrop.remove();
  }

  dispose(): void {
    this.unmount();
    this.tabContainer.dispose();
  }

  addTab(tab: TabDefinition): void {
    this.tabContainer.addTab(tab);
  }

  open(): void {
    if (this.isOpen || this.animating) return;

    this.animating = true;
    this.isOpen = true;

    applyStyles(this.backdrop, mergeStyles(STYLES.backdrop.base, STYLES.backdrop.visible));
    applyStyles(this.modal, mergeStyles(STYLES.modal.base, STYLES.modal.visible));

    setTimeout(() => {
      this.animating = false;
    }, 200);
  }

  close(): void {
    if (!this.isOpen || this.animating) return;

    this.animating = true;

    applyStyles(this.backdrop, STYLES.backdrop.base);
    applyStyles(this.modal, STYLES.modal.base);

    setTimeout(() => {
      this.isOpen = false;
      this.animating = false;
    }, 200);
  }

  toggle(): void {
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  }

  isVisible(): boolean {
    return this.isOpen;
  }
}
