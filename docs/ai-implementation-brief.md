# DeepGuard Technical Delegation Brief

Use this document when delegating DeepGuard work to another AI assistant. It is written to match the current repository, not an imaginary greenfield system.

## 1. Project Identity

- Project name: `DeepGuard`
- Product type: multi-modal authenticity verification platform
- Modalities:
  - image deepfake detection
  - fake news and credibility analysis
  - synthetic audio or voice-clone detection
- Primary outcome: a user uploads or submits suspicious media, then receives a verdict, confidence score, signal breakdown, evidence notes, and recommended next actions

## 2. Current Repo State

This repository is already a working prototype. Do not rebuild it from scratch.

What exists now:
- `frontend/`: Next.js App Router application with a styled landing page, analysis flows, result board, and history view
- `backend/`: FastAPI API with JWT auth, verification endpoints, task polling, history, SQLAlchemy models, upload persistence, rate limiting, API usage logging, and background or Celery-backed processing
- `ml_models/`: actual model, inference, utility, and training scaffolds for the three detector families
- `docker-compose.yml`: local stack for frontend, backend, Postgres, and Redis

What is still prototype-level:
- analyzer logic in [`backend/app/services/analyzers.py`](/mnt/c/Users/dayan/Projects/deepguard/backend/app/services/analyzers.py) is heuristic and deterministic, not real PyTorch inference
- Celery and Redis are wired for dispatch, but local development still defaults to FastAPI background tasks unless `DEEPGUARD_ENABLE_CELERY_WORKERS=true`
- there are no Alembic migrations yet
- model weights, dataset pipelines, and GPU training code are not implemented

## 3. Architectural Rules

If another AI works on this repo, it must follow these rules:

- Respect existing route paths, schema field names, and repo structure unless explicitly asked to change them.
- Keep the existing stack choices unless there is a concrete blocker.
- Preserve the result contract shape across frontend and backend.
- Return runnable code, not pseudo-code.
- Add tests for behavior changes.
- Prefer extending the current scaffold over replacing it.
- Keep uncertainty explicit. Never collapse `authenticity_score` and `confidence` into one number.

## 4. Tech Stack In This Repo

### Frontend

- Framework: Next.js `^15.0.0`
- React: `^19.0.0`
- Language: TypeScript `^5.6.3`
- Styling: Tailwind CSS `^3.4.14`
- State: Zustand `^5.0.1`
- HTTP client: Axios `^1.7.7`
- Icons: Lucide React `^0.468.0`

### Backend

- Python: `>=3.11`
- Framework: FastAPI `>=0.115.0,<1.0.0`
- Server: Uvicorn `>=0.30.0,<1.0.0`
- ORM: SQLAlchemy `>=2.0.30,<3.0.0`
- Settings: pydantic-settings `>=2.4.0,<3.0.0`
- Auth: python-jose `>=3.3.0,<4.0.0`
- Password hashing: passlib bcrypt `>=1.7.4,<2.0.0`
- Upload handling: python-multipart
- Queue hooks: Celery `>=5.4.0,<6.0.0`
- Cache/broker: Redis `>=5.0.7,<6.0.0`
- Database driver: psycopg `>=3.2.0,<4.0.0`

### Infrastructure

- Database: PostgreSQL via Docker Compose
- Cache/broker: Redis via Docker Compose
- Containers: Docker
- Local orchestration: Docker Compose
- Async worker: Celery worker service in Compose

### ML Target Stack

These are target technologies for the real analyzer modules. They are not fully wired into the app yet.

- PyTorch
- torchvision
- OpenCV
- dlib or an equivalent facial landmark stack
- Hugging Face Transformers
- librosa
- scikit-learn
- pandas and numpy

## 5. Monorepo Structure

```text
deepguard/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   ├── services/
│   │   ├── tasks/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── security.py
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/app/
│   ├── src/components/
│   ├── src/lib/
│   ├── src/store/
│   └── src/types/
├── ml_models/
│   ├── image_deepfake_detector/
│   ├── fake_news_detector/
│   └── audio_detector/
├── docs/
└── docker-compose.yml
```

## 6. Implemented API Contract

