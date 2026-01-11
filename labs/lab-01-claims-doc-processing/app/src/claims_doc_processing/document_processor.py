"""
Document processor for insurance claim documents.

This module provides the core processing logic that can be used both
locally and in Lambda functions.
"""
import boto3
import json
import os
import logging
from datetime import datetime
from typing import Dict, Optional

from .utils.prompt_template_manager import PromptTemplateManager
from .utils.model_comparison import compare_models

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize AWS clients (will be initialized on first use)
_bedrock_runtime = None
_s3_client = None


def get_bedrock_client():
    """Get or create Bedrock runtime client."""
    global _bedrock_runtime
    if _bedrock_runtime is None:
        _bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))
    return _bedrock_runtime


def get_s3_client():
    """Get or create S3 client."""
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'us-east-1'))
    return _s3_client


def invoke_bedrock_model(model_id: str, prompt: str, temperature: float = 0.0, max_tokens: int = 1000) -> str:
    """
    Invoke a Bedrock model with the given prompt.
    
    Args:
        model_id: The Bedrock model ID
        prompt: The prompt text
        temperature: Temperature for generation (0.0-1.0)
        max_tokens: Maximum tokens to generate
    
    Returns:
        The model response text
    """
    try:
        bedrock_runtime = get_bedrock_client()
        
        # Use Claude 3.5 API format with correct message structure
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            ]
        }
        
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        
        # Extract text from Claude 3.5 response format
        if 'content' in response_body and len(response_body['content']) > 0:
            first_content = response_body['content'][0]
            if isinstance(first_content, dict) and 'text' in first_content:
                return first_content['text']
            elif isinstance(first_content, str):
                return first_content
            else:
                logger.error(f"Unexpected content format: {first_content}")
                return ""
        else:
            logger.error(f"Unexpected response format: {response_body}")
            return ""
            
    except Exception as e:
        logger.error(f"Error invoking Bedrock model {model_id}: {str(e)}")
        raise


def process_document_understanding(
    document_text: str,
    model_id: str,
    template_manager: PromptTemplateManager
) -> str:
    """
    Analyze and understand the document structure and content.
    
    Args:
        document_text: The document text content
        model_id: Bedrock model ID to use
        template_manager: PromptTemplateManager instance
    
    Returns:
        Analysis result
    """
    prompt = template_manager.get_prompt(
        "document_understanding",
        document_text=document_text
    )
    
    return invoke_bedrock_model(
        model_id,
        prompt,
        temperature=0.1,
        max_tokens=2000
    )


def extract_information(
    document_text: str,
    model_id: str,
    template_manager: PromptTemplateManager
) -> str:
    """
    Extract structured information from the document.
    
    Args:
        document_text: The document text content
        model_id: Bedrock model ID to use
        template_manager: PromptTemplateManager instance
    
    Returns:
        Extracted information in JSON format
    """
    prompt = template_manager.get_prompt(
        "extract_info",
        document_text=document_text
    )
    
    result = invoke_bedrock_model(
        model_id,
        prompt,
        temperature=0.0,
        max_tokens=1500
    )
    
    # Try to parse and clean JSON if needed
    try:
        # Remove markdown code blocks if present
        if result.strip().startswith('```'):
            lines = result.strip().split('\n')
            result = '\n'.join(lines[1:-1])
        
        # Parse to validate JSON
        json.loads(result)
        return result
    except json.JSONDecodeError:
        logger.warning("Response is not valid JSON, returning as-is")
        return result


def generate_summary(
    extracted_info: str,
    model_id: str,
    template_manager: PromptTemplateManager
) -> str:
    """
    Generate a concise summary of the claim.
    
    Args:
        extracted_info: The extracted information (JSON string)
        model_id: Bedrock model ID to use
        template_manager: PromptTemplateManager instance
    
    Returns:
        Summary text
    """
    prompt = template_manager.get_prompt(
        "generate_summary",
        extracted_info=extracted_info
    )
    
    return invoke_bedrock_model(
        model_id,
        prompt,
        temperature=0.7,
        max_tokens=500
    )


