from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urlparse

import httpx


class _ArticleTextExtractor(HTMLParser):
    """Collect visible text while skipping obvious non-content tags."""

    def __init__(self) -> None:
        super().__init__()
        self._ignored_depth = 0
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[override]
        if tag in {"script", "style", "noscript", "svg"}:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str) -> None:  # type: ignore[override]
        if tag in {"script", "style", "noscript", "svg"} and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:  # type: ignore[override]
        if self._ignored_depth:
            return
        text = re.sub(r"\s+", " ", data).strip()
        if text:
            self._chunks.append(text)

    def text(self) -> str:
        return " ".join(self._chunks)


@dataclass(slots=True)
class ResolvedNewsInput:
    text: str
    url: str | None
    source_domain: str | None
    fetched_from_url: bool


def _extract_article_text(html: str) -> str:
    parser = _ArticleTextExtractor()
    parser.feed(html)
    text = parser.text()
    return re.sub(r"\s+", " ", text).strip()


def _fetch_url_text(url: str, timeout_seconds: float = 8.0) -> str:
    with httpx.Client(
        follow_redirects=True,
        timeout=timeout_seconds,
        headers={"User-Agent": ("DeepGuard/0.1 (+https://github.com/) teacher-demo article ingestion")},
    ) as client:
        response = client.get(url)
        response.raise_for_status()
        return _extract_article_text(response.text)


def resolve_news_input(*, text: str | None, url: str | None) -> ResolvedNewsInput:
    normalized_text = (text or "").strip()
    normalized_url = str(url).strip() or None if url is not None else None
    source_domain = urlparse(normalized_url).hostname if normalized_url else None

    if normalized_text:
        return ResolvedNewsInput(
            text=normalized_text,
            url=normalized_url,
            source_domain=source_domain,
            fetched_from_url=False,
        )

    if not normalized_url:
        return ResolvedNewsInput(text="", url=None, source_domain=None, fetched_from_url=False)

    try:
        fetched_text = _fetch_url_text(normalized_url)
    except Exception:
        fetched_text = ""

    return ResolvedNewsInput(
        text=fetched_text,
        url=normalized_url,
        source_domain=source_domain,
        fetched_from_url=bool(fetched_text),
    )
