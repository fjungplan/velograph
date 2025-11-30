import { describe, it, expect, vi } from 'vitest';
import { PerformanceMonitor } from '../../src/utils/performanceMonitor';

describe('PerformanceMonitor', () => {
  it('tracks timings and averages', () => {
    const pm = new PerformanceMonitor();
    const start = pm.startTiming('render');
    // simulate ~5ms
    const nowSpy = vi.spyOn(performance, 'now');
    let t = start;
    nowSpy.mockImplementation(() => {
      t += 5;
      return t;
    });
    pm.endTiming('render', start);
    nowSpy.mockRestore();
    expect(pm.metrics.renderTime.length).toBe(1);
    expect(pm.getAverageTime('render')).toBeGreaterThan(0);
  });

  it('logs metrics without throwing', () => {
    const pm = new PerformanceMonitor();
    const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
    pm.logMetrics();
    expect(logSpy).toHaveBeenCalled();
    logSpy.mockRestore();
  });
});
