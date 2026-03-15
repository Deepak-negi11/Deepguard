FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml README.md ./
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app
COPY tests ./tests

RUN pip install --upgrade pip && pip install -e .[ml]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
