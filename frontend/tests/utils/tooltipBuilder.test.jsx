import { describe, it, expect } from 'vitest';
import React from 'react';
import { TooltipBuilder } from '../../src/utils/tooltipBuilder';

describe('TooltipBuilder', () => {
  it('builds node tooltip with sponsors', () => {
    const node = {
      founding_year: 2000,
      eras: [{ year: 2020, name: 'Team A', tier: 1, uci_code: 'AAA', sponsors: [{ brand: 'BrandX', color: '#FF0000', prominence: 60 }] }]
    };
    const content = TooltipBuilder.buildNodeTooltip(node);
    expect(content).toBeTruthy();
  });

  it('builds link tooltip with source/target names', () => {
    const nodes = [
      { id: 'n1', eras: [{ name: 'Team A' }] },
      { id: 'n2', eras: [{ name: 'Team B' }] },
    ];
    const link = { type: 'LEGAL_TRANSFER', source: 'n1', target: 'n2', year: 2010 };
    const content = TooltipBuilder.buildLinkTooltip(link, nodes);
    expect(content).toBeTruthy();
  });

  it('handles missing nodes gracefully', () => {
    const content = TooltipBuilder.buildLinkTooltip({ type: 'LEGAL_TRANSFER', source: 'x', target: 'y' }, []);
    expect(content).toBeNull();
  });
});
