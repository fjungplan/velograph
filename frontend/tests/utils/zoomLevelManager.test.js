import { describe, it, expect, vi } from 'vitest';
import { ZoomLevelManager, ZOOM_LEVELS } from '../../src/utils/zoomLevelManager';

describe('ZoomLevelManager', () => {
  describe('initialization', () => {
    it('should start at OVERVIEW level', () => {
      const manager = new ZoomLevelManager(() => {});
      expect(manager.currentLevel).toBe('OVERVIEW');
      expect(manager.currentScale).toBe(1);
    });
  });

  describe('updateScale', () => {
    it('should stay at OVERVIEW for scales below detail threshold', () => {
      const callback = vi.fn();
      const manager = new ZoomLevelManager(callback);
      
      manager.updateScale(0.8);
      
      expect(manager.currentLevel).toBe('OVERVIEW');
      expect(manager.currentScale).toBe(0.8);
      expect(callback).not.toHaveBeenCalled(); // No level change
    });

    it('should transition to DETAIL at threshold', () => {
      const callback = vi.fn();
      const manager = new ZoomLevelManager(callback);
      
      manager.updateScale(1.5);
      
      expect(manager.currentLevel).toBe('DETAIL');
      expect(manager.currentScale).toBe(1.5);
      expect(callback).toHaveBeenCalledWith('DETAIL', 1.5);
    });

    it('should transition back to OVERVIEW', () => {
      const callback = vi.fn();
      const manager = new ZoomLevelManager(callback);
      
      // Go to detail
      manager.updateScale(1.5);
      callback.mockClear();
      
      // Go back to overview
      manager.updateScale(1.0);
      
      expect(manager.currentLevel).toBe('OVERVIEW');
      expect(callback).toHaveBeenCalledWith('OVERVIEW', 1.0);
    });

    it('should not trigger callback if level stays the same', () => {
      const callback = vi.fn();
      const manager = new ZoomLevelManager(callback);
      
      manager.updateScale(0.8);
      callback.mockClear();
      manager.updateScale(1.0);
      
      expect(callback).not.toHaveBeenCalled();
    });

    it('should handle exactly at threshold', () => {
      const callback = vi.fn();
      const manager = new ZoomLevelManager(callback);
      
      manager.updateScale(ZOOM_LEVELS.DETAIL.min);
      
      expect(manager.currentLevel).toBe('DETAIL');
      expect(callback).toHaveBeenCalledWith('DETAIL', ZOOM_LEVELS.DETAIL.min);
    });
  });

  describe('determineLevel', () => {
    it('should return OVERVIEW for low scales', () => {
      const manager = new ZoomLevelManager(() => {});
      expect(manager.determineLevel(0.5)).toBe('OVERVIEW');
      expect(manager.determineLevel(1.0)).toBe('OVERVIEW');
      expect(manager.determineLevel(1.19)).toBe('OVERVIEW');
    });

    it('should return DETAIL for high scales', () => {
      const manager = new ZoomLevelManager(() => {});
      expect(manager.determineLevel(1.2)).toBe('DETAIL');
      expect(manager.determineLevel(2.0)).toBe('DETAIL');
      expect(manager.determineLevel(5.0)).toBe('DETAIL');
    });
  });

  describe('shouldShowDetail', () => {
    it('should return false at overview level', () => {
      const manager = new ZoomLevelManager(() => {});
      expect(manager.shouldShowDetail()).toBe(false);
    });

    it('should return true at detail level', () => {
      const manager = new ZoomLevelManager(() => {});
      manager.updateScale(1.5);
      expect(manager.shouldShowDetail()).toBe(true);
    });
  });
});
