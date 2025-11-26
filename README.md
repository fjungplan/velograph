# Cycling Team Lineage Timeline

An open-source visualization of the evolutionary history of professional cycling teams from 1900 to present.

## Overview

This project tracks the lineage of professional cycling teams through time, visualizing how teams evolve through rebrands, mergers, splits, and successions. The system uses a **Managerial Node** concept to represent the persistent legal entity that survives name changes.

### Key Features

- **Interactive Timeline Visualization**: Desktop D3.js "river" chart showing team evolution
- **Mobile-Optimized List View**: Chronological team history for mobile devices
- **Community-Driven**: Wiki-style editing with moderation system
- **Data Integrity**: Tracks team eras, sponsors, and structural events (mergers/splits)
- **Gentle Web Scraping**: Automated data collection from ProCyclingStats, Wikipedia, and FirstCycling

### Core Concepts

- **Managerial Node**: The persistent legal entity (e.g., "Lefevere Management")
- **Team Era**: A specific season snapshot with metadata (name, UCI code, tier, sponsors)
- **Jersey Slice**: Visual representation using sponsor color proportions
- **Lineage Event**: Structural changes (legal transfer, spiritual succession, merge, split)

## Tech Stack

- **Backend**: Python 3.11, FastAPI, PostgreSQL 15, SQLAlchemy (async)
- **Frontend**: React, Vite, D3.js
- **Infrastructure**: Docker Compose
- **Authentication**: Google OAuth + JWT

## Project Status

🚧 **In Development** - Following incremental implementation via structured prompts

## Getting Started

_(Instructions will be added after initial setup)_

## License

MIT License (or your preferred license)

## Contributing

Contributions welcome! More details coming soon.
