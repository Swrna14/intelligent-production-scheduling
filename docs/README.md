# Intelligent Production Scheduling & Optimization System

This repository contains the initial end-to-end implementation of the production scheduling system through Phase 6.

## Current status

- SQLAlchemy schema and local database initialization.
- Deterministic master and transaction data generation with anomaly records.
- Validation and ground-truth exports.
- CP-SAT scheduling path with an environment-safe fallback.
- FastAPI health, dashboard summary, generated-data, and scheduling routes.
- Backend tests covering the implemented phases.

## API

Start the backend from the repository root with:

```powershell
py -3.11 -m uvicorn backend.app.main:app --reload
```

Available endpoints:

- `GET /health`
- `GET /api/dashboard/summary`
- `GET /api/data/{dataset_name}?limit=100&offset=0`
- `POST /api/scheduling/run` with `{"scale":"starter","seed":20261022}`
- `GET /docs` for the interactive OpenAPI page

Data endpoints read the default generated export when available. Scheduling requests with another scale or seed generate a matching deterministic dataset before solving.

Run the React dashboard from the `frontend` directory with Node.js installed:

```powershell
npm install
npm run dev
```

The Vite development server uses `http://localhost:5173` by default. Set `VITE_API_BASE_URL` if the backend is hosted somewhere other than `http://127.0.0.1:8000`; configure `FRONTEND_ORIGINS` on the backend if the frontend uses a different origin.

## Local environment

Use Python 3.11 and install the backend dependencies from `backend/requirements.txt`.
