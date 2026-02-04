# LinkedIn Post: Build-to-Learn Framework Amplification

**Type:** Amplification + Short Storytelling
**Amplifies:** build-to-learn-framework-devto.md
**Platform:** LinkedIn
**Article Link:** https://dev.to/rivadaviam/the-build-to-learn-framework-how-a-near-disaster-taught-me-to-learn-in-public-c2e

## Publishing Strategy

1. **Create post as an IMAGE post** -- upload the architecture diagram as the image:
   `labs/lab-01-claims-doc-processing/diagrams/generated-diagrams/insurance-claim-processing-architecture-lab01.png`
   - Do NOT paste the Dev.to link in the post body (LinkedIn penalizes external links, reducing reach ~40-50%)
   - The architecture diagram is a scroll-stopper for the technical audience and directly supports the narrative
2. **Immediately after publishing**, post the first comment below with the Dev.to link
   - LinkedIn will auto-generate a preview card in the comment with the article's OG image, title, and description
3. This gives maximum organic reach + visual impact + accessible link

---

## Post Content

I almost created an infinite loop that would have cost me thousands in AWS bills.

And I'm grateful it almost happened.

I was building an automated insurance claim processing pipeline with Amazon Bedrock — not for a client, but as a learning exercise while preparing for the AWS GenAI Developer certification.

My architecture looked elegant: one S3 bucket, two prefixes — input documents go in, processed results come out.

Clean. Simple. Catastrophic.

Every output file would re-trigger the Lambda. Every re-trigger would generate another output. An infinite loop with an infinite bill.

I caught it mid-sentence while writing an Architecture Decision Record. The act of documenting my bucket strategy forced me to think through what would actually happen in production — and I realized the flaw before it cost me anything.

That moment crystallized something I now follow with every project: build real things, document every decision, and share the messy middle. Not the polished success story — the wrong turns, the trade-offs, the near-misses that actually teach something.

Documentation isn't overhead. It's thinking made visible.

I wrote the full story — including the three-step AI pipeline, model selection trade-offs, and every ADR — in my first Build-to-Learn article. Link in the comments.

If you're studying for a certification: do you build alongside your studies, or focus on the material first? And if you're ready to try it yourself, the repo is open source — fork it and build your own lab.

I'd genuinely love to hear your approach.

#BuildToLearn #AWSCommunity #LearnInPublic #AmazonBedrock

---

## First Comment (post immediately after publishing)

Here's the full article with code, architecture diagrams, and every decision documented:
https://dev.to/rivadaviam/the-build-to-learn-framework-how-a-near-disaster-taught-me-to-learn-in-public-c2e

The entire project is open source — clone it, break it, improve it:
https://github.com/rivadaviam/aws-genai-cert-learning-journey
