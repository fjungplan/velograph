# Prompt for Gemini 3: Team Lineage Link Visualization Enhancement

**Context**: You're working on an interactive D3.js timeline visualization of professional cycling team evolution. Teams are represented as horizontal rectangles arranged in swimlanes (rows), positioned along a horizontal timeline (1900-2025).

**Current State**: 
- Team succession links (edges) are simple SVG paths: solid or dashed lines
- Very plain visual treatment - barely stands out
- Limited to basic stroke styling (color, width, dash-array)
- Looking to make them much more visually attractive and informative

**Goals**:
1. Make links more visually appealing and engaging
2. Maintain clarity - shouldn't obscure the timeline
3. Work within the constraint of a horizontal timeline
4. Be inspired by Sankey diagram aesthetics (gradients, flow, magnitude)
5. Support 50-100+ links at once without performance degradation

**Key Constraints**:
- Links must remain "almost vertical" connectors (mostly Y-direction) because timeline is horizontal
- Can't use traditional arrows (would look odd pointing mostly up/down)
- Need to preserve zoom/pan functionality
- Must handle different event types: LEGAL_TRANSFER, SPIRITUAL_SUCCESSION, MERGE, SPLIT

---

## Specific Questions for Gemini 3:

### 1. **Animated Particle Flow**
We're considering small animated dots flowing along link paths to indicate direction. 

**Questions**:
- SVG `<animateMotion>` vs Canvas-based particles - which would be better integrated with D3?
- Should particles speed vary by event type (faster for legal, slower for spiritual)?
- How many particles per link before performance becomes an issue?
- Should particles loop infinitely or just once when hovered?

### 2. **Color & Gradient Strategy**
We want to use gradients like Sankey, but our links are mostly vertical.

**Questions**:
- Should gradient go source-to-target (left to right in timeline)?
- Or should it go top-to-bottom along the link path?
- For MERGE events (A+B→C): blend source colors in gradient?
- For SPLIT events (A→B+C): should each branch get a sub-gradient?
- Any concerns with 20+ different gradient definitions (one per link)?

### 3. **Variable Stroke Width**
We want wider lines for legal transfers, narrower for spiritual.

**Questions**:
- Should width also reflect team "size" or importance?
- For MERGE: should total width = sum of source widths?
- For SPLIT: should branches share the parent width?
- Any performance issues with dynamic stroke width in D3 transitions?

### 4. **Interactive Behaviors**
Rich hover and click states for exploration.

**Questions**:
- Best way to highlight a link and its connected nodes simultaneously in D3?
- Should fading other links be smooth (CSS opacity transition) or instant?
- Any accessibility concerns with hiding information on hover?
- Should selected links persist, or deselect on click elsewhere?

### 5. **Merges & Splits Visualization**
These are special cases with multiple inputs or outputs.

**Questions**:
- Should MERGE/SPLIT use completely different rendering than regular succession?
- Can we show "which source was dominant" visually (thicker merge path from legal source)?
- Should we visualize staff transfer percentage if available?
- Any examples of good flow diagram renderings for inspiration?

### 6. **Curve Shape Optimization**
Links currently use basic cubic Bézier curves.

**Questions**:
- Should curve radius scale with vertical distance (longer = more curved)?
- Any benefit to using SVG path commands other than cubic Bézier (quadratic, arc)?
- Should same-swimlane links use a different curve shape than cross-swimlane?
- How to avoid link paths "interfering" with node rectangles visually?

### 7. **Glow & Shadow Effects**
Adding subtle visual feedback on interaction.

**Questions**:
- SVG `<filter>` with `<feGaussianBlur>` and `<feColorMatrix>` for glow?
- Should glow color match event type (blue for legal, green for spiritual)?
- Any performance impact of applying filters to 50+ paths?
- Better to use CSS filters or SVG filters for D3?

### 8. **Zoom & Pan Integration**
Links must scale smoothly with D3 zoom behavior.

**Questions**:
- Should animated particles maintain consistent speed at different zoom levels?
- Should particle size scale with zoom, or stay fixed screen-size?
- Any issues with SVG filters/gradients when group is transformed?
- Should transitions be disabled at high zoom levels for performance?

---

## Technical Context:

**Stack**: React 18 + D3.js v7 + SVG

**Current Link Implementation**:
```javascript
d3.select(svgRef.current)
  .selectAll('path')
  .data(links)
  .join('path')
    .attr('d', d => d.path) // Pre-calculated cubic Bézier path
    .attr('stroke', d => d.type === 'SPIRITUAL_SUCCESSION' ? '#999' : '#333')
    .attr('stroke-width', VISUALIZATION.LINK_STROKE_WIDTH) // 2px
    .attr('stroke-dasharray', d => d.type === 'SPIRITUAL_SUCCESSION' ? '5,5' : '0')
```

**Event Types Available**:
- `LEGAL_TRANSFER`: Team formally transferred (e.g., license sale)
- `SPIRITUAL_SUCCESSION`: Informal succession (similar roster/staff)
- `MERGE`: Multiple teams → one team
- `SPLIT`: One team → multiple teams

**Timeline Constraints**:
- X-axis: Temporal (1900-2025, ~800px range typically)
- Y-axis: Swimlanes (variable, usually 200-800px)
- Links are mostly vertical with gentle curves
- Can zoom 1x to 10x on both axes

---

## Deliverables Expected:

1. **Visual Design** showing at least 3 different link styles (LEGAL, SPIRITUAL, MERGE/SPLIT)
2. **Implementation Strategy** with code snippets for D3 + SVG
3. **Performance Considerations** - what might be slow, how to optimize
4. **Color Palette** suitable for colorblind viewers
5. **Animation Strategy** if using particles or other motion effects
6. **Questions Back** if anything is unclear

---

## Budget Guidance:

- **Must have**: Better visuals that don't sacrifice clarity
- **Should have**: Animated elements that indicate direction
- **Nice to have**: Context-aware styling (merge/split special handling)
- **Performance target**: 50-100 links rendering at 60fps with smooth zoom/pan

---

**Note**: We have full control over the link path geometry and styling. The main constraint is the timeline orientation (horizontal time) and swimlane layout. Be creative within these bounds!
