import { STYLES, applyStyles, mergeStyles } from "./styles";

export interface TabContent {
  render(): HTMLElement;
  onActivate?(): void;
  onDeactivate?(): void;
  dispose?(): void;
}

export interface TabDefinition {
  id: string;
  label: string;
  icon?: string;
  content: TabContent;
}

interface ButtonHandlers {
  mouseenter: () => void;
  mouseleave: () => void;
  click: () => void;
}

export class TabContainer {
  private container: HTMLDivElement;
  private sidebar: HTMLDivElement;
  private contentArea: HTMLDivElement;
  private tabs: TabDefinition[];
  private activeTabId: string;
  private buttonMap: Map<string, HTMLButtonElement> = new Map();
  private buttonHandlers: Map<HTMLButtonElement, ButtonHandlers> = new Map();

  constructor(tabs: TabDefinition[]) {
    this.tabs = tabs;
    this.activeTabId = tabs[0]?.id ?? "";

    this.container = document.createElement("div");
    this.container.style.cssText = "display: flex; flex: 1; overflow: hidden;";

    this.sidebar = this.createSidebar();
    this.contentArea = this.createContentArea();

    this.container.appendChild(this.sidebar);
    this.container.appendChild(this.contentArea);

    this.renderActiveTabContent();
  }

  private createSidebar(): HTMLDivElement {
    const sidebar = document.createElement("div");
    applyStyles(sidebar, STYLES.tabSidebar);

    for (const tab of this.tabs) {
      const button = this.createTabButton(tab);
      this.buttonMap.set(tab.id, button);
      sidebar.appendChild(button);
    }

    return sidebar;
  }

  private createTabButton(tab: TabDefinition): HTMLButtonElement {
    const button = document.createElement("button");
    button.textContent = tab.icon ? `${tab.icon} ${tab.label}` : tab.label;

    const isActive = tab.id === this.activeTabId;
    this.applyButtonStyles(button, isActive);

    const handlers: ButtonHandlers = {
      mouseenter: () => {
        if (tab.id !== this.activeTabId) {
          applyStyles(button, mergeStyles(STYLES.tabButton.base, STYLES.tabButton.hover));
        }
      },
      mouseleave: () => {
        this.applyButtonStyles(button, tab.id === this.activeTabId);
      },
      click: () => {
        this.setActiveTab(tab.id);
      },
    };

    this.buttonHandlers.set(button, handlers);
    button.addEventListener("mouseenter", handlers.mouseenter);
    button.addEventListener("mouseleave", handlers.mouseleave);
    button.addEventListener("click", handlers.click);

    return button;
  }

  private applyButtonStyles(button: HTMLButtonElement, isActive: boolean): void {
    if (isActive) {
      applyStyles(button, mergeStyles(STYLES.tabButton.base, STYLES.tabButton.active));
    } else {
      applyStyles(button, STYLES.tabButton.base);
    }
  }

  private createContentArea(): HTMLDivElement {
    const contentArea = document.createElement("div");
    applyStyles(contentArea, STYLES.contentArea);
    return contentArea;
  }

  private renderActiveTabContent(): void {
    const activeTab = this.tabs.find((t) => t.id === this.activeTabId);
    if (activeTab) {
      this.contentArea.innerHTML = "";
      this.contentArea.appendChild(activeTab.content.render());
      activeTab.content.onActivate?.();
    }
  }

  getElement(): HTMLDivElement {
    return this.container;
  }

  setActiveTab(tabId: string): void {
    if (tabId === this.activeTabId) return;

    const oldTab = this.tabs.find((t) => t.id === this.activeTabId);
    const newTab = this.tabs.find((t) => t.id === tabId);

    if (!newTab) return;

    oldTab?.content.onDeactivate?.();

    const oldButton = this.buttonMap.get(this.activeTabId);
    if (oldButton) {
      this.applyButtonStyles(oldButton, false);
    }

    this.activeTabId = tabId;

    const newButton = this.buttonMap.get(tabId);
    if (newButton) {
      this.applyButtonStyles(newButton, true);
    }

    this.contentArea.innerHTML = "";
    this.contentArea.appendChild(newTab.content.render());
    newTab.content.onActivate?.();
  }

  getActiveTab(): string {
    return this.activeTabId;
  }

  addTab(tab: TabDefinition): void {
    this.tabs.push(tab);
    const button = this.createTabButton(tab);
    this.buttonMap.set(tab.id, button);
    this.sidebar.appendChild(button);
  }

  dispose(): void {
    for (const tab of this.tabs) {
      tab.content.dispose?.();
    }
    for (const [button, handlers] of this.buttonHandlers) {
      button.removeEventListener("mouseenter", handlers.mouseenter);
      button.removeEventListener("mouseleave", handlers.mouseleave);
      button.removeEventListener("click", handlers.click);
    }
    this.buttonHandlers.clear();
    this.buttonMap.clear();
  }
}
