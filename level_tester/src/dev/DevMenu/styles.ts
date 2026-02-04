/**
 * CSS-in-JS styles for DevMenu component
 */

export const STYLES = {
  backdrop: {
    base: `
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(4px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 2000;
      opacity: 0;
      visibility: hidden;
      transition: opacity 200ms ease-out, visibility 200ms ease-out;
    `,
    visible: `
      opacity: 1;
      visibility: visible;
    `,
  },

  modal: {
    base: `
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
      width: 600px;
      height: 400px;
      max-width: 90vw;
      max-height: 80vh;
      border-radius: 12px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      display: flex;
      overflow: hidden;
      transform: scale(0.95);
      transition: transform 200ms ease-out;
    `,
    visible: `
      transform: scale(1);
    `,
  },

  tabSidebar: `
    width: 140px;
    background: rgba(0, 0, 0, 0.3);
    border-right: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    flex-direction: column;
    padding: 8px 0;
  `,

  tabButton: {
    base: `
      padding: 12px 16px;
      background: transparent;
      border: none;
      border-left: 3px solid transparent;
      color: rgba(255, 255, 255, 0.6);
      font-family: system-ui, -apple-system, sans-serif;
      font-size: 14px;
      text-align: left;
      cursor: pointer;
      transition: background 150ms ease, color 150ms ease, border-color 150ms ease;
    `,
    hover: `
      background: rgba(255, 255, 255, 0.05);
      color: rgba(255, 255, 255, 0.8);
    `,
    active: `
      background: rgba(79, 172, 254, 0.1);
      border-left-color: #4facfe;
      color: #4facfe;
    `,
  },

  contentArea: `
    flex: 1;
    padding: 24px;
    overflow-y: auto;
    color: white;
    font-family: system-ui, -apple-system, sans-serif;
  `,

  label: `
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    font-size: 14px;
    color: rgba(255, 255, 255, 0.7);
  `,

  select: `
    width: 100%;
    padding: 8px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    background-color: #1a1a2e;
    color: white;
    font-size: 14px;
    cursor: pointer;
    outline: none;
  `,

  option: `
    background-color: #1a1a2e;
    color: white;
    padding: 8px;
  `,
} as const;

/**
 * Apply CSS text to an element's style
 */
export function applyStyles(element: HTMLElement, cssText: string): void {
  element.style.cssText = cssText.replace(/\s+/g, " ").trim();
}

/**
 * Merge multiple CSS text strings into one
 */
export function mergeStyles(...styles: string[]): string {
  return styles.map((s) => s.replace(/\s+/g, " ").trim()).join(" ");
}
