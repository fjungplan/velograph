import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { LayoutCalculator } from '../utils/layoutCalculator';
import { validateGraphData } from '../utils/graphUtils';
import { VISUALIZATION } from '../constants/visualization';
import './TimelineGraph.css';

export default function TimelineGraph({ data }) {
  const svgRef = useRef(null);
  const containerRef = useRef(null);
  
  useEffect(() => {
    if (!data || !data.nodes || !data.links) return;
    
      try {
        validateGraphData(data);
        renderGraph(data);
      } catch (error) {
        console.error('Graph render error:', error);
      }
  }, [data]);
  
  const renderGraph = (graphData) => {
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    // Calculate layout
    const calculator = new LayoutCalculator(graphData, width, height);
    const layout = calculator.calculateLayout();
    
    // Clear previous render
    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove();
    
    // Set dimensions
    svg
      .attr('width', width)
      .attr('height', height);
    
    // Create main group
    const g = svg.append('g');
    
    // Render links first (so nodes appear on top)
    renderLinks(g, layout.links);
    
    // Render nodes
    renderNodes(g, layout.nodes);
    
    // Add zoom
    const zoom = d3.zoom()
      .scaleExtent([VISUALIZATION.ZOOM_MIN, VISUALIZATION.ZOOM_MAX])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });
    
    svg.call(zoom);
  };
  
  const renderLinks = (g, links) => {
    g.append('g')
      .attr('class', 'links')
      .selectAll('path')
      .data(links)
      .join('path')
        .attr('d', d => d.path)
        .attr('fill', 'none')
        .attr('stroke', d => 
          d.type === 'SPIRITUAL_SUCCESSION' 
            ? VISUALIZATION.LINK_COLOR_SPIRITUAL 
            : VISUALIZATION.LINK_COLOR_LEGAL
        )
        .attr('stroke-width', VISUALIZATION.LINK_STROKE_WIDTH)
        .attr('stroke-dasharray', d => 
          d.type === 'SPIRITUAL_SUCCESSION' ? '5,5' : '0'
        );
  };
  
  const renderNodes = (g, nodes) => {
    const nodeGroups = g.append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(nodes)
      .join('g')
        .attr('transform', d => `translate(${d.x},${d.y})`);
    
    // For now, render as simple rectangles
    nodeGroups.append('rect')
      .attr('width', d => d.width)
      .attr('height', d => d.height)
      .attr('fill', '#4A90E2')
      .attr('stroke', '#333')
      .attr('stroke-width', 1)
      .attr('rx', 4);
    
    // Add team name
    nodeGroups.append('text')
      .attr('x', d => d.width / 2)
      .attr('y', d => d.height / 2)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('fill', 'white')
      .attr('font-size', '12px')
      .text(d => d.eras[0]?.name || 'Unknown');
  };

  return (
    <div 
      ref={containerRef} 
      className="timeline-graph-container"
    >
      <svg ref={svgRef}></svg>
    </div>
  );
}
