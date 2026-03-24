"""Rough token count estimates for local sanity checks (not billing-grade)."""

from __future__ import annotations

from pathlib import Path


def approximate_token_count(text: str) -> int:
    """
    Fast heuristic: ~4 characters per token for Latin-heavy technical text.

    Embedding models use their own tokenizers; this is only for comparing
    small vs large inputs before you sync to a Knowledge Base.
    """
    if not text or not text.strip():
        return 0
    # Common rule-of-thumb for English; clamp to at least 1 for non-empty strings
    n = max(1, len(text) // 4)
    return n


def read_text_file(path: str | Path) -> str:
    p = Path(path)
    return p.read_text(encoding="utf-8", errors="replace")
