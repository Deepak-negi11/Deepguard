const fs = require('fs');
fs.writeFileSync(
  '_codex_ci.sh',
  "pip install -e '.[dev]'\npytest\npython -m ruff check alembic app debug_task.py sqlite_test.py test_pipeline.py tests\npython -m ruff format --check alembic app debug_task.py sqlite_test.py test_pipeline.py tests\n",
);
