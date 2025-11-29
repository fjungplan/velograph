import * as d3 from 'd3';

export class JerseyRenderer {
  static createGradientDefinition(svg, node) {
    const gradientId = `gradient-${node.id}`;
    const latestEra = node.eras[node.eras.length - 1];
    const sponsors = latestEra.sponsors || [];
    if (sponsors.length === 0) {
      return null;
    }
    const defs = svg.select('defs').empty() ? svg.append('defs') : svg.select('defs');
    const gradient = defs.append('linearGradient')
      .attr('id', gradientId)
      .attr('x1', '0%')
      .attr('y1', '0%')
      .attr('x2', '0%')
      .attr('y2', '100%');
    let cumulativePercent = 0;
    sponsors.forEach((sponsor) => {
      const startPercent = cumulativePercent;
      const endPercent = cumulativePercent + sponsor.prominence;
      gradient.append('stop')
        .attr('offset', `${startPercent}%`)
        .attr('stop-color', sponsor.color);
      gradient.append('stop')
        .attr('offset', `${endPercent}%`)
        .attr('stop-color', sponsor.color);
      cumulativePercent = endPercent;
    });
    return gradientId;
  }

  static renderNode(nodeGroup, node, svg) {
    const gradientId = this.createGradientDefinition(svg, node);
    const rect = nodeGroup.append('rect')
      .attr('width', node.width)
      .attr('height', node.height)
      .attr('rx', 6)
      .attr('ry', 6)
      .attr('stroke', '#333')
      .attr('stroke-width', 2);
    if (gradientId) {
      rect.attr('fill', `url(#${gradientId})`);
    } else {
      rect.attr('fill', '#4A90E2');
    }
    rect.attr('filter', 'url(#drop-shadow)');
    return rect;
  }

  static createShadowFilter(svg) {
    const defs = svg.select('defs').empty() ? svg.append('defs') : svg.select('defs');
    const filter = defs.append('filter')
      .attr('id', 'drop-shadow')
      .attr('height', '130%');
    filter.append('feGaussianBlur')
      .attr('in', 'SourceAlpha')
      .attr('stdDeviation', 2);
    filter.append('feOffset')
      .attr('dx', 2)
      .attr('dy', 2)
      .attr('result', 'offsetblur');
    const feMerge = filter.append('feMerge');
    feMerge.append('feMergeNode');
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic');
  }

  static addNodeLabel(nodeGroup, node) {
    const latestEra = node.eras[node.eras.length - 1];
    const name = latestEra.name || 'Unknown Team';
    const displayName = name.length > 25 ? name.substring(0, 22) + '...' : name;
    nodeGroup.append('text')
      .attr('x', node.width / 2)
      .attr('y', node.height / 2)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('fill', 'white')
      .attr('font-size', '11px')
      .attr('font-weight', 'bold')
      .attr('style', 'text-shadow: 1px 1px 2px rgba(0,0,0,0.8)')
      .text(displayName);
    const yearRange = node.dissolution_year
      ? `${node.founding_year}-${node.dissolution_year}`
      : `${node.founding_year}-`;
    nodeGroup.append('text')
      .attr('x', node.width / 2)
      .attr('y', node.height / 2 + 14)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('fill', 'white')
      .attr('font-size', '9px')
      .attr('style', 'text-shadow: 1px 1px 2px rgba(0,0,0,0.8)')
      .text(yearRange);
  }
}
