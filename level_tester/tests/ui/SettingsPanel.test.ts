/**
 * @vitest-environment jsdom
 */
// level_tester/tests/ui/SettingsPanel.test.ts

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { getAvailableTerrainModes } from "../../src/config";

describe("SettingsPanel", () => {
  let SettingsPanel: typeof import("../../src/ui/SettingsPanel").SettingsPanel;
  let container: HTMLDivElement;

  beforeEach(async () => {
    vi.resetModules();

    // Setup DOM
    container = document.createElement("div");
    document.body.appendChild(container);

    const module = await import("../../src/ui/SettingsPanel");
    SettingsPanel = module.SettingsPanel;
  });

  afterEach(() => {
    document.body.innerHTML = "";
  });

  it("should create panel element", () => {
    const panel = new SettingsPanel(() => {});
    expect(panel.getElement()).toBeInstanceOf(HTMLDivElement);
  });

  it("should mount to parent element", () => {
    const panel = new SettingsPanel(() => {});
    panel.mount(container);
    expect(container.children.length).toBe(1);
  });

  it("should unmount from parent element", () => {
    const panel = new SettingsPanel(() => {});
    panel.mount(container);
    panel.unmount();
    expect(container.children.length).toBe(0);
  });

  it("should contain dropdown with terrain mode options", () => {
    const panel = new SettingsPanel(() => {});
    const element = panel.getElement();
    const select = element.querySelector("select");

    expect(select).not.toBeNull();
    expect(select?.options.length).toBe(3);
  });

  it("should have Merged, Batched, Group options", () => {
    const panel = new SettingsPanel(() => {});
    const element = panel.getElement();
    const select = element.querySelector("select") as HTMLSelectElement;

    const values = Array.from(select.options).map((o) => o.value);
    expect(values).toContain("merged");
    expect(values).toContain("batched");
    expect(values).toContain("group");
  });

  it("should call callback on mode change", () => {
    const callback = vi.fn();
    const panel = new SettingsPanel(callback);
    const element = panel.getElement();
    const select = element.querySelector("select") as HTMLSelectElement;

    select.value = "batched";
    select.dispatchEvent(new Event("change"));

    expect(callback).toHaveBeenCalledWith("batched");
  });

  it("should update dropdown value with setTerrainMode", () => {
    const panel = new SettingsPanel(() => {});
    panel.setTerrainMode("group");

    const select = panel.getElement().querySelector("select") as HTMLSelectElement;
    expect(select.value).toBe("group");
  });

  it("should not call callback when setTerrainMode is called", () => {
    const callback = vi.fn();
    const panel = new SettingsPanel(callback);
    panel.setTerrainMode("batched");

    expect(callback).not.toHaveBeenCalled();
  });

  it("should clean up event listeners on destroy", () => {
    const callback = vi.fn();
    const panel = new SettingsPanel(callback);
    panel.mount(container);

    panel.destroy();

    const select = panel.getElement().querySelector("select") as HTMLSelectElement;
    select.value = "batched";
    select.dispatchEvent(new Event("change"));

    expect(callback).not.toHaveBeenCalled();
  });

  it("should have accessible label association", () => {
    const panel = new SettingsPanel(() => {});
    const element = panel.getElement();
    const select = element.querySelector("select") as HTMLSelectElement;
    const label = element.querySelector("label") as HTMLLabelElement;

    expect(label.htmlFor).toBe(select.id);
    expect(select.id).not.toBe("");
  });

  it("should return current terrain mode", () => {
    const panel = new SettingsPanel(() => {});
    panel.setTerrainMode("batched");
    expect(panel.getTerrainMode()).toBe("batched");
  });

  it("should show and hide panel", () => {
    const panel = new SettingsPanel(() => {});
    panel.hide();
    expect(panel.getElement().style.display).toBe("none");

    panel.show();
    expect(panel.getElement().style.display).toBe("block");
  });
});

describe("SettingsPanel terrain mode filtering", () => {
  let SettingsPanel: typeof import("../../src/ui/SettingsPanel").SettingsPanel;
  let container: HTMLDivElement;

  beforeEach(async () => {
    vi.resetModules();

    container = document.createElement("div");
    document.body.appendChild(container);

    const module = await import("../../src/ui/SettingsPanel");
    SettingsPanel = module.SettingsPanel;
  });

  afterEach(() => {
    document.body.innerHTML = "";
  });

  it("should filter terrain mode options by available modes", () => {
    const availableModes = getAvailableTerrainModes();
    const panel = new SettingsPanel(() => {});
    const element = panel.getElement();
    const select = element.querySelector("select") as HTMLSelectElement;
    const options = Array.from(select.options);

    // All displayed options should be in available modes
    options.forEach((option) => {
      expect(availableModes).toContain(option.value);
    });

    // Number of options should match available modes
    expect(options.length).toBe(availableModes.length);
  });

  it("should show all modes in dev environment", () => {
    const availableModes = getAvailableTerrainModes();
    const panel = new SettingsPanel(() => {});
    const element = panel.getElement();
    const select = element.querySelector("select") as HTMLSelectElement;

    // Tests run in DEV mode
    expect(select.options.length).toBe(3);
    expect(availableModes.length).toBe(3);
  });

  it("should include merged option in all environments", () => {
    const panel = new SettingsPanel(() => {});
    const element = panel.getElement();
    const select = element.querySelector("select") as HTMLSelectElement;
    const optionValues = Array.from(select.options).map((opt) => opt.value);

    expect(optionValues).toContain("merged");
  });

  it("should only show options that are in getAvailableTerrainModes", () => {
    const availableModes = getAvailableTerrainModes();
    const panel = new SettingsPanel(() => {});
    const element = panel.getElement();
    const select = element.querySelector("select") as HTMLSelectElement;
    const displayedValues = Array.from(select.options).map((opt) => opt.value);

    // Every displayed option must be in available modes
    for (const value of displayedValues) {
      expect(availableModes).toContain(value);
    }

    // Every available mode must be displayed
    for (const mode of availableModes) {
      expect(displayedValues).toContain(mode);
    }
  });
});