def process_document(
    document_text: str,
    model_understanding: Optional[str] = None,
    model_extraction: Optional[str] = None,
    model_summary: Optional[str] = None,
    enable_model_comparison: bool = False,
    comparison_models: Optional[list] = None
) -> Dict:
    """
    Process a document through the full pipeline.
    
    Args:
        document_text: The document text to process
        model_understanding: Model ID for understanding (defaults to env var)
        model_extraction: Model ID for extraction (defaults to env var)
        model_summary: Model ID for summary (defaults to env var)
        enable_model_comparison: Whether to run model comparison
        comparison_models: List of model IDs for comparison
    
    Returns:
        Dictionary with processing results
    """
    # Get model IDs from args or environment
    model_understanding = model_understanding or os.getenv(
        'BEDROCK_MODEL_UNDERSTANDING',
        'anthropic.claude-3-5-sonnet-20240620-v1:0'
    )
    model_extraction = model_extraction or os.getenv(
        'BEDROCK_MODEL_EXTRACTION',
        'anthropic.claude-3-5-sonnet-20240620-v1:0'
    )
    model_summary = model_summary or os.getenv(
        'BEDROCK_MODEL_SUMMARY',
        'anthropic.claude-3-haiku-20240307-v1:0'
    )
    
    # Initialize template manager
    template_manager = PromptTemplateManager()
    
    # Step 1: Document Understanding
    logger.info("Step 1: Document Understanding")
    understanding_result = process_document_understanding(
        document_text, model_understanding, template_manager
    )
    
    # Step 2: Information Extraction
    logger.info("Step 2: Information Extraction")
    extracted_info = extract_information(
        document_text, model_extraction, template_manager
    )
    
    # Step 3: Summary Generation
    logger.info("Step 3: Summary Generation")
    summary = generate_summary(extracted_info, model_summary, template_manager)
    
    # Prepare output
    result = {
        "document_understanding": understanding_result,
        "extracted_information": json.loads(extracted_info) if extracted_info else {},
        "summary": summary,
        "processing_metadata": {
            "models_used": {
                "understanding": model_understanding,
                "extraction": model_extraction,
                "summary": model_summary
            },
            "processed_at": datetime.utcnow().isoformat() + "Z"
        }
    }
    
    # Optional: Model Comparison
    if enable_model_comparison and comparison_models:
        logger.info("Running model comparison...")
        try:
            comparison_results = compare_models(
                document_text=document_text,
                models=comparison_models,
                prompt_template="Extract key information from this insurance claim document: {document_text}"
            )
            result["comparison_results"] = comparison_results
        except Exception as e:
            logger.error(f"Error during model comparison: {str(e)}", exc_info=True)
    
    return result


def process_document_local(
    input_path: str,
    output_path: Optional[str] = None,
    model_understanding: Optional[str] = None,
    model_extraction: Optional[str] = None,
    model_summary: Optional[str] = None
) -> Dict:
    """
    Process a document from a local file.
    
    Args:
        input_path: Path to input document file
        output_path: Optional path to save results (if None, returns dict)
        model_understanding: Model ID for understanding
        model_extraction: Model ID for extraction
        model_summary: Model ID for summary
    
    Returns:
        Dictionary with processing results
    """
    # Read document
    with open(input_path, 'r', encoding='utf-8') as f:
        document_text = f.read()
    
    logger.info(f"Processing document: {input_path} ({len(document_text)} characters)")
    
    # Process document
    result = process_document(
        document_text=document_text,
        model_understanding=model_understanding,
        model_extraction=model_extraction,
        model_summary=model_summary
    )
    
    # Add source document info
    result["source_document"] = {
        "path": input_path,
        "size": len(document_text)
    }
    
    # Save to file if output_path provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        logger.info(f"Results saved to: {output_path}")
    
    return result

