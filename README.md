# DeepGuard

DeepGuard is a full-stack blueprint for a multi-modal verification platform that flags suspicious image, news, and audio content. This repo ships with a polished Next.js interface, a FastAPI backend, async-style verification flows, Celery-ready task dispatch, persistent upload handling, and replaceable analyzer modules so you can start with a working prototype and later swap in real ML models.

## What is inside

- `frontend/` - Next.js App Router UI with an editorial forensic look and dedicated flows for image, news, and audio verification.
- `backend/` - FastAPI API with JWT auth, request history, API usage logging, rate limiting, storage-backed processing, and structured result objects.
- `docs/ai-implementation-brief.md` - a clean delegation brief you can hand to another AI assistant for module-specific work.
- `ml_models/` - model, training, inference, and preprocessing scaffolds for image, news, and audio detectors.
- `docker-compose.yml` - local orchestration for frontend, backend, Postgres, and Redis.

## Current implementation status

This repo is a strong starter and demo scaffold. The backend currently uses deterministic prototype analyzers so the app is usable before expensive model training, dataset downloads, and GPU work are added. The interfaces, task flow, storage hooks, and extension points are already shaped for the real pipeline.

## Quick start

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
alembic upgrade head
uvicorn app.main:app --reload
```

### Full stack with Docker

```bash
docker compose up --build
```

This starts:

- frontend on `http://localhost:3000`
- backend on `http://localhost:8000`
- Postgres
- Redis
- a Celery worker for async verification execution

## API overview

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/verify/image`
- `POST /api/v1/verify/news`
- `POST /api/v1/verify/audio`
- `GET /api/v1/results/{task_id}`
- `GET /api/v1/history`
- `GET /api/v1/system/status`

## Demo-friendly behavior

- News verification can now ingest a public article URL directly. If article text is not provided, the backend attempts to fetch and extract readable page text before analysis.
- `GET /api/v1/system/status` exposes the currently supported modes, whether prototype analyzers are enabled, and the dataset/sample-source links used by the project. This is useful in teacher demos because it shows exactly what is implemented versus what is still scaffold-level.

## Suggested next build steps

1. Replace the prototype analyzers in `backend/app/services/analyzers.py` with real PyTorch inference wired to the `ml_models/` packages.
2. Use `alembic revision --autogenerate -m "..."` and `alembic upgrade head` for all future schema changes.
3. Replace local upload storage with S3 or GCS-backed persistence.
4. Expand frontend history and reporting screens with charts and downloadable forensic reports.
