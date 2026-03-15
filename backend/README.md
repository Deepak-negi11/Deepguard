# DeepGuard Backend

FastAPI service for:

- authentication
- verification request intake
- polling and history retrieval
- API usage logging
- rate limiting
- storage-backed async verification dispatch
- optional Celery worker execution

Local setup:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
alembic upgrade head
uvicorn app.main:app --reload
```
