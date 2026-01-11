# AWS Generative AI Learning Journey

> **Learn in public, build in production.** This repository is a hands-on journey through AWS Generative AI services, focusing on Amazon Bedrock and real-world use cases. Each lab is production-ready, well-documented, and designed to teach you not just *what* to build, but *why* we made these choices.

## Why This Journey Exists

Generative AI is transforming how we build applications, but learning it can feel overwhelming. This repository breaks down complex AWS AI services into practical, reproducible labs. You'll build real systems, understand architectural trade-offs, and learn from decisions documented in Architecture Decision Records (ADRs).

**What makes this different:**
- ✅ **Production-ready code** - Not just demos, but real implementations
- ✅ **Decision transparency** - Every architectural choice is documented with rationale
- ✅ **Learn from mistakes** - We share what worked, what didn't, and why
- ✅ **Community-first** - Built to help others learn and contribute

## Certification Context

This repository documents my learning journey toward the **AWS Certified Generative AI Developer – Professional (AIP-C01)** certification. The labs in this repository are derived from tasks and Bonus Assignments in the **AWS Skill Builder** course: "Exam Prep Plan: AWS Certified Generative AI Developer – Professional." Some labs are derived from specific AWS Skill Builder tasks (for example, Task 1.1: Analyze requirements and design GenAI solutions) and their associated Bonus Assignments.

**Important Notes:**
- This repository is **not official AWS material**—it represents my personal interpretation and production-grade implementation of Skill Builder assignments
- Bonus Assignments are intentionally open-ended, designed to assess overall understanding rather than test specific knowledge
- AWS explicitly encourages sharing exam preparation work publicly using `#awsexamprep`
- All architectural decisions, model selections, and design choices are documented in Architecture Decision Records (ADRs) to support learning and knowledge sharing

**Learning in Public:**
By sharing this journey, I hope to help others preparing for AIP-C01 understand not just *what* to build, but *why* certain architectural decisions were made. This aligns with AWS's community-first approach to knowledge sharing and the "learn in public" philosophy.

## Who This Is For

- **AWS practitioners** learning Generative AI services
- **Developers** building AI-powered applications
- **Architects** evaluating AWS AI services for production use
- **Students** and **bootcamp participants** looking for hands-on projects
- **Anyone** who learns best by building real systems

## Labs

| Lab | What You Build | Core AWS Services | Key Outcomes |
|-----|----------------|-------------------|--------------|
| **[Lab 01: Insurance Claim Document Processing](./labs/lab-01-claims-doc-processing/)** | Automated document processing pipeline | Amazon S3, AWS Lambda, Amazon Bedrock | Serverless architecture, multi-model orchestration, event-driven processing |

**Coming soon:**
- Lab 02: RAG (Retrieval-Augmented Generation) with vector databases
- Lab 03: Multi-modal AI applications
- Lab 04: Real-time AI inference patterns

## How to Use This Repository

### 1. Pick a Lab
Navigate to a lab directory and read its README for the full scenario and architecture.

### 2. Check Prerequisites
Each lab lists specific prerequisites. Generally, you'll need:
- **AWS CLI** configured with credentials
- **Python 3.12+** (or as specified)
- **Terraform >= 1.0**
- **AWS account** with appropriate service access

### 3. Run Locally First
Most labs support local execution before deploying to AWS. This helps you:
- Understand the code flow
- Test with sample data
- Debug issues faster
- Save on AWS costs during development

### 4. Deploy with Terraform
Each lab includes Terraform infrastructure as code:
```bash
cd labs/lab-XX-name/infra/terraform
terraform init
terraform plan
terraform apply
```

### 5. Test and Learn
Follow the lab's testing guide, experiment with different inputs, and review the outputs.

### 6. Clean Up
Always destroy resources when done:
```bash
terraform destroy
```

## Principles

### Learn in Public
We document our journey—decisions, trade-offs, and lessons learned. Every lab includes ADRs explaining *why* we chose specific architectures, models, and patterns.

### Reproducible Labs
Every lab is self-contained with:
- Clear prerequisites
- Step-by-step instructions
- Sample data for testing
- Expected outputs documented

### Security-First
We follow AWS security best practices:
- Least privilege IAM policies
- Encryption at rest and in transit
- No hardcoded credentials
- Security decisions documented in ADRs

### Production-Ready Code
Labs aren't just demos—they're structured like production code:
- Proper error handling
- Logging and monitoring
- Configuration management
- Clean architecture patterns

## Repository Structure

```
labs/
  lab-01-claims-doc-processing/  # First lab: document processing
    app/                          # Application code
    infra/                        # Infrastructure (Terraform)
    data/                         # Test data and samples
    diagrams/                     # Architecture diagrams
    ADR.md                        # Architecture Decision Records
    README.md                     # Lab-specific guide
  _template/                      # Template for creating new labs

shared/
  python/src/shared_aws/          # Shared AWS utilities (optional)
```

Each lab is self-contained and can be run independently.

## Roadmap

**Planned Labs:**
- **Lab 02: RAG with Vector Search** - Build a retrieval-augmented generation system using Amazon OpenSearch Serverless or Amazon Bedrock Knowledge Bases
- **Lab 03: Multi-Modal AI** - Process images and text together using Claude 3.5 Sonnet's vision capabilities
- **Lab 04: Real-Time AI Inference** - Build streaming AI applications with WebSockets and Bedrock
- **Lab 05: Cost Optimization** - Compare model costs, implement caching, and optimize token usage

**Contributions welcome!** See [labs/_template/](./labs/_template/) for the lab structure template.

## Community & Share

**Share your journey:**
- Tag your posts: `#AWSGenAI #LearnInPublic #AmazonBedrock #awsexamprep`
- Mention: `@AWSCommunityBuilders` (if applicable)
- Link back to this repo so others can learn too

**Contribute:**
- Found a bug? Open an issue
- Improved a lab? Submit a PR
- Built a new lab? Follow the template and share it
- Have questions? Start a discussion

**Connect:**
- Follow AWS Community Builders on [Twitter/X](https://twitter.com/AWSCommunityBuilders)
- Join AWS User Groups in your region
- Share your learnings in AWS forums and communities

## Getting Started

Ready to dive in? Start with **[Lab 01: Insurance Claim Document Processing](./labs/lab-01-claims-doc-processing/)**. It's a complete, production-ready system that teaches serverless architecture, multi-model AI orchestration, and event-driven processing.

```bash
cd labs/lab-01-claims-doc-processing
cat README.md  # Read the full guide
```

## License

This repository is provided as-is for educational purposes. Use at your own risk in production environments.

---

**Built with ❤️ by the AWS community, for the AWS community.**
