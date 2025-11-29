import { describe, it, expect, beforeEach, vi } from 'vitest';
import { GraphNavigation } from '../../src/utils/graphNavigation';
import * as d3 from 'd3';

describe('GraphNavigation', () => {
  let mockSvg;
  let navigation;
  const width = 1000;
  const height = 800;

  beforeEach(() => {
    // Create a mock SVG element
    document.body.innerHTML = '<svg><g></g></svg>';
    mockSvg = document.querySelector('svg');
    navigation = new GraphNavigation(mockSvg, width, height);
  });

  it('creates navigation instance with correct dimensions', () => {
    expect(navigation.svg).toBe(mockSvg);
    expect(navigation.width).toBe(width);
    expect(navigation.height).toBe(height);
  });

  describe('findPath', () => {
    it('finds path between connected nodes', () => {
      const links = [
        { source: '1', target: '2', id: 'link-1' },
        { source: '2', target: '3', id: 'link-2' },
        { source: '3', target: '4', id: 'link-3' }
      ];

      const path = navigation.findPath('1', '4', links);
      
      expect(path).toBeDefined();
      expect(path.length).toBe(3);
      expect(path[0].id).toBe('link-1');
      expect(path[1].id).toBe('link-2');
      expect(path[2].id).toBe('link-3');
    });

    it('returns null when no path exists', () => {
      const links = [
        { source: '1', target: '2', id: 'link-1' },
        { source: '3', target: '4', id: 'link-2' }
      ];

      const path = navigation.findPath('1', '4', links);
      
      expect(path).toBeNull();
    });

    it('returns empty path for same source and target', () => {
      const links = [
        { source: '1', target: '2', id: 'link-1' }
      ];

      const path = navigation.findPath('1', '1', links);
      
      expect(path).toEqual([]);
    });

    it('finds shortest path in graph with multiple routes', () => {
      const links = [
        { source: '1', target: '2', id: 'link-1' },
        { source: '2', target: '4', id: 'link-2' },
        { source: '1', target: '3', id: 'link-3' },
        { source: '3', target: '5', id: 'link-4' },
        { source: '5', target: '4', id: 'link-5' }
      ];

      const path = navigation.findPath('1', '4', links);
      
      // Should find shorter path: 1 -> 2 -> 4
      expect(path.length).toBe(2);
      expect(path[0].id).toBe('link-1');
      expect(path[1].id).toBe('link-2');
    });

    it('handles cyclic graphs', () => {
      const links = [
        { source: '1', target: '2', id: 'link-1' },
        { source: '2', target: '3', id: 'link-2' },
        { source: '3', target: '1', id: 'link-3' },
        { source: '3', target: '4', id: 'link-4' }
      ];

      const path = navigation.findPath('1', '4', links);
      
      expect(path).toBeDefined();
      expect(path.length).toBe(3);
    });
  });

  describe('focusOnNode', () => {
    it('calls focus without errors', () => {
      const node = { id: '1', x: 200, y: 150 };
      
      // Just verify it doesn't throw - actual D3 behavior is integration tested
      expect(() => navigation.focusOnNode(node, 0)).not.toThrow();
    });
  });

  describe('highlightNode', () => {
    it('does not error when node element not found', () => {
      const node = { id: 'nonexistent' };
      
      // Should not throw
      expect(() => navigation.highlightNode(node, 0)).not.toThrow();
    });
  });

  describe('highlightPath', () => {
    it('does not error when path not found', () => {
      const sourceNode = { id: '1' };
      const targetNode = { id: '99' };
      const links = [
        { source: '1', target: '2', id: 'link-1' }
      ];

      // Should not throw, just log warning
      expect(() => navigation.highlightPath(sourceNode, targetNode, links)).not.toThrow();
    });
  });
});
