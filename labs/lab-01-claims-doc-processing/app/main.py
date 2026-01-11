#!/usr/bin/env python3
"""CLI entrypoint for local document processing."""
import argparse
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from claims_doc_processing.document_processor import process_document_local
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    from claims_doc_processing.document_processor import process_document_local


def main():
    parser = argparse.ArgumentParser(description="Process insurance claim documents")
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--output", help="Output file path (default: stdout)")
    parser.add_argument(
        "--model-understanding",
        default=os.getenv("BEDROCK_MODEL_UNDERSTANDING"),
        help="Model ID for document understanding"
    )
    parser.add_argument(
        "--model-extraction",
        default=os.getenv("BEDROCK_MODEL_EXTRACTION"),
        help="Model ID for information extraction"
    )
    parser.add_argument(
        "--model-summary",
        default=os.getenv("BEDROCK_MODEL_SUMMARY"),
        help="Model ID for summary generation"
    )
    
    args = parser.parse_args()
    
    # Process document
    result = process_document_local(
        input_path=args.input,
        output_path=args.output,
        model_understanding=args.model_understanding,
        model_extraction=args.model_extraction,
        model_summary=args.model_summary
    )
    
    # Output
    if args.output:
        import json
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Results saved to: {args.output}")
    else:
        import json
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

