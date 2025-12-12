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
  onEditSuccess,
  currentStartYear,
  currentEndYear,
  filtersVersion = 0
}) {
  const svgRef = useRef(null);
  const containerRef = useRef(null);
  const rulerTopRef = useRef(null);
  const rulerBottomRef = useRef(null);
  const zoomManager = useRef(null);
  const zoomBehavior = useRef(null);
  const currentLayout = useRef(null);
  const navigationRef = useRef(null);
  const viewportManager = useRef(null);
  const performanceMonitor = useRef(new PerformanceMonitor());
  const optimizedRenderer = useRef(null);
  const currentTransform = useRef(d3.zoomIdentity);
  const graphDataRef = useRef(null);
  const virtualizationTimeout = useRef(null);
  
  const [zoomLevel, setZoomLevel] = useState('OVERVIEW');
  const [tooltip, setTooltip] = useState({ visible: false, content: null, position: null });
  const [showEditWizard, setShowEditWizard] = useState(false);
  const [showMergeWizard, setShowMergeWizard] = useState(false);
  const [showSplitWizard, setShowSplitWizard] = useState(false);
  const [showCreateWizard, setShowCreateWizard] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [toast, setToast] = useState({ visible: false, message: '', type: 'success' });
  const [currentFilters, setCurrentFilters] = useState({
    startYear: currentStartYear || initialStartYear,
    endYear: currentEndYear || initialEndYear
  });
  
  const VERTICAL_PADDING = VISUALIZATION.NODE_HEIGHT + 20;
  
  const { user, canEdit } = useAuth();
  const navigate = useNavigate();
  
  // Note: props-change effect moved below zoomToYearRange definition to avoid TDZ
  
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

  // Helper to compute responsive minimum zoom
  // This is the "fit everything" scale - can't zoom out further than this
  const computeMinScale = useCallback((layout) => {
    const containerWidth = containerRef.current?.clientWidth || 1;
    const containerHeight = containerRef.current?.clientHeight || 1;

    const spanX = layout?.xScale
      ? layout.xScale(layout.yearRange.max) - layout.xScale(layout.yearRange.min)
      : 0;
    const nodes = layout?.nodes || [];
    const maxNodeBottom = nodes.length
      ? Math.max(...nodes.map(n => (n.y || 0) + (n.height || 0)))
      : 0;
    const minNodeTop = nodes.length ? Math.min(...nodes.map(n => n.y || 0)) : 0;
    const paddedMinY = minNodeTop - VERTICAL_PADDING;
    const paddedMaxY = maxNodeBottom + VERTICAL_PADDING;
    const spanY = Math.max(1, paddedMaxY - paddedMinY);

    if (!spanX || spanX <= 0) return VISUALIZATION.ZOOM_MIN;

    // Minimum scale is the one that fits BOTH dimensions
    // (the smaller of the two - more zoomed out)
    const scaleX = containerWidth / spanX;
    const scaleY = containerHeight / spanY;

    // Add safety floor of 0.01 to prevent invalid transforms
    return Math.max(0.01, Math.min(scaleX, scaleY));
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

  // Recalculate layout/zoom bounds on resize so minimum zoom remains responsive
  useEffect(() => {
    const handleResize = () => {
      if (currentLayout.current) {
        // Re-render with current layout when viewport changes
        if (viewportManager.current && svgRef.current && containerRef.current) {
          const container = containerRef.current;
          const width = container.clientWidth;
          const height = container.clientHeight;

          const layout = currentLayout.current;
          const minScale = computeMinScale(layout);
          zoomBehavior.current?.scaleExtent([minScale, VISUALIZATION.ZOOM_MAX]);
          
          // Trigger full re-render
          renderGraph(graphDataRef.current);
        }
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [computeMinScale]);

  // Prevent browser zoom on SVG container
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const preventBrowserZoom = (e) => {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
      }
    };

    container.addEventListener('wheel', preventBrowserZoom, { passive: false });
    return () => container.removeEventListener('wheel', preventBrowserZoom);
  }, []);
  
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
    zoomToYearRange(currentFilters.startYear, currentFilters.endYear);
  }, [currentFilters]);
  
  const zoomToYearRange = useCallback((startYear, endYear) => {
    if (!currentLayout.current || !svgRef.current || !containerRef.current || !zoomBehavior.current) return;
    
    const layout = currentLayout.current;
    const containerWidth = containerRef.current.clientWidth;
    
    const x1 = layout.xScale(startYear);
    const x2 = layout.xScale(endYear);
    const yearRangeWidth = Math.max(1, x2 - x1);
    
    const padding = 80;
    const rawScale = (containerWidth - 2 * padding) / yearRangeWidth;
    const minScale = computeMinScale(layout);
    const targetScale = Math.min(VISUALIZATION.ZOOM_MAX, Math.max(minScale, rawScale));
    
    const centerX = (x1 + x2) / 2;
    const targetX = containerWidth / 2 - centerX * targetScale;
    const targetY = 0;
    
    const svg = d3.select(svgRef.current);
    const transform = d3.zoomIdentity
      .translate(targetX, targetY)
      .scale(targetScale);
    
    svg.transition()
      .duration(750)
      .call(zoomBehavior.current.transform, transform);
  }, [computeMinScale]);

  // Update filters when props change and trigger zoom (defined after zoomToYearRange to avoid TDZ)
  useEffect(() => {
    if (currentStartYear !== undefined && currentEndYear !== undefined) {
      setCurrentFilters({ startYear: currentStartYear, endYear: currentEndYear });
      if (currentLayout.current) {
        setTimeout(() => {
          zoomToYearRange(currentStartYear, currentEndYear);
        }, 50);
      }
    }
  }, [currentStartYear, currentEndYear, filtersVersion, zoomToYearRange]);
  
  const getGridInterval = (scale) => {
    // Only years or decades based on zoom level (grid switches earlier)
    return scale >= 1.2 ? 1 : 10;
  };

  const getLabelInterval = (scale) => {
    // Labels switch later to avoid overlap; stay on decades until more zoomed in
    return scale >= 1.8 ? 1 : 10;
  };

  const renderBackgroundGrid = (g, layout, scale = 1) => {
    let gridGroup = g.select('.grid');
    if (gridGroup.empty()) {
      gridGroup = g.append('g')
        .attr('class', 'grid')
        .style('pointer-events', 'none');
    } else {
      gridGroup.selectAll('*').remove();
    }
    
    // Use actual year bounds and the same scale as layout
    const yearRange = layout?.yearRange ?? { min: 0, max: 1 };
    const xScale = layout?.xScale ?? ((year) => year);
    
    // Dynamic spacing by zoom level for grid only
    const interval = getGridInterval(scale);
    const gridSpacingYears = interval;
    
    // Draw vertical grid lines - extend to actual node bounds, not just viewport
    const start = Math.floor(yearRange.min / gridSpacingYears) * gridSpacingYears;
    const end = Math.ceil(yearRange.max / gridSpacingYears) * gridSpacingYears;
    const nodes = layout?.nodes || [];
    const maxNodeBottom = nodes.length
      ? Math.max(...nodes.map(n => (n.y || 0) + (n.height || 0)))
      : (containerRef.current?.clientHeight || 1000);
    const minNodeTop = nodes.length ? Math.min(...nodes.map(n => n.y || 0)) : -100;
    const paddedMinY = minNodeTop - VERTICAL_PADDING;
    const paddedMaxY = maxNodeBottom + VERTICAL_PADDING;

    for (let year = start; year <= end; year += gridSpacingYears) {
      const x = xScale(year);
      gridGroup.append('line')
        .attr('x1', x)
        .attr('y1', paddedMinY - 100)
        .attr('x2', x)
        .attr('y2', paddedMaxY + 100)
        .attr('stroke', '#444')
        .attr('stroke-width', Math.max(0.7, 0.7 / scale))
        .attr('stroke-dasharray', scale >= 1.5 ? '1,3' : '3,3');
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
    // Extend the filter range by 1 year to show full span of the end year
    const filterYearRange = { min: currentFilters.startYear, max: currentFilters.endYear + 1 };
    let calculator = new LayoutCalculator(dedupedData, width, height, filterYearRange);
    let layout = calculator.calculateLayout();

    // If the container is wider relative to content height, stretch the x-axis to eliminate horizontal gutters
    const spanX = layout.xScale(layout.yearRange.max) - layout.xScale(layout.yearRange.min);
    const nodesForSpan = layout.nodes || [];
    const maxNodeBottom = nodesForSpan.length
      ? Math.max(...nodesForSpan.map(n => (n.y || 0) + (n.height || 0)))
      : height;
    const minNodeTop = nodesForSpan.length ? Math.min(...nodesForSpan.map(n => n.y || 0)) : 0;
    const paddedMinY = minNodeTop - VERTICAL_PADDING;
    const paddedMaxY = maxNodeBottom + VERTICAL_PADDING;
    const spanY = Math.max(1, paddedMaxY - paddedMinY);
    const scaleX = width / spanX;
    const scaleY = height / spanY;

    if (scaleX > scaleY * 1.001) {
      const stretchFactor = scaleX / scaleY;
      console.log('Applying x-axis stretch for aspect fit', { scaleX, scaleY, stretchFactor, spanX, spanY });
      calculator = new LayoutCalculator(dedupedData, width, height, filterYearRange, stretchFactor);
      layout = calculator.calculateLayout();
    }
    performanceMonitor.current.endTiming('layout', layoutStart);
    performanceMonitor.current.metrics.nodeCount = layout.nodes.length;
    performanceMonitor.current.metrics.linkCount = layout.links.length;
    currentLayout.current = layout;
    graphDataRef.current = graphData;

    // Perform actual rendering (will be called after all render functions are defined)
    renderGraphVirtualized(layout);
  };

  // This will be defined later after helper functions, but called from renderGraph
  const renderGraphVirtualized = (layout) => {
    if (!viewportManager.current || !layout) return;
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Update zoom min scale when layout recalculates
    const minScale = computeMinScale(layout);
    zoomBehavior.current?.scaleExtent([minScale, VISUALIZATION.ZOOM_MAX]);

    // Calculate initial transform if this is first render (identity transform)
    if (currentTransform.current.k === 1 && currentTransform.current.x === 0 && currentTransform.current.y === 0) {
      const nodes = layout.nodes || [];
      
      if (nodes.length === 0) {
        console.error('No nodes to display!');
        return;
      }
      
      const maxNodeBottom = Math.max(...nodes.map(n => (n.y || 0) + (n.height || 0)));
      const minNodeTop = Math.min(...nodes.map(n => n.y || 0));
      const paddedMinY = minNodeTop - VERTICAL_PADDING;
      const paddedMaxY = maxNodeBottom + VERTICAL_PADDING;
      
      const spanX = layout.xScale(layout.yearRange.max) - layout.xScale(layout.yearRange.min);
      const spanY = Math.max(1, paddedMaxY - paddedMinY);

      // Initial scale: fit ALL content (both width and height)
      const scaleX = width / spanX;
      const scaleY = height / spanY;
      const targetScale = Math.max(0.01, Math.min(scaleX, scaleY));

      // Center the content in the viewport using padded bounds so labels don't overlap
      const centerX = (layout.xScale(layout.yearRange.min) + layout.xScale(layout.yearRange.max)) / 2;
      const centerY = (paddedMinY + paddedMaxY) / 2;
      const targetX = width / 2 - centerX * targetScale;
      const targetY = height / 2 - centerY * targetScale;
      
      console.log('🎯 INITIAL TRANSFORM CALC:', {
        nodeCount: nodes.length,
        yearRange: [layout.yearRange.min, layout.yearRange.max],
        spanX,
        spanY,
        containerWidth: width,
        containerHeight: height,
        scaleX,
        scaleY,
        targetScale,
        minScale,
        centerX,
        centerY,
        targetX,
        targetY,
        minNodeTop,
        maxNodeBottom,
        paddedMinY,
        paddedMaxY
      });      currentTransform.current = d3.zoomIdentity.translate(targetX, targetY).scale(targetScale);
    }

    // Use current transform
    const transform = currentTransform.current;

    const visibleNodes = viewportManager.current.getVisibleNodes(layout.nodes, transform);
    const visibleNodeIds = new Set(visibleNodes.map((n) => n.id));
    const visibleLinks = viewportManager.current.getVisibleLinks(layout.links, visibleNodeIds);

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();
    svg.attr('width', width).attr('height', height);

    // Add gradient definitions for different link styles
    const defs = svg.append('defs');
    
    // Gradient for MERGE connections (multiple sources converging)
    const mergeGradient = defs.append('linearGradient')
      .attr('id', 'mergeGradient')
      .attr('x1', '0%')
      .attr('y1', '0%')
      .attr('x2', '100%')
      .attr('y2', '0%');
    
    mergeGradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', VISUALIZATION.LINK_COLOR_LEGAL)
      .attr('stop-opacity', 0.6);
    
    mergeGradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', VISUALIZATION.LINK_COLOR_LEGAL)
      .attr('stop-opacity', 1);

    const g = svg.append('g');
    // Apply current transform immediately to avoid initial flash before zoom attaches
    g.attr('transform', currentTransform.current);
    
    // Add background grid
    renderBackgroundGrid(g, layout);
    
    // Render links and nodes first
    renderLinks(g, visibleLinks);
    renderNodes(g, visibleNodes, svg);
    
    // Render transition markers LAST so they appear on top
    renderTransitionMarkers(g, visibleLinks);

    renderRulers(layout, transform);

    setupZoomWithVirtualization(svg, g, layout);
  };

  const setupZoomWithVirtualization = (svg, g, layout) => {
    const containerWidth = containerRef.current?.clientWidth || 1;
    const containerHeight = containerRef.current?.clientHeight || 1;
    const minScale = computeMinScale(layout);

    // Constrain panning: calculate extent that prevents panning outside year bounds
    // translateExtent is in world coords, so we need to account for scale and pan
    const span = layout.xScale(layout.yearRange.max) - layout.xScale(layout.yearRange.min);
    const yearMin = layout.xScale(layout.yearRange.min);
    const yearMax = layout.xScale(layout.yearRange.max);

    const nodes = layout.nodes || [];
    const maxNodeBottom = nodes.length
      ? Math.max(...nodes.map(n => (n.y || 0) + (n.height || 0)))
      : containerHeight;
    const minNodeTop = nodes.length ? Math.min(...nodes.map(n => n.y || 0)) : 0;
    const paddedMinY = minNodeTop - VERTICAL_PADDING;
    const paddedMaxY = maxNodeBottom + VERTICAL_PADDING;

    // translateExtent defines the area that can be panned to
    // [[x0, y0], [x1, y1]] means: top-left corner can pan from x0,y0 to x1,y1
    // We want the viewport to never see empty space; keep extent tight to content + padding
    const extent = [
      [yearMin, paddedMinY],
      [yearMax, paddedMaxY]
    ];
    
    console.log('🔧 ZOOM SETUP:', {
      minScale,
      maxScale: VISUALIZATION.ZOOM_MAX,
      extent,
      currentTransform: { k: currentTransform.current.k, x: currentTransform.current.x, y: currentTransform.current.y },
      containerWidth,
      containerHeight,
      span,
      yearMin,
      yearMax
    });

    const zoom = d3
      .zoom()
      .scaleExtent([minScale, VISUALIZATION.ZOOM_MAX])
      .translateExtent(extent)
      .filter((event) => {
        // Allow mouse wheel, touch gestures, but block right-click drag
        if (event.type === 'wheel') return !event.ctrlKey;
        if (event.type === 'mousedown') return !event.button;
        return true; // Allow touch events
      })
      .on('zoom', (event) => {
        console.log('🎯 ZOOM EVENT:', { k: event.transform.k, x: event.transform.x, y: event.transform.y });
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

        // Update grid density with zoom
        renderBackgroundGrid(g, layout, event.transform.k);
        renderRulers(layout, event.transform);

        // Debounce virtualization updates
        clearTimeout(virtualizationTimeout.current);
        virtualizationTimeout.current = setTimeout(() => {
          updateVirtualization(layout, event.transform);
        }, 100);
      });
    zoomBehavior.current = zoom;
    
    // Initialize zoom behavior and set the current transform
    svg.call(zoom);
    
    console.log('📍 BEFORE D3 TRANSFORM:', { k: currentTransform.current.k, x: currentTransform.current.x, y: currentTransform.current.y });
    
    // Always apply the current transform to D3's zoom state
    // This will trigger the zoom event handler which will set g.attr('transform')
    svg.call(zoom.transform, currentTransform.current);
    console.log('✅ APPLIED TRANSFORM TO D3');
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
      .data(visibleLinks, (d) => d.id || `${d.source}-${d.target}-${d.year || ''}-${d.type || ''}`);

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

  const renderRulers = useCallback((layout, transform = d3.zoomIdentity) => {
    if (!layout || !layout.xScale || !layout.yearRange) return;
    if (!rulerTopRef.current || !rulerBottomRef.current || !containerRef.current) return;

    const containerWidth = containerRef.current.clientWidth;
    const interval = getLabelInterval(transform.k || 1);
    const start = Math.floor(layout.yearRange.min / interval) * interval;
    const end = Math.ceil(layout.yearRange.max / interval) * interval;

    const positions = [];
    for (let year = start; year <= end; year += interval) {
      const midYear = year + interval / 2;
      const screenX = layout.xScale(midYear) * transform.k + transform.x;
      if (screenX < -100 || screenX > containerWidth + 100) continue;
      const label = interval >= 10 ? `${year}s` : `${year}`;
      positions.push({ x: screenX, label });
    }

    const renderInto = (ref) => {
      ref.innerHTML = '';
      positions.forEach(({ x, label }) => {
        const span = document.createElement('span');
        span.className = 'timeline-ruler-label';
        span.style.left = `${x}px`;
        span.textContent = label;
        ref.appendChild(span);
      });
    };

    renderInto(rulerTopRef.current);
    renderInto(rulerBottomRef.current);
  }, []);
  
  const renderLinks = (g, links) => {
    // Only render links with paths (curved arrows, not same-swimlane transitions)
    const linkData = links.filter(d => d.path !== null);
    
    g.append('g')
      .attr('class', 'links')
      .selectAll('path')
      .data(linkData, (d) => d.id || `${d.source}-${d.target}-${d.year || ''}-${d.type || ''}`)
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
  
  const renderTransitionMarkers = (g, links) => {
    // Only render markers for same-swimlane transitions
    const markerData = links.filter(d => d.sameSwimlane && d.path === null);
    
    const markerGroup = g.append('g').attr('class', 'transition-markers');
    
    const markers = markerGroup
      .selectAll('g.transition-marker')
      .data(markerData, (d) => `marker-${d.source}-${d.target}-${d.year || ''}`)
      .join('g')
        .attr('class', 'transition-marker')
        .style('cursor', 'pointer')
        .on('mouseenter', (event, d) => {
          d3.select(event.currentTarget).select('line').attr('stroke-width', 3);
          d3.select(event.currentTarget).select('circle').attr('r', 5);
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
          d3.select(event.currentTarget).select('line').attr('stroke-width', 2);
          d3.select(event.currentTarget).select('circle').attr('r', 3.5);
          setTooltip({ visible: false, content: null, position: null });
        });

    // Vertical line marker
    markers
      .append('line')
      .attr('x1', (d) => d.targetX)
      .attr('y1', (d) => d.targetY - 15)
      .attr('x2', (d) => d.targetX)
      .attr('y2', (d) => d.targetY + 15)
      .attr('stroke', (d) => 
        d.type === 'SPIRITUAL_SUCCESSION' ? VISUALIZATION.LINK_COLOR_SPIRITUAL : VISUALIZATION.LINK_COLOR_LEGAL
      )
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', (d) => (d.type === 'SPIRITUAL_SUCCESSION' ? '4,2' : '0'));

    // Circle at center
    markers
      .append('circle')
      .attr('cx', (d) => d.targetX)
      .attr('cy', (d) => d.targetY)
      .attr('r', 3.5)
      .attr('fill', (d) => 
        d.type === 'SPIRITUAL_SUCCESSION' ? VISUALIZATION.LINK_COLOR_SPIRITUAL : VISUALIZATION.LINK_COLOR_LEGAL
      )
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5);
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
    setShowCreateWizard(false);
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
      .attr('filter', 'url(#underglow)');
  };

  const handleNodeHoverEnd = (event) => {
    d3.select(event.currentTarget)
      .select('rect')
      .transition()
      .duration(200)
      .attr('filter', 'url(#drop-shadow)');
  };

  return (
    <div className="timeline-layout">
      <div 
        ref={containerRef} 
        className="timeline-graph-container"
      >
        <div className="timeline-ruler top" ref={rulerTopRef} aria-hidden="true" />
        <div className="timeline-ruler bottom" ref={rulerBottomRef} aria-hidden="true" />
        <div className="timeline-copyright" aria-label="Copyright">
          © 2025 - {new Date().getFullYear()} ChainLines
        </div>
        <svg ref={svgRef}></svg>
      </div>

      {/* Right sidebar with controls and actions */}
      <div className="timeline-sidebar">
        <ControlPanel 
          onYearRangeChange={onYearRangeChange}
          onTierFilterChange={onTierFilterChange}
          onZoomReset={handleZoomReset}
          onTeamSelect={handleTeamSelect}
          searchNodes={data?.nodes || []}
          initialStartYear={initialStartYear}
          initialEndYear={initialEndYear}
          initialTiers={initialTiers}
        />
        
        {/* Action buttons for merge/split/create - only show if user can edit */}
        {canEdit() && (
          <div className="wizard-actions">
            <button 
              className="wizard-action-btn wizard-create"
              onClick={() => setShowCreateWizard(true)}
              title="Create a new team from scratch"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="16"/>
                <line x1="8" y1="12" x2="16" y2="12"/>
              </svg>
              Create Team
            </button>
            <button 
              className="wizard-action-btn"
              onClick={() => setShowMergeWizard(true)}
              title="Create a merge event"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ transform: 'rotate(90deg)' }}>
                <path d="m8 6 4-4 4 4"/>
                <path d="M12 2v10.3a4 4 0 0 1-1.172 2.872L4 22"/>
                <path d="m20 22-5-5"/>
              </svg>
              Merge Teams
            </button>
            <button 
              className="wizard-action-btn"
              onClick={() => setShowSplitWizard(true)}
              title="Create a split event"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ transform: 'rotate(90deg)' }}>
                <path d="M16 3h5v5"/>
                <path d="M8 3H3v5"/>
                <path d="M12 22v-8.3a4 4 0 0 0-1.172-2.872L3 3"/>
                <path d="m21 3-7.929 7.929A4 4 0 0 0 12 13.828V22"/>
              </svg>
              Split Team
            </button>
          </div>
        )}
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
