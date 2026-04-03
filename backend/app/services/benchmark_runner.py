from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from app.services.analyzers import BinaryArtifactInput, analyze_binary_artifact, analyze_news
from app.services.system_registry import load_benchmark_suite


@dataclass(slots=True)
class BenchmarkResult:
    key: str
    mode: str
    title: str
    expected_verdict: str
    actual_verdict: str | None
    status: Literal["passed", "failed", "skipped"]
    confidence: float | None
    notes: list[str]


def run_benchmark_suite(project_root: Path) -> list[BenchmarkResult]:
    results: list[BenchmarkResult] = []
    suite = load_benchmark_suite()

    for case in suite:
        mode = case.get("mode")
        input_kind = case.get("input_kind")
        expected_verdict = case.get("expected_verdict")
        title = case.get("title", case.get("key", "Unnamed benchmark"))
        notes = list(case.get("notes", []))

        if mode == "news" and input_kind == "text":
            text = case.get("text") or ""
            url = case.get("url")
            payload = analyze_news(text=text, url=url)
            results.append(
                BenchmarkResult(
                    key=case.get("key", title),
                    mode=mode,
                    title=title,
                    expected_verdict=expected_verdict,
                    actual_verdict=payload.verdict,
                    status="passed" if payload.verdict == expected_verdict else "failed",
                    confidence=payload.confidence,
                    notes=notes,
                )
            )
            continue

        if input_kind == "file":
            sample_path = case.get("sample_path")
            resolved_path = (project_root / sample_path).resolve() if sample_path else None
            if not resolved_path or not resolved_path.exists():
                skip_notes = notes + [f"Sample file missing: {sample_path or 'n/a'}"]
                results.append(
                    BenchmarkResult(
                        key=case.get("key", title),
                        mode=mode,
                        title=title,
                        expected_verdict=expected_verdict,
                        actual_verdict=None,
                        status="skipped",
                        confidence=None,
                        notes=skip_notes,
                    )
                )
                continue

            content_type = "image/jpeg"
            payload = analyze_binary_artifact(
                BinaryArtifactInput(
                    request_type=mode,
                    file_name=resolved_path.name,
                    raw_bytes=resolved_path.read_bytes(),
                    content_type=content_type,
                )
            )
            results.append(
                BenchmarkResult(
                    key=case.get("key", title),
                    mode=mode,
                    title=title,
                    expected_verdict=expected_verdict,
                    actual_verdict=payload.verdict,
                    status="passed" if payload.verdict == expected_verdict else "failed",
                    confidence=payload.confidence,
                    notes=notes,
                )
            )
            continue

        results.append(
            BenchmarkResult(
                key=case.get("key", title),
                mode=mode or "unknown",
                title=title,
                expected_verdict=expected_verdict or "uncertain",
                actual_verdict=None,
                status="skipped",
                confidence=None,
                notes=notes + ["Unsupported benchmark configuration."],
            )
        )

    return results


def benchmark_results_as_dicts(results: list[BenchmarkResult]) -> list[dict]:
    return [asdict(item) for item in results]
