import { VISUALIZATION } from '../constants/visualization';

/**
 * Calculate positions for all nodes using Sankey-like layout
 */
export class LayoutCalculator {
  constructor(graphData, width, height, yearRange = null, stretchFactor = 1) {
    this.nodes = graphData.nodes;
    this.links = graphData.links;
    this.width = width;
    this.height = height;
    this.stretchFactor = stretchFactor;
    
    console.log('LayoutCalculator constructor:');
    console.log('  Total nodes:', this.nodes.length);
    console.log('  First 3 nodes:', this.nodes.slice(0, 3).map(n => ({
      id: n.id,
      name: n.eras?.[0]?.name,
      founding: n.founding_year,
      dissolution: n.dissolution_year,
      era_years: n.eras.map(e => e.year)
    })));
    console.log('  First node keys:', Object.keys(this.nodes[0] || {}));
    
    // Always calculate yearRange from actual node data to ensure xScale covers all nodes
    // The yearRange parameter (filterYearRange) is ignored; we use the real data
    this.yearRange = this.calculateYearRange();
    this.xScale = this.createXScale();
  }
  
  calculateYearRange() {
    const allYears = [];
    const eraYears = [];
    const foundingYears = [];
    const dissolutionYears = [];
    
    // Get years from eras
    this.nodes.forEach(node => {
      node.eras.forEach(era => {
        eraYears.push(era.year);
        allYears.push(era.year);
      });
      // Also include founding and dissolution years
      foundingYears.push(node.founding_year);
      allYears.push(node.founding_year);
      if (node.dissolution_year) {
        dissolutionYears.push(node.dissolution_year);
        allYears.push(node.dissolution_year);
      }
    });
    
    // Include current year so active teams extend to today
    const currentYear = new Date().getFullYear();
    allYears.push(currentYear);

    // Calculate range from actual data without arbitrary minimums
    const minYear = Math.min(...allYears, 1900);
    const maxYear = Math.max(...allYears);
    
    // Debug logging
    console.log('calculateYearRange: eraYears min/max:', Math.min(...eraYears), '/', Math.max(...eraYears));
    console.log('calculateYearRange: foundingYears min/max:', Math.min(...foundingYears), '/', Math.max(...foundingYears));
    console.log('calculateYearRange: dissolutionYears min/max:', Math.min(...dissolutionYears), '/', Math.max(...dissolutionYears));
    console.log('calculateYearRange: currentYear:', currentYear);
    console.log('calculateYearRange: final min/max:', minYear, '/', maxYear, 'returned range:', minYear, '-', maxYear + 1);
    
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
    const span = max - min;
    const availableWidth = this.width - 2 * padding;
    const pixelsPerYear = (availableWidth / span) * this.stretchFactor;
    
    console.log(`createXScale: this.width=${this.width}, padding=${padding}, availableWidth=${availableWidth}, stretchFactor=${this.stretchFactor}`);
    console.log(`  yearRange=${min}-${max}, span=${span}`);
    console.log(`  pixelsPerYear=${pixelsPerYear.toFixed(4)}`);
    console.log(`  Example: year 2000 should map to ${padding + ((2000 - min) / span) * availableWidth}, year 2008 should map to ${padding + ((2008 - min) / span) * availableWidth}`);
    
    return (year) => {
      const range = max - min;
      const position = (year - min) / range;
      const result = padding + (position * (this.width - 2 * padding) * this.stretchFactor);
      // Only log for key years to avoid spam
      if ([1900, 2000, 2007, 2008, 2025, 2026, this.yearRange.max - 1].includes(year)) {
        console.log(`  xScale(${year}) = ${result.toFixed(2)} [position=${position.toFixed(4)}, effective_width=${this.width - 2 * padding}]`);
      }
      return result;
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
    return this.nodes.map(node => {
      console.log(`assignXPositions - ${node.eras?.[0]?.name}: dissolution_year=${node.dissolution_year}`);
      return {
        ...node,
        x: this.xScale(node.founding_year),
        width: this.calculateNodeWidth(node)
      };
    });
  }
  
  calculateNodeWidth(node) {
    // Node should span from start of founding year to END of dissolution year
    // A team founded in 2000 and dissolved in 2005 should span 2000-2005 inclusive
    // So width = xScale(2006) - xScale(2000) to reach the grid line at start of 2006
    // Active teams (no dissolution) extend to current year boundary without +1
    const startX = this.xScale(node.founding_year);
    let endX;
    const teamName = node.eras?.[0]?.name || `Node ${node.id}`;
    
    if (node.dissolution_year) {
      // Dissolved: extend to start of next year after dissolution
      endX = this.xScale(node.dissolution_year + 1);
      const scaledWidth = endX - startX;
      console.log(`${teamName}: [${node.founding_year}-${node.dissolution_year}] startX=${startX.toFixed(2)}, endX(${node.dissolution_year+1})=${endX.toFixed(2)}, width=${scaledWidth.toFixed(2)}`);
      // DON'T apply MIN_NODE_WIDTH for dissolved teams - keep accurate year boundaries
      return scaledWidth;
    } else {
      // Active: extend to end of yearRange (already includes +1 from filterYearRange)
      endX = this.xScale(this.yearRange.max);
      const scaledWidth = endX - startX;
      console.log(`${teamName}: [${node.founding_year}-active] startX=${startX.toFixed(2)}, endX(${this.yearRange.max})=${endX.toFixed(2)}, width=${scaledWidth.toFixed(2)}`);
      // For active teams, apply MIN_NODE_WIDTH if needed
      return Math.max(VISUALIZATION.MIN_NODE_WIDTH, scaledWidth);
    }
  }
  
  assignYPositions(nodes) {
    // Build lineage families: groups of nodes connected by any link
    const adjacencyMap = new Map();
    
    // Initialize adjacency map with all nodes
    nodes.forEach(node => {
      if (!adjacencyMap.has(node.id)) {
        adjacencyMap.set(node.id, new Set());
      }
    });
    
    // Add all links (both directions for undirected family grouping)
    this.links.forEach(link => {
      if (!adjacencyMap.has(link.source)) adjacencyMap.set(link.source, new Set());
      if (!adjacencyMap.has(link.target)) adjacencyMap.set(link.target, new Set());
      adjacencyMap.get(link.source).add(link.target);
      adjacencyMap.get(link.target).add(link.source);
    });
    
    // Find connected components (families) using BFS
    const visited = new Set();
    const families = [];
    
    const buildFamily = (startNodeId) => {
      const family = [];
      const queue = [startNodeId];
      const familyVisited = new Set();
      
      while (queue.length > 0) {
        const nodeId = queue.shift();
        if (familyVisited.has(nodeId)) continue;
        
        familyVisited.add(nodeId);
        family.push(nodeId);
        visited.add(nodeId);
        
        const neighbors = adjacencyMap.get(nodeId) || new Set();
        neighbors.forEach(neighborId => {
          if (!familyVisited.has(neighborId)) {
            queue.push(neighborId);
          }
        });
      }
      
      return family;
    };
    
    // Build all families
    nodes.forEach(node => {
      if (!visited.has(node.id)) {
        const family = buildFamily(node.id);
        families.push(family);
      }
    });
    
    // Sort families by earliest founding year
    families.sort((familyA, familyB) => {
      const earliestA = Math.min(...familyA.map(nodeId => 
        nodes.find(n => n.id === nodeId)?.founding_year || Infinity
      ));
      const earliestB = Math.min(...familyB.map(nodeId => 
        nodes.find(n => n.id === nodeId)?.founding_year || Infinity
      ));
      return earliestA - earliestB;
    });
    
    // NEW: Improved swimlane assignment with sharing for linear chains
    const rowHeight = VISUALIZATION.NODE_HEIGHT + 20;
    const positioned = [];
    const nodePositions = new Map();
    let swimlaneIndex = 0;
    
    families.forEach(family => {
      let swimlaneAssignments = this.assignSwimlanes(family, nodes);
      
      // OPTIMIZE: Detect and minimize connector crossings while respecting temporal constraints
      const optimized = this.optimizeCrossings(family, swimlaneAssignments, nodes);
      if (optimized) {
        swimlaneAssignments = optimized;
      }
      
      // Get all unique swimlane indices and sort them
      const uniqueLanes = [...new Set(Object.values(swimlaneAssignments))].sort((a, b) => a - b);
      
      // NEW: Group nodes by swimlane and sort within each lane by temporal position
      const nodesPerLane = new Map();
      family.forEach(nodeId => {
        const node = nodes.find(n => n.id === nodeId);
        if (node) {
          const relativeLane = swimlaneAssignments[nodeId];
          if (!nodesPerLane.has(relativeLane)) {
            nodesPerLane.set(relativeLane, []);
          }
          nodesPerLane.get(relativeLane).push(node);
        }
      });
      
      // Sort nodes within each lane by temporal position (founding_year, then dissolution_year)
      nodesPerLane.forEach((laneNodes, lane) => {
        laneNodes.sort((a, b) => {
          if (a.founding_year !== b.founding_year) {
            return a.founding_year - b.founding_year;
          }
          const aEnd = a.dissolution_year || Infinity;
          const bEnd = b.dissolution_year || Infinity;
          return aEnd - bEnd;
        });
      });
      
      // Assign Y positions based on swimlane assignments and temporal ordering
      nodesPerLane.forEach((laneNodes, relativeLane) => {
        laneNodes.forEach(node => {
          const y = 50 + (swimlaneIndex + relativeLane) * rowHeight;
          nodePositions.set(node.id, {
            ...node,
            y,
            height: VISUALIZATION.NODE_HEIGHT
          });
          positioned.push(nodePositions.get(node.id));
        });
      });
      
      // Move swimlane index past this family
      swimlaneIndex += uniqueLanes.length;
    });
    
    return positioned;
  }
  
  /**
   * Assign a node to a lane, finding the closest available lane without temporal overlap.
   * Returns the final lane assignment for the node.
   */
  assignToLaneWithSpaceMaking(nodeId, preferredLane, assignments, nodeMap, family, visited) {
    const node = nodeMap.get(nodeId);
    const nodeStart = node.founding_year;
    const nodeEnd = node.dissolution_year || Infinity;
    
    // Helper to check if a lane has overlap with our node
    const hasOverlapInLane = (lane) => {
      const nodesInLane = family.filter(id => 
        visited.has(id) && id !== nodeId && assignments[id] === lane
      );
      
      return nodesInLane.some(otherId => {
        const otherNode = nodeMap.get(otherId);
        const otherStart = otherNode.founding_year;
        const otherEnd = otherNode.dissolution_year || Infinity;
        
        // Overlap if: (start1 < end2) AND (start2 < end1)
        return nodeStart < otherEnd && otherStart < nodeEnd;
      });
    };
    
    // Try preferred lane first
    if (!hasOverlapInLane(preferredLane)) {
      return preferredLane;
    }
    
    // Preferred lane has conflict - search for nearest available lane
    // Try: preferred, preferred+1, preferred-1, preferred+2, preferred-2, etc.
    for (let offset = 1; offset <= 20; offset++) {
      const laneAbove = preferredLane + offset;
      const laneBelow = preferredLane - offset;
      
      if (!hasOverlapInLane(laneAbove)) {
        return laneAbove;
      }
      if (!hasOverlapInLane(laneBelow)) {
        return laneBelow;
      }
    }
    
    // Fallback (should rarely happen)
    return preferredLane + 21;
  }
  
  /**
   * DEPRECATED: Replaced by finding available lanes during assignment
   * Push a set of nodes down by incrementing their lane assignments,
   * and recursively push their descendants as well.
   */
  pushNodesDown(nodeIds, assignments, family, visited) {
    // Find all nodes that need to move (the conflicts + anything at or below them)
    const nodesToMove = new Set(nodeIds);
    
    // Also move any nodes in lanes equal to or greater than the max conflicting lane
    const maxConflictLane = Math.max(...nodeIds.map(id => assignments[id]));
    
    family.forEach(id => {
      if (visited.has(id) && assignments[id] >= maxConflictLane) {
        nodesToMove.add(id);
      }
    });
    
    // Increment all their lanes
    nodesToMove.forEach(id => {
      assignments[id] = (assignments[id] || 0) + 1;
    });
  }

  /**
   * Assign swimlane indices within a family using improved algorithm:
   * - Linear chains (single predecessor/successor) share the same lane if temporally compatible
   * - Splits/merges create Y-patterns with branches surrounding the common node
   * - Minimize link crossings by keeping related nodes close
   * - Priority: legal transfers over spiritual successions
   */
  assignSwimlanes(family, allNodes) {
    const assignments = {};
    const nodeMap = new Map(allNodes.map(n => [n.id, n]));
    
    // Build predecessor/successor maps with event types
    const predecessors = new Map(); // nodeId -> [{nodeId, type}]
    const successors = new Map();   // nodeId -> [{nodeId, type}]
    
    this.links.forEach(link => {
      if (family.includes(link.source) && family.includes(link.target)) {
        if (!predecessors.has(link.target)) predecessors.set(link.target, []);
        if (!successors.has(link.source)) successors.set(link.source, []);
        predecessors.get(link.target).push({ nodeId: link.source, type: link.type });
        successors.get(link.source).push({ nodeId: link.target, type: link.type });
      }
    });
    
    // Find the starting node (earliest founding year, or node with no predecessors)
    const rootNodes = family.filter(id => !predecessors.has(id) || predecessors.get(id).length === 0);
    let startNode;
    if (rootNodes.length > 0) {
      startNode = rootNodes.reduce((earliest, nodeId) => {
        const node = nodeMap.get(nodeId);
        const earliestNode = nodeMap.get(earliest);
        return (!earliestNode || node.founding_year < earliestNode.founding_year) ? nodeId : earliest;
      });
    } else {
      // Circular or complex graph - start with earliest founding year
      startNode = family.reduce((earliest, nodeId) => {
        const node = nodeMap.get(nodeId);
        const earliestNode = nodeMap.get(earliest);
        return (!earliestNode || node.founding_year < earliestNode.founding_year) ? nodeId : earliest;
      });
    }
    
    // Assign swimlanes using topological sort with crossing minimization
    const visited = new Set();
    let nextAvailableLane = 0;
    
    const assignNode = (nodeId, preferredLane) => {
      if (visited.has(nodeId)) return;
      visited.add(nodeId);
      
      // Check if this lane has temporal overlap - if so, push conflicting nodes down
      const finalLane = this.assignToLaneWithSpaceMaking(
        nodeId, preferredLane, assignments, nodeMap, family, visited
      );
      
      assignments[nodeId] = finalLane;
      
      const preds = predecessors.get(nodeId) || [];
      const succs = successors.get(nodeId) || [];
      
      // Try to use predecessor's lane to minimize crossings
      let suggestedLane = preferredLane;
      if (preds.length === 1) {
        const predId = preds[0].nodeId;
        if (assignments[predId] !== undefined) {
          suggestedLane = assignments[predId];
        }
      }
      
      // Process successors
      if (succs.length === 0) {
        // Terminal node
        return;
      } else if (succs.length === 1) {
        // Linear chain - check temporal overlap
        const successor = succs[0];
        const currentNode = nodeMap.get(nodeId);
        const successorNode = nodeMap.get(successor.nodeId);
        
        const currentEnd = currentNode.dissolution_year || Infinity;
        const successorStart = successorNode.founding_year;
        const noTemporalOverlap = currentEnd < successorStart;
        
        if (noTemporalOverlap) {
          // No overlap - share lane with predecessor if possible
          assignNode(successor.nodeId, suggestedLane);
        } else {
          // Temporal overlap - need different lane
          // Check if we can place it without increasing lane count too much
          const node = nodeMap.get(nodeId);
          const succNode = nodeMap.get(successor.nodeId);
          
          // Find the best alternative lane to minimize crossings
          // Prefer lanes closer to parent, but avoid temporal overlaps
          let bestLane = suggestedLane + 1;
          let minCrossings = Infinity;
          
          // Try a few lane options
          for (let offset = 1; offset <= 3; offset++) {
            const testLane = suggestedLane + offset;
            const crossings = this.estimateLinkCrossings(nodeId, successor.nodeId, testLane, assignments, nodeMap);
            if (crossings < minCrossings) {
              minCrossings = crossings;
              bestLane = testLane;
            }
            
            // Also try negative offset
            const negTestLane = suggestedLane - offset;
            const negCrossings = this.estimateLinkCrossings(nodeId, successor.nodeId, negTestLane, assignments, nodeMap);
            if (negCrossings < minCrossings) {
              minCrossings = negCrossings;
              bestLane = negTestLane;
            }
          }
          
          assignNode(successor.nodeId, bestLane);
        }
      } else {
        // Split: multiple successors
        const sortedSuccs = [...succs].sort((a, b) => {
          const priorityA = a.type === 'LEGAL_TRANSFER' ? 3 : a.type === 'SPIRITUAL_SUCCESSION' ? 2 : 1;
          const priorityB = b.type === 'LEGAL_TRANSFER' ? 3 : b.type === 'SPIRITUAL_SUCCESSION' ? 2 : 1;
          return priorityB - priorityA;
        });
        
        const currentNode = nodeMap.get(nodeId);
        const currentEnd = currentNode.dissolution_year || Infinity;
        
        // Check if we have a clear hierarchy (legal transfer as first, and it's unique)
        const hasLegalPriority = sortedSuccs[0].type === 'LEGAL_TRANSFER' && 
            (sortedSuccs.length === 1 || sortedSuccs[1].type !== 'LEGAL_TRANSFER');
        
        if (hasLegalPriority) {
          // Clear hierarchy: legal transfer gets priority
          const legalSucc = sortedSuccs[0];
          const legalNode = nodeMap.get(legalSucc.nodeId);
          const legalStart = legalNode.founding_year;
          const noOverlap = currentEnd < legalStart;
          
          // Legal transfer can share lane if no temporal overlap
          if (noOverlap) {
            assignNode(legalSucc.nodeId, suggestedLane);
          } else {
            // Temporal overlap - place slightly offset
            assignNode(legalSucc.nodeId, suggestedLane + 1);
          }
          
          // Place other branches in Y-pattern around the legal transfer
          const otherSuccs = sortedSuccs.slice(1);
          otherSuccs.forEach((succ, idx) => {
            const offset = Math.floor((idx + 1) / 2) * (idx % 2 === 0 ? 1 : -1);
            const branchLane = suggestedLane + offset * 2;
            assignNode(succ.nodeId, branchLane);
          });
        } else {
          // No clear priority - check temporal compatibility for ALL successors
          const compatibleSuccs = [];
          const incompatibleSuccs = [];
          
          sortedSuccs.forEach(succ => {
            const succNode = nodeMap.get(succ.nodeId);
            const succStart = succNode.founding_year;
            const noOverlap = currentEnd < succStart;
            
            if (noOverlap) {
              compatibleSuccs.push(succ);
            } else {
              incompatibleSuccs.push(succ);
            }
          });
          
          // If only one is temporally compatible, it can share the lane
          if (compatibleSuccs.length === 1 && incompatibleSuccs.length > 0) {
            assignNode(compatibleSuccs[0].nodeId, suggestedLane);
            
            // Others form Y-pattern
            incompatibleSuccs.forEach((succ, idx) => {
              const offset = Math.ceil((idx + 1) / 2) * (idx % 2 === 0 ? 1 : -1);
              const branchLane = suggestedLane + offset;
              assignNode(succ.nodeId, branchLane);
            });
          } else {
            // All compatible OR all incompatible OR multiple compatible: TRUE Y-SHAPE
            // Distribute all branches symmetrically away from parent
            sortedSuccs.forEach((succ, idx) => {
              const offset = Math.ceil((idx + 1) / 2) * (idx % 2 === 0 ? 1 : -1);
              const branchLane = suggestedLane + offset;
              assignNode(succ.nodeId, branchLane);
            });
          }
        }
      }
    };
    
    // Start assignment
    assignNode(startNode, 0);
    
    // Handle unvisited nodes
    family.forEach(nodeId => {
      if (!visited.has(nodeId)) {
        nextAvailableLane++;
        assignNode(nodeId, nextAvailableLane);
      }
    });
    
    // Normalize lanes
    const usedLanes = Object.values(assignments);
    const minLane = Math.min(...usedLanes);
    const normalized = {};
    Object.entries(assignments).forEach(([nodeId, lane]) => {
      normalized[nodeId] = lane - minLane;
    });
    
    return normalized;
  }
  
  /**
   * Estimate how many links would cross if a node is placed in a given lane
   * Returns a heuristic value (lower is better)
   */
  estimateLinkCrossings(fromNodeId, toNodeId, testLane, assignments, nodeMap) {
    // Simple heuristic: crossing distance from assigned neighbors
    let crossings = 0;
    const nodeMap2 = nodeMap;
    
    // Check distance from neighboring assigned nodes
    Object.entries(assignments).forEach(([otherId, otherLane]) => {
      if (otherId === fromNodeId || otherId === toNodeId) return;
      
      // Penalty for being far from the main line
      const laneDiff = Math.abs(testLane - otherLane);
      if (laneDiff > 2) crossings += 1;
    });
    
    return crossings;
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
    
    const links = this.links.map(link => {
      const source = nodeMap.get(link.source);
      const target = nodeMap.get(link.target);
      
      if (!source || !target) {
        console.warn('Link references missing node:', link);
        return null;
      }
      
      // Check if nodes are on the same swimlane (within 5px tolerance)
      const sameSwimlane = Math.abs(source.y - target.y) < 5;
      
      // Viscous Connectors Implementation
      const pathData = this.generateLinkPath(source, target, link, sameSwimlane);

      const result = {
        ...link,
        sourceX: source.x + source.width,
        sourceY: source.y + source.height / 2,
        targetX: target.x,
        targetY: target.y + target.height / 2,
        sameSwimlane,
        path: pathData.d,
        debugPoints: pathData.debugPoints,
        topPathD: pathData.topPathD,
        bottomPathD: pathData.bottomPathD
      };
      
      // Debug log first few links
      if (this.links.indexOf(link) < 3) {
        const sourceName = source.eras?.[source.eras.length - 1]?.name || `Node ${link.source}`;
        const targetName = target.eras?.[0]?.name || `Node ${link.target}`;
        console.log(`Link ${link.source}->${link.target} (${sourceName}->${targetName}): sourceY=${source.y}, targetY=${target.y}, sameSwimlane=${sameSwimlane}`);
      }
      
      return result;
    }).filter(Boolean);
    
    console.log('calculateLinkPaths: regenerated', links.length, 'links with updated positions');
    return links;
  }
  
  generateLinkPath(source, target, link, sameSwimlane) {
    // Restore logic: same-swimlane transitions use markers (null path)
    if (sameSwimlane && link?.type !== 'MERGE' && link?.type !== 'SPLIT') {
      return { d: null, debugPoints: null, topPathD: null, bottomPathD: null };
    }

    // Viscous Connectors Implementation
    return this.generateViscousPath(source, target, link);
  }

  generateViscousPath(source, target, link) {
    // 1. Calculate Construction Points
    const sxEnd = source.x + source.width;
    const txStart = target.x;

    // Connector edges must be vertically aligned with the date of the connection.
    // That means: BOTH the source attachment edge and target attachment edge use the SAME X.
    // With the user-confirmed "vertical diameters" rule, this also ensures every semicircle
    // segment has a vertical diameter (p1.x === p2.x).
    let eventX = null;
    if (link?.year != null && this.xScale) {
      eventX = this.xScale(link.year);
    }

    // Fallback: if year is missing, use the midpoint between the two node edges, but still
    // force both endpoints onto the same vertical line so the arc-diameter rule holds.
    if (eventX == null) {
      eventX = (sxEnd + txStart) / 2;
    }

    // Clamp the attachment X into each node’s horizontal bounds (tiny tolerance), but keep
    // the two edges aligned by choosing a single clamped value that fits BOTH nodes.
    const clamp = (v, min, max) => Math.max(min, Math.min(max, v));
    const sourceMinX = source.x - 1;
    const sourceMaxX = sxEnd + 1;
    const targetMinX = target.x - 1;
    const targetMaxX = (target.x + target.width) + 1;

    const sharedMinX = Math.max(sourceMinX, targetMinX);
    const sharedMaxX = Math.min(sourceMaxX, targetMaxX);

    // Prefer keeping the connector exactly on the event year, but guarantee it stays within
    // the shared feasible range if one exists.
    const spineX = (sharedMinX <= sharedMaxX)
      ? clamp(eventX, sharedMinX, sharedMaxX)
      : (clamp(eventX, sourceMinX, sourceMaxX) + clamp(eventX, targetMinX, targetMaxX)) / 2;
     
    const sy = source.y;
    const sh = source.height;
    const ty = target.y;
    const th = target.height;

    const st = { x: spineX, y: sy };
    const sb = { x: spineX, y: sy + sh };
    const tt = { x: spineX, y: ty };
    const tb = { x: spineX, y: ty + th };

    // Center Points (Waist)
    const midX = spineX;
    
    // Calculate vertical center of the "inner gap"
    let midY;
    if (sb.y <= tt.y) { // Source Above Target
       midY = (sb.y + tt.y) / 2;
    } else if (tb.y <= st.y) { // Source Below Target
       midY = (st.y + tb.y) / 2;
    } else { // Overlap
       midY = (sy + sh/2 + ty + th/2) / 2;
    }

    // Waist points - pinched (nearly coincident)
    // IMPORTANT: spec naming: cb = center bottom, ct = center top.
    // With SVG Y-down, that means: ct.y < cb.y.
    let pinch = 2;
    if (sb.y <= tt.y) {
      const gap = tt.y - sb.y;
      // Keep the pinch small and inside the gap, but never exactly 0.
      pinch = Math.max(0.01, Math.min(2, gap / 4));
      pinch = Math.min(pinch, Math.max(0.01, gap / 2 - 0.01));
    } else if (tb.y <= st.y) {
      const gap = st.y - tb.y;
      pinch = Math.max(0.01, Math.min(2, gap / 4));
      pinch = Math.min(pinch, Math.max(0.01, gap / 2 - 0.01));
    }

    const ct = { x: midX, y: midY - pinch }; // center top
    const cb = { x: midX, y: midY + pinch }; // center bottom
    
    // Save points to link for debug rendering
    const debugPoints = { st, sb, tt, tb, ct, cb };

    // 2. Generate Arcs Helper
    // User confirmed: every segment is a perfect semicircle with a VERTICAL diameter.
    // Therefore, consecutive endpoints must share the same X (we enforce `spineX`).
    // We choose the sweep flag based on the desired bulge direction.
    const generateVerticalSemiCircle = (p1, p2, bulge /* 'right' | 'left' */) => {
      const dy = p2.y - p1.y;
      const absDy = Math.abs(dy);
      const R = Math.max(0.01, absDy / 2);

      // Moving down vs up flips which sweep produces a right/left bulge.
      const movingDown = dy > 0;
      const sweep = (() => {
        if (movingDown) {
          return bulge === 'right' ? 1 : 0;
        }
        return bulge === 'right' ? 0 : 1;
      })();

      return `A ${R} ${R} 0 0 ${sweep} ${p2.x} ${p2.y}`;
    };

    // Construct boundary arcs
    // Top outline must be: st -> cb -> tt
    // Bottom outline must be: tb -> ct -> sb
    const a1 = generateVerticalSemiCircle(st, cb, 'right'); // D
    const a2 = generateVerticalSemiCircle(cb, tt, 'left');  // C
    const a4 = generateVerticalSemiCircle(tb, ct, 'left');  // C
    const a5 = generateVerticalSemiCircle(ct, sb, 'right'); // D

    const topPath = `${a1} ${a2}`;
    const bottomPath = `${a4} ${a5}`;
    
    // Store sub-paths for outline rendering
    const topPathD = `M ${st.x},${st.y} ${topPath}`;       // st->cb->tt
    const bottomPathD = `M ${tb.x},${tb.y} ${bottomPath}`; // tb->ct->sb

    // Full closed loop: fill strictly between the top and bottom outlines,
    // with straight vertical closures at the node attachment edges.
    const d = `M ${st.x},${st.y} ${a1} ${a2} L ${tb.x},${tb.y} ${a4} ${a5} L ${st.x},${st.y} Z`;
    
    return { d, debugPoints, topPathD, bottomPathD };
  }

  /**
   * Optimize swimlane assignments to minimize connector crossings.
   * Detects when a connector crosses intermediate nodes that exist during the connection timespan,
   * and tries swapping Y-shaped branch positions to eliminate crossings.
   */
  optimizeCrossings(family, assignments, allNodes) {
    const nodeMap = new Map(allNodes.map(n => [n.id, n]));
    
    // Build links within this family
    const familyLinks = this.links.filter(link => 
      family.includes(link.source) && family.includes(link.target)
    );
    
    // Find all split/merge points (nodes with multiple successors/predecessors)
    const predecessors = new Map();
    const successors = new Map();
    
    familyLinks.forEach(link => {
      if (!predecessors.has(link.target)) predecessors.set(link.target, []);
      if (!successors.has(link.source)) successors.set(link.source, []);
      predecessors.get(link.target).push({ nodeId: link.source, type: link.type, year: link.year });
      successors.get(link.source).push({ nodeId: link.target, type: link.type, year: link.year });
    });
    
    // Try swapping positions of Y-shaped branches to reduce crossings
    const optimized = { ...assignments };
    let improved = true;
    let iterations = 0;
    const maxIterations = 10;
    
    while (improved && iterations < maxIterations) {
      improved = false;
      iterations++;
      
      // For each node with multiple successors (splits)
      for (const [nodeId, succs] of successors.entries()) {
        if (succs.length < 2) continue;
        
        // Get successors in same relative position (Y-pattern branches)
        const branches = succs.map(s => s.nodeId);
        const parentLane = optimized[nodeId];
        
        // Try all permutations of branch positions
        const branchLanes = branches.map(b => optimized[b]);
        const uniqueBranchLanes = [...new Set(branchLanes)];
        
        if (uniqueBranchLanes.length < 2) continue; // All in same lane, nothing to swap
        
        // Count crossings for current arrangement
        const currentCrossings = this.countCrossingsForBranches(
          nodeId, branches, optimized, nodeMap, familyLinks
        );
        
        // Try swapping adjacent pairs
        for (let i = 0; i < branches.length - 1; i++) {
          for (let j = i + 1; j < branches.length; j++) {
            // Create test assignment with swapped lanes
            const testAssignments = { ...optimized };
            const temp = testAssignments[branches[i]];
            testAssignments[branches[i]] = testAssignments[branches[j]];
            testAssignments[branches[j]] = temp;
            
            // VALIDATE: Only accept swap if it doesn't create temporal overlaps
            if (this.swapCreatesOverlaps(branches[i], branches[j], optimized, testAssignments, nodeMap, family)) {
              continue; // Skip this swap
            }
            
            const testCrossings = this.countCrossingsForBranches(
              nodeId, branches, testAssignments, nodeMap, familyLinks
            );
            
            if (testCrossings < currentCrossings) {
              // Apply the swap
              optimized[branches[i]] = testAssignments[branches[i]];
              optimized[branches[j]] = testAssignments[branches[j]];
              improved = true;
            }
          }
        }
      }
      
      // For each node with multiple predecessors (merges)
      for (const [nodeId, preds] of predecessors.entries()) {
        if (preds.length < 2) continue;
        
        const branches = preds.map(p => p.nodeId);
        const targetLane = optimized[nodeId];
        
        // Count crossings for current arrangement
        const currentCrossings = this.countCrossingsForMerges(
          branches, nodeId, optimized, nodeMap, familyLinks
        );
        
        // Try swapping adjacent pairs
        for (let i = 0; i < branches.length - 1; i++) {
          for (let j = i + 1; j < branches.length; j++) {
            const testAssignments = { ...optimized };
            const temp = testAssignments[branches[i]];
            testAssignments[branches[i]] = testAssignments[branches[j]];
            testAssignments[branches[j]] = temp;
            
            // VALIDATE: Only accept swap if it doesn't create temporal overlaps
            if (this.swapCreatesOverlaps(branches[i], branches[j], optimized, testAssignments, nodeMap, family)) {
              continue; // Skip this swap
            }
            
            const testCrossings = this.countCrossingsForMerges(
              branches, nodeId, testAssignments, nodeMap, familyLinks
            );
            
            if (testCrossings < currentCrossings) {
              optimized[branches[i]] = testAssignments[branches[i]];
              optimized[branches[j]] = testAssignments[branches[j]];
              improved = true;
            }
          }
        }
      }
    }
    
    return optimized;
  }

  /**
   * Count connector crossings for split branches.
   * A crossing occurs when a connector from branch A to another node D crosses lane C,
   * where C contains a node that exists during the connection timespan.
   */
  countCrossingsForBranches(parentId, branches, assignments, nodeMap, familyLinks) {
    let crossings = 0;
    
    // For each branch, check all its outgoing connections
    branches.forEach(branchId => {
      const branchNode = nodeMap.get(branchId);
      const branchLane = assignments[branchId];
      
      // Find all links from this branch
      const outgoingLinks = familyLinks.filter(link => link.source === branchId);
      
      outgoingLinks.forEach(link => {
        const targetNode = nodeMap.get(link.target);
        const targetLane = assignments[link.target];
        
        if (targetLane === branchLane) return; // Same lane, no crossing
        
        // Connection goes from branchLane to targetLane
        const minLane = Math.min(branchLane, targetLane);
        const maxLane = Math.max(branchLane, targetLane);
        const connectionYear = link.year || targetNode.founding_year || branchNode.dissolution_year;
        
        // Check all intermediate lanes for nodes that exist during connection
        for (let lane = minLane + 1; lane < maxLane; lane++) {
          // Find nodes in this lane
          const nodesInLane = Array.from(nodeMap.values()).filter(n => assignments[n.id] === lane);
          
          nodesInLane.forEach(intermediateNode => {
            // Check if this node exists during the connection timespan
            const nodeStart = intermediateNode.founding_year;
            const nodeEnd = intermediateNode.dissolution_year || Infinity;
            
            if (connectionYear >= nodeStart && connectionYear <= nodeEnd) {
              crossings++;
            }
          });
        }
      });
    });
    
    return crossings;
  }

  /**
   * Count connector crossings for merge branches (similar to splits, but reversed).
   */
  countCrossingsForMerges(branches, targetId, assignments, nodeMap, familyLinks) {
    let crossings = 0;
    
    branches.forEach(branchId => {
      const branchNode = nodeMap.get(branchId);
      const branchLane = assignments[branchId];
      const targetLane = assignments[targetId];
      
      if (targetLane === branchLane) return;
      
      // Find the merge link
      const mergeLink = familyLinks.find(link => link.source === branchId && link.target === targetId);
      if (!mergeLink) return;
      
      const targetNode = nodeMap.get(targetId);
      const connectionYear = mergeLink.year || targetNode.founding_year || branchNode.dissolution_year;
      
      const minLane = Math.min(branchLane, targetLane);
      const maxLane = Math.max(branchLane, targetLane);
      
      for (let lane = minLane + 1; lane < maxLane; lane++) {
        const nodesInLane = Array.from(nodeMap.values()).filter(n => assignments[n.id] === lane);
        
        nodesInLane.forEach(intermediateNode => {
          const nodeStart = intermediateNode.founding_year;
          const nodeEnd = intermediateNode.dissolution_year || Infinity;
          
          if (connectionYear >= nodeStart && connectionYear <= nodeEnd) {
            crossings++;
          }
        });
      }
    });
    
    return crossings;
  }

  /**
   * Check if swapping two nodes would create temporal overlaps in their new lanes.
   * Returns true if the swap would create overlaps (meaning we should reject it).
   */
  swapCreatesOverlaps(nodeId1, nodeId2, currentAssignments, newAssignments, nodeMap, family) {
    const node1 = nodeMap.get(nodeId1);
    const node2 = nodeMap.get(nodeId2);
    
    const node1Start = node1.founding_year;
    const node1End = node1.dissolution_year || Infinity;
    const node2Start = node2.founding_year;
    const node2End = node2.dissolution_year || Infinity;
    
    const node1NewLane = newAssignments[nodeId1];
    const node2NewLane = newAssignments[nodeId2];
    
    // Check if node1 would overlap with any existing node in its new lane
    for (const otherId of family) {
      if (otherId === nodeId1 || otherId === nodeId2) continue;
      
      const otherLane = currentAssignments[otherId];
      
      // Check node1's new lane
      if (otherLane === node1NewLane) {
        const otherNode = nodeMap.get(otherId);
        const otherStart = otherNode.founding_year;
        const otherEnd = otherNode.dissolution_year || Infinity;
        
        // Check for temporal overlap: (start1 < end2) AND (start2 < end1)
        if (node1Start < otherEnd && otherStart < node1End) {
          return true; // Overlap detected
        }
      }
      
      // Check node2's new lane
      if (otherLane === node2NewLane) {
        const otherNode = nodeMap.get(otherId);
        const otherStart = otherNode.founding_year;
        const otherEnd = otherNode.dissolution_year || Infinity;
        
        // Check for temporal overlap
        if (node2Start < otherEnd && otherStart < node2End) {
          return true; // Overlap detected
        }
      }
    }
    
    return false; // No overlaps, swap is safe
  }

  /**
   * DEPRECATED: No longer needed - we now validate swaps before applying them
   * Resolve temporal overlaps in swimlanes.
   * After crossing optimization, nodes in the same lane might have temporal overlaps.
   * Move overlapping nodes to adjacent lanes.
   */
  resolveTemporalOverlaps(family, assignments, allNodes) {
    const nodeMap = new Map(allNodes.map(n => [n.id, n]));
    const resolved = { ...assignments };
    
    // Group nodes by lane
    const laneGroups = new Map();
    family.forEach(nodeId => {
      const lane = resolved[nodeId];
      if (!laneGroups.has(lane)) {
        laneGroups.set(lane, []);
      }
      laneGroups.get(lane).push(nodeId);
    });
    
    // For each lane, check for temporal overlaps
    laneGroups.forEach((nodeIds, lane) => {
      // Sort by founding year
      const sortedNodes = nodeIds
        .map(id => ({ id, node: nodeMap.get(id) }))
        .sort((a, b) => a.node.founding_year - b.node.founding_year);
      
      // Check consecutive pairs for overlap
      for (let i = 0; i < sortedNodes.length - 1; i++) {
        const current = sortedNodes[i];
        const next = sortedNodes[i + 1];
        
        const currentEnd = current.node.dissolution_year || Infinity;
        const nextStart = next.node.founding_year;
        
        // If they overlap, move the second one to an adjacent lane
        if (currentEnd >= nextStart) {
          // Find an available lane (try above and below current lane)
          let newLane = null;
          for (let offset = 1; offset <= 5; offset++) {
            const testLaneAbove = lane + offset;
            const testLaneBelow = lane - offset;
            
            // Check if this lane has space
            const nodesInAbove = family.filter(id => resolved[id] === testLaneAbove);
            const nodesInBelow = family.filter(id => resolved[id] === testLaneBelow);
            
            // Check if moving to this lane would create overlap
            const canUseAbove = !this.hasTemporalOverlapInLane(
              next.id, testLaneAbove, resolved, nodeMap, family
            );
            const canUseBelow = !this.hasTemporalOverlapInLane(
              next.id, testLaneBelow, resolved, nodeMap, family
            );
            
            if (canUseAbove) {
              newLane = testLaneAbove;
              break;
            } else if (canUseBelow) {
              newLane = testLaneBelow;
              break;
            }
          }
          
          if (newLane !== null) {
            resolved[next.id] = newLane;
            // Update the lane group for next iteration
            const currentLaneNodes = laneGroups.get(lane);
            const index = currentLaneNodes.indexOf(next.id);
            if (index > -1) {
              currentLaneNodes.splice(index, 1);
            }
            if (!laneGroups.has(newLane)) {
              laneGroups.set(newLane, []);
            }
            laneGroups.get(newLane).push(next.id);
          }
        }
      }
    });
    
    return resolved;
  }

  /**
   * Check if a node would have temporal overlap with existing nodes in a lane
   */
  hasTemporalOverlapInLane(nodeId, lane, assignments, nodeMap, family) {
    const node = nodeMap.get(nodeId);
    const nodeStart = node.founding_year;
    const nodeEnd = node.dissolution_year || Infinity;
    
    // Find all other nodes in this lane
    const nodesInLane = family.filter(id => id !== nodeId && assignments[id] === lane);
    
    for (const otherId of nodesInLane) {
      const otherNode = nodeMap.get(otherId);
      const otherStart = otherNode.founding_year;
      const otherEnd = otherNode.dissolution_year || Infinity;
      
      // Check for overlap: (start1 < end2) AND (start2 < end1)
      if (nodeStart < otherEnd && otherStart < nodeEnd) {
        return true;
      }
    }
    
    return false;
  }
}
