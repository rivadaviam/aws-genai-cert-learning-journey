variable "aws_region" {
  type        = string
  description = "AWS region for the scratch bucket"
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Short prefix for resource names"
  default     = "lab02-kb-basics"
}

variable "environment" {
  type        = string
  description = "Environment tag (e.g. dev)"
  default     = "dev"
}

variable "bucket_suffix" {
  type        = string
  description = "Unique suffix for global S3 bucket name (e.g. your initials + random)"
  default     = "changeme"
}