### Authentication

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`

Both return:

```json
{
  "user_id": 1,
  "email": "analyst@example.com",
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

### Verification endpoints

- `POST /api/v1/verify/image`
- `POST /api/v1/verify/news`
- `POST /api/v1/verify/audio`

The media endpoints are authenticated and queue a task:

```json
{
  "task_id": "uuid",
  "request_id": "uuid",
  "status": "queued",
  "message": "Video queued for analysis"
}
```

### Polling

- `GET /api/v1/results/{task_id}`

Current response shape:

```json
{
  "task_id": "uuid",
  "status": "completed",
  "progress": 100,
  "current_step": "Analysis complete",
  "result": {
    "authenticity_score": 0.31,
    "verdict": "likely fake",
    "confidence": 0.89,
    "summary": "The recording shows spectral and cadence irregularities consistent with synthetic or cloned speech.",
    "disclaimer": "Prototype analyzer only. This output is suitable for triage and demo flows, not for legal or financial proof on its own.",
    "breakdown": {
      "artifact_detector": 0.78,
      "temporal_consistency": 0.66,
      "source_provenance": 0.42
    },
    "evidence": [
      {
        "category": "spectral",
        "severity": "high",
        "description": "Detected synthetic harmonics and over-regularized resonance bands.",
        "timestamp": 12.4,
        "details": {
          "artifact_signal": 0.74,
          "content_type": "audio/wav"
        },
        "visualization_hint": "timeline-marker"
      }
    ],
    "recommended_actions": [
      "Preserve the original file and its metadata before re-encoding or editing.",
      "Verify provenance through the claimed source and capture chain."
    ],
    "input_profile": {
      "mode": "audio",
      "filename": "sample.wav",
      "content_type": "audio/wav",
      "size_bytes": 48231,
      "url_domain": null,
      "text_length": null,
      "analyzer_family": "artifact-and-consistency-heuristics"
    },
    "processing_time_seconds": 0.005,
    "model_version": "prototype-audio-v1"
  }
}
```

### History

- `GET /api/v1/history`

Returns paginated user history with request metadata and final verdict information when available.

## 7. Backend Domain Model

Current SQLAlchemy models:

- `User`
  - `id`
  - `email`
  - `password_hash`
  - `tier`
  - `monthly_usage`
  - `created_at`

- `VerificationRequest`
  - `id`
  - `user_id`
  - `request_type`
  - `status`
  - `url`
  - `file_name`
  - `payload_excerpt`
  - `created_at`

- `VerificationResult`
  - `id`
  - `request_id`
  - `authenticity_score`
  - `verdict`
  - `confidence`
  - `evidence` as JSON
  - `breakdown` as JSON
  - `processing_time_seconds`
  - `model_version`
  - `completed_at`

- `EvidenceItemRecord`
  - normalized evidence rows for structured forensic evidence storage

- `StoredAnalysisPayload`
  - persistent JSON payload snapshot used by the polling endpoint even if in-memory job state is gone

- `ApiUsage`
  - endpoint usage logging with response time and status code

Important constraint:
- There is no migration system yet, so avoid schema drift unless you also introduce Alembic and migration scripts.

## 8. Verification Flow

The current verification lifecycle is:

1. User authenticates or uses the seeded demo account flow in the frontend.
2. User submits a video, news payload, or audio file.
3. Backend validates the input.
4. A `VerificationRequest` row is created.
5. A task entry is created in the in-memory job store.
6. The request is dispatched either to FastAPI background tasks or Celery, depending on settings.
7. A `VerificationResult` row, normalized evidence rows, and a persistent payload snapshot are stored.
8. Frontend polls `/results/{task_id}` until completion.
9. The result board renders verdict, breakdown, evidence, recommended actions, and input profile.

## 9. Current Validation and Security Defaults

Already present or partially present:

- JWT bearer auth
- bcrypt password hashing
- request-scoped database sessions
- upload size limits from settings
- media type validation by extension and content type
- CORS configuration via environment variables
- in-memory rate limiting with a default ceiling of `100` requests per hour
- API usage logging to the `api_usage` table
- local upload persistence with optional deletion after processing

Security expectations for future code:

- Never trust client file names or content types alone.
- Keep upload validation in the API layer even after real model inference is added.
- Preserve authorization checks on results and history endpoints.
- Do not log secrets, raw tokens, or full sensitive payloads.
- Keep demo defaults clearly separated from production settings.

## 10. Frontend Responsibilities

The frontend should continue to provide:

- landing page and positioning
- mode-specific analysis entry points
- authenticated submission flow
- polling and progressive status display
- result board with:
  - verdict
  - confidence
  - authenticity score
  - processing time
  - model version
  - signal breakdown
  - evidence ledger
  - input profile
  - recommended actions
- history screen

If the UI is extended, preserve the current editorial and forensic visual language instead of replacing it with generic dashboard design.

## 11. ML Integration Plan

### Adapter boundary

Real inference should plug in behind:

- [`backend/app/services/analyzers.py`](/mnt/c/Users/dayan/Projects/deepguard/backend/app/services/analyzers.py)

The rest of the API should not need to know whether the result came from heuristics or PyTorch.

### Suggested production analyzer layout

- `ml_models/image_deepfake_detector/`
  - EfficientNet-B4 image model
  - DCT/FFT frequency module
  - noise uniformity feature extractor
  - grad-cam visualization wrapper
  - ensemble scorer

- `ml_models/fake_news_detector/`
  - article normalization
  - BERT-style text classifier
  - source reputation service
  - optional multimodal image branch

- `ml_models/audio_detector/`
  - waveform normalization
  - spectrogram generation
  - CNN or conformer-style classifier
  - prosody and artifact features

### Non-negotiable output rule

Real analyzers must still produce the exact result schema the frontend already expects:

- `authenticity_score`
- `verdict`
- `confidence`
- `summary`
- `disclaimer`
- `breakdown`
- `evidence`
- `recommended_actions`
- `input_profile`
- `processing_time_seconds`
- `model_version`

## 12. Dataset Guidance

Use primary or official sources when possible.

Recommended dataset starting points:

- GenImage: large-scale dataset of real and AI-generated images
- CIFAKE: dataset for CNN vs human-generated images
- LIAR: original fake-news benchmark from UCSB
- ASVspoof 2019: official synthetic speech and spoofing benchmark

Use these sources as discovery points:

- GenImage: `https://github.com/GenImage-Dataset/GenImage`
- CIFAKE: `https://kaggle.com/datasets/birdy654/cifake-real-and-ai-generated-synthetic-images`
- LIAR: `https://www.cs.ucsb.edu/~william/data/liar_dataset.zip`
- ASVspoof 2019: `https://datashare.ed.ac.uk/handle/10283/3336`

Notes:

- Keep dataset download logic outside request-time inference.
- Record licenses and access restrictions before training.
- For news credibility, combine benchmark datasets with a curated source-trust layer rather than relying on text classification alone.

## 13. Priority Work Order

If another AI is asked to continue this project, use this order:

1. Introduce Alembic migrations before changing or expanding the SQLAlchemy schema further.
2. Replace prototype analyzers with real inference adapters one modality at a time.
3. Replace local upload storage with S3 or GCS-backed persistence.
4. Expand history and reporting for analyst workflows.
5. Add training, evaluation, and model versioning workflows under `ml_models/`.

## 14. Definition Of Done For Future Tasks

A DeepGuard task is only complete if it:

- fits the current repo structure
- preserves or updates tests
- keeps API and frontend types aligned
- handles failure paths, not only happy paths
- uses typed code
- keeps the prototype honest about uncertainty

## 15. Good Delegation Prompts

Use prompts like these when handing work to another AI:

- "Using the existing DeepGuard repo structure, implement Alembic migrations for the current SQLAlchemy models without changing the API contract."
- "Replace the prototype audio analyzer adapter with a real PyTorch inference pipeline while preserving the current `AnalysisPayload` response shape."
- "Build the FastAPI Celery worker flow for `/verify/image` and `/results/{task_id}` while keeping the existing frontend polling contract stable."
- "Extend the Next.js results UI to visualize evidence details and breakdown trends without changing the backend field names."
- "Add dataset preprocessing scripts under `ml_models/image_deepfake_detector/` for GenImage and document how to train and export inference weights."
