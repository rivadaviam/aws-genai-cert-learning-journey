# Test Documents

This folder contains synthetic documents for testing the insurance claim document processing system.

## Usage

To test the system, upload these documents to the S3 input bucket:

```bash
aws s3 cp test-documents/<document-name> s3://<input-bucket-name>/claims/<document-name>
```

Replace `<input-bucket-name>` with the actual input bucket name from Terraform outputs, and `<document-name>` with the name of your test document.

## Example

After deploying the infrastructure with Terraform, you can get the input bucket name from the outputs:

```bash
cd terraform
terraform output input_bucket_name
```

Then upload a test document:

```bash
aws s3 cp test-documents/claim-example.txt s3://claim-documents-poc-mr-input-123456789/claims/claim-example.txt
```

## Monitoring

After uploading a document, you can:

1. **Check Lambda logs** in CloudWatch:
   ```bash
   aws logs tail /aws/lambda/claim-document-processor-mr --follow
   ```

2. **Check processed results** in the output bucket:
   ```bash
   aws s3 ls s3://<output-bucket-name>/processed/
   aws s3 cp s3://<output-bucket-name>/processed/<document-name>.json .
   ```

## Document Format

The system processes text documents containing insurance claim information. Documents should include:

- Claimant information (name, policy number, contact details)
- Incident details (date, location, description)
- Claim amount
- Any other relevant claim information

The Lambda function will automatically:
1. Analyze the document structure
2. Extract structured information
3. Generate a summary
4. Save results as JSON in the output bucket

