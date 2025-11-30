export class PerformanceMonitor {
  constructor() {
    this.metrics = {
      renderTime: [],
      layoutTime: [],
      nodeCount: 0,
      linkCount: 0,
    };
  }

  startTiming(_label) {
    return performance.now();
  }

  endTiming(label, startTime) {
    const duration = performance.now() - startTime;

    if (this.metrics[`${label}Time`]) {
      this.metrics[`${label}Time`].push(duration);
      if (this.metrics[`${label}Time`].length > 10) {
        this.metrics[`${label}Time`].shift();
      }
    }

    if (duration > 100) {
      // eslint-disable-next-line no-console
      console.warn(`${label} took ${duration.toFixed(2)}ms`);
    }
  }

  getAverageTime(label) {
    const times = this.metrics[`${label}Time`];
    if (!times || times.length === 0) return 0;
    return times.reduce((a, b) => a + b, 0) / times.length;
  }

  logMetrics() {
    // eslint-disable-next-line no-console
    console.log('Performance Metrics:', {
      avgRenderTime: this.getAverageTime('render').toFixed(2) + 'ms',
      avgLayoutTime: this.getAverageTime('layout').toFixed(2) + 'ms',
      nodeCount: this.metrics.nodeCount,
      linkCount: this.metrics.linkCount,
    });
  }
}
