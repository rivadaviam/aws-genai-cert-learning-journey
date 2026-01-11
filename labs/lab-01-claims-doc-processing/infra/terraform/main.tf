terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = var.tags
  }
}

# Local values for resource naming
locals {
  input_bucket_name  = "${var.bucket_prefix}-input"
  output_bucket_name = "${var.bucket_prefix}-output"
}

# Get current AWS account ID
data "aws_caller_identity" "current" {}

# ============================================================================
# S3 BUCKETS
# ============================================================================

# Input bucket for claim documents
resource "aws_s3_bucket" "input" {
  bucket = local.input_bucket_name

  tags = merge(var.tags, {
    Name        = "Claim Documents Input"
    Purpose     = "Input"
    Description = "Bucket for incoming insurance claim documents"
  })
}

# Enable versioning on input bucket
resource "aws_s3_bucket_versioning" "input" {
  bucket = aws_s3_bucket.input.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable encryption on input bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "input" {
  bucket = aws_s3_bucket.input.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access on input bucket
resource "aws_s3_bucket_public_access_block" "input" {
  bucket = aws_s3_bucket.input.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Output bucket for processed results
# Separated from input bucket to prevent infinite loops (AWS best practice)
# See ARCHITECTURE_DECISIONS.md ADR-002 for rationale
resource "aws_s3_bucket" "output" {
  bucket = local.output_bucket_name

  tags = merge(var.tags, {
    Name        = "Claim Documents Output"
    Purpose     = "Output"
    Description = "Bucket for processed claim document results"
  })
}

# Enable versioning on output bucket
resource "aws_s3_bucket_versioning" "output" {
  bucket = aws_s3_bucket.output.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable encryption on output bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "output" {
  bucket = aws_s3_bucket.output.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access on output bucket
resource "aws_s3_bucket_public_access_block" "output" {
  bucket = aws_s3_bucket.output.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ============================================================================
# IAM ROLE FOR LAMBDA
# ============================================================================

# IAM role for Lambda execution
resource "aws_iam_role" "lambda_execution" {
  name = "${var.lambda_function_name}-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "Lambda Execution Role"
  })
}

# IAM policy for Lambda to access S3
resource "aws_iam_role_policy" "lambda_s3" {
  name = "${var.lambda_function_name}-s3-policy"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion"
        ]
        Resource = "${aws_s3_bucket.input.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl"
        ]
        Resource = "${aws_s3_bucket.output.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.input.arn,
          aws_s3_bucket.output.arn
        ]
      }
    ]
  })
}

# IAM policy for Lambda to invoke Bedrock models
# IMPORTANT: Anthropic models (Claude) require AWS Marketplace permissions to enable model access.
# The second statement grants these permissions, allowing the Lambda to subscribe to Anthropic
# models through AWS Marketplace on first invocation.
resource "aws_iam_role_policy" "lambda_bedrock" {
  name = "${var.lambda_function_name}-bedrock-policy"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.bedrock_models.document_understanding}",
          "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.bedrock_models.information_extraction}",
          "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.bedrock_models.summary_generation}"
        ]
      },
      {
        # AWS Marketplace permissions required for Anthropic models
        # These allow the Lambda to enable Anthropic model subscriptions on first invocation
        # Note: Your AWS account must also allow Marketplace subscriptions
        Effect = "Allow"
        Action = [
          "aws-marketplace:ViewSubscriptions",
          "aws-marketplace:Subscribe"
        ]
        Resource = "*"
      }
    ]
  })
}

# IAM policy for Lambda to write CloudWatch Logs
resource "aws_iam_role_policy" "lambda_logs" {
  name = "${var.lambda_function_name}-logs-policy"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"
      }
    ]
  })
}

# ============================================================================
# LAMBDA FUNCTION
# ============================================================================

# Archive Lambda function code
# Includes all Python files from the app/src directory
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../app/src"
  output_path = "${path.module}/lambda_function.zip"
  excludes    = ["__pycache__", "*.pyc", "tests/"]
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = 14

  tags = merge(var.tags, {
    Name = "Lambda Log Group"
  })
}

# Lambda function
# Timeout and memory configured for three-step Bedrock processing pipeline
# See ARCHITECTURE_DECISIONS.md ADR-011 for configuration rationale
resource "aws_lambda_function" "document_processor" {
  filename      = data.archive_file.lambda_zip.output_path
  function_name = var.lambda_function_name
  role          = aws_iam_role.lambda_execution.arn
  handler       = "claims_doc_processing.lambda_handler.lambda_handler"
  runtime       = "python3.12"
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size

  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      INPUT_BUCKET                = aws_s3_bucket.input.id
      OUTPUT_BUCKET               = aws_s3_bucket.output.id
      BEDROCK_MODEL_UNDERSTANDING = var.bedrock_models.document_understanding
      BEDROCK_MODEL_EXTRACTION    = var.bedrock_models.information_extraction
      BEDROCK_MODEL_SUMMARY       = var.bedrock_models.summary_generation
      ENABLE_MODEL_COMPARISON     = var.enable_model_comparison ? "true" : "false"
      COMPARISON_MODELS           = join(",", var.comparison_models)
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_s3,
    aws_iam_role_policy.lambda_bedrock,
    aws_iam_role_policy.lambda_logs,
    aws_cloudwatch_log_group.lambda
  ]

  tags = merge(var.tags, {
    Name = "Document Processor Lambda"
  })
}

# ============================================================================
# S3 EVENT NOTIFICATION
# ============================================================================

# Permission for S3 to invoke Lambda
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.document_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.input.arn
}

# S3 bucket notification to trigger Lambda
# Event-driven processing: automatically invokes Lambda when documents are uploaded
# Prefix filter limits processing to files in 'claims/' directory
# See ARCHITECTURE_DECISIONS.md ADR-007 for rationale
resource "aws_s3_bucket_notification" "lambda_trigger" {
  bucket = aws_s3_bucket.input.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.document_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = var.s3_event_prefix
    filter_suffix       = ""
  }

  depends_on = [aws_lambda_permission.allow_s3]
}

