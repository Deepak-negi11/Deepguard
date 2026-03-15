.PHONY: frontend backend worker test-backend

frontend:
	cd frontend && npm install && npm run dev

backend:
	cd backend && python -m venv .venv && . .venv/bin/activate && pip install -e . && uvicorn app.main:app --reload

worker:
	cd backend && python -m venv .venv && . .venv/bin/activate && pip install -e . && celery -A app.tasks.celery_app:celery_app worker --loglevel=info

test-backend:
	cd backend && pytest
