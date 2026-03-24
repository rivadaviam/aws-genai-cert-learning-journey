# Lab 02: Knowledge Base Ingestion — Foundations First

> **What this lab is about:** Learning the **basics of chunking, embeddings, and Knowledge Base sync** *before* you pay to ingest large PDFs at scale. Includes small local tools to **estimate tokens and preview chunks** so you can reason about cost and quality.

## The honest scenario (why this lab exists)

I wanted a working RAG pipeline over technical PDFs. I wired up Amazon Bedrock Knowledge Bases, pointed them at S3, and started **syncing and re-syncing** while I was still figuring out parsers, chunk sizes, deduplication, and what “good” retrieval even looked like. **The bill taught me what the docs hadn’t yet:** ingestion and embedding are not free experiments, and **re-ingesting the same content repeatedly** is an expensive way to learn.

This lab is the lesson distilled: **foundations and measurement first, bulk ingestion second.**

It does **not** replace a full production pipeline. For the **end-to-end implementation** (Terraform, Lambda, PDF processing, Bedrock Knowledge Base, S3 Vectors), use the companion repo **[aws-pdf-rag-mr](https://github.com/rivadaviam/aws-pdf-rag-mr)**. This lab folder focuses on **mindset, checks, and small scripts** you should have used *before* the first big sync.

## What you’ll learn

- **Why** “upload PDF and sync” is the last step, not the first
- **How** to approximate **token counts** locally (ingestion/embedding is priced in tokens)
- **How** to **preview chunk boundaries** before they become immutable objects in S3
- **What** to verify in the AWS console (data source, sync jobs, model dimensions) before scaling
- **When** to graduate from this lab to a full IaC pipeline

## Architecture (conceptual)

```text
┌─────────────────────────────────────────────────────────────────┐
│  Lab 02 (this repo): foundations                                 │
│  Local text → token estimate → chunk preview → (optional) retrieve │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Later: full pipeline — github.com/rivadaviam/aws-pdf-rag-mr      │
│  PDF → extract/clean/chunk → S3 processed/ → KB sync → retrieve   │
└─────────────────────────────────────────────────────────────────┘
```

**Rule of thumb:** If you cannot explain your chunk size and approximate token count for one document, **do not** schedule a full-corpus sync yet.

## Prerequisites

- **AWS CLI** configured (for optional retrieve demo)
- **Python 3.12+**
- **Terraform >= 1.0** (only if you use the optional scratch bucket in `infra/terraform`)
- Access to **Amazon Bedrock** in your region (for optional retrieval against an existing Knowledge Base)

## Quick start

### 1. Local development (no AWS spend)

```bash
cd labs/lab-02-kb-ingestion-basics/app
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Estimate tokens for a tiny sample (included):**

```bash
python main.py estimate --input ../data/sample-documents/tiny-tech-note.txt
```

**Preview naive chunks (approximate tokens, overlap):**

```bash
python main.py chunks --input ../data/sample-documents/tiny-tech-note.txt \
  --target-tokens 200 --overlap-tokens 40
```

Read the output. If the splits look wrong for your domain, **fix chunking before** you pay for embeddings at scale.

### 2. Optional: one retrieval call (existing KB)

If you already have a Knowledge Base ID and a query that should work:

```bash
cp .env.example .env
# Set KB_ID, AWS_REGION, optionally AWS_PROFILE

python main.py retrieve --query "Your test question"
```

This uses `bedrock-agent-runtime` `retrieve` — useful to validate **retrieval** separately from **ingestion** costs.

### 3. Optional infrastructure: scratch bucket

The Terraform stack is **optional** and minimal: a **single S3 bucket** you can use for tiny experiments (e.g. a few hand-authored `.md` chunks), with a clear prefix layout. See `infra/terraform/README.md`.

```bash
cd labs/lab-02-kb-ingestion-basics/infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars
terraform init
terraform plan
terraform apply
```

### 4. Cleanup

```bash
cd infra/terraform
terraform destroy
```

Empty the bucket first if Terraform reports objects in the way (see Terraform README).

## Sample data

See `data/sample-documents/`: start with **small** text files. **Do not** use a 500-page PDF as your first ingestion test.

## Project layout

```text
lab-02-kb-ingestion-basics/
├── README.md                 # This file
├── ADR.md                    # Decisions: basics-first, measure before sync
├── app/                      # Local CLI: estimate, chunks, optional retrieve
├── data/sample-documents/    # Tiny files for safe experiments
├── diagrams/                 # Optional diagrams
└── infra/terraform/          # Optional S3 scratch bucket
```

## Relationship to other work

| Artifact | Role |
|----------|------|
| **This lab** | Mindset + local measurement + optional minimal AWS |
| **[aws-pdf-rag-mr](https://github.com/rivadaviam/aws-pdf-rag-mr)** (companion code) | End-to-end extraction, chunking, KB, S3 Vectors — use **after** you’re clear on basics |

## Troubleshooting

- **`retrieve` fails with access denied:** KB IAM role, model access, and region must align with your Bedrock setup.
- **Token counts “feel” wrong:** We use a **rough** character-based approximation for quick sanity checks, not billing-grade precision. For exact counts, align with your embedding model’s tokenizer when you integrate deeply.
- **Chunks look bad:** That is the point — **fix offline**, then sync.

## Architecture decisions

See [ADR.md](./ADR.md).

---

**Tags:** `#BuildToLearn` `#AWSGenAI` `#AmazonBedrock` `#LearnInPublic`
