import { describe, it, expect } from 'vitest';
import { LayoutCalculator } from '../../src/utils/layoutCalculator';
import { VISUALIZATION } from '../../src/constants/visualization';

describe('LayoutCalculator', () => {
  const createMockGraphData = () => ({
    nodes: [
      {
        id: 'node1',
        founding_year: 2010,
        dissolution_year: 2015,
        eras: [
          { year: 2010, name: 'Team A', tier: 1 },
          { year: 2011, name: 'Team A', tier: 1 }
        ]
      },
      {
        id: 'node2',
        founding_year: 2012,
        dissolution_year: null,
        eras: [
          { year: 2012, name: 'Team B', tier: 2 },
          { year: 2013, name: 'Team B', tier: 2 }
        ]
      },
      {
        id: 'node3',
        founding_year: 2014,
        dissolution_year: 2018,
        eras: [
          { year: 2014, name: 'Team C', tier: 1 }
        ]
      }
    ],
    links: [
      {
        source: 'node1',
        target: 'node2',
        type: 'LEGAL_TRANSFER',
        year: 2012
      },
      {
        source: 'node2',
        target: 'node3',
        type: 'SPIRITUAL_SUCCESSION',
        year: 2014
      }
    ]
  });

  describe('calculateYearRange', () => {
    it('should calculate correct year range from nodes', () => {
      const graphData = createMockGraphData();
      const calculator = new LayoutCalculator(graphData, 1000, 800);
      const yearRange = calculator.calculateYearRange();

      expect(yearRange.min).toBe(2010);
      expect(yearRange.max).toBe(2014);
    });

    it('should handle single node', () => {
      const graphData = {
        nodes: [
          {
            id: 'node1',
            founding_year: 2010,
            eras: [{ year: 2010, name: 'Team', tier: 1 }]
          }
        ],
        links: []
      };
      const calculator = new LayoutCalculator(graphData, 1000, 800);
      const yearRange = calculator.calculateYearRange();

      expect(yearRange.min).toBe(2010);
      expect(yearRange.max).toBe(2010);
    });
  });

  describe('createXScale', () => {
    it('should map years to X coordinates correctly', () => {
      const graphData = createMockGraphData();
      const calculator = new LayoutCalculator(graphData, 1000, 800);
      const xScale = calculator.xScale;

      // First year should be at padding
      expect(xScale(2010)).toBeCloseTo(50, 1);
      
      // Last year should be near width - padding
      expect(xScale(2014)).toBeCloseTo(950, 1);
      
      // Middle year should be in middle
      const midYear = 2012;
      const midX = xScale(midYear);
      expect(midX).toBeGreaterThan(50);
      expect(midX).toBeLessThan(950);
    });
  });

  describe('calculateNodeWidth', () => {
    it('should calculate width for dissolved team', () => {
      const graphData = createMockGraphData();
      const calculator = new LayoutCalculator(graphData, 1000, 800);
      const node = graphData.nodes[0]; // 2010-2015, 5 years

      const width = calculator.calculateNodeWidth(node);
      
      // Width should be based on year span
      const expectedWidth = 5 * (VISUALIZATION.YEAR_WIDTH / 10);
      expect(width).toBe(expectedWidth);
    });

    it('should calculate width for active team (no dissolution)', () => {
      const graphData = createMockGraphData();
      const calculator = new LayoutCalculator(graphData, 1000, 800);
      const node = graphData.nodes[1]; // 2012-present

      const width = calculator.calculateNodeWidth(node);
      
      // Width should be from founding to max year in data
      const expectedYearSpan = 2014 - 2012; // 2 years
      const expectedWidth = expectedYearSpan * (VISUALIZATION.YEAR_WIDTH / 10);
      expect(width).toBe(expectedWidth);
    });

    it('should respect minimum node width', () => {
      const graphData = {
        nodes: [
          {
            id: 'node1',
            founding_year: 2010,
            dissolution_year: 2010, // Same year
            eras: [{ year: 2010, name: 'Team', tier: 1 }]
          }
        ],
        links: []
      };
      const calculator = new LayoutCalculator(graphData, 1000, 800);
      const width = calculator.calculateNodeWidth(graphData.nodes[0]);

      expect(width).toBe(VISUALIZATION.MIN_NODE_WIDTH);
    });
  });

  describe('assignYPositions', () => {
    it('should distribute nodes vertically by tier', () => {
      const graphData = createMockGraphData();
      const calculator = new LayoutCalculator(graphData, 1000, 800);
      const nodesWithX = calculator.assignXPositions();
      const positioned = calculator.assignYPositions(nodesWithX);

      // Tier 1 nodes should have same Y
      const tier1Nodes = positioned.filter(n => 
        n.eras.some(e => e.tier === 1)
      );
      expect(tier1Nodes.length).toBe(2);
      expect(tier1Nodes[0].y).toBe(tier1Nodes[1].y);

      // All nodes should have height
      positioned.forEach(node => {
        expect(node.height).toBe(VISUALIZATION.NODE_HEIGHT);
      });
    });

    it('should handle nodes with no tier (default to 2)', () => {
      const graphData = {
        nodes: [
          {
            id: 'node1',
            founding_year: 2010,
            eras: [{ year: 2010, name: 'Team', tier: null }]
          }
        ],
        links: []
      };
      const calculator = new LayoutCalculator(graphData, 1000, 800);
      const nodesWithX = calculator.assignXPositions();
      const positioned = calculator.assignYPositions(nodesWithX);

      expect(positioned[0].y).toBeGreaterThan(0);
    });
  });

  describe('calculateLinkPaths', () => {
    it('should generate valid SVG paths for all links', () => {
      const graphData = createMockGraphData();
      const calculator = new LayoutCalculator(graphData, 1000, 800);
      const layout = calculator.calculateLayout();

      expect(layout.links.length).toBe(2);
      
      layout.links.forEach(link => {
        // Should have path property
        expect(link.path).toBeDefined();
        expect(typeof link.path).toBe('string');
        
        // Should start with M (move to)
        expect(link.path).toMatch(/^M /);
        
        // Should contain C (cubic bezier)
        expect(link.path).toContain('C ');
        
        // Should have source/target coordinates
        expect(link.sourceX).toBeDefined();
        expect(link.sourceY).toBeDefined();
        expect(link.targetX).toBeDefined();
        expect(link.targetY).toBeDefined();
      });
    });

    it('should filter out links with missing nodes', () => {
      const graphData = {
        nodes: [
          {
            id: 'node1',
            founding_year: 2010,
            eras: [{ year: 2010, name: 'Team A', tier: 1 }]
          }
        ],
        links: [
          {
            source: 'node1',
            target: 'nonexistent',
            type: 'LEGAL_TRANSFER',
            year: 2012
          }
        ]
      };
      const calculator = new LayoutCalculator(graphData, 1000, 800);
      const layout = calculator.calculateLayout();

      // Invalid link should be filtered out
      expect(layout.links.length).toBe(0);
    });
  });

  describe('calculateLayout (integration)', () => {
    it('should return complete layout with positioned nodes and links', () => {
      const graphData = createMockGraphData();
      const calculator = new LayoutCalculator(graphData, 1000, 800);
      const layout = calculator.calculateLayout();

      // Should have all nodes
      expect(layout.nodes.length).toBe(3);

      // All nodes should have position and size
      layout.nodes.forEach(node => {
        expect(node.x).toBeDefined();
        expect(node.y).toBeDefined();
        expect(node.width).toBeDefined();
        expect(node.height).toBeDefined();
        expect(node.x).toBeGreaterThanOrEqual(0);
        expect(node.y).toBeGreaterThanOrEqual(0);
      });

      // Should have all valid links
      expect(layout.links.length).toBe(2);

      // All links should have paths
      layout.links.forEach(link => {
        expect(link.path).toBeDefined();
        expect(link.type).toBeDefined();
      });
    });

    it('should handle empty nodes array', () => {
      const graphData = { nodes: [], links: [] };
      const calculator = new LayoutCalculator(graphData, 1000, 800);

      // Should not throw
      expect(() => calculator.calculateYearRange()).toThrow();
    });

    it('should handle nodes with no links', () => {
      const graphData = {
        nodes: [
          {
            id: 'node1',
            founding_year: 2010,
            eras: [{ year: 2010, name: 'Team', tier: 1 }]
          }
        ],
        links: []
      };
      const calculator = new LayoutCalculator(graphData, 1000, 800);
      const layout = calculator.calculateLayout();

      expect(layout.nodes.length).toBe(1);
      expect(layout.links.length).toBe(0);
    });
  });
});
