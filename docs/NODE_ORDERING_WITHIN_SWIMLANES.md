# The Real Problem: Node Ordering Within Swimlanes

## Current Situation (From Screenshot)

```
Lima Pro (2008-2017)
Kilo Pro (1998-2008) ──O
Mike WorldTour (2009-)
Papa Pro (2005-2014)
Quebec Pro (2015-)

When Lima connects to Quebec:
The line MUST pass through Mike's Y space
because Mike is positioned between them!
```

## The Issue

You have **multiple teams on the same swimlane**, but they're not ordered by time:

```
Current order in swimlane:
1. Lima Pro (ends 2017)
2. Kilo Pro (ends 2008)
3. Mike WorldTour (starts 2009, ongoing)
4. Papa Pro (ends 2014)
5. Quebec Pro (starts 2015, ongoing)

When Lima (2008-2017) connects to Quebec (2015-):
The line path goes:
  Start at Lima's right edge (year 2017)
  → Go to Quebec (year 2015+)
  → Must pass through Mike's rectangle (2009-)
  → BEHIND Mike's node ✗
```

## The Solution

**Sort nodes within each swimlane by temporal position:**

```
Correct temporal order:
1. Kilo Pro (1998-2008) ← Earliest start, ends earliest
2. Papa Pro (2005-2014) ← Overlaps Kilo, ends before Lima
3. Lima Pro (2008-2017) ← Overlaps Papa/Kilo, ends mid-range
4. Mike WorldTour (2009-) ← Starts after Kilo ends, continues
5. Quebec Pro (2015-) ← Latest start

Visual result:
═══════════════════════════════════════════════
Kilo Pro (1998-2008) ──O
Papa Pro (2005-2014)    ├─ Connected
Lima Pro (2008-2017) ───┤   nodes are
Mike WorldTour (2009-)  │   now adjacent
Quebec Pro (2015-) ─────┘   in order!
═══════════════════════════════════════════════

Now Lima → Quebec line doesn't cross Mike!
The nodes are in temporal order.
```

## Sorting Algorithm

For each swimlane, sort nodes by:

```javascript
nodes.sort((a, b) => {
  // Primary: by founding year (earliest first)
  if (a.founding_year !== b.founding_year) {
    return a.founding_year - b.founding_year;
  }
  
  // Tiebreaker: by dissolution year (earliest dissolution first)
  // This handles overlapping nodes - shorter-lived ones come first
  const aEnd = a.dissolution_year || Infinity;
  const bEnd = b.dissolution_year || Infinity;
  
  if (aEnd !== bEnd) {
    return aEnd - bEnd;
  }
  
  // Final tiebreaker: by node ID for consistency
  return a.id.localeCompare(b.id);
});
```

## Why This Works

**Key insight**: If nodes are sorted by `(founding_year, dissolution_year)`:
- Non-overlapping nodes are in clear temporal order
- Overlapping nodes are sorted by end date (shorter-lived first)
- Connection lines between temporally separated nodes won't cross intermediate nodes

**Example from your data:**
```
Sorted order:
Kilo (1998-2008)     ← Ends first
Papa (2005-2014)     ← Overlaps, ends second
Lima (2008-2017)     ← Overlaps, ends third
Mike (2009-∞)        ← Starts after Kilo, ongoing
Quebec (2015-∞)      ← Latest start, ongoing

Connections:
- Lima → Quebec: Both on same lane, adjacent! No crossing ✓
- Papa → Quebec: Both on same lane, adjacent! No crossing ✓
- Kilo → (Lima + Mike): Y-pattern from top, no crossing ✓
```

## Implementation Location

This fix should go in `layoutCalculator.js` in the `assignYPositions()` method, after swimlanes are assigned but before Y positions are calculated.

It's a simple sort within each swimlane group.

---

**Is this the fix you're looking for?** Should I implement it now?
