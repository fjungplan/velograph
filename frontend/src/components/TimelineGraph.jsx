import { useEffect, useRef, useState, useCallback } from 'react';
import * as d3 from 'd3';
import { LayoutCalculator } from '../utils/layoutCalculator';
import { validateGraphData } from '../utils/graphUtils';
import { VISUALIZATION } from '../constants/visualization';
import './TimelineGraph.css';
import { JerseyRenderer } from '../utils/jerseyRenderer';
import { ZoomLevelManager } from '../utils/zoomLevelManager';
import { DetailRenderer } from '../utils/detailRenderer';
import ControlPanel from './ControlPanel';
import Tooltip from './Tooltip';
import { TooltipBuilder } from '../utils/tooltipBuilder.jsx';
import SearchBar from './SearchBar';
import { GraphNavigation } from '../utils/graphNavigation';
import { ViewportManager } from '../utils/virtualization';
import { PerformanceMonitor } from '../utils/performanceMonitor';
import { OptimizedRenderer } from '../utils/optimizedRenderer';
import EditMetadataWizard from './EditMetadataWizard';
import MergeWizard from './MergeWizard';
import SplitWizard from './SplitWizard';
import CreateTeamWizard from './CreateTeamWizard';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function TimelineGraph({ 
  data, 
  onYearRangeChange, 
  onTierFilterChange,
  initialStartYear = 2020,
  initialEndYear = new Date().getFullYear(),
  initialTiers = [1, 2, 3],
  onEditSuccess
}) {
  const svgRef = useRef(null);
  const containerRef = useRef(null);
  const zoomManager = useRef(null);
  const zoomBehavior = useRef(null);
  const currentLayout = useRef(null);
  const navigationRef = useRef(null);
  const viewportManager = useRef(null);
  const performanceMonitor = useRef(new PerformanceMonitor());
  const optimizedRenderer = useRef(null);
  const currentTransform = useRef(d3.zoomIdentity);
  const virtualizationTimeout = useRef(null);
  
  const [zoomLevel, setZoomLevel] = useState('OVERVIEW');
  const [tooltip, setTooltip] = useState({ visible: false, content: null, position: null });
  const [showEditWizard, setShowEditWizard] = useState(false);
  const [showMergeWizard, setShowMergeWizard] = useState(false);
  const [showSplitWizard, setShowSplitWizard] = useState(false);
  const [showCreateWizard, setShowCreateWizard] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [toast, setToast] = useState({ visible: false, message: '', type: 'success' });
  
  const { user, canEdit } = useAuth();
  const navigate = useNavigate();
  
  useEffect(() => {
    // Initialize zoom manager
    zoomManager.current = new ZoomLevelManager((level, scale) => {
      setZoomLevel(level);
      updateDetailLevel(level, scale);
    });
    
    // Initialize navigation manager
    if (svgRef.current && containerRef.current) {
      navigationRef.current = new GraphNavigation(
        svgRef.current,
        containerRef.current.clientWidth,
        containerRef.current.clientHeight
      );
    }

    // Initialize viewport and optimized renderer
    if (containerRef.current && svgRef.current) {
      viewportManager.current = new ViewportManager(
        containerRef.current.clientWidth,
        containerRef.current.clientHeight
      );
      optimizedRenderer.current = new OptimizedRenderer(
        svgRef.current,
        performanceMonitor.current
      );
    }
  }, []);

  // Log performance metrics in development
  useEffect(() => {
    if (typeof process !== 'undefined' && process.env && process.env.NODE_ENV === 'development') {
      const interval = setInterval(() => {
        performanceMonitor.current.logMetrics();
      }, 10000);
      return () => clearInterval(interval);
    }
  }, []);
  
  useEffect(() => {
    if (!data || !data.nodes || !data.links) return;
    
    // Log raw API data to check for duplicates at source
    const nodeIds = data.nodes.map(n => n.id);
    const uniqueNodeIds = new Set(nodeIds);
    console.log('API Response - Total nodes:', nodeIds.length, 'Unique IDs:', uniqueNodeIds.size);
    if (nodeIds.length !== uniqueNodeIds.size) {
      const duplicates = nodeIds.filter((id, idx) => nodeIds.indexOf(id) !== idx);
      console.error('DUPLICATES IN API RESPONSE:', [...new Set(duplicates)]);
    }
    
    try {
      validateGraphData(data);
      renderGraph(data);
    } catch (error) {
      console.error('Graph render error:', error);
    }
  }, [data]);
  
  const updateDetailLevel = useCallback((level, scale) => {
    if (!currentLayout.current) return;
    
    const g = d3.select(svgRef.current).select('g');
    
    if (level === 'DETAIL') {
      // Show detailed features
      DetailRenderer.renderDetailedLinks(g, currentLayout.current.links, scale);
      
      // Render era timelines
      g.selectAll('.node').each(function(d) {
        const group = d3.select(this);
        DetailRenderer.renderEraTimeline(group, d, scale);
      });
    } else {
      // Hide detailed features
      g.selectAll('.era-segment').remove();
      g.selectAll('.links path').attr('marker-end', null);
    }
  }, []);
  
  const handleZoom = useCallback((event) => {
    const { transform } = event;
    const g = d3.select(svgRef.current).select('g');
    g.attr('transform', transform);
    if (zoomManager.current) {
      zoomManager.current.updateScale(transform.k);
    }
  }, []);
  
  const handleZoomReset = useCallback(() => {
    const svg = d3.select(svgRef.current);
    svg.transition()
      .duration(750)
      .call(zoomBehavior.current.transform, d3.zoomIdentity);
  }, []);
  
  const renderBackgroundGrid = (g, layout) => {
    const gridGroup = g.append('g')
      .attr('class', 'grid')
      .style('pointer-events', 'none');
    
    // Estimate year boundaries from node positions
    const yearRange = currentLayout.current?.nodes?.length > 0
      ? {
          min: Math.min(...currentLayout.current.nodes.map(n => n.x)),
          max: Math.max(...currentLayout.current.nodes.map(n => n.x + n.width))
        }
      : { min: 0, max: 1000 };
    
    // Calculate year spacing (roughly 120px per year from YEAR_WIDTH)
    const yearWidth = VISUALIZATION.YEAR_WIDTH;
    const gridSpacing = yearWidth;
    
    // Draw vertical grid lines
    for (let x = yearRange.min; x <= yearRange.max; x += gridSpacing) {
      gridGroup.append('line')
        .attr('x1', x)
        .attr('y1', -100)
        .attr('x2', x)
        .attr('y2', containerRef.current?.clientHeight || 1000)
        .attr('stroke', '#e0e0e0')
        .attr('stroke-width', 0.5)
        .attr('stroke-dasharray', '2,2');
    }
  };
  
  
  const renderGraph = (graphData) => {
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    // Deduplicate nodes by ID
    const deduplicatedNodes = [];
    const seenIds = new Set();
    const duplicateMap = {};
    
    for (const node of graphData.nodes) {
      if (!seenIds.has(node.id)) {
        deduplicatedNodes.push(node);
        seenIds.add(node.id);
      } else {
        duplicateMap[node.id] = (duplicateMap[node.id] || 1) + 1;
      }
    }
    
    if (deduplicatedNodes.length < graphData.nodes.length) {
      const removedCount = graphData.nodes.length - deduplicatedNodes.length;
      console.warn('Found duplicate nodes:', removedCount, duplicateMap);
      console.log('Original nodes:', graphData.nodes.map(n => ({ id: n.id, name: n.eras?.[0]?.name })));
      console.log('Deduplicated nodes:', deduplicatedNodes.map(n => ({ id: n.id, name: n.eras?.[0]?.name })));
    }
    
    console.log('Rendering with nodes:', deduplicatedNodes.map(n => ({
      id: n.id,
      name: n.eras?.[0]?.name,
      founding: n.founding_year,
      dissolution: n.dissolution_year,
      eras: n.eras?.length
    })));
    
    const dedupedData = {
      ...graphData,
      nodes: deduplicatedNodes
    };
    
    const layoutStart = performanceMonitor.current.startTiming('layout');
    const calculator = new LayoutCalculator(dedupedData, width, height);
    const layout = calculator.calculateLayout();
    performanceMonitor.current.endTiming('layout', layoutStart);
    performanceMonitor.current.metrics.nodeCount = layout.nodes.length;
    performanceMonitor.current.metrics.linkCount = layout.links.length;
    currentLayout.current = layout;

    renderWithVirtualization(layout);
  };

  const renderWithVirtualization = useCallback((layout) => {
    if (!viewportManager.current) return;
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    const transform = currentTransform.current;

    const visibleNodes = viewportManager.current.getVisibleNodes(layout.nodes, transform);
    const visibleNodeIds = new Set(visibleNodes.map((n) => n.id));
    const visibleLinks = viewportManager.current.getVisibleLinks(layout.links, visibleNodeIds);

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();
    svg.attr('width', width).attr('height', height);

    const g = svg.append('g').attr('transform', transform);
    
    // Add background grid
    renderBackgroundGrid(g, layout);
    
    renderLinks(g, visibleLinks);
    renderNodes(g, visibleNodes, svg);

    setupZoomWithVirtualization(svg, g, layout);
  }, []);

  const setupZoomWithVirtualization = (svg, g, layout) => {
    const zoom = d3
      .zoom()
      .scaleExtent([VISUALIZATION.ZOOM_MIN, VISUALIZATION.ZOOM_MAX])
      .on('zoom', (event) => {
        currentTransform.current = event.transform;
        g.attr('transform', event.transform);

        // Zoom level manager and LOD updates
        if (zoomManager.current) {
          zoomManager.current.updateScale(event.transform.k);
        }
        if (optimizedRenderer.current) {
          optimizedRenderer.current.renderWithLOD(
            currentLayout.current?.nodes || [],
            currentLayout.current?.links || [],
            event.transform.k
          );
        }

        // Debounce virtualization updates
        clearTimeout(virtualizationTimeout.current);
        virtualizationTimeout.current = setTimeout(() => {
          updateVirtualization(layout, event.transform);
        }, 100);
      });
    zoomBehavior.current = zoom;
    svg.call(zoom);
  };

  const updateVirtualization = (layout, transform) => {
    if (!viewportManager.current) return;

    const visibleNodes = viewportManager.current.getVisibleNodes(layout.nodes, transform);
    const visibleNodeIds = new Set(visibleNodes.map((n) => n.id));
    const visibleLinks = viewportManager.current.getVisibleLinks(layout.links, visibleNodeIds);

    const g = d3.select(svgRef.current).select('g');

    // Update links
    const linkSel = g
      .select('.links')
      .selectAll('path')
      .data(visibleLinks, (d, i) => `link-${i}`);

    linkSel
      .join(
        (enter) =>
          enter
            .append('path')
            .attr('d', (d) => d.path)
            .attr('fill', 'none')
            .attr('stroke', (d) =>
              d.type === 'SPIRITUAL_SUCCESSION' ? VISUALIZATION.LINK_COLOR_SPIRITUAL : VISUALIZATION.LINK_COLOR_LEGAL
            )
            .attr('stroke-width', VISUALIZATION.LINK_STROKE_WIDTH)
            .attr('stroke-dasharray', (d) => (d.type === 'SPIRITUAL_SUCCESSION' ? '5,5' : '0'))
            .style('cursor', 'pointer')
            .on('mouseenter', (event, d) => {
              d3.select(event.currentTarget).attr('stroke-width', VISUALIZATION.LINK_STROKE_WIDTH * 2);
              const content = TooltipBuilder.buildLinkTooltip(d, currentLayout.current?.nodes || []);
              if (content) {
                setTooltip({ visible: true, content, position: { x: event.pageX, y: event.pageY } });
              }
            })
            .on('mousemove', (event) => {
              if (tooltip.visible) {
                setTooltip((prev) => ({ ...prev, position: { x: event.pageX, y: event.pageY } }));
              }
            })
            .on('mouseleave', (event) => {
              d3.select(event.currentTarget).attr('stroke-width', VISUALIZATION.LINK_STROKE_WIDTH);
              setTooltip({ visible: false, content: null, position: null });
            }),
        (update) => update,
        (exit) => exit.remove()
      );

    // Update nodes
    const nodeSel = g
      .select('.nodes')
      .selectAll('.node')
      .data(visibleNodes, (d) => d.id);

    nodeSel
      .join(
        (enter) => {
          const groups = enter
            .append('g')
            .attr('class', 'node')
            .attr('data-id', (d) => d.id)
            .attr('transform', (d) => `translate(${d.x},${d.y})`)
            .style('cursor', 'pointer')
            .on('click', (_event, d) => handleNodeClick(d))
            .on('mouseenter', (event, d) => {
              handleNodeHover(event, d);
              const content = TooltipBuilder.buildNodeTooltip(d);
              setTooltip({ visible: true, content, position: { x: event.pageX, y: event.pageY } });
            })
            .on('mousemove', (event) => {
              if (tooltip.visible) {
                setTooltip((prev) => ({ ...prev, position: { x: event.pageX, y: event.pageY } }));
              }
            })
            .on('mouseleave', (event) => {
              handleNodeHoverEnd(event);
              setTooltip({ visible: false, content: null, position: null });
            });

          groups.each(function (d) {
            const group = d3.select(this);
            JerseyRenderer.renderNode(group, d, d3.select(svgRef.current));
            JerseyRenderer.addNodeLabel(group, d);
          });

          return groups;
        },
        (update) => update.attr('transform', (d) => `translate(${d.x},${d.y})`),
        (exit) => exit.remove()
      );
  };
  
  const renderLinks = (g, links) => {
    g.append('g')
      .attr('class', 'links')
      .selectAll('path')
      .data(links)
      .join('path')
        .attr('data-id', (d, i) => `link-${i}`)
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
        )
        .style('cursor', 'pointer')
        .on('mouseenter', (event, d) => {
          d3.select(event.currentTarget)
            .attr('stroke-width', VISUALIZATION.LINK_STROKE_WIDTH * 2);
          const content = TooltipBuilder.buildLinkTooltip(d, currentLayout.current?.nodes || []);
          if (content) {
            setTooltip({ visible: true, content, position: { x: event.pageX, y: event.pageY } });
          }
        })
        .on('mousemove', (event) => {
          if (tooltip.visible) {
            setTooltip(prev => ({ ...prev, position: { x: event.pageX, y: event.pageY } }));
          }
        })
        .on('mouseleave', (event) => {
          d3.select(event.currentTarget)
            .attr('stroke-width', VISUALIZATION.LINK_STROKE_WIDTH);
          setTooltip({ visible: false, content: null, position: null });
        });
  };
  
  const renderNodes = (g, nodes, svg) => {
    console.log('renderNodes called with', nodes.length, 'nodes:', nodes.map(n => ({ id: n.id, x: n.x, y: n.y, width: n.width, height: n.height })));
    
    // Create shadow filter once
    JerseyRenderer.createShadowFilter(svg);

    const nodeGroups = g.append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(nodes)
      .join('g')
        .attr('class', 'node')
        .attr('data-id', d => d.id)
        .attr('transform', d => `translate(${d.x},${d.y})`)
        .style('cursor', 'pointer')
        .on('click', (event, d) => handleNodeClick(d))
        .on('mouseenter', (event, d) => {
          handleNodeHover(event, d);
          const content = TooltipBuilder.buildNodeTooltip(d);
          setTooltip({ visible: true, content, position: { x: event.pageX, y: event.pageY } });
        })
        .on('mousemove', (event) => {
          if (tooltip.visible) {
            setTooltip(prev => ({ ...prev, position: { x: event.pageX, y: event.pageY } }));
          }
        })
        .on('mouseleave', (event) => {
          handleNodeHoverEnd(event);
          setTooltip({ visible: false, content: null, position: null });
        });

    // Render each node with jersey styling
    nodeGroups.each(function(d) {
      const group = d3.select(this);
      JerseyRenderer.renderNode(group, d, svg);
      JerseyRenderer.addNodeLabel(group, d);
    });
  };

  const handleTeamSelect = useCallback((node) => {
    if (navigationRef.current) {
      navigationRef.current.focusOnNode(node);
    }
  }, []);

  const handleNodeClick = (node) => {
    console.log('Clicked node:', node);
    
    // Only allow edits if user can edit (authenticated with proper role)
    if (canEdit()) {
      setSelectedNode(node);
      setShowEditWizard(true);
    } else {
      // Navigate to team detail page for non-editors
      navigate(`/team/${node.id}`);
    }
  };
  
  const showToast = (message, type = 'success', duration = 3000) => {
    setToast({ visible: true, message, type });
    setTimeout(() => {
      setToast({ visible: false, message: '', type: 'success' });
    }, duration);
  };

  const handleWizardSuccess = (result) => {
    console.log('Edit submitted successfully:', result);
    setShowEditWizard(false);
    setShowMergeWizard(false);
    setShowSplitWizard(false);
    setSelectedNode(null);
    
    // Show toast notification (no browser dialog)
    if (result.status === 'APPROVED') {
      showToast('Edit applied successfully!', 'success');
      // Refetch data to show changes immediately
      if (onEditSuccess) {
        onEditSuccess();
      }
    } else {
      showToast('Edit submitted for moderation', 'info');
    }
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
    <div className="timeline-graph-wrapper">
      <SearchBar 
        nodes={data?.nodes || []}
        onTeamSelect={handleTeamSelect}
      />
      <ControlPanel 
        onYearRangeChange={onYearRangeChange}
        onTierFilterChange={onTierFilterChange}
        onZoomReset={handleZoomReset}
        initialStartYear={initialStartYear}
        initialEndYear={initialEndYear}
        initialTiers={initialTiers}
      />
      <div className="zoom-indicator">
        Zoom Level: {zoomLevel}
      </div>
      <div 
        ref={containerRef} 
        className="timeline-graph-container"
      >
        <svg ref={svgRef}></svg>
      </div>
      <Tooltip 
        content={tooltip.content}
        position={tooltip.position}
        visible={tooltip.visible}
      />
      
      {/* Wizard Modals */}
      {showEditWizard && selectedNode && selectedNode.eras && selectedNode.eras.length > 0 && (
        <EditMetadataWizard
          node={selectedNode}
          era={selectedNode.eras[selectedNode.eras.length - 1]}
          onClose={() => {
            setShowEditWizard(false);
            setSelectedNode(null);
          }}
          onSuccess={handleWizardSuccess}
        />
      )}
      
      {showMergeWizard && selectedNode && (
        <MergeWizard
          initialNode={selectedNode}
          onClose={() => {
            setShowMergeWizard(false);
            setSelectedNode(null);
          }}
          onSuccess={handleWizardSuccess}
        />
      )}
      
      {showSplitWizard && selectedNode && (
        <SplitWizard
          sourceNode={selectedNode}
          onClose={() => {
            setShowSplitWizard(false);
            setSelectedNode(null);
          }}
          onSuccess={handleWizardSuccess}
        />
      )}
      
      {showCreateWizard && (
        <CreateTeamWizard
          onClose={() => setShowCreateWizard(false)}
          onSuccess={handleWizardSuccess}
        />
      )}
      
      {/* Action buttons for merge/split/create - only show if user can edit */}
      {canEdit() && (
        <div className="wizard-actions">
          <button 
            className="wizard-action-btn wizard-create"
            onClick={() => setShowCreateWizard(true)}
            title="Create a new team from scratch"
          >
            + Create Team
          </button>
          <button 
            className="wizard-action-btn"
            onClick={() => setShowMergeWizard(true)}
            title="Create a merge event"
          >
            Merge Teams
          </button>
          <button 
            className="wizard-action-btn"
            onClick={() => setShowSplitWizard(true)}
            title="Create a split event"
          >
            Split Team
          </button>
        </div>
      )}
      
      {/* Toast Notification */}
      {toast.visible && (
        <div className={`toast toast-${toast.type}`}>
          <div className="toast-content">
            {toast.type === 'success' && <span className="toast-icon">✓</span>}
            {toast.type === 'info' && <span className="toast-icon">ℹ</span>}
            {toast.type === 'error' && <span className="toast-icon">✕</span>}
            <span className="toast-message">{toast.message}</span>
          </div>
        </div>
      )}
    </div>
  );
}
