# Terraform Infrastructure for Insurance Claim Document Processing

This Terraform configuration deploys the complete infrastructure for automated insurance claim document processing using Amazon S3, AWS Lambda, and Amazon Bedrock.

## Architecture Overview

The infrastructure includes:

- **S3 Input Bucket**: Stores incoming claim documents
- **S3 Output Bucket**: Stores processed results (JSON format)
- **Lambda Function**: Processes documents using Bedrock models
- **IAM Roles & Policies**: Secure access to S3 and Bedrock
- **S3 Event Notification**: Automatically triggers Lambda when documents are uploaded

### Reusable Components

The Lambda function uses modular, reusable components:

- **PromptTemplateManager** (`prompt_template_manager.py`): Centralizes all prompt templates for easy maintenance and customization
- **Model Comparison** (`model_comparison.py`): Optional functionality to compare different Bedrock models on the same document

These components are included in the Lambda deployment package and can be customized without modifying the main processing logic.

## Prerequisites

1. **AWS CLI** configured with appropriate credentials
2. **Terraform** >= 1.0 installed
3. **AWS Account** with permissions to create:
   - S3 buckets
   - Lambda functions
   - IAM roles and policies
   - CloudWatch Log Groups
   - Bedrock model access
4. **AWS Marketplace Permissions** (required for Anthropic models):
   - Account must allow AWS Marketplace subscriptions
   - User/role must have `aws-marketplace:ViewSubscriptions` and `aws-marketplace:Subscribe` permissions
   - These permissions are automatically included in the Lambda execution role

### Resource Naming

Resources are named using the pattern `claim-documents-poc-<your-initials>`. For example, with initials "mr":
- Input bucket: `claim-documents-poc-mr-input`
- Output bucket: `claim-documents-poc-mr-output`
- Lambda function: `claim-processor-mr`

You can customize these names by setting the `bucket_prefix` and `lambda_function_name` variables in `variables.tf` or `terraform.tfvars`.

## Bedrock Model Access and Anthropic Permissions

### Important: AWS Marketplace Permissions Required

**Anthropic models (Claude) require AWS Marketplace permissions to be enabled.** The Terraform configuration includes the necessary IAM permissions (`aws-marketplace:ViewSubscriptions` and `aws-marketplace:Subscribe`), but you may need to:

1. **Ensure your AWS account/user has Marketplace permissions** - Contact your AWS administrator if you encounter access denied errors
2. **First-time model invocation** - Serverless foundation models are automatically enabled when first invoked, but Anthropic models may require:
   - Submitting use case details (one-time process)
   - A user with AWS Marketplace permissions invoking the model once to enable it account-wide

### Model Access Process

1. Models are automatically enabled when first invoked (no manual activation needed)
2. For Anthropic models, ensure the Lambda execution role has Marketplace permissions (already included in this configuration)
3. If you see "Model access is denied" errors:
   - Verify IAM role has Marketplace permissions (check `main.tf` IAM policy)
   - Ensure your AWS account allows Marketplace subscriptions
   - Try invoking the model once from AWS Console Playground to enable it

### Models Used

- **Document Understanding**: `anthropic.claude-3-5-sonnet-20240620-v1:0` (Claude 3.5 Sonnet v1)
- **Information Extraction**: `anthropic.claude-3-5-sonnet-20240620-v1:0` (Claude 3.5 Sonnet v1)
- **Summary Generation**: `anthropic.claude-3-haiku-20240307-v1:0` (Claude 3 Haiku)

**Note**: We use Claude 3.5 Sonnet v1 (not v2) and Claude 3 Haiku (not 3.5) because:
- v2 models may not support on-demand throughput in all regions
- Claude 3 Haiku provides sufficient quality for summaries at lower cost

## Quick Start

### 1. Initialize Terraform

```bash
cd labs/lab-01-claims-doc-processing/infra/terraform
terraform init
```

### 2. Review and Customize Variables

Edit `variables.tf` or create a `terraform.tfvars` file to customize:

```hcl
bucket_prefix = "my-claim-documents"
aws_region    = "us-east-1"
lambda_timeout = 300
```

### 3. Plan Deployment

```bash
terraform plan
```

### 4. Deploy Infrastructure

```bash
terraform apply
```

Type `yes` when prompted to confirm.

### 5. Verify Deployment

After deployment, Terraform will output:

- Input bucket name
- Output bucket name
- Lambda function ARN
- Lambda function name

## Usage

### Upload a Document

Upload a claim document to the input bucket:

```bash
aws s3 cp ../../data/test-documents/claim-001-auto-accident.txt s3://<input-bucket-name>/claims/claim-001-auto-accident.txt
```

The Lambda function will automatically:
1. Process the document
2. Extract information using Bedrock
3. Generate a summary
4. Save results to the output bucket

### Check Results

Results are saved in the output bucket under `processed/`:

```bash
aws s3 ls s3://<output-bucket-name>/processed/
aws s3 cp s3://<output-bucket-name>/processed/claim-document.txt.json .
```

## Configuration

### Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `bucket_prefix` | Prefix for S3 bucket names | `claim-documents-poc` |
| `lambda_function_name` | Name of Lambda function | `claim-document-processor` |
| `bedrock_models` | Map of Bedrock models | See `variables.tf` |
| `aws_region` | AWS region | `us-east-1` |
| `lambda_timeout` | Lambda timeout (seconds) | `300` |
| `lambda_memory_size` | Lambda memory (MB) | `512` |
| `s3_event_prefix` | S3 event prefix filter | `claims/` |
| `enable_model_comparison` | Enable model comparison feature | `false` |
| `comparison_models` | List of model IDs for comparison | `[]` |
| `tags` | Common tags | See `variables.tf` |

