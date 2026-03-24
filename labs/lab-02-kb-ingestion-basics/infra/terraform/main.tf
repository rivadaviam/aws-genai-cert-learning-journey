terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    Lab         = "lab-02-kb-ingestion-basics"
    Purpose     = "optional-scratch-artifacts-before-kb-scale"
  }
}

resource "aws_s3_bucket" "scratch" {
  bucket = "${local.name_prefix}-scratch-${var.bucket_suffix}"

  tags = local.common_tags
}

resource "aws_s3_bucket_versioning" "scratch" {
  bucket = aws_s3_bucket.scratch.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "scratch" {
  bucket = aws_s3_bucket.scratch.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "scratch" {
  bucket = aws_s3_bucket.scratch.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
