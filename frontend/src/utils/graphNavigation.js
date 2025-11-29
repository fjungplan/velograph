import * as d3 from 'd3';

export class GraphNavigation {
  constructor(svg, width, height) {
    this.svg = svg;
    this.width = width;
    this.height = height;
  }
  
  /**
   * Focus on a specific node with animation
   */
  focusOnNode(node, duration = 750) {
    const svg = d3.select(this.svg);
    const g = svg.select('g');
    
    // Calculate transform to center node
    const scale = 2; // Zoom in to 2x
    const x = -node.x * scale + this.width / 2;
    const y = -node.y * scale + this.height / 2;
    
    const transform = d3.zoomIdentity
      .translate(x, y)
      .scale(scale);
    
    // Animate to position
    svg.transition()
      .duration(duration)
      .call(
        d3.zoom().transform,
        transform
      );
    
    // Highlight the node
    this.highlightNode(node, duration);
  }
  
  /**
   * Highlight a node temporarily
   */
  highlightNode(node, duration = 2000) {
    const svg = d3.select(this.svg);
    
    // Find the node element
    const nodeElement = svg.select(`.node[data-id="${node.id}"]`);
    
    if (nodeElement.empty()) return;
    
    // Pulse animation
    nodeElement.select('rect')
      .transition()
      .duration(300)
      .attr('stroke', '#FFD700')
      .attr('stroke-width', 4)
      .transition()
      .duration(300)
      .attr('stroke-width', 6)
      .transition()
      .duration(300)
      .attr('stroke-width', 4)
      .transition()
      .delay(duration - 900)
      .duration(300)
      .attr('stroke', '#333')
      .attr('stroke-width', 2);
  }
  
  /**
   * Show path between two nodes
   */
  highlightPath(sourceNode, targetNode, links) {
    // Find path using BFS
    const path = this.findPath(sourceNode.id, targetNode.id, links);
    
    if (!path) {
      console.warn('No path found between nodes');
      return;
    }
    
    // Highlight links in path
    const svg = d3.select(this.svg);
    path.forEach((link, index) => {
      setTimeout(() => {
        svg.select(`.links path[data-id="${link.id}"]`)
          .transition()
          .duration(300)
          .attr('stroke', '#FFD700')
          .attr('stroke-width', 4)
          .transition()
          .delay(2000)
          .duration(300)
          .attr('stroke', d => 
            d.type === 'SPIRITUAL_SUCCESSION' ? '#999' : '#333'
          )
          .attr('stroke-width', 2);
      }, index * 200);
    });
  }
  
  findPath(sourceId, targetId, links) {
    // Build adjacency list
    const graph = new Map();
    links.forEach(link => {
      if (!graph.has(link.source)) graph.set(link.source, []);
      graph.get(link.source).push({ node: link.target, link });
    });
    
    // BFS
    const queue = [[sourceId, []]];
    const visited = new Set([sourceId]);
    
    while (queue.length > 0) {
      const [current, path] = queue.shift();
      
      if (current === targetId) {
        return path;
      }
      
      const neighbors = graph.get(current) || [];
      for (const { node, link } of neighbors) {
        if (!visited.has(node)) {
          visited.add(node);
          queue.push([node, [...path, link]]);
        }
      }
    }
    
    return null; // No path found
  }
}
