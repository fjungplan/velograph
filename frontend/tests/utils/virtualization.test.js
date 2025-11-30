import { describe, it, expect } from 'vitest';
import { ViewportManager } from '../../src/utils/virtualization';

describe('ViewportManager', () => {
  const width = 800;
  const height = 600;
  const transform = { x: 0, y: 0, k: 1 };

  it('returns nodes within viewport', () => {
    const vm = new ViewportManager(width, height);
    const nodes = [
      { id: 'in', x: 10, y: 10, width: 50, height: 30 },
      { id: 'out', x: 5000, y: 5000, width: 10, height: 10 },
    ];
    const visible = vm.getVisibleNodes(nodes, transform);
    expect(visible.map((n) => n.id)).toContain('in');
    expect(visible.map((n) => n.id)).not.toContain('out');
  });

  it('returns links that touch visible nodes', () => {
    const vm = new ViewportManager(width, height);
    const nodes = [
      { id: 'a', x: 10, y: 10, width: 50, height: 30 },
      { id: 'b', x: 10000, y: 10000, width: 50, height: 30 },
    ];
    const links = [
      { source: 'a', target: 'b' },
      { source: 'b', target: 'b' },
    ];
    const visibleNodes = vm.getVisibleNodes(nodes, transform);
    const visibleIds = new Set(visibleNodes.map((n) => n.id));
    const visibleLinks = vm.getVisibleLinks(links, visibleIds);
    expect(visibleLinks.length).toBe(1);
    expect(visibleLinks[0].source).toBe('a');
  });
});
