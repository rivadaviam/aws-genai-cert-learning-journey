"""Optional one-off Knowledge Base retrieval (requires existing KB)."""

from __future__ import annotations

import os
from typing import Any

import boto3


def retrieve_once(
    knowledge_base_id: str,
    query: str,
    region: str | None = None,
    number_of_results: int = 5,
) -> dict[str, Any]:
    """Call Bedrock Agent Runtime retrieve API once."""
    kwargs: dict[str, Any] = {"region_name": region} if region else {}
    client = boto3.client("bedrock-agent-runtime", **kwargs)
    return client.retrieve(
        knowledgeBaseId=knowledge_base_id,
        retrievalQuery={"text": query},
        retrievalConfiguration={
            "vectorSearchConfiguration": {"numberOfResults": number_of_results}
        },
    )


def kb_id_from_env() -> str:
    kb = os.environ.get("KB_ID", "").strip()
    if not kb:
        raise ValueError("Set KB_ID in the environment or .env file")
    return kb
