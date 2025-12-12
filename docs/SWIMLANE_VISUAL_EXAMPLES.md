# Visual Examples: Before & After Swimlane Improvement

## Example 1: Simple Linear Chain

### Before (Old Behavior)
Each team gets its own row:
```
2000              2010              2020
├─────────────────┼─────────────────┤
│
├─ Team Alpha WorldTour ──────────────────────┤  ← Row 1
│
├─────────────── Team Bravo Pro ──────────────┤  ← Row 2
│
├──────────────────────── Team Charlie ───────┤  ← Row 3
```

### After (New Behavior)
Linear succession shares the same row with transition markers:
```
2000              2010              2020
├─────────────────┼─────────────────┤
│
├─ Team Alpha ───|── Team Bravo ──|── Team Charlie ───┤
                 ↑                 ↑
             transition        transition
              marker            marker
              (2010)            (2017)
```

---

## Example 2: Split (One Team → Two Teams)

### Before (Old Behavior)
```
2000              2010              2020
├─────────────────┼─────────────────┤
│
├─ Delta Pro Cycling ──────────┤                        ← Row 1
│
├──────────────────────── Echo Racing ─────────────┤    ← Row 2
│
├──────────────────────── Foxtrot Continental ─────┤    ← Row 3
```

### After (New Behavior)
Y-pattern with branches surrounding the parent:
```
2000              2010              2020
├─────────────────┼─────────────────┤
│                              ┌─ Echo Racing ──────────┤
│                             ╱
├─ Delta Pro Cycling ────────┤                            (legal transfer)
│                             ╲
│                              └─ Foxtrot Continental ───┤
```

---

## Example 3: Merge (Two Teams → One Team)

### Before (Old Behavior)
```
2000              2010              2020
├─────────────────┼─────────────────┤
│
├─ Uniform Continental ────┤                             ← Row 1
│
├─ Whiskey Racing ─────────┤                             ← Row 2
│
├──────────────────────── Victor Racing ────────────┤    ← Row 3
```

### After (New Behavior)
Y-pattern converging:
```
2000              2010              2020
├─────────────────┼─────────────────┤
│
├─ Uniform Continental ────╲
│                           ╲
│                            ├─ Victor Racing ──────────┤
│                           ╱
├─ Whiskey Racing ─────────╱
```

---

## Example 4: Complex Family (Mixed Patterns)

### Before (Old Behavior)
```
2000              2010              2020
├─────────────────┼─────────────────┤
│
├─ Alpha WorldTour ────────┤                             ← Row 1
│
├─ Bravo Pro Cycling ──────┤                             ← Row 2
│
├──────────────────── Charlie Racing ────────────────┤   ← Row 3
│
├──────────────────────────── Delta Team ────────────┤   ← Row 4
```
(Alpha merges into Charlie, Bravo merges into Charlie, Charlie continues to Delta)

### After (New Behavior)
```
2000              2010              2020
├─────────────────┼─────────────────┤
│
├─ Alpha WorldTour ────────╲
│                           ╲
│                            ├─ Charlie |─ Delta Team ──┤
│                           ╱            ↑
├─ Bravo Pro Cycling ──────╱         transition
│                                      marker
```

---

## Visual Legend

### Transition Markers (Same Swimlane)
```
───|───  Legal Transfer (solid vertical line + filled circle)
   ↑
   
───¦───  Spiritual Succession (dashed vertical line + filled circle)
   ↑
```

### Curved Links (Different Swimlanes)
```
────────  Legal Transfer (solid gray line)

- - - -   Spiritual Succession (dashed gray line)
```

### Y-Patterns
```
     ╱   Split (one source → multiple targets)
────┤    
     ╲

     ╲   Merge (multiple sources → one target)
      ├──
     ╱
```

---

## Color Coding

- **Legal Transfer**: Dark gray (#333), solid line
- **Spiritual Succession**: Light gray (#999), dashed line
- **Hover Effect**: Line thickens, circle enlarges, tooltip appears

---

## Real-World Example: Team Sky → Ineos

### Before
```
├─ Team Sky ──────────────────┤     ← Row 1
│
├──────────────────── Team Ineos Grenadiers ──────────┤  ← Row 2
```

### After
```
├─ Team Sky ───|─── Team Ineos Grenadiers ──────────┤
               ↑
          2019 transition
         (legal transfer)
```

This is the same team with a sponsor change, so they should share a swimlane!
