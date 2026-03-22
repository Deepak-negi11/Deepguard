# Contributing to DeepGuard

## Prerequisites

- Node.js 20+
- Python 3.12+
- Docker + Docker Compose (recommended for full-stack)

## Local development (recommended: Docker Compose)

From the repo root:

```bash
docker compose up --build
```

Services:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`

## Backend-only (without Docker)

From `backend/`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest
```

## Frontend-only (without Docker)

From `frontend/`:

```bash
npm install
npm run dev
```

Typecheck:

```bash
npm run typecheck
```

## Environment variables

- Backend settings use `.env` with `DEEPGUARD_` prefix. See `.env.example`.
- Frontend uses `NEXT_PUBLIC_API_URL`.

## Large files policy

Do not commit large model weights (e.g. `ml_models/weights/`). Store them in object storage or release assets and download at runtime.

