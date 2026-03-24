# Terraform — optional scratch bucket (Lab 02)

This stack provisions **only** an encrypted, private **S3 bucket** for tiny experiments (for example a few `.md` chunks you validate by hand).

It does **not** create:

- A Bedrock Knowledge Base
- A vector index or data source
- Lambda or event notifications

Those belong in the full pipeline repo **[aws-pdf-rag-mr](https://github.com/rivadaviam/aws-pdf-rag-mr)** once you have finished the **foundations** exercises in the lab `app/` CLI.

## Prerequisites

- Terraform >= 1.0
- AWS credentials with permission to create S3 buckets

## Usage

```bash
cd labs/lab-02-kb-ingestion-basics/infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit bucket_suffix to something globally unique

terraform init
terraform plan
terraform apply
```

## Cleanup

Empty the bucket (including versioned objects if you uploaded test files), then:

```bash
terraform destroy
```

If destroy fails because objects remain:

```bash
aws s3 rm s3://YOUR_BUCKET_NAME --recursive
# Then delete versioned objects if versioning was used — see AWS docs for list-object-versions delete pattern
terraform destroy
```
