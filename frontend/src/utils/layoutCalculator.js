import { VISUALIZATION } from '../constants/visualization';

/**
 * Calculate positions for all nodes using Sankey-like layout
 */
export class LayoutCalculator {
  constructor(graphData, width, height) {
    this.nodes = graphData.nodes;
    this.links = graphData.links;
    this.width = width;
    this.height = height;
    
    this.yearRange = this.calculateYearRange();
    this.xScale = this.createXScale();
  }
  
  calculateYearRange() {
    const allYears = this.nodes.flatMap(node => 
      node.eras.map(era => era.year)
    );
    return {
      min: Math.min(...allYears),
      max: Math.max(...allYears)
    };
  }
  
  createXScale() {
    // Map years to X coordinates
    const padding = 50;
    const { min, max } = this.yearRange;
    
    return (year) => {
      const range = max - min;
      const position = (year - min) / range;
      return padding + (position * (this.width - 2 * padding));
    };
  }
  
  calculateLayout() {
    // Step 1: Assign X positions based on founding year
    const nodesWithX = this.assignXPositions();
    
    // Step 2: Assign Y positions to minimize crossings
    const nodesWithXY = this.assignYPositions(nodesWithX);
    
    // Step 3: Calculate link paths
    const linkPaths = this.calculateLinkPaths(nodesWithXY);
    
    return {
      nodes: nodesWithXY,
      links: linkPaths
    };
  }
  
  assignXPositions() {
    return this.nodes.map(node => ({
      ...node,
      x: this.xScale(node.founding_year),
      width: this.calculateNodeWidth(node)
    }));
  }
  
  calculateNodeWidth(node) {
    // Width based on years active
    const yearSpan = node.dissolution_year 
      ? node.dissolution_year - node.founding_year
      : this.yearRange.max - node.founding_year;
    
    return Math.max(
      VISUALIZATION.MIN_NODE_WIDTH,
      yearSpan * (VISUALIZATION.YEAR_WIDTH / 10)
    );
  }
  
  assignYPositions(nodes) {
    // Simple tier-based layout for now
    // Will improve with crossing minimization later
    const tiers = this.groupNodesByTier(nodes);
    const tierHeight = this.height / (tiers.length + 1);
    
    let positioned = [];
    tiers.forEach((tierNodes, tierIndex) => {
      tierNodes.forEach((node, nodeIndex) => {
        positioned.push({
          ...node,
          y: (tierIndex + 1) * tierHeight,
          height: VISUALIZATION.NODE_HEIGHT
        });
      });
    });
    
    return positioned;
  }
  
  groupNodesByTier(nodes) {
    // Group nodes by their most common tier level
    const tierMap = new Map();
    
    nodes.forEach(node => {
      const tiers = node.eras.map(e => e.tier).filter(t => t);
      const avgTier = tiers.length > 0 
        ? Math.round(tiers.reduce((a, b) => a + b) / tiers.length)
        : 2; // Default to ProTeam
      
      if (!tierMap.has(avgTier)) {
        tierMap.set(avgTier, []);
      }
      tierMap.get(avgTier).push(node);
    });
    
    // Sort tiers (1 = WorldTour at top)
    return Array.from(tierMap.entries())
      .sort(([a], [b]) => a - b)
      .map(([_, nodes]) => nodes);
  }
  
  calculateLinkPaths(nodes) {
    // Create node position lookup
    const nodeMap = new Map(nodes.map(n => [n.id, n]));
    
    return this.links.map(link => {
      const source = nodeMap.get(link.source);
      const target = nodeMap.get(link.target);
      
      if (!source || !target) {
        console.warn('Link references missing node:', link);
        return null;
      }
      
      return {
        ...link,
        sourceX: source.x + source.width,
        sourceY: source.y + source.height / 2,
        targetX: target.x,
        targetY: target.y + target.height / 2,
        path: this.generateLinkPath(source, target)
      };
    }).filter(Boolean);
  }
  
  generateLinkPath(source, target) {
    const sx = source.x + source.width;
    const sy = source.y + source.height / 2;
    const tx = target.x;
    const ty = target.y + target.height / 2;
    
    // Cubic Bezier curve
    const dx = tx - sx;
    const controlPointOffset = Math.abs(dx) * 0.3;
    
    return `M ${sx},${sy} 
            C ${sx + controlPointOffset},${sy} 
              ${tx - controlPointOffset},${ty} 
              ${tx},${ty}`;
  }
}
