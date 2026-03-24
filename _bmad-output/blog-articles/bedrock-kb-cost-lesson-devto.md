---
title: "I Spent ~$363 in Two Days on Bedrock — Cheap Lesson or Expensive One?"
published: true
description: A PDF Knowledge Base experiment taught me more about AWS GenAI billing than any pricing page. Here's what showed up on the invoice — and what I changed afterward.
tags: aws, amazonbedrock, generativeai, learninpublic
cover_image: https://raw.githubusercontent.com/rivadaviam/aws-genai-cert-learning-journey/main/_bmad-output/blog-articles/cover-devto.png
series: Build-to-Learn with AWS GenAI
---

The pricing page told me embeddings were "per thousand tokens." The **bill** told me what that actually means when you sync a corpus more than once while you are still learning.

This is the story of a **two-day spike** on my AWS account — mostly **Amazon Bedrock** — and what I took away from it. Spoiler: I do not think it was only money down the drain.

---

## The receipt (literally)

I pulled up **Cost Explorer** after a weekend of experiments. Two consecutive days in December looked like this:

![AWS billing breakdown: Bedrock and OpenSearch over two days](https://raw.githubusercontent.com/rivadaviam/aws-genai-cert-learning-journey/main/_bmad-output/blog-articles/rag-pdf-cost-anomaly.png)

Roughly:

| | Total (two days) |
|--|--:|
| **All services (shown)** | **~$363** |
| **Amazon Bedrock** | **~$353** |
| **Amazon OpenSearch Service** | **~$7** |

Most of that was **not** me chatting with Claude in the playground. It was **Knowledge Base work**: pointing Bedrock at data in S3, running **ingestion / sync jobs**, and **re-running** them while I changed chunking, parsers, and paths — before I had a clear picture of how **embedding tokens** accumulate across **retries**.

I had expected "some cost." I had not internalized how fast **repeat syncs** turn into **repeat embeddings** for the same underlying text.

---

## What I thought I was doing

I was building a **RAG-style pipeline** over **technical PDFs**: extract text, get it into a **Bedrock Knowledge Base**, run **retrieval**, and eventually wire that into an application.

That sounds linear. In practice my early loop looked more like:

1. Upload or point at objects in S3.
2. Start a sync.
3. Notice something wrong — layout, chunk boundaries, metadata, or retrieval quality.
4. **Change the preprocessing**, upload again, **sync again**.
5. Repeat step 4 until I understood what "good" looked like.

Every pass felt like "fixing configuration." In billing terms, many passes looked like **new embedding work**. The console does not always feel like spending money; **Cost Explorer** does.

---

## What the invoice taught me (that the docs had not fully sunk in yet)

**GenAI on AWS is not one line item.** For Knowledge Bases, the mental model that finally stuck:

- **Ingestion / embedding** is where large PDFs hurt — you pay for **tokens processed into the vector store**, not for "having a PDF on disk."
- **Retrieval** and **downstream model calls** are **additional** meters. Separating "sync cost" from "query cost" matters when you debug.
- **Re-syncing the same corpus** while you tune chunking is not a free redo. You are often paying for **another full pass** over the same content unless you have designed for **incremental** or **diff-aware** updates.

None of that is a secret — it is all in the documentation. **The bill was the tutorial that actually stuck.**

---

## ¿Lección cara o barata?

If you judge only by the number on the screen, it was an **expensive** lesson.

If you judge by what I would pay for the same misunderstanding **in production**, under deadline, with a team and customer trust on the line — **learning it on my own lab account** starts to look **cheap**. I paid once in dollars and once in humility. I would rather do that **before** I ever optimize someone else's budget.

So my answer: **it was both.** Painful in the moment, **valuable** in context — and only "wasteful" if I pretended nothing needed to change afterward.

---

## What I changed in how I build

**1. Measure before sync.**  
I stopped treating "upload and sync" as the first step. I added **local** steps: approximate **token counts**, **preview chunk boundaries**, and sanity-check **file sizes** *before* triggering another full ingestion. That mindset is documented in **[Lab 02: KB Ingestion — Foundations First](https://github.com/rivadaviam/aws-genai-cert-learning-journey/tree/main/labs/lab-02-kb-ingestion-basics)** in the learning-journey repo — small CLI helpers, no cloud required for the first pass.

**2. Separate "pipeline quality" from "vector store plumbing."**  
I invested in a clearer **PDF → clean text → intentional chunks → S3** path in **[aws-pdf-rag-mr](https://github.com/rivadaviam/aws-pdf-rag-mr)** — the companion repo with the **full pipeline code** (Terraform, Lambda processor, Bedrock KB, S3 Vectors) that matches what Lab 02 points you toward *after* the foundations. That way Bedrock sees **stable, deliberate** chunks instead of whatever the default path produced on raw PDFs while I was still iterating.

**3. Use the cloud bill as a design review.**  
**Billing alerts** and **Cost Explorer** by service are now part of my **definition of done** for experiments, not something I check when I get curious.

---

## If you are about to do the same experiment

- **Start with tiny files** — one short text, one sync, one retrieve — until the **numbers** make sense.
- **Read embedding and KB pricing** as **token math**, then estimate **tokens × price × number of sync attempts**.
- **Treat re-sync as a budget line**, not a config tweak.
- **Document decisions** (I use ADRs) so the next you does not repeat the same loop "just one more time."

---

## Closing

I did not write this to scare anyone away from Bedrock or Knowledge Bases. I still use them. I write it because **the messy middle** — including an invoice that made me stare at the screen — is part of **learning in public** honestly.

**Documentation is not overhead. It is thinking made visible.** So is a cost breakdown when it forces you to redraw your architecture.

If this story saved you one accidental **full re-embedding** of a giant PDF, it was worth more than those two days of spend.

---

**Repos:**  
- **[aws-genai-cert-learning-journey](https://github.com/rivadaviam/aws-genai-cert-learning-journey)** — learning path, ADRs, and **Lab 02** docs (`labs/lab-02-kb-ingestion-basics/`).  
- **[aws-pdf-rag-mr](https://github.com/rivadaviam/aws-pdf-rag-mr)** — **implementation code** for the PDF → KB pipeline (the “after Lab 02” stack).

**Tags I'll use when I share:** `#BuildToLearn` `#AWSGenAI` `#AmazonBedrock` `#LearnInPublic` `#RAG`

---

*Have you had a GenAI bill that taught you something the docs alone did not? I would genuinely like to hear what changed in your process afterward.*
