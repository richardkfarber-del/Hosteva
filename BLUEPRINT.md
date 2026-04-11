# Hosteva Technical Blueprint v1.0
## Architecture
- **Frontend:** Modern PWA (Progressive Web App)
  - **Tooling:** Vite for asset build pipeline (replacing CDN links)
  - **Core PWA Features:** 
    - Service Workers (e.g., Workbox) for caching and network interception.
    - App Manifest (`manifest.json`) for installability.
    - Offline capabilities (IndexedDB/CacheStorage for local data syncing).
- **Backend:** FastAPI (Python 3)
  - Lightweight, async API for handling core business logic (e.g., Address Eligibility).
- **Database:** SQLite (Current local progress)

## Design Tokens (Stitch)
- Primary: #008080 (Teal)
- Secondary: #FFFFFF (White)
- Accent: #334155 (Slate)
