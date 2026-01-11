"""Shared Bedrock client utilities."""

import boto3
import os
from typing import Optional


def get_bedrock_runtime_client(region: Optional[str] = None) -> boto3.client:
    """
    Get a Bedrock runtime client.
    
    Args:
        region: AWS region (defaults to AWS_REGION env var or us-east-1)
    
    Returns:
        boto3 Bedrock runtime client
    """
    region = region or os.getenv('AWS_REGION', 'us-east-1')
    return boto3.client('bedrock-runtime', region_name=region)

