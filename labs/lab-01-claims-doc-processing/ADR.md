# Architecture Decision Records (ADR)

> **Executive Summary:** This document captures 12 key architectural decisions for the Insurance Claim Document Processing system. We chose a serverless architecture with separate S3 buckets, Claude 3.5 Sonnet v1 for understanding/extraction, Claude 3 Haiku for summaries, and a three-step processing pipeline. All decisions prioritize production readiness, security, and cost-effectiveness while maintaining quality.

## Executive Summary

**Key Decisions at a Glance:**
- ✅ **Serverless architecture** (S3 + Lambda + Bedrock) for zero infrastructure management
- ✅ **Separate input/output buckets** to prevent infinite loops (AWS best practice)
- ✅ **Claude 3.5 Sonnet v1** for document understanding and extraction (quality + on-demand support)
- ✅ **Claude 3 Haiku** for summary generation (cost efficiency + on-demand support)
- ✅ **AWS Marketplace permissions** in IAM policy for automatic model enablement
- ✅ **Three-step sequential pipeline** for comprehensive document processing
- ✅ **JSON output format** for structured, parseable results
- ✅ **Security-first approach** with encryption, versioning, and least privilege
- ✅ **Lambda timeout: 5 minutes, memory: 512 MB** (balanced for cost and reliability)
- ✅ **CloudWatch Logs: 14-day retention** (cost/utility balance)

**Decision Map:**

| ADR | Decision | Key Rationale |
|-----|----------|---------------|
| ADR-001 | Serverless Architecture | Zero infrastructure management, auto-scaling, pay-per-use |
| ADR-002 | Separate S3 Buckets | Prevents infinite loops, better security isolation |
| ADR-003 | Claude 3.5 Sonnet v1 (Understanding) | Quality + on-demand support (v2 limitations) |
| ADR-004 | Claude 3.5 Sonnet v1 (Extraction) | Precision + consistency for structured output |
| ADR-005 | Claude 3 Haiku (Summary) | Cost efficiency (~10x cheaper) + sufficient quality |
| ADR-006 | Marketplace Permissions in IAM | Automatic model enablement, no manual steps |
| ADR-007 | S3 Event-Driven Processing | Real-time, automatic, scalable |
| ADR-008 | Three-Step Pipeline | Quality through separation of concerns |
| ADR-009 | JSON Output Format | Structured, parseable, self-contained |
| ADR-010 | Security Layers | Encryption, versioning, least privilege |
| ADR-011 | Lambda Config (5min/512MB) | Balanced for cost, performance, reliability |
| ADR-012 | 14-Day Log Retention | Cost/utility balance for debugging |

---

## ADR-001: Serverless Architecture Pattern

**Status:** Accepted  
**Date:** 2026-01-07  
**Context:** Need to process insurance claim documents automatically with minimal infrastructure management.

**Decision:** Use a fully serverless architecture with:
- Amazon S3 for document storage
- AWS Lambda for processing orchestration
- Amazon Bedrock for AI/ML capabilities

**Consequences:**
- ✅ No infrastructure to manage (no servers, containers, or clusters)
- ✅ Automatic scaling based on workload
- ✅ Pay-per-use cost model
- ✅ Event-driven processing (automatic trigger on document upload)
- ⚠️ Cold start latency for Lambda (mitigated with appropriate timeout/memory)
- ⚠️ Lambda execution time limits (15 minutes max, configured for 5 minutes)

**Alternatives Considered:**
- ECS/Fargate containers: More complex, requires container management
- EC2 instances: Requires server management, scaling configuration
- Step Functions: Could add orchestration complexity for this simple workflow

**Why This Choice:** Serverless is perfect for event-driven, variable-workload scenarios. The trade-off of cold starts is minimal compared to the operational simplicity and cost benefits.

---

## ADR-002: Separation of Input and Output S3 Buckets

**Status:** Accepted  
**Date:** 2026-01-07  
**Context:** Lambda function needs to read from input bucket and write to output bucket. AWS best practice warns against using the same bucket for both to avoid infinite loops.

**Decision:** Use separate S3 buckets:
- `{prefix}-input-{account-id}`: For incoming claim documents
- `{prefix}-output-{account-id}`: For processed results

**Consequences:**
- ✅ Prevents infinite loop scenarios (Lambda writing to input bucket would retrigger itself)
- ✅ Clear separation of concerns
- ✅ Different lifecycle policies can be applied to each bucket
- ✅ Better security isolation (different access patterns)
- ⚠️ Slightly more complex bucket management

**Alternatives Considered:**
- Single bucket with prefixes: Simpler but violates AWS best practices
- Single bucket with event filtering: Possible but risky if filters misconfigured

