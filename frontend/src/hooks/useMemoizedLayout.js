import { useMemo } from 'react';
import { LayoutCalculator } from '../utils/layoutCalculator';

export function useMemoizedLayout(data, width, height, filters) {
  return useMemo(() => {
    if (!data || !data.nodes || !data.links) return null;

    const filteredNodes = filterNodes(data.nodes, filters);
    const filteredLinks = filterLinks(data.links, filteredNodes);

    const calculator = new LayoutCalculator(
      { nodes: filteredNodes, links: filteredLinks },
      width,
      height
    );
    return calculator.calculateLayout();
  }, [data, width, height, filters]);
}

function filterNodes(nodes, filters) {
  if (!filters) return nodes;
  return nodes.filter((node) => {
    const hasEraInRange = node.eras?.some(
      (era) => era.year >= filters.startYear && era.year <= filters.endYear
    );
    if (filters.startYear != null && filters.endYear != null && !hasEraInRange) return false;

    if (filters.tiers && filters.tiers.length > 0) {
      const hasTier = node.eras?.some((era) => filters.tiers.includes(era.tier));
      if (!hasTier) return false;
    }

    return true;
  });
}

function filterLinks(links, filteredNodes) {
  const nodeIds = new Set(filteredNodes.map((n) => n.id));
  return links.filter((link) => nodeIds.has(link.source) && nodeIds.has(link.target));
}
