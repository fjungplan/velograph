import { describe, it, expect, beforeEach, vi } from 'vitest';
import * as d3 from 'd3';
import { JSDOM } from 'jsdom';
import { DetailRenderer } from '../../src/utils/detailRenderer';
import { ZOOM_LEVELS } from '../../src/utils/zoomLevelManager';

describe('DetailRenderer', () => {
  let svg, g;

  beforeEach(() => {
    const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>');
    global.document = dom.window.document;
    global.window = dom.window;

    const container = d3.select(document.body)
      .append('svg')
      .attr('width', 800)
      .attr('height', 600);

    svg = container;
    g = container.append('g');
  });

  describe('renderDetailedLinks', () => {
    it('should apply thicker stroke for MERGE links', () => {
      const links = [
        { type: 'MERGE', path: 'M0,0L100,100' },
        { type: 'LEGAL_TRANSFER', path: 'M100,0L200,100' }
      ];

      g.append('g')
        .attr('class', 'links')
        .selectAll('path')
        .data(links)
        .join('path')
        .attr('d', d => d.path);

      DetailRenderer.renderDetailedLinks(g, links, 2.0);

      const paths = g.selectAll('.links path').nodes();
      expect(paths).toHaveLength(2);
      
      // MERGE should have thicker line
      const mergeWidth = parseFloat(d3.select(paths[0]).attr('stroke-width'));
      const legalWidth = parseFloat(d3.select(paths[1]).attr('stroke-width'));
      expect(mergeWidth).toBeGreaterThan(legalWidth);
    });

    it('should apply lower opacity for SPIRITUAL_SUCCESSION', () => {
      const links = [
        { type: 'SPIRITUAL_SUCCESSION', path: 'M0,0L100,100' },
        { type: 'LEGAL_TRANSFER', path: 'M100,0L200,100' }
      ];

      g.append('g')
        .attr('class', 'links')
        .selectAll('path')
        .data(links)
        .join('path')
        .attr('d', d => d.path);

      DetailRenderer.renderDetailedLinks(g, links, 2.0);

      const paths = g.selectAll('.links path').nodes();
      const spiritualOpacity = parseFloat(d3.select(paths[0]).attr('opacity'));
      const legalOpacity = parseFloat(d3.select(paths[1]).attr('opacity'));
      
      expect(spiritualOpacity).toBeLessThan(legalOpacity);
      expect(spiritualOpacity).toBe(0.6);
      expect(legalOpacity).toBe(0.9);
    });

    it('should add arrowheads to links', () => {
      const links = [{ type: 'LEGAL_TRANSFER', path: 'M0,0L100,100' }];

      g.append('g')
        .attr('class', 'links')
        .selectAll('path')
        .data(links)
        .join('path')
        .attr('d', d => d.path);

      DetailRenderer.renderDetailedLinks(g, links, 2.0);

      // Check marker definition exists
      const marker = g.select('marker#arrowhead');
      expect(marker.empty()).toBe(false);
      
      // Check paths reference the marker
      const path = g.select('.links path');
      expect(path.attr('marker-end')).toBe('url(#arrowhead)');
    });
  });

  describe('addArrowheads', () => {
    it('should create defs if not present', () => {
      const links = [];
      
      DetailRenderer.addArrowheads(g, links);
      
      const defs = g.select('defs');
      expect(defs.empty()).toBe(false);
    });

    it('should reuse existing defs', () => {
      g.append('defs');
      const links = [];
      
      DetailRenderer.addArrowheads(g, links);
      
      const allDefs = g.selectAll('defs').nodes();
      expect(allDefs).toHaveLength(1);
    });

    it('should clear old markers before creating new ones', () => {
      const links = [];
      g.append('defs').append('marker').attr('id', 'old-marker');
      
      DetailRenderer.addArrowheads(g, links);
      
      const oldMarker = g.select('#old-marker');
      expect(oldMarker.empty()).toBe(true);
      
      const arrowhead = g.select('#arrowhead');
      expect(arrowhead.empty()).toBe(false);
    });
  });

  describe('renderEraTimeline', () => {
    it('should not render if scale below detail threshold', () => {
      const node = {
        width: 100,
        height: 60,
        eras: [
          { year: 2020, sponsors: [{ color: '#FF0000' }] },
          { year: 2022, sponsors: [{ color: '#00FF00' }] }
        ]
      };

      const nodeGroup = g.append('g');
      DetailRenderer.renderEraTimeline(nodeGroup, node, 1.0);

      const segments = nodeGroup.selectAll('.era-segment').nodes();
      expect(segments).toHaveLength(0);
    });

    it('should not render if only one era', () => {
      const node = {
        width: 100,
        height: 60,
        eras: [{ year: 2020, sponsors: [{ color: '#FF0000' }] }]
      };

      const nodeGroup = g.append('g');
      DetailRenderer.renderEraTimeline(nodeGroup, node, 2.0);

      const segments = nodeGroup.selectAll('.era-segment').nodes();
      expect(segments).toHaveLength(0);
    });

    it('should not render if no eras', () => {
      const node = {
        width: 100,
        height: 60,
        eras: null
      };

      const nodeGroup = g.append('g');
      DetailRenderer.renderEraTimeline(nodeGroup, node, 2.0);

      const segments = nodeGroup.selectAll('.era-segment').nodes();
      expect(segments).toHaveLength(0);
    });

    it('should render era segments at detail level', () => {
      const node = {
        width: 100,
        height: 60,
        eras: [
          { year: 2020, sponsors: [{ color: '#FF0000' }] },
          { year: 2022, sponsors: [{ color: '#00FF00' }] },
          { year: 2024, sponsors: [{ color: '#0000FF' }] }
        ]
      };

      const nodeGroup = g.append('g');
      DetailRenderer.renderEraTimeline(nodeGroup, node, 2.0);

      const segments = nodeGroup.selectAll('.era-segment').nodes();
      // Should have n-1 segments for n eras
      expect(segments).toHaveLength(2);
    });

    it('should use sponsor color for segments', () => {
      const node = {
        width: 100,
        height: 60,
        eras: [
          { year: 2020, sponsors: [{ color: '#FF0000' }] },
          { year: 2022, sponsors: [{ color: '#00FF00' }] }
        ]
      };

      const nodeGroup = g.append('g');
      DetailRenderer.renderEraTimeline(nodeGroup, node, 2.0);

      const segment = nodeGroup.select('.era-segment');
      expect(segment.attr('fill')).toBe('#FF0000');
    });

    it('should use default color if no sponsors', () => {
      const node = {
        width: 100,
        height: 60,
        eras: [
          { year: 2020, sponsors: [] },
          { year: 2022, sponsors: [] }
        ]
      };

      const nodeGroup = g.append('g');
      DetailRenderer.renderEraTimeline(nodeGroup, node, 2.0);

      const segment = nodeGroup.select('.era-segment');
      expect(segment.attr('fill')).toBe('#ccc');
    });

    it('should calculate segment widths proportional to duration', () => {
      const node = {
        width: 100,
        height: 60,
        eras: [
          { year: 2020, sponsors: [{ color: '#FF0000' }] },
          { year: 2022, sponsors: [{ color: '#00FF00' }] },
          { year: 2023, sponsors: [{ color: '#0000FF' }] }
        ]
      };

      const nodeGroup = g.append('g');
      DetailRenderer.renderEraTimeline(nodeGroup, node, 2.0);

      const segments = nodeGroup.selectAll('.era-segment').nodes();
      const width1 = parseFloat(d3.select(segments[0]).attr('width'));
      const width2 = parseFloat(d3.select(segments[1]).attr('width'));
      
      // First segment (2020-2022) should be twice as wide as second (2022-2023)
      expect(width1).toBeCloseTo(width2 * 2, 1);
    });
  });
});
