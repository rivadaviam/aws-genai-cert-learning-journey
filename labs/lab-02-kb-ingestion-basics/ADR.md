# Architecture Decision Records — Lab 02: KB Ingestion Basics

> **Executive summary:** This lab prioritizes **understanding and measurement** over **large-scale ingestion**. The main “architecture” here is procedural: learn chunking and cost drivers locally, then connect to AWS Knowledge Bases with intention.

---

## ADR-L02-001: Foundations before bulk sync

**Status:** Accepted  

**Context:** Ingesting and re-ingesting large PDFs into a Knowledge Base while still learning parsers, chunk strategies, and retrieval behavior can generate **avoidable embedding and sync cost**.

**Decision:** Treat **Lab 02** as a **basics checkpoint**: token awareness, chunk preview, and optional minimal AWS resources — **before** relying on a full automated pipeline.

**Consequences:**

- ✅ Lower risk of expensive “learning loops”
- ✅ Clearer mental model when moving to full IaC
- ⚠️ Does not by itself deliver production RAG — it precedes that work

---

## ADR-L02-002: Local token approximation for sanity checks

**Status:** Accepted  

**Context:** Embedding and many Bedrock operations are **token-sensitive**. Developers need fast feedback without always invoking cloud APIs.

**Decision:** Provide a **simple local estimator** (roughly ~4 characters per token for Latin-heavy text) in `app/`. Document that this is **approximate**, not a billing guarantee.

**Consequences:**

- ✅ Fast iteration with no AWS spend
- ✅ Good enough to compare “small doc vs huge doc” before sync
- ⚠️ Must be recalibrated against the **specific embedding model** for production accuracy

---

## ADR-L02-003: Naive chunk preview vs production chunking

**Status:** Accepted  

**Context:** Production RAG often needs **command-aware** or structure-aware chunking (see external PDF RAG projects). Lab 02 uses **naive token-targeted splits** for teaching.

**Decision:** Implement **transparent, simple** chunk preview in Python. Call out in README that **domain-specific chunkers** replace this later.

**Consequences:**

- ✅ Easy to read and modify for experiments
- ⚠️ Output must not be mistaken for optimal chunks for every corpus

---

## ADR-L02-004: Optional Terraform — single scratch bucket only

**Status:** Accepted  

**Context:** Full KB + vector store stacks are non-trivial; not everyone needs them on day one of “basics.”

**Decision:** Ship **optional** Terraform that provisions at most a **small experimental S3 bucket** (naming via variables, encryption, blocked public access). No Bedrock KB resources in this lab’s default story — those belong in a dedicated pipeline repo or a later lab.

**Consequences:**

- ✅ Isolated place for a few test objects
- ✅ `terraform destroy` scope stays small
- ⚠️ Users still attach KB / data sources in console or other IaC when ready

---

## ADR-L02-005: Optional `retrieve` CLI for retrieval-only validation

**Status:** Accepted  

**Context:** **Ingestion cost** and **retrieval quality** are related but separable concerns.

**Decision:** Offer an **optional** `retrieve` command that calls `bedrock-agent-runtime` when `KB_ID` is set, so learners can test **queries** without re-running full ingestion.

**Consequences:**

- ✅ Separates “did sync work?” from “does retrieval answer my question?”
- ⚠️ Requires existing KB configuration and permissions

---

## ADR-L02-006: Document the expensive lesson explicitly

**Status:** Accepted  

**Context:** Personal narrative increases retention and helps others avoid the same mistake.

**Decision:** State clearly in the lab README that **repeated syncs while still learning** drove real cost, and that **this lab** is the distilled response.

**Consequences:**

- ✅ Aligns with “learn in public” and honest engineering storytelling
- ⚠️ No substitute for each reader’s own budget alerts and AWS Cost Explorer review

---

## Future considerations

- Add a follow-up lab that imports **only** the Terraform modules from the companion repo **[aws-pdf-rag-mr](https://github.com/rivadaviam/aws-pdf-rag-mr)**
- Optional diagram of Bedrock KB + S3 data source lifecycle
- Compare rough local estimates with **actual** token usage from a single small `StartIngestionJob` run (once per experiment, not in a loop)
