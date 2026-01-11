output "input_bucket_name" {
  description = "Name of the S3 input bucket"
  value       = aws_s3_bucket.input.id
}

output "input_bucket_arn" {
  description = "ARN of the S3 input bucket"
  value       = aws_s3_bucket.input.arn
}

output "output_bucket_name" {
  description = "Name of the S3 output bucket"
  value       = aws_s3_bucket.output.id
}

output "output_bucket_arn" {
  description = "ARN of the S3 output bucket"
  value       = aws_s3_bucket.output.arn
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.document_processor.arn
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.document_processor.function_name
}

output "lambda_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_execution.arn
}

