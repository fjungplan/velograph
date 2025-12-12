# Team Lineage Visualization Enhancement Proposal

**Date**: December 10, 2025  
**Goal**: Improve visual appeal and clarity of team succession links  
**Inspiration**: Sankey diagrams, flow visualizations, and timeline aesthetics

## Problem Statement

Currently, lineage links (arrows connecting teams) are visually bland:
- Plain dotted or solid lines barely stand out
- No visual hierarchy between different connection types
- No indication of flow or magnitude
- Same width regardless of context
- Minimal visual integration with the timeline

Example issues:
- Lima Pro → Quebec Pro arrow passes behind Mike WorldTour
- Links feel disconnected from the overall design
- Hard to distinguish relationship types at a glance

## Proposed Visual Enhancements

### 1. **Gradient Color Flow**

**Concept**: Use gradient colors to indicate flow from predecessor to successor, inspired by Sankey diagrams.

**Implementation**:
```
Legal Transfer:    ■━━━━━━━━━■  (Dark gray → slightly lighter gray)
Spiritual:         ░┈┈┈┈┈┈┈┈░  (Light gray → slightly darker gray)
Merge/Split:       ━━━━━━━━━━  (Color transitions show multiple flows)
```

**Benefits**:
- Visual directionality (flow from left to right)
- Subtle depth effect
- Professional appearance
- Easy to distinguish types

**Technical approach**:
- Define `<defs><linearGradient>` for each connection type
- Apply gradient ID to path stroke
- Adjust gradient angle to follow path curve

### 2. **Variable Stroke Width Based on Magnitude**

**Concept**: Thicker lines for more significant transfers, thinner for minor ones.

**Use cases**:
- Merges with multiple predecessors: show which had more "weight"
- Can indicate staff transfer percentage if available
- Visual importance based on event type

**Implementation**:
```javascript
// Thicker for legal transfers, thinner for spiritual
const baseWidth = d.type === 'LEGAL_TRANSFER' ? 3 : 1.5;
const magnitudeMultiplier = estimateTeamSize(d.source) / 100;
path.attr('stroke-width', baseWidth * magnitudeMultiplier);
```

**Benefits**:
- Immediate visual sense of relationship importance
- Works well with curved paths
- Can be animated on hover

### 3. **Animated Arrow Markers**

**Concept**: Small animated particles flowing along the connection path.

**Visual effect**:
```
────●────●────●────  (Small dots flowing along path)
     ↓   ↓   ↓
Shows direction and creates sense of motion
```

**Implementation approaches**:

**Option A: SVG Animations** (Simpler)
```svg
<circle r="2" fill="color">
  <animateMotion dur="3s" repeatCount="indefinite">
    <mpath href="#linkPath"/>
  </animateMotion>
</circle>
```
- Multiple circles with staggered delays
- Loop continuously
- Pause/resume on interaction

**Option B: Canvas Rendering** (Performance)
- Draw particles during canvas render cycle
- Update position each frame
- Fade in/out at endpoints
- Better for many links

**Benefits**:
- Dynamic, engaging visualization
- Shows directionality without arrows
- Can be toggled on/off for performance
- Works especially well for same-swimlane transitions

### 4. **Link Glow & Shadow Effects**

**Concept**: Add subtle glow on hover, stronger visibility on focus.

**Implementation**:
```css
.lineage-link {
  filter: drop-shadow(0 0 2px rgba(0,0,0,0.2));
  transition: filter 0.2s ease;
}

.lineage-link:hover {
  filter: drop-shadow(0 0 6px rgba(100,150,255,0.5));
  stroke-width: increase by 1.5x;
}
```

**Benefits**:
- Better hover feedback
- Visual hierarchy through emphasis
- No performance impact on static render
- Accessible without animation

### 5. **Curved Path Improvements**

**Current**: Cubic Bézier curves feel disconnected from timeline geometry

**Proposed**:
- Increase curve intensity for longer-distance links
- Use variable control point offsets based on vertical distance
- Add gentle arc to emphasize flow direction
- For same-swimlane: smooth vertical curve with handles

**Formula**:
```javascript
const dx = targetX - sourceX;
const dy = targetY - sourceY;
const distance = Math.sqrt(dx*dx + dy*dy);
const curvature = Math.min(distance * 0.5, 200); // Cap at 200px
// Use curvature to adjust control points
```

### 6. **Merge/Split Visualization**

**Current**: All splits look similar, hard to distinguish key flows

