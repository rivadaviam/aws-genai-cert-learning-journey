# LinkedIn Post: Bedrock KB Cost Lesson (Amplification)

**Type:** Amplification + proof / story  
**Amplifies:** `bedrock-kb-cost-lesson-devto.md` (dev.to)  
**Platform:** LinkedIn  
**Suggested image:** `_bmad-output/blog-articles/rag-pdf-cost-anomaly.png` (upload as the post image — the billing screenshot is the scroll-stopper)

## Publishing strategy

1. **Create an image post** — upload **`rag-pdf-cost-anomaly.png`** (AWS billing table: ~$363 over two days, Bedrock vs OpenSearch). The chart is the proof; it supports the narrative without requiring the reader to trust adjectives alone.
2. **Do not put the dev.to URL in the post body** — LinkedIn often reduces reach when external links are in the main text. Keep the story and the question in the body.
3. **Immediately after publishing**, add a **first comment** with the dev.to article link and optionally the GitHub repo link. LinkedIn will generate a preview card in the comment.

---

## Post content (copy for LinkedIn body)

I ran a two-day experiment with Amazon Bedrock Knowledge Bases and technical PDFs.

Then I opened Cost Explorer.

The total for those two days was about **three hundred sixty dollars** — almost all **Bedrock**, plus a small **OpenSearch** line. Way more than I had mentally budgeted for "I'll just sync this and see."

Here's what I had actually been doing: **re-syncing** while I was still learning chunking, parsers, and paths. Every pass felt like fixing configuration. In billing terms, many passes looked like **paying to embed the same corpus again**.

I'm not sharing this to flex a bill or to scare anyone off RAG on AWS. I'm sharing it because **the invoice taught me the pricing model** in a way the docs had not fully sunk in yet — especially how **ingestion and embedding** add up when you treat "one more sync" as free.

After that, I changed how I build: **measure tokens and preview chunks locally first**, treat re-sync as a **budget line**, and document the pipeline so future me does not repeat the loop.

So was it a **cheap lesson or an expensive one**?

Painful on the receipt. Cheap compared to learning the same lesson on a production system with someone else's trust on the line.

If you've ever had a cloud bill teach you something, what did you change the next day?

#BuildToLearn #AWSGenAI #AmazonBedrock #LearnInPublic #GenerativeAI

---

## First comment (post right after the main post)

Full write-up with numbers, what I misunderstood, and what I changed in my repo (including Lab 02 — foundations before big KB syncs):

**[LINK TO DEV.TO ARTICLE — add after you publish]**

Learning journey (labs, ADRs — includes Lab 02 write-up):

https://github.com/rivadaviam/aws-genai-cert-learning-journey

Full PDF → Bedrock KB pipeline code (Lab 2 companion implementation):

https://github.com/rivadaviam/aws-pdf-rag-mr

---

## Post content — Spanish variant (optional)

Misma imagen: **`rag-pdf-cost-anomaly.png`**.

---

Hice un experimento de dos días con **Amazon Bedrock Knowledge Bases** y PDFs técnicos.

Después abrí **Cost Explorer**.

El total en esas **48 horas** fue del orden de **trescientos sesenta dólares**: casi todo **Bedrock**, más una línea pequeña de **OpenSearch**. Bastante más de lo que yo tenía en la cabeza para un “sync y vemos qué pasa”.

Lo que estaba haciendo, sin querer: **volver a sincronizar** mientras seguía aprendiendo chunking, parsers y rutas. Cada vuelta se sentía como “arreglar config”. En facturación, muchas vueltas se parecían a **volver a embedear el mismo corpus**.

No comparto esto para asustar ni para presumir gasto. Comparto porque **la factura me enseñó el modelo de costos** de una forma que la documentación todavía no me había hecho sentir del todo: sobre todo cómo suma **ingesta y embeddings** cuando “un sync más” no es gratis.

Después cambié cómo construyo: **medir tokens y previsualizar chunks en local primero**, tratar el **re-sync como partida de presupuesto**, y documentar el pipeline para que el yo del futuro no repita el bucle.

¿Lección **cara** o **barata**? Dolorosa en el recibo. Barata comparada con aprender lo mismo en producción con la confianza de otros en juego.

¿Alguna vez una factura de nube te enseñó algo que los docs no habían cerrado? ¿Qué cambiaste al día siguiente?

#BuildToLearn #AWSGenAI #AmazonBedrock #LearnInPublic #GenerativeAI

---

## Notes for the author

- Replace the dev.to placeholder with the live URL once published.
- Ensure **`rag-pdf-cost-anomaly.png`** is committed on `main` at `_bmad-output/blog-articles/` so the raw GitHub URL in the dev.to article resolves for readers.
- Optional: pin the comment with links for visibility.
- **Language:** The dev.to article is in **English** (matches the repo and global dev.to audience). Use the **Spanish** block above for LinkedIn if your network engages more in Spanish; keep **hashtags** as-is or localize only if you prefer.
