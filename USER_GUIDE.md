# Velograph – User Guide
### The Cycling Team Lineage Timeline

## Overview
Velograph visualizes and manages the historical evolution of professional cycling teams, including mergers, splits, and successions, using a structured data model and interactive UI.

## Key Concepts
- **Team Node**: Represents a legal/managerial entity (the core of a team across years).
- **Team Era**: A single season snapshot of a team (name, sponsors, tier, etc.).
- **Lineage Event**: Records structural changes (succession, merge, split) between teams.

## Canonicalization of MERGE/SPLIT Events
### What Changed?
To ensure data integrity and clarity, the system now automatically converts ("canonicalizes") any attempted MERGE or SPLIT event that only has a single leg (i.e., only one predecessor or one successor) into a standard succession event (LEGAL_TRANSFER or SPIRITUAL_SUCCESSION). This prevents accidental mislabeling and keeps the lineage graph semantically correct.

- **MERGE**: Only used when two or more teams combine into one (multiple predecessors, one successor, same year).
- **SPLIT**: Only used when one team branches into two or more (one predecessor, multiple successors, same year).
- **Succession**: Any one-to-one transition (one predecessor, one successor) is always a LEGAL_TRANSFER or SPIRITUAL_SUCCESSION, never a MERGE or SPLIT.

### Why?
- Prevents confusion in the graph and analytics.
- Ensures that warnings about incomplete merges/splits do not persist indefinitely.
- Keeps the data model clean and easy to interpret.

### How It Works
- When a MERGE or SPLIT is created, the system checks if there are at least two related events for the same node and year.
- If not, the event is automatically reclassified as a succession (LEGAL_TRANSFER by default; can be changed to SPIRITUAL_SUCCESSION if needed).
- Any warning notes about incomplete merges/splits are removed.

## Documentation Structure
- This `USER_GUIDE.md` provides a high-level overview and key user-facing logic.
- As the project grows, consider splitting documentation:
  - `docs/BACKEND.md`: API, data model, migrations, backend setup.
  - `docs/FRONTEND.md`: UI, visualization, React usage, D3.js.
  - `docs/DATA_MANAGEMENT.md`: Admin tools, data import/export, moderation.
  - `docs/CONTRIBUTING.md`: For developers and contributors.

## Further Reading
- See the in-app help or the `/docs` folder for more details on specific features.
- For technical details, refer to the backend and frontend documentation as they are developed.
