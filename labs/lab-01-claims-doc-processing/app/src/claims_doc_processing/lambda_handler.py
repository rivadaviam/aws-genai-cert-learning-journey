"""
Lambda handler for processing S3 events.

This module handles S3 events and processes documents using the document_processor module.
"""
import boto3
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any

from .document_processor import process_document

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3 = boto3.client('s3')
bedrock_runtime = boto3.client('bedrock-runtime')

# Get environment variables
INPUT_BUCKET = os.environ.get('INPUT_BUCKET')
OUTPUT_BUCKET = os.environ.get('OUTPUT_BUCKET')
BEDROCK_MODEL_UNDERSTANDING = os.environ.get(
    'BEDROCK_MODEL_UNDERSTANDING',
    'anthropic.claude-3-5-sonnet-20240620-v1:0'
)
BEDROCK_MODEL_EXTRACTION = os.environ.get(
    'BEDROCK_MODEL_EXTRACTION',
    'anthropic.claude-3-5-sonnet-20240620-v1:0'
)
BEDROCK_MODEL_SUMMARY = os.environ.get(
    'BEDROCK_MODEL_SUMMARY',
    'anthropic.claude-3-haiku-20240307-v1:0'
)
ENABLE_MODEL_COMPARISON = os.environ.get('ENABLE_MODEL_COMPARISON', 'false').lower() == 'true'
COMPARISON_MODELS = os.environ.get('COMPARISON_MODELS', '').split(',') if os.environ.get('COMPARISON_MODELS') else []


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for processing S3 events.
    
    Args:
        event: S3 event containing bucket and object information
        context: Lambda context
    
    Returns:
        Processing result
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract S3 event information
        for record in event.get('Records', []):
            if record.get('eventSource') != 'aws:s3':
                continue
            
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            
            logger.info(f"Processing document: s3://{bucket}/{key}")
            
            # Validate bucket
            if bucket != INPUT_BUCKET:
                logger.warning(f"Event from unexpected bucket: {bucket}")
                continue
            
            # Read document from S3
            try:
                response = s3.get_object(Bucket=bucket, Key=key)
                document_text = response['Body'].read().decode('utf-8')
                logger.info(f"Document size: {len(document_text)} characters")
            except Exception as e:
                logger.error(f"Error reading document from S3: {str(e)}")
                raise
            
            # Process document
            result = process_document(
                document_text=document_text,
                model_understanding=BEDROCK_MODEL_UNDERSTANDING,
                model_extraction=BEDROCK_MODEL_EXTRACTION,
                model_summary=BEDROCK_MODEL_SUMMARY,
                enable_model_comparison=ENABLE_MODEL_COMPARISON,
                comparison_models=[m.strip() for m in COMPARISON_MODELS if m.strip()] if COMPARISON_MODELS else None
            )
            
            # Prepare output with S3 metadata
            output_data = {
                "source_document": {
                    "bucket": bucket,
                    "key": key,
                    "processed_at": datetime.utcnow().isoformat() + "Z"
                },
                **result
            }
            
            # Save results to output bucket
            output_key = f"processed/{key.replace('claims/', '')}.json"
            s3.put_object(
                Bucket=OUTPUT_BUCKET,
                Key=output_key,
                Body=json.dumps(output_data, indent=2),
                ContentType='application/json',
                ServerSideEncryption='AES256'
            )
            
            logger.info(f"Results saved to: s3://{OUTPUT_BUCKET}/{output_key}")
            
            # Save comparison results separately if available
            if "comparison_results" in result:
                comparison_key = f"comparisons/{key.replace('claims/', '')}.json"
                comparison_data = {
                    "source_document": {
                        "bucket": bucket,
                        "key": key,
                        "compared_at": datetime.utcnow().isoformat() + "Z"
                    },
                    "comparison_results": result["comparison_results"]
                }
                
                s3.put_object(
                    Bucket=OUTPUT_BUCKET,
                    Key=comparison_key,
                    Body=json.dumps(comparison_data, indent=2),
                    ContentType='application/json',
                    ServerSideEncryption='AES256'
                )
                
                logger.info(f"Comparison results saved to: s3://{OUTPUT_BUCKET}/{comparison_key}")
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Document processed successfully',
                    'output_location': f"s3://{OUTPUT_BUCKET}/{output_key}"
                })
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'No records to process'})
        }
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Error processing document',
                'message': str(e)
            })
        }

