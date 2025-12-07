import { VISUALIZATION } from '../constants/visualization';

/**
 * Calculate positions for all nodes using Sankey-like layout
 */
export class LayoutCalculator {
  constructor(graphData, width, height, yearRange = null) {
    this.nodes = graphData.nodes;
    this.links = graphData.links;
    this.width = width;
    this.height = height;
    
    this.yearRange = yearRange || this.calculateYearRange();
    this.xScale = this.createXScale();
  }
  
  calculateYearRange() {
    const allYears = [];
    
    // Get years from eras
    this.nodes.forEach(node => {
      node.eras.forEach(era => {
        allYears.push(era.year);
      });
      // Also include founding and dissolution years
      allYears.push(node.founding_year);
      if (node.dissolution_year) {
        allYears.push(node.dissolution_year);
      }
    });
    
    // Include current year so active teams extend to today
    const currentYear = new Date().getFullYear();
    allYears.push(currentYear);

    // Clamp overall range to a sensible viewport (requested 1900–2040)
    const minYear = Math.min(1900, ...allYears);
    const maxYear = Math.max(2040, ...allYears);
    
    // Add +1 year to show the full span of the final year
    return {
      min: minYear,
      max: maxYear + 1
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
      links: linkPaths,
      yearRange: this.yearRange,
      xScale: this.xScale
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
    // Width based on the shared x-scale so duration matches the rendered horizontal spacing
    const endYear = node.dissolution_year ?? this.yearRange.max;
    const scaledWidth = this.xScale(endYear) - this.xScale(node.founding_year);

    return Math.max(
      VISUALIZATION.MIN_NODE_WIDTH,
      scaledWidth
    );
  }
  
  assignYPositions(nodes) {
    // Tier-based layout with collision detection
    const tiers = this.groupNodesByTier(nodes);
    const tierHeight = this.height / (tiers.length + 1);
    
    let positioned = [];
    const rows = []; // Track occupied space for each tier
    
    tiers.forEach((tierNodes, tierIndex) => {
      rows[tierIndex] = []; // Initialize row tracking for this tier
      const baseY = (tierIndex + 1) * tierHeight;
      
      // Sort nodes by X position to process left to right
      const sortedNodes = tierNodes.sort((a, b) => a.x - b.x);
      
      sortedNodes.forEach((node) => {
        let yOffset = 0;
        let rowIndex = 0;
        let hasCollision = true;
        
        // Find first available row (vertically offset) that doesn't collide
        while (hasCollision) {
          hasCollision = false;
          const candidateY = baseY + (rowIndex * (VISUALIZATION.NODE_HEIGHT + 10));
          
          // Check collision with all nodes already positioned in this tier group
          for (const placed of rows[tierIndex]) {
            const xOverlap = !(node.x + node.width < placed.x || node.x > placed.x + placed.width);
            const yClose = Math.abs(candidateY - placed.y) < (VISUALIZATION.NODE_HEIGHT + 15);
            
            if (xOverlap && yClose) {
              hasCollision = true;
              rowIndex++;
              break;
            }
          }
        }
        
        const finalY = baseY + (rowIndex * (VISUALIZATION.NODE_HEIGHT + 10));
        const positionedNode = {
          ...node,
          y: finalY,
          height: VISUALIZATION.NODE_HEIGHT
        };
        
        rows[tierIndex].push(positionedNode);
        positioned.push(positionedNode);
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
