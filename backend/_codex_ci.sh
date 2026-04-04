pip install -e '.[dev]'
pytest
python -m ruff check alembic app debug_task.py sqlite_test.py test_pipeline.py tests
python -m ruff format --check alembic app debug_task.py sqlite_test.py test_pipeline.py tests