**Proposed - Split (A → B + C)**:
```
Team A ━━━┓
          ├─ Team B (thicker if legal)
          ┗─ Team C (thinner if spiritual)
```

**Proposed - Merge (A + B → C)**:
```
Team A ━━┓
         ├─ Team C
Team B ━━┛
```

**Implementation**:
- Different line joins for merges vs splits
- Gradient follows the direction of split/merge
- Color intensity indicates priority type

### 7. **Interactive Link States**

**Concept**: Rich interaction model for links

**States**:
- **Normal**: Subtle, doesn't distract
- **Hover**: Highlight, show tooltip, emphasize direction
- **Selected**: Full styling, show related nodes
- **Fade**: Dim other links when one is selected

**Implementation**:
```javascript
.on('mouseenter', (event, d) => {
  // Highlight this link
  d3.select(event.currentTarget).attr('stroke-width', baseWidth * 3);
  
  // Fade other links
  g.selectAll('.lineage-link').attr('opacity', 0.2);
  d3.select(event.currentTarget).attr('opacity', 1);
  
  // Highlight source and target nodes
  g.selectAll('.node').attr('opacity', 0.3);
  g.select(`[data-id="${d.source}"]`).attr('opacity', 1);
  g.select(`[data-id="${d.target}"]`).attr('opacity', 1);
})
```

## Visual Hierarchy Proposal

### By Event Type:

```
LEGAL_TRANSFER
├─ Color: #333 (dark gray)
├─ Style: Solid line
├─ Width: 3px base
├─ Glow: Blue (#1E88E5)
└─ Animation: Medium speed

SPIRITUAL_SUCCESSION
├─ Color: #999 (light gray)
├─ Style: Dashed (5px on, 3px off)
├─ Width: 1.5px base
├─ Glow: Green (#43A047)
└─ Animation: Slower speed (shows less certainty)

MERGE
├─ Color: Blend of input colors
├─ Style: Solid gradient
├─ Width: 2-3px variable
├─ Glow: Multi-color
└─ Animation: Converging particles

SPLIT
├─ Color: Parent color → child colors
├─ Style: Solid gradient diverging
├─ Width: Parent wider than children
├─ Glow: Diverging colors
└─ Animation: Diverging particles
```

## Implementation Priority

### Phase 1 (Immediate):
1. ✅ Fix link crossing algorithm (already done)
2. Gradient color flow (easy, high impact)
3. Variable stroke width based on type (easy)
4. Better curve parameters

### Phase 2 (Short-term):
1. Animated arrow particles (option A - SVG)
2. Link glow & shadow effects
3. Interactive link states (fade + highlight)
4. Improve same-swimlane transition markers

### Phase 3 (Optional):
1. Animated particles (option B - Canvas)
2. Custom merge/split renders
3. Performance optimizations
4. Theme customization

## Testing Considerations

1. **Performance**: Test with 50+ nodes and 100+ links
2. **Accessibility**: Ensure colorblind-friendly palette
3. **Mobile**: Disable animations on touch devices for performance
4. **Browser compatibility**: Test gradient and animation support
5. **Zoom levels**: Ensure markers visible at all zoom levels

## Color Palette Proposal

```
Legal Transfer:
- Primary: #333333 (dark gray)
- Gradient: #333 → #555 (adds depth)
- Glow: #1E88E5 (blue, trust)

Spiritual Succession:
- Primary: #999999 (light gray)
- Gradient: #999 → #BBB
- Glow: #43A047 (green, growth)

Merge/Split:
- Uses source/target team colors
- Blends smoothly
- Glow: multi-color blend

Hover: +20% lightness on all
Selected: +40% saturation
```

## Questions for Gemini Refinement

1. **Particle animation**: SVG vs Canvas - which would integrate better?
2. **Color palette**: Is the proposed hierarchy clear and accessible?
3. **Curve parameters**: What algorithm works best for minimize-crossing constraints?
4. **Performance**: Any concerns with animated particles + D3 zoom/pan?
5. **Merge/Split**: Should we show aggregate "weight" visually?

## References

- **Sankey Diagram inspiration**: Flow visualization with gradient colors
- **D3 examples**: https://bl.ocks.org/d3noob/
- **Timeline UI patterns**: Connected timelines with smooth flows
- **Motion design**: Purposeful animations that communicate

---

**Next Steps**:
1. Get feedback on proposed visual improvements
2. Consult Gemini 3 for detailed implementation strategy
3. Implement Phase 1 changes
4. Test with real data
5. Iterate based on user feedback
