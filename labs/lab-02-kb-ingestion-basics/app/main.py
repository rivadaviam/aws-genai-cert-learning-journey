#!/usr/bin/env python3
"""Lab 02 CLI: estimate tokens, preview chunks, optionally retrieve from a KB."""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # type: ignore[assignment]

from kb_ingestion_basics.chunk_preview import preview_chunks
from kb_ingestion_basics.retrieve_sample import kb_id_from_env, retrieve_once
from kb_ingestion_basics.token_estimate import approximate_token_count, read_text_file


def cmd_estimate(args: argparse.Namespace) -> None:
    text = read_text_file(args.input)
    n = approximate_token_count(text)
    print(f"file: {args.input}")
    print(f"characters: {len(text)}")
    print(f"approx_tokens (rough): {n}")


def cmd_chunks(args: argparse.Namespace) -> None:
    text = read_text_file(args.input)
    chunks = preview_chunks(
        text,
        target_tokens=args.target_tokens,
        overlap_tokens=args.overlap_tokens,
    )
    print(f"file: {args.input}")
    print(f"chunks: {len(chunks)} (target_tokens={args.target_tokens}, overlap={args.overlap_tokens})")
    for c in chunks:
        sep = "-" * 40
        print(sep)
        print(f"### chunk {c.index} approx_tokens={c.approx_tokens}")
        print(c.text[:2000])
        if len(c.text) > 2000:
            print("... [truncated in CLI output; full length in chunk]")


def cmd_retrieve(args: argparse.Namespace) -> None:
    if load_dotenv:
        load_dotenv()
    region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    kb_id = args.kb_id or kb_id_from_env()
    resp = retrieve_once(
        knowledge_base_id=kb_id,
        query=args.query,
        region=region,
        number_of_results=args.number_of_results,
    )
    if args.raw_json:
        print(json.dumps(resp, default=str, indent=2))
    else:
        rcs = resp.get("retrievalResults") or []
        print(f"results: {len(rcs)}")
        for i, r in enumerate(rcs):
            content = (r.get("content") or {}).get("text", "")
            loc = r.get("location") or {}
            score = r.get("score")
            print("-" * 40)
            print(f"[{i}] score={score} location={loc}")
            print(content[:1500])
            if len(content) > 1500:
                print("...")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lab 02: token estimate, chunk preview, optional KB retrieve"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_est = sub.add_parser("estimate", help="Approximate token count for a text file")
    p_est.add_argument("--input", required=True, help="Path to UTF-8 text file")
    p_est.set_defaults(func=cmd_estimate)

    p_chunk = sub.add_parser("chunks", help="Preview naive token-based chunks")
    p_chunk.add_argument("--input", required=True, help="Path to UTF-8 text file")
    p_chunk.add_argument("--target-tokens", type=int, default=500)
    p_chunk.add_argument("--overlap-tokens", type=int, default=0)
    p_chunk.set_defaults(func=cmd_chunks)

    p_ret = sub.add_parser(
        "retrieve",
        help="One retrieve() call against an existing Knowledge Base (costs AWS API use)",
    )
    p_ret.add_argument("--query", required=True)
    p_ret.add_argument("--kb-id", dest="kb_id", default=None)
    p_ret.add_argument("--number-of-results", type=int, default=5)
    p_ret.add_argument("--raw-json", action="store_true")
    p_ret.set_defaults(func=cmd_retrieve)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
