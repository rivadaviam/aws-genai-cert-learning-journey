import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from kb_ingestion_basics.chunk_preview import preview_chunks
from kb_ingestion_basics.token_estimate import approximate_token_count


def test_approximate_token_count_empty():
    assert approximate_token_count("") == 0
    assert approximate_token_count("   ") == 0


def test_approximate_token_count_non_empty():
    assert approximate_token_count("hello") >= 1


def test_preview_chunks_empty():
    assert preview_chunks("") == []


def test_preview_chunks_single_window():
    text = "word " * 100
    chunks = preview_chunks(text, target_tokens=500, overlap_tokens=0)
    assert len(chunks) >= 1
    assert chunks[0].index == 0
