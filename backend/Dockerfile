FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml README.md ./
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app
COPY tests ./tests

ARG PIP_EXTRAS=""
ENV TRANSFORMERS_CACHE=/app/models
ENV HF_HOME=/app/models

RUN pip install --upgrade pip && \
    pip install torch --extra-index-url https://download.pytorch.org/whl/cpu && \
    if [ -n "$PIP_EXTRAS" ]; then pip install -e ".[${PIP_EXTRAS}]"; else pip install -e .; fi

RUN python -c "from transformers import pipeline; pipeline('image-classification', model='Ateeqq/ai-vs-human-image-detector')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
