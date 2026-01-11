"""Model comparison utilities for Bedrock models."""

import boto3
import json
import time
import logging
import os

logger = logging.getLogger()

# Initialize Bedrock client (will be created on first use)
_bedrock_runtime = None


def get_bedrock_client():
    """Get or create Bedrock runtime client."""
    global _bedrock_runtime
    if _bedrock_runtime is None:
        _bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
    return _bedrock_runtime


def invoke_bedrock_model_for_comparison(model_id, prompt, temperature=0.0, max_tokens=1000):
    """
    Invoke a Bedrock model with the given prompt (for comparison purposes).
    Uses Claude 3.5 API format.
    
    Args:
        model_id: The Bedrock model ID
        prompt: The prompt text
        temperature: Temperature for generation (0.0-1.0)
        max_tokens: Maximum tokens to generate
    
    Returns:
        Tuple of (response_text, elapsed_time)
    """
    try:
        start_time = time.time()
        
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
        
        elapsed_time = time.time() - start_time
        
        response_body = json.loads(response['body'].read())
        
        # Extract text from Claude 3.5 response format
        if 'content' in response_body and len(response_body['content']) > 0:
            first_content = response_body['content'][0]
            if isinstance(first_content, dict) and 'text' in first_content:
                output = first_content['text']
            elif isinstance(first_content, str):
                output = first_content
            else:
                logger.error(f"Unexpected content format: {first_content}")
                output = ""
        else:
            logger.error(f"Unexpected response format: {response_body}")
            output = ""
        
        return output, elapsed_time
        
    except Exception as e:
        logger.error(f"Error invoking Bedrock model {model_id}: {str(e)}")
        raise


def compare_models(document_text, models, prompt_template="Extract key information from this document: {document_text}"):
    """
    Compare multiple Bedrock models on the same document.
    
    Args:
        document_text: The document text to process
        models: List of model IDs to compare
        prompt_template: Template for the prompt (default: simple extraction)
    
    Returns:
        Dictionary with comparison results for each model:
        {
            "model_id": {
                "time_seconds": float,
                "output_length": int,
                "output_sample": str,
                "success": bool,
                "error": str (if failed)
            }
        }
    """
    results = {}
    
    # Format prompt with document text
    prompt = prompt_template.format(document_text=document_text)
    
    for model_id in models:
        logger.info(f"Comparing model: {model_id}")
        try:
            output, elapsed_time = invoke_bedrock_model_for_comparison(
                model_id=model_id,
                prompt=prompt,
                temperature=0.0,
                max_tokens=1000
            )
            
            results[model_id] = {
                "time_seconds": round(elapsed_time, 3),
                "output_length": len(output),
                "output_sample": output[:200] + "..." if len(output) > 200 else output,
                "success": True,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error comparing model {model_id}: {str(e)}")
            results[model_id] = {
                "time_seconds": None,
                "output_length": 0,
                "output_sample": "",
                "success": False,
                "error": str(e)
            }
    
    return results

