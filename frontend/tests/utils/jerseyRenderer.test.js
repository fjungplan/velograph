
import { describe, it, expect, beforeEach } from 'vitest';
import * as d3 from 'd3';
import { JerseyRenderer } from '../../src/utils/jerseyRenderer';

describe('JerseyRenderer', () => {
  let svg;
  beforeEach(() => {
    document.body.innerHTML = '';
    svg = d3.select(document.body).append('svg');
  });

  it('creates gradient for single sponsor', () => {
    const node = { id: 'n1', eras: [{ sponsors: [{ color: '#FF0000', prominence: 100 }] }] };
    const gradId = JerseyRenderer.createGradientDefinition(svg, node);
    expect(gradId).toBe('gradient-n1');
    const stops = svg.select(`#${gradId}`).selectAll('stop').nodes();
    expect(stops.length).toBe(2);
    expect(stops[0].getAttribute('stop-color')).toBe('#FF0000');
  });

  it('creates gradient for multiple sponsors', () => {
    const node = { id: 'n2', eras: [{ sponsors: [
      { color: '#FF0000', prominence: 60 },
      { color: '#00FF00', prominence: 40 }
    ] }] };
    const gradId = JerseyRenderer.createGradientDefinition(svg, node);
    expect(gradId).toBe('gradient-n2');
    const stops = svg.select(`#${gradId}`).selectAll('stop').nodes();
    expect(stops.length).toBe(4);
    expect(stops[2].getAttribute('stop-color')).toBe('#00FF00');
  });

  it('returns null for no sponsors', () => {
    const node = { id: 'n3', eras: [{ sponsors: [] }] };
    expect(JerseyRenderer.createGradientDefinition(svg, node)).toBeNull();
  });

  it('creates shadow filter', () => {
    JerseyRenderer.createShadowFilter(svg);
    expect(svg.select('filter#drop-shadow').empty()).toBe(false);
  });

  it('truncates long node label', () => {
    const group = svg.append('g');
    const node = { width: 100, height: 30, eras: [{ name: 'A very very very long team name that should be truncated' }] };
    JerseyRenderer.addNodeLabel(group, node);
    const text = group.select('text').text();
    expect(text.endsWith('...')).toBe(true);
  });

  it('formats year range', () => {
    const group = svg.append('g');
    const node = { width: 100, height: 30, founding_year: 2000, dissolution_year: 2010, eras: [{ name: 'Team' }] };
    JerseyRenderer.addNodeLabel(group, node);
    const texts = group.selectAll('text').nodes();
    expect(texts[1].textContent).toBe('2000-2010');
  });
});
