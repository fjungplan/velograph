import * as d3 from 'd3';
import { ZOOM_LEVELS } from './zoomLevelManager';

export class DetailRenderer {
  /**
   * Render detailed link types when zoomed in
   */
  static renderDetailedLinks(g, links, scale) {
    g.selectAll('.links path')
      .attr('stroke-width', d => {
        const baseWidth = 2;
        // Thicker lines for merges/splits
        const multiplier = (d.type === 'MERGE' || d.type === 'SPLIT') ? 1.5 : 1;
        return baseWidth * multiplier;
      })
      .attr('opacity', d => {
        // Spiritual succession more transparent
        return d.type === 'SPIRITUAL_SUCCESSION' ? 0.6 : 0.9;
      });
    
    // Arrowheads removed for Viscous Connectors
    // this.addArrowheads(g, links);
  }
  
  static addArrowheads(g, links) {
    // Deprecated for Viscous Connectors
  }
  
  /**
   * Add era timeline within node at detail level
   */
  static renderEraTimeline(nodeGroup, node, scale) {
    if (scale < ZOOM_LEVELS.DETAIL.min) return;
    
    const eras = node.eras;
    if (!eras || eras.length <= 1) return;
    
    const timelineHeight = 4;
    const y = node.height - timelineHeight - 5;
    
    // Calculate era widths
    const totalYears = eras[eras.length - 1].year - eras[0].year + 1;
    
    eras.forEach((era, index) => {
      const nextEra = eras[index + 1];
      if (!nextEra) return;
      
      const eraYears = nextEra.year - era.year;
      const width = (eraYears / totalYears) * node.width;
      const x = ((era.year - eras[0].year) / totalYears) * node.width;
      
      nodeGroup.append('rect')
        .attr('class', 'era-segment')
        .attr('x', x)
        .attr('y', y)
        .attr('width', width)
        .attr('height', timelineHeight)
        .attr('fill', era.sponsors?.[0]?.color || '#ccc')
        .attr('opacity', 0.7);
    });
  }
}
