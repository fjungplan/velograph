import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { LayoutCalculator } from '../utils/layoutCalculator';
import { validateGraphData } from '../utils/graphUtils';
import { VISUALIZATION } from '../constants/visualization';
import './TimelineGraph.css';
import { JerseyRenderer } from '../utils/jerseyRenderer';

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
    renderNodes(g, layout.nodes, svg);
    
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
  const renderNodes = (g, nodes, svg) => {
    // Create shadow filter once
    JerseyRenderer.createShadowFilter(svg);

    const nodeGroups = g.append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(nodes)
      .join('g')
        .attr('class', 'node')
        .attr('transform', d => `translate(${d.x},${d.y})`)
        .style('cursor', 'pointer')
        .on('click', (event, d) => handleNodeClick(d))
        .on('mouseenter', (event, d) => handleNodeHover(event, d))
        .on('mouseleave', handleNodeHoverEnd);

    // Render each node with jersey styling
    nodeGroups.each(function(d) {
      const group = d3.select(this);
      JerseyRenderer.renderNode(group, d, svg);
      JerseyRenderer.addNodeLabel(group, d);
    });
  };

  const handleNodeClick = (node) => {
    console.log('Clicked node:', node);
    // TODO: Navigate to team detail page
  };

  const handleNodeHover = (event, node) => {
    d3.select(event.currentTarget)
      .select('rect')
      .transition()
      .duration(200)
      .attr('stroke-width', 3)
      .attr('stroke', '#FFD700'); // Gold highlight
  };

  const handleNodeHoverEnd = (event) => {
    d3.select(event.currentTarget)
      .select('rect')
      .transition()
      .duration(200)
      .attr('stroke-width', 2)
      .attr('stroke', '#333');
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