**Why This Choice:** Following AWS best practices prevents production issues. The slight complexity increase is worth avoiding infinite loops and security risks.

**Reference:** [AWS Lambda S3 Event Documentation](https://docs.aws.amazon.com/lambda/latest/dg/with-s3.html)

---

## ADR-003: Model Selection for Document Understanding

**Status:** Accepted  
**Date:** 2026-01-07  
**Context:** Need to analyze and understand insurance claim document structure and content.

**Decision:** Use `anthropic.claude-3-5-sonnet-20240620-v1:0` (Claude 3.5 Sonnet v1)

**Rationale:**
- **Performance:** Excellent at understanding complex document structures
- **Multimodal support:** Can handle both text and images (future-proof for scanned documents)
- **Context window:** Large context window (200K tokens) handles long documents
- **Version choice:** v1 chosen over v2 because:
  - v2 may not support on-demand throughput in all regions
  - v1 is more stable and widely available
  - v1 provides sufficient quality for document understanding tasks

**Alternatives Considered:**
- Claude 3.5 Sonnet v2: Better performance but on-demand throughput limitations
- Claude Opus 4: Higher quality but significantly more expensive
- Amazon Nova Pro: No Marketplace needed but lower quality for complex documents
- Claude 3 Sonnet: Older version, less capable than 3.5

**Trade-offs:**
- ✅ High quality document understanding
- ✅ Good balance of cost and performance
- ⚠️ Requires AWS Marketplace permissions
- ⚠️ Higher cost than lighter models (justified by quality requirements)

**Why This Choice:** Document understanding is a complex task requiring high-quality models. Sonnet v1 provides the best balance of quality, availability, and on-demand support.

---

## ADR-004: Model Selection for Information Extraction

**Status:** Accepted  
**Date:** 2026-01-07  
**Context:** Need to extract structured information (names, dates, amounts, descriptions) from unstructured claim documents.

**Decision:** Use `anthropic.claude-3-5-sonnet-20240620-v1:0` (Claude 3.5 Sonnet v1)

**Rationale:**
- **Precision:** Excellent at following structured output formats (JSON)
- **Consistency:** Reliable extraction of key fields
- **Handles variations:** Can extract information even when document format varies
- **Same model as understanding:** Reuses model for consistency and cost efficiency

**Alternatives Considered:**
- Specialized extraction models: Not available in Bedrock
- Claude 3 Haiku: Lower cost but less reliable for complex extraction
- Amazon Textract: Good for forms but not for unstructured text extraction

**Trade-offs:**
- ✅ High accuracy for structured data extraction
- ✅ Consistent JSON output format
- ⚠️ Same model used for understanding (could use different model for optimization)
- ⚠️ Higher cost than lighter models (justified by accuracy requirements)

**Why This Choice:** Information extraction requires precision and consistency. Sonnet provides the reliability needed for production use, and reusing the same model simplifies configuration.

---

## ADR-005: Model Selection for Summary Generation

**Status:** Accepted  
**Date:** 2026-01-07  
**Context:** Need to generate concise summaries of extracted claim information.

**Decision:** Use `anthropic.claude-3-haiku-20240307-v1:0` (Claude 3 Haiku)

**Rationale:**
- **Cost efficiency:** Significantly cheaper than Sonnet (~10x lower cost)
- **Speed:** Faster inference time (lower latency)
- **Sufficient quality:** Haiku provides adequate quality for summary generation
- **On-demand support:** Claude 3 Haiku supports on-demand throughput (3.5 Haiku v1 does not)
- **Version choice:** v1 chosen because 3.5 Haiku v1 doesn't support on-demand throughput

**Alternatives Considered:**
- Claude 3.5 Haiku v1: Doesn't support on-demand throughput
- Claude 3.5 Sonnet: Higher quality but unnecessary cost for summaries
- Claude 3 Haiku 3.5: Not available or doesn't support on-demand
- Amazon Nova Lite: No Marketplace needed but lower quality

**Trade-offs:**
- ✅ Cost-effective for high-volume processing
- ✅ Fast response times
- ✅ Good enough quality for summary tasks
- ⚠️ Slightly lower quality than Sonnet (acceptable trade-off for summaries)

**Why This Choice:** Summary generation is a simpler task that doesn't require Sonnet's capabilities. Haiku provides sufficient quality at a fraction of the cost, making it ideal for high-volume processing.

---

## ADR-006: AWS Marketplace Permissions for Anthropic Models

**Status:** Accepted  
**Date:** 2026-01-07  
**Context:** Anthropic models (Claude) are distributed through AWS Marketplace and require subscription permissions to enable access.

**Decision:** Include AWS Marketplace permissions in Lambda execution role IAM policy:
- `aws-marketplace:ViewSubscriptions`
- `aws-marketplace:Subscribe`

**Rationale:**
- **Automatic enablement:** Models are automatically enabled on first invocation, but require Marketplace permissions
- **Account-wide enablement:** Once a model is invoked with Marketplace permissions, it's enabled for the entire AWS account
- **Best practice:** Grant permissions at the service role level rather than requiring manual console actions

**Implementation Details:**
- Permissions granted to Lambda execution role (not user/account level)
- Resource set to `*` (Marketplace subscriptions are account-level)
- Included in the same IAM policy as Bedrock invoke permissions for simplicity

**Alternatives Considered:**
- Manual enablement via console: Requires user intervention, not automated
- Account-level permissions: Less secure, grants broader access
- Using Amazon models only: Avoids Marketplace but lower quality for this use case

**Trade-offs:**
- ✅ Enables automatic model access
- ✅ No manual intervention required
- ⚠️ Requires account to allow Marketplace subscriptions
- ⚠️ May require account administrator approval

**Why This Choice:** Automation is key for production systems. Including Marketplace permissions in the IAM role enables seamless model access without manual steps.

**Reference:** [AWS Bedrock Model Access Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)

---

## ADR-007: Event-Driven Processing with S3 Notifications

**Status:** Accepted  
**Date:** 2026-01-07  
**Context:** Need automatic processing when documents are uploaded.

**Decision:** Use S3 bucket notifications to trigger Lambda automatically on object creation.

**Implementation:**
- Event type: `s3:ObjectCreated:*` (covers PUT, POST, COPY, etc.)
- Prefix filter: `claims/` (only processes files in this prefix)
- Asynchronous invocation: Lambda invoked asynchronously by S3

**Rationale:**
- **Simplicity:** No need for polling or scheduled jobs
- **Real-time processing:** Documents processed immediately upon upload
- **Cost efficient:** No idle resources waiting for events
- **Scalable:** Automatically handles concurrent uploads

**Alternatives Considered:**
- EventBridge rules: More complex, adds another service
- SQS polling: Requires polling logic, adds latency
- Scheduled Lambda: Not real-time, processes in batches

**Trade-offs:**
- ✅ Automatic and immediate processing
- ✅ Simple configuration
- ⚠️ No built-in retry mechanism (Lambda handles retries)
- ⚠️ Asynchronous (no immediate response to uploader)

**Why This Choice:** S3 notifications are the simplest and most cost-effective way to trigger processing. The asynchronous nature is acceptable for this use case.

---

## ADR-008: Three-Step Processing Pipeline

**Status:** Accepted  
**Date:** 2026-01-07  
**Context:** Need comprehensive document processing with understanding, extraction, and summarization.

**Decision:** Implement three sequential processing steps:
1. Document Understanding: Analyze document structure and content
2. Information Extraction: Extract structured data (JSON)
3. Summary Generation: Create concise summary

**Rationale:**
- **Separation of concerns:** Each step has a specific purpose
- **Quality improvement:** Understanding step provides context for extraction
- **Flexibility:** Can modify or skip steps independently
- **Debugging:** Easier to identify which step failed

**Alternatives Considered:**
- Single-step processing: Simpler but less comprehensive
- Parallel processing: Faster but more complex error handling
- Two-step (extract + summarize): Missing understanding step reduces quality

**Trade-offs:**
- ✅ Comprehensive processing pipeline
- ✅ Better quality through multi-step approach
- ⚠️ Higher latency (sequential processing)
- ⚠️ Higher cost (three model invocations per document)

**Optimization Opportunities:**
- Could combine understanding and extraction in single prompt (future optimization)
- Could cache understanding results if processing multiple documents from same source

**Why This Choice:** Quality and maintainability outweigh the cost and latency of sequential processing. The three-step approach provides better results and easier debugging.

---

## ADR-009: JSON Output Format

**Status:** Accepted  
**Date:** 2026-01-07  
**Context:** Need structured output format for processed results.

**Decision:** Store results as JSON files in output bucket with structure:
```json
{
  "source_document": {...},
  "document_understanding": "...",
  "extracted_information": {...},
  "summary": "...",
  "processing_metadata": {...}
}
```

**Rationale:**
- **Structured data:** Easy to parse and integrate with other systems
- **Complete information:** Includes all processing steps
- **Metadata:** Tracks models used and processing timestamp
- **Standard format:** JSON is widely supported

**Alternatives Considered:**
- CSV format: Less flexible for nested data
- XML format: More verbose, less commonly used
- Database storage: Adds complexity, requires database infrastructure

**Trade-offs:**
- ✅ Human-readable and machine-parseable
- ✅ Self-contained (all information in one file)
- ✅ Easy to version and audit
- ⚠️ File-based (requires parsing, not queryable like database)

**Why This Choice:** JSON provides the best balance of structure, readability, and compatibility. File-based storage is simple and sufficient for this use case.

---

## ADR-010: Security and Encryption

**Status:** Accepted  
**Date:** 2026-01-07  
**Context:** Insurance claim documents contain sensitive personal and financial information.

**Decision:** Implement multiple security layers:
- S3 server-side encryption (SSE-S3) on both buckets
- S3 versioning enabled for audit trail
- Public access blocked on both buckets
- IAM least privilege policies
- Separate buckets for input/output isolation

**Rationale:**
- **Compliance:** Meets data protection requirements
- **Audit trail:** Versioning enables tracking of changes
- **Access control:** IAM policies restrict access to necessary services only
- **Defense in depth:** Multiple security layers

**Alternatives Considered:**
- SSE-KMS: More control but adds KMS key management complexity
- Client-side encryption: More secure but adds application complexity
- No encryption: Violates security best practices

**Trade-offs:**
- ✅ Strong security posture
- ✅ Compliance-ready
- ⚠️ Slightly higher cost (versioning storage)
- ⚠️ More complex IAM policies

**Why This Choice:** Security is non-negotiable for sensitive data. Multiple layers provide defense in depth, and SSE-S3 is sufficient without adding KMS complexity.

---

## ADR-011: Lambda Configuration (Timeout and Memory)

**Status:** Accepted  
**Date:** 2026-01-07  
**Context:** Need to balance processing time, cost, and reliability.

**Decision:** Configure Lambda with:
- Timeout: 300 seconds (5 minutes)
- Memory: 512 MB

**Rationale:**
- **Timeout:** Three Bedrock invocations can take 15-30 seconds each, plus S3 operations
- **Memory:** 512 MB is sufficient for document processing (text-based, not image processing)
- **Cost optimization:** Higher memory = faster CPU, but 512 MB is cost-effective for this workload

**Alternatives Considered:**
- 1024 MB memory: Faster but higher cost
- 256 MB memory: Lower cost but may hit memory limits
- 600 second timeout: More headroom but unnecessary for current workload

**Trade-offs:**
- ✅ Adequate for current processing needs
- ✅ Cost-effective configuration
- ⚠️ May need adjustment if processing larger documents or adding image processing

**Why This Choice:** 5 minutes and 512 MB provide a good balance of cost, performance, and reliability. Can be adjusted based on actual metrics.

---

## ADR-012: CloudWatch Logs Retention

**Status:** Accepted  
**Date:** 2026-01-07  
**Context:** Need logging for debugging and monitoring, but want to control costs.

**Decision:** Configure CloudWatch Log Group with 14-day retention.

**Rationale:**
- **Debugging window:** 14 days sufficient for troubleshooting recent issues
- **Cost control:** Prevents indefinite log accumulation
- **Compliance:** Meets typical audit requirements

**Alternatives Considered:**
- 30 days: Longer retention but higher cost
- 7 days: Lower cost but shorter debugging window
- Indefinite: Too expensive for high-volume processing

**Trade-offs:**
- ✅ Good balance of debugging capability and cost
- ✅ Automatic log cleanup
- ⚠️ May lose logs for issues discovered after 14 days

**Why This Choice:** 14 days provides sufficient debugging window while controlling costs. Can be increased if needed for compliance.

---

## Future Considerations

**Potential Improvements:**
- **PDF Processing:** Current implementation only handles text files. Consider adding Amazon Textract for PDF extraction.
- **Model Optimization:** Could experiment with using Haiku for extraction to reduce costs (quality trade-off).
- **Caching:** Could cache document understanding results for similar documents.
- **Error Handling:** Could add Dead Letter Queue (DLQ) for failed processing.
- **Monitoring:** Could add CloudWatch alarms for error rates and processing times.
- **Cost Optimization:** Implement token usage tracking and optimize prompts to reduce costs.
- **Multi-Modal:** Leverage Claude 3.5 Sonnet's vision capabilities for scanned documents.

**These are documented for future iterations, not current requirements.**

---

## Summary

This system prioritizes **production readiness, security, and cost-effectiveness** while maintaining **high quality results**. Every decision was made with these principles in mind, and trade-offs were carefully evaluated. The architecture is designed to be **maintainable, scalable, and secure** while remaining **simple enough to understand and modify**.

For questions or suggestions on these decisions, please open an issue or discussion.
