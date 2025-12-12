# Swimlane Visualization Improvement

## Overview

This document describes the improved swimlane algorithm for the ChainLines team lineage visualization, implemented on December 10, 2025.

## Problem Statement

Previously, every team node was assigned its own horizontal swimlane, even when teams had direct linear succession relationships. This created a "cascading Gantt-chart" appearance that didn't effectively communicate team continuity and made the visualization unnecessarily tall and difficult to navigate.

## Solution

The new algorithm intelligently shares swimlanes for linear succession chains while creating Y-shaped patterns for splits and merges.

### Key Principles

1. **Linear Chains Share Lanes**: When there's a single predecessor and single successor (no branching), teams occupy the same swimlane to show continuity.

2. **Y-Patterns for Splits/Merges**: When a team splits into multiple successors or multiple teams merge into one, branches are arranged to "surround" the common node, forming a horizontal Y-pattern.

3. **Priority System**: When choosing which successor continues on the main line during a split:
   - `LEGAL_TRANSFER` has priority over `SPIRITUAL_SUCCESSION`
   - If there's one clear legal transfer among multiple successors, it continues the lane
   - If multiple successors have equal priority, all branches surround the parent

## Implementation Details

### Files Modified

1. **`frontend/src/utils/layoutCalculator.js`**
   - Enhanced `assignYPositions()` method
   - Added new `assignSwimlanes()` method
   - Modified `calculateLinkPaths()` to detect same-swimlane transitions
   - Updated `generateLinkPath()` to handle same-swimlane cases

2. **`frontend/src/components/TimelineGraph.jsx`**
   - Added rendering logic for transition markers
   - Separated normal links from same-swimlane transitions
   - Created visual markers for same-swimlane transitions

### Algorithm: `assignSwimlanes(family, allNodes)`

The algorithm uses depth-first traversal with these steps:

```
1. Build predecessor/successor maps with event types
2. Find the root node (earliest founding year, no predecessors)
3. Traverse from root using DFS:
   a. If node has 0 successors: terminal node
   b. If node has 1 successor: assign same lane (linear continuation)
   c. If node has multiple successors (split):
      - Sort by priority (LEGAL_TRANSFER > SPIRITUAL_SUCCESSION > others)
      - If clear legal transfer exists: continues main lane
      - Other branches: alternate above/below parent lane
      - If no clear priority: all branches surround parent
4. Normalize lane assignments to start from 0
```

### Visual Design for Same-Swimlane Transitions

Since end-to-end arrows would be invisible when teams share a swimlane, we use **vertical transition markers**:

- **Vertical line** (30px tall) at the transition year
- **Circle** at the center point
- **Color coding**:
  - Solid line/filled circle: `LEGAL_TRANSFER` (dark gray #333)
  - Dashed line: `SPIRITUAL_SUCCESSION` (light gray #999)
- **Interactive**:
  - Hover enlarges marker
  - Displays tooltip with transition details
  - Same tooltip format as regular links

### Example Patterns

#### Before (Old Algorithm)
```
Team A ━━━━━━━━━━━━━━
Team B ━━━━━━━━━━━━━━  (all separate lanes)
Team C ━━━━━━━━━━━━━━
```

#### After (New Algorithm)

**Linear Chain:**
```
Team A ━━━|━ Team B ━━━|━ Team C
          ↑           ↑
      transition   transition
       markers      markers
```

**Split (with legal transfer priority):**
```
━━━━━━━━━ Team B (legal)
         ╱
Team A ━━
         ╲
━━━━━━━━━ Team C (spiritual)
```

**Merge:**
```
Team A ━━╲
          ╲
           Team C
          ╱
Team B ━━╱
```

## Benefits

1. **Improved Visual Continuity**: Linear team evolution is immediately apparent
2. **Reduced Vertical Space**: Fewer swimlanes means more compact, readable visualization
3. **Clear Hierarchy**: Legal transfers vs spiritual successions are visually differentiated
4. **Better Patterns**: Y-shapes make splits/merges more intuitive than cascading rows
5. **Maintains Interactivity**: Transition markers preserve all tooltip functionality

## Edge Cases Handled

1. **Circular References**: Start from earliest founding year, handle remaining nodes
2. **Disconnected Subgraphs**: Each unvisited node gets its own lane
3. **Equal Priority Successors**: All branch equally around parent
4. **Complex Merges**: Handled by existing MERGE/SPLIT event type logic

## Future Enhancements

Potential improvements for future iterations:

1. **Configurable Patterns**: Allow users to toggle between old and new layout
2. **Branch Ordering**: More sophisticated logic for above/below branch placement
3. **Lane Compaction**: Further optimize vertical space usage
4. **Animation**: Smooth transitions when switching between layouts
5. **Manual Overrides**: Allow users to manually adjust specific swimlane assignments

## Testing Recommendations

1. Test with linear chains (A → B → C → D)
2. Test with simple splits (A → B + C)
3. Test with merges (A + B → C)
4. Test with complex graphs (mixed splits, merges, and linear sections)
5. Test with disconnected families
6. Verify transition markers appear correctly
7. Check tooltip functionality on markers
8. Test zoom behavior with new markers

## Related Files

- `frontend/src/utils/layoutCalculator.js` - Core layout algorithm
- `frontend/src/components/TimelineGraph.jsx` - Rendering logic
- `backend/app/models/lineage.py` - Event type definitions
- `backend/app/models/enums.py` - EventType enum (LEGAL_TRANSFER, SPIRITUAL_SUCCESSION, etc.)
