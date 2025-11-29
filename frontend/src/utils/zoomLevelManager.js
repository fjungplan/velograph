export const ZOOM_LEVELS = {
  OVERVIEW: { min: 0.5, max: 1.2, name: 'Overview' },
  DETAIL: { min: 1.2, max: 5, name: 'Detail' }
};

export class ZoomLevelManager {
  constructor(onLevelChange) {
    this.currentLevel = 'OVERVIEW';
    this.currentScale = 1;
    this.onLevelChange = onLevelChange;
  }
  
  updateScale(scale) {
    this.currentScale = scale;
    const newLevel = this.determineLevel(scale);
    
    if (newLevel !== this.currentLevel) {
      this.currentLevel = newLevel;
      this.onLevelChange(newLevel, scale);
    }
  }
  
  determineLevel(scale) {
    if (scale < ZOOM_LEVELS.DETAIL.min) {
      return 'OVERVIEW';
    }
    return 'DETAIL';
  }
  
  shouldShowDetail() {
    return this.currentLevel === 'DETAIL';
  }
}
