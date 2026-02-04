---
title: "The Build-to-Learn Framework: How a Near-Disaster Taught Me to Learn in Public"
published: false
description: I almost created an infinite loop that would have cost thousands. Documentation saved me. Here's the framework that emerged.
tags: aws, amazonbedrock, generativeai, learninpublic
cover_image: https://raw.githubusercontent.com/rivadaviam/aws-genai-cert-learning-journey/main/_bmad-output/blog-articles/cover-devto.png
canonical_url: https://github.com/rivadaviam/aws-genai-cert-learning-journey
series: Build-to-Learn with AWS GenAI
---

I almost created an infinite loop that would have cost me thousands in AWS bills.

And I'm grateful it almost happened.

---

## The Setup

When I decided to pursue the **AWS Certified Generative AI Developer** certification, I made myself a promise: I wouldn't just study for an exam. I would build real systems, make real mistakes, and share everything publicly—including the wrong turns.

The AWS Skill Builder course has these "Bonus Assignments" scattered throughout. Most people skip them or treat them as quick checkboxes.

I saw something different: each one was an invitation to build something **production-ready**.

My first assignment: an automated insurance claim processing pipeline using Amazon Bedrock.

![Architecture Diagram](https://raw.githubusercontent.com/rivadaviam/aws-genai-cert-learning-journey/main/labs/lab-01-claims-doc-processing/diagrams/generated-diagrams/insurance-claim-processing-architecture-lab01.png)
*User uploads to S3 → Lambda orchestrates 3-step Bedrock pipeline → Results saved to output bucket*

---

## The Near-Disaster

My initial architecture was elegant. One S3 bucket, two prefixes:
- `/input` for uploaded documents
- `/output` for processed results

Clean. Simple. **Catastrophic.**

Here's what happens with that design:

```
1. Document lands in /input
2. Lambda triggers, processes document
3. Result written to /output (same bucket)
4. S3 event triggers Lambda again
5. Lambda processes the output file...
6. → Infinite loop. Infinite cost.
```

I caught this because I was writing an **Architecture Decision Record**—ADR-002—explaining my bucket strategy.

The act of documenting forced me to think through the consequences. Mid-sentence, I realized what would happen in production.

```markdown
# ADR-002: Separate S3 Buckets for Input and Output

## Decision
Use separate S3 buckets for input and output

## Consequences
- Prevents infinite loop scenarios
- Better security isolation
- Different lifecycle policies per bucket
- Slight increase in bucket management complexity

## Why This Choice
Following AWS best practices prevents production issues.
The slight complexity increase is worth avoiding infinite loops.
```

That ADR saved me real money. But more importantly, it taught me something:

> **Documentation isn't overhead. It's thinking made visible.**

---

## The Build-to-Learn Framework

That near-miss crystallized into a methodology:

### 1. Build Real Things
Not tutorials. Not sandboxes. Production-grade systems with real constraints.

### 2. Document Every Decision
Architecture Decision Records for the big choices. Comments for the small ones. Capture the *why*, not just the *what*.

### 3. Share the Messy Middle
Don't just show the finished product. Show the wrong turns, the trade-offs, the moments of doubt.

---

## The Implementation

Instead of one monolithic prompt, I designed a **three-step AI pipeline** where each step uses the optimal model:

| Step | Model | Why |
|------|-------|-----|
| Document Understanding | Claude 3.5 Sonnet | Complex reasoning needed |
| Information Extraction | Claude 3.5 Sonnet | Precision for structured JSON |
| Summary Generation | Claude 3 Haiku | Cost-efficient for simple output |

### Step 1: Document Understanding

```python
def process_document_understanding(document_text, model_id, template_manager):
    """Analyze and understand the document structure and content."""
    prompt = template_manager.get_prompt(
        "document_understanding",
        document_text=document_text
    )

    return invoke_bedrock_model(
        model_id,
        prompt,
        temperature=0.1,  # Low temperature for accuracy
        max_tokens=2000
    )
```

**Why this step?** Complex documents need context before extraction. Understanding the document type (auto claim vs. health expense) improves downstream accuracy.

### Step 2: Information Extraction

```python
def extract_information(document_text, model_id, template_manager):
    """Extract structured information from the document."""
    prompt = template_manager.get_prompt(
        "extract_info",
        document_text=document_text
    )

    result = invoke_bedrock_model(
        model_id,
        prompt,
        temperature=0.0,  # Zero temperature for deterministic output
        max_tokens=1500
    )
    return result
```

**Key insight:** Using `temperature=0.0` ensures consistent, deterministic extraction. This matters when downstream systems depend on specific JSON fields.

### Step 3: Summary Generation

```python
def generate_summary(extracted_info, model_id, template_manager):
    """Generate a concise summary of the claim."""
    prompt = template_manager.get_prompt(
        "generate_summary",
        extracted_info=extracted_info
    )

    return invoke_bedrock_model(
        model_id,
        prompt,
        temperature=0.7,  # Higher temperature for natural language
        max_tokens=500
    )
```

**Why Haiku here?** The heavy lifting is done. We're just formatting extracted data into prose. Claude 3 Haiku does this well at **~10x lower cost** than Sonnet.

This decision is captured in ADR-005:

```markdown
# ADR-005: Use Claude 3 Haiku for Summary Generation

## Decision
Use Claude 3 Haiku for summary generation (not Sonnet)

## Rationale
- Summaries are the final step - context is already extracted
- Haiku is ~10x cheaper than Sonnet
- Quality is sufficient for 2-3 sentence summaries
- Maintains on-demand throughput support

## Trade-off
Slight quality reduction for significant cost savings
```

---

## Model Selection: The Certification Question

If you're preparing for AIP-C01, model selection is a core topic. Here's my real-world decision matrix:

**Why Sonnet v1 instead of v2?**

This surprised me. Claude 3.5 Sonnet v2 is newer and "better," but:
- On-demand throughput may not be available in all regions
- Provisioned Throughput might be required
- v1 is stable and widely available

For a learning project that others will deploy, **availability beats marginal quality improvements**.

---

## The Infrastructure

Everything is Terraform. Here's the Lambda configuration:

```hcl
resource "aws_lambda_function" "processor" {
  function_name = "${var.project_name}-processor"
  runtime       = "python3.12"
  handler       = "lambda_handler.handler"
  timeout       = 300   # 5 minutes
  memory_size   = 512   # MB

  environment {
    variables = {
      OUTPUT_BUCKET               = aws_s3_bucket.output.id
      BEDROCK_MODEL_UNDERSTANDING = "anthropic.claude-3-5-sonnet-20240620-v1:0"
      BEDROCK_MODEL_EXTRACTION    = "anthropic.claude-3-5-sonnet-20240620-v1:0"
      BEDROCK_MODEL_SUMMARY       = "anthropic.claude-3-haiku-20240307-v1:0"
    }
  }
}
```

**Why 5 minutes and 512MB?**

Document processing with three Bedrock calls takes 30-90 seconds typically. 5 minutes provides buffer for:
- Cold starts
- Larger documents
- Network latency to Bedrock

512MB is the sweet spot—enough memory for boto3 and JSON processing without overpaying.

---

## What I Learned (Beyond the Tech)

### Documentation is a Feature
Writing ADRs forced me to justify every decision. Several times I changed my approach mid-documentation because writing it out revealed flaws.

### Local Development Saves Money
The system supports local execution before AWS deployment:

```bash
python main.py --input claim.txt --output result.json
```

I processed dozens of test documents locally before incurring any Lambda or Bedrock costs.

### The Certification Topics Are Real
Every topic I encountered in Skill Builder appeared in this implementation:
- Model selection criteria
- Prompt engineering
- Cost optimization
- Security best practices
- Serverless patterns

Building something real made these concepts stick.

---

## Try It Yourself

The entire project is open source:

{% github rivadaviam/aws-genai-cert-learning-journey %}

```bash
# Clone and explore
git clone https://github.com/rivadaviam/aws-genai-cert-learning-journey.git
cd labs/lab-01-claims-doc-processing

# Read the full guide
cat README.md

# Deploy with Terraform
cd infra/terraform
terraform init && terraform apply
```

---

## What's Next

This is just the beginning.

I'm continuing to build through the AWS GenAI certification curriculum, turning each challenge into a production-ready implementation. More labs are coming—each one following the same Build-to-Learn principles:

- **Production-ready code** you can actually deploy
- **Every decision documented** with ADRs
- **The messy middle shared** so you learn from my mistakes too

Want to follow along? Star the repo or [connect with me on LinkedIn](https://www.linkedin.com/in/martin-rivadavia/) to get notified when the next lab drops.

---

## The Invitation

If you're preparing for a certification, don't just study.

**Build something real. Document your decisions. Share your journey.**

If you find a flaw in my implementation, [open an issue](https://github.com/rivadaviam/aws-genai-cert-learning-journey/issues). If you have a better approach, propose it. If you build something using the framework, tell me about it.

> Certifications prove you can learn.
> Projects prove you can build.
> Documentation proves you can teach.
>
> **The Build-to-Learn Framework asks: why not do all three?**

---

*Have questions? [Connect with me on LinkedIn](https://www.linkedin.com/in/martin-rivadavia/) or drop a comment below.*

**Build. Document. Share. Repeat.**

`#BuildToLearn` `#AWSCommunity` `#LearnInPublic`