### Bedrock Models

Default models used:

- **Document Understanding**: `anthropic.claude-3-5-sonnet-20240620-v1:0` (Claude 3.5 Sonnet v1)
- **Information Extraction**: `anthropic.claude-3-5-sonnet-20240620-v1:0` (Claude 3.5 Sonnet v1)
- **Summary Generation**: `anthropic.claude-3-haiku-20240307-v1:0` (Claude 3 Haiku)

**Model Selection Rationale**: See [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) for detailed explanation of model choices.

To use different models, update the `bedrock_models` variable in `variables.tf` or `terraform.tfvars`.

### Customizing Prompts

Prompts are managed through the `PromptTemplateManager` class in `lambda/prompt_template_manager.py`. To customize prompts:

1. Edit the template strings in `prompt_template_manager.py`
2. Redeploy the Lambda function:
   ```bash
   terraform apply
   ```

Available templates:
- `document_understanding`: Analysis of document structure and content
- `extract_info`: Information extraction prompt
- `generate_summary`: Summary generation prompt

### Model Comparison Feature

The Lambda function includes an optional model comparison feature that can compare multiple Bedrock models on the same document. This is useful for evaluating model performance.

To enable model comparison:

1. Set `enable_model_comparison = true` in `variables.tf` or `terraform.tfvars`
2. Specify models to compare in `comparison_models`:
   ```hcl
   enable_model_comparison = true
   comparison_models = [
     "anthropic.claude-3-5-sonnet-20240620-v1:0",
     "anthropic.claude-3-haiku-20240307-v1:0"
   ]
   ```
3. Apply changes: `terraform apply`

When enabled, comparison results are saved to the output bucket under `comparisons/` prefix as separate JSON files. The comparison includes:
- Processing time for each model
- Output length
- Sample output
- Success/failure status

**Note**: Model comparison adds processing time and cost. Use only for evaluation purposes.

## Output Format

The Lambda function generates JSON output with the following structure:

```json
{
  "source_document": {
    "bucket": "input-bucket-name",
    "key": "claims/document.txt",
    "processed_at": "2024-01-01T12:00:00Z"
  },
  "document_understanding": "...",
  "extracted_information": {
    "Claimant Name": "...",
    "Policy Number": "...",
    "Incident Date": "...",
    "Claim Amount": "...",
    "Incident Description": "..."
  },
  "summary": "...",
  "processing_metadata": {
    "models_used": {
      "understanding": "...",
      "extraction": "...",
      "summary": "..."
    }
  }
}
```

## Monitoring

### CloudWatch Logs

Lambda logs are available in CloudWatch:

```bash
aws logs tail /aws/lambda/claim-document-processor --follow
```

### Lambda Metrics

Monitor Lambda performance in CloudWatch:
- Invocations
- Duration
- Errors
- Throttles

## Security

The infrastructure implements security best practices:

- ✅ S3 buckets with encryption (SSE-S3)
- ✅ Versioning enabled on both buckets
- ✅ Public access blocked
- ✅ IAM least privilege policies
- ✅ Separate input/output buckets to prevent loops

## Troubleshooting

### Lambda Not Triggering

1. Check S3 bucket notification configuration:
   ```bash
   aws s3api get-bucket-notification-configuration --bucket <input-bucket-name>
   ```

2. Verify Lambda permission:
   ```bash
   aws lambda get-policy --function-name claim-document-processor
   ```

### Bedrock Access Denied

1. **Check IAM permissions**: Verify the Lambda role has both Bedrock and Marketplace permissions:
   ```bash
   aws iam get-role-policy --role-name claim-document-processor-mr-execution-role --policy-name claim-document-processor-mr-bedrock-policy
   ```
   Should include: `bedrock:InvokeModel`, `aws-marketplace:ViewSubscriptions`, `aws-marketplace:Subscribe`

2. **Marketplace permissions**: Ensure your AWS account/user has permissions to subscribe to AWS Marketplace products
   - Contact AWS administrator if needed
   - Models are auto-enabled on first invocation, but require Marketplace permissions

3. **Model availability**: Verify model IDs are correct and available in your region:
   ```bash
   aws bedrock list-foundation-models --query 'modelSummaries[?contains(modelId, `claude-3-5-sonnet`)].{ModelId:modelId,ModelName:modelName}'
   ```

4. **First-time enablement**: Try invoking the model once from AWS Bedrock Console Playground to enable it account-wide

### Lambda Timeout

Increase timeout in `variables.tf`:
```hcl
lambda_timeout = 600  # 10 minutes
```

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will delete all S3 buckets and their contents. Ensure you have backups if needed.

## Cost Estimation

Approximate monthly costs (varies by usage):

- **S3 Storage**: ~$0.023 per GB
- **Lambda**: ~$0.20 per 1M requests + compute time
- **Bedrock**: 
  - Claude Sonnet 3.5: ~$3.00 per 1M input tokens, ~$15.00 per 1M output tokens
  - Claude Haiku 3.5: ~$0.25 per 1M input tokens, ~$1.25 per 1M output tokens
- **CloudWatch Logs**: ~$0.50 per GB ingested

## Support

For issues or questions:
1. Check CloudWatch Logs for errors
2. Review Terraform plan output
3. Verify AWS service quotas and limits

## License

This infrastructure code is part of the Insurance Claim Processing POC project.

