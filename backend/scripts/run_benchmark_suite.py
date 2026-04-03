from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from app.services.benchmark_runner import benchmark_results_as_dicts, run_benchmark_suite


def main() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    project_root = backend_root if (backend_root / "docs").exists() else backend_root.parent
    results = run_benchmark_suite(project_root)

    output_dir = project_root / "output" / "benchmarks"
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "total": len(results),
        "passed": sum(item.status == "passed" for item in results),
        "failed": sum(item.status == "failed" for item in results),
        "skipped": sum(item.status == "skipped" for item in results),
        "results": benchmark_results_as_dicts(results),
    }

    latest_path = output_dir / "latest.json"
    latest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
