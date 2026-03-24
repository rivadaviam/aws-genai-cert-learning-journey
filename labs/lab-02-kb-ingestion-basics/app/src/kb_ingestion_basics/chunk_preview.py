"""Naive chunking preview using approximate token counts."""

from __future__ import annotations

from dataclasses import dataclass

from kb_ingestion_basics.token_estimate import approximate_token_count


@dataclass
class ChunkPreview:
    index: int
    text: str
    approx_tokens: int


def preview_chunks(
    text: str,
    target_tokens: int = 500,
    overlap_tokens: int = 0,
) -> list[ChunkPreview]:
    """
    Split text into overlapping windows using character budgets derived from
    approximate token targets. For teaching only — replace with domain chunkers
    (headings, commands, pages) in production.
    """
    if target_tokens < 1:
        raise ValueError("target_tokens must be at least 1")
    if overlap_tokens < 0 or overlap_tokens >= target_tokens:
        raise ValueError("overlap_tokens must be in [0, target_tokens)")

    char_budget = target_tokens * 4
    overlap_chars = overlap_tokens * 4

    text = text.strip()
    if not text:
        return []

    chunks: list[ChunkPreview] = []
    start = 0
    idx = 0
    n = len(text)

    while start < n:
        end = min(start + char_budget, n)
        piece = text[start:end]
        chunks.append(
            ChunkPreview(
                index=idx,
                text=piece,
                approx_tokens=approximate_token_count(piece),
            )
        )
        idx += 1
        if end >= n:
            break
        next_start = end - overlap_chars
        if next_start <= start:
            next_start = start + 1
        start = next_start

    return chunks
