variable "bucket_prefix" {
  description = "Prefix for S3 bucket names (e.g., 'claim-documents-poc-mr')"
  type        = string
  default     = "claim-documents-poc-mr"
}

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "claim-processor-mr"
}

variable "bedrock_models" {
  description = <<-EOT
    Map of Bedrock models to use for different tasks.
    
    IMPORTANT NOTES:
    - Anthropic models (Claude) require AWS Marketplace permissions (included in IAM policy)
    - Models are automatically enabled on first invocation (no manual activation needed)
    - Model selection rationale:
      * Claude 3.5 Sonnet v1: Used for understanding/extraction (better than v2 for on-demand)
      * Claude 3 Haiku: Used for summaries (sufficient quality, lower cost than 3.5)
    - See ARCHITECTURE_DECISIONS.md for detailed model selection reasoning
    
    Alternative models to consider:
    - Document Understanding: amazon.nova-pro-v1:0 (no Marketplace needed)
    - Information Extraction: anthropic.claude-3-sonnet-20240229-v1:0 (older but stable)
    - Summary Generation: amazon.nova-lite-v1:0 (no Marketplace needed)
  EOT
  type = object({
    document_understanding = string
    information_extraction = string
    summary_generation     = string
  })
  default = {
    # Using Claude 3.5 Sonnet v1 (not v2) because v2 may not support on-demand throughput
    document_understanding = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    information_extraction = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    # Using Claude 3 Haiku (not 3.5) because 3.5 Haiku v1 doesn't support on-demand
    summary_generation     = "anthropic.claude-3-haiku-20240307-v1:0"
  }
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "InsuranceClaimProcessing"
    Environment = "POC"
    ManagedBy   = "Terraform"
  }
}

variable "lambda_timeout" {
  description = "Timeout for Lambda function in seconds"
  type        = number
  default     = 300
}

variable "lambda_memory_size" {
  description = "Memory size for Lambda function in MB"
  type        = number
  default     = 512
}

variable "s3_event_prefix" {
  description = "Prefix filter for S3 events (e.g., 'claims/')"
  type        = string
  default     = "claims/"
}

variable "enable_model_comparison" {
  description = "Enable model comparison feature (runs comparison after normal processing)"
  type        = bool
  default     = false
}

variable "comparison_models" {
  description = "List of model IDs to compare when model comparison is enabled"
  type        = list(string)
  default     = []
}

