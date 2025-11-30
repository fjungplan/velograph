import { describe, it, expect } from 'vitest';
import * as d3 from 'd3';
import { OptimizedRenderer } from '../../src/utils/optimizedRenderer';

describe('OptimizedRenderer', () => {
  it('queues and processes renders', async () => {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    document.body.appendChild(svg);
    const renderer = new OptimizedRenderer(svg, { startTiming: () => 0, endTiming: () => {} });
    let ran = false;
    renderer.queueRender(() => {
      ran = true;
    });
    await new Promise((r) => setTimeout(r, 16));
    expect(ran).toBe(true);
  });

  it('toggles LOD display of text', () => {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    document.body.appendChild(svg);
    const g = d3.select(svg).append('g');
    const nodeG = g.append('g').attr('class', 'node');
    nodeG.append('rect');
    nodeG.append('text').text('Label');

    const renderer = new OptimizedRenderer(svg, { startTiming: () => 0, endTiming: () => {} });
    const nodes = [{ eras: [{ sponsors: [] }] }];
    const links = [];
    renderer.renderWithLOD(nodes, links, 0.5);
    // Text should be hidden in low detail
    expect(g.selectAll('.node text').style('display')).toBe('none');

    renderer.renderWithLOD(nodes, links, 2);
    // Text should be visible in high detail (not 'none')
    expect(g.selectAll('.node text').style('display')).not.toBe('none');
  });
});
