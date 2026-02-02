/**
 * LoadingScreen - Manages the loading overlay UI
 */

export interface LoadingPhase {
  name: string;
  weight: number; // Relative weight for progress calculation
}

export class LoadingScreen {
  private container: HTMLElement;
  private progressBar: HTMLElement;
  private statusText: HTMLElement;
  private errorText: HTMLElement;

  private phases: LoadingPhase[] = [];
  private currentPhaseIndex = 0;
  private phaseProgress = 0;
  private totalWeight = 0;

  constructor() {
    this.container = document.getElementById("loading-screen")!;
    this.progressBar = document.getElementById("loading-progress-bar")!;
    this.statusText = document.getElementById("loading-status")!;
    this.errorText = document.getElementById("loading-error")!;
  }

  /**
   * Define loading phases with relative weights
   */
  setPhases(phases: LoadingPhase[]): void {
    this.phases = phases;
    this.totalWeight = phases.reduce((sum, p) => sum + p.weight, 0);
    this.currentPhaseIndex = 0;
    this.phaseProgress = 0;
  }

  /**
   * Start a new phase
   */
  startPhase(phaseName: string): void {
    const index = this.phases.findIndex((p) => p.name === phaseName);
    if (index !== -1) {
      this.currentPhaseIndex = index;
      this.phaseProgress = 0;
    }
    this.setStatus(phaseName);
    this.updateProgress();
  }

  /**
   * Update progress within current phase (0-1)
   */
  setPhaseProgress(progress: number): void {
    this.phaseProgress = Math.max(0, Math.min(1, progress));
    this.updateProgress();
  }

  /**
   * Set status text
   */
  setStatus(text: string): void {
    this.statusText.textContent = text;
  }

  /**
   * Show error message
   */
  showError(message: string): void {
    this.errorText.textContent = message;
    this.errorText.classList.add("visible");
    this.setStatus("Loading failed");
  }

  /**
   * Hide the loading screen with fade animation
   */
  hide(): void {
    this.container.classList.add("hidden");
  }

  /**
   * Show the loading screen
   */
  show(): void {
    this.container.classList.remove("hidden");
    this.errorText.classList.remove("visible");
    this.setProgress(0);
    this.setStatus("Initializing...");
  }

  /**
   * Set progress directly (0-100)
   */
  setProgress(percent: number): void {
    this.progressBar.style.width = `${Math.max(0, Math.min(100, percent))}%`;
  }

  /**
   * Calculate and update overall progress based on phases
   */
  private updateProgress(): void {
    if (this.phases.length === 0) return;

    // Sum completed phases
    let completedWeight = 0;
    for (let i = 0; i < this.currentPhaseIndex; i++) {
      completedWeight += this.phases[i].weight;
    }

    // Add current phase progress
    const currentPhase = this.phases[this.currentPhaseIndex];
    if (currentPhase) {
      completedWeight += currentPhase.weight * this.phaseProgress;
    }

    const percent = (completedWeight / this.totalWeight) * 100;
    this.setProgress(percent);
  }

  /**
   * Complete loading and hide
   */
  complete(): void {
    this.setProgress(100);
    this.setStatus("Complete!");
    // Small delay before hiding for visual feedback
    setTimeout(() => this.hide(), 300);
  }
}
