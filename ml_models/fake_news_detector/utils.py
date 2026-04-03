from __future__ import annotations

from urllib.parse import urlparse

import torch

TRUSTED_DOMAINS = {"reuters.com", "apnews.com", "bbc.com", "nytimes.com"}


def normalize_article_text(text: str) -> str:
    return " ".join(text.strip().split())


def extract_domain(url: str | None) -> str:
    if not url:
        return ""
    return urlparse(url).netloc.replace("www.", "")


def build_source_features(url: str | None) -> torch.Tensor:
    domain = extract_domain(url)
    features = torch.zeros(8, dtype=torch.float32)
    if domain:
        features[0] = 1.0
        features[1] = 1.0 if domain in TRUSTED_DOMAINS else 0.0
        features[2] = min(len(domain) / 30.0, 1.0)
    return features
