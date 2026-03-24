output "scratch_bucket_name" {
  description = "S3 bucket for tiny experiments (hand-authored chunks, not full PDF pipeline)"
  value       = aws_s3_bucket.scratch.bucket
}

output "scratch_bucket_arn" {
  value = aws_s3_bucket.scratch.arn
}
