# process_log.md — Hour-by-Hour Timeline
**Made in Rwanda Recommender · S2.T1.3**
**Candidate: Gabriel Ntwari**

---

## Hour-by-Hour Timeline

| Time | What I worked on |
|---|---|
| Hour 1 | Read the brief carefully. Understood the two core requirements: (1) content-based recommender with TF-IDF, (2) offline artisan lead workflow. Set up project folder, generated synthetic data with `generator.py`. |
| Hour 2 | Built first TF-IDF index. Ran eval loop — got NDCG@5 ≈ 0.00. Diagnosed root cause: catalog titles like "Premium Kigali Leather" had zero token overlap with queries like "leather boots". All evaluated queries missed top-5, avg rank ~36. |
| Hour 3 | Rewrote `generator.py` so product titles and descriptions include real search terms (e.g. "boots shoes sandals cowhide"). NDCG rose to ~0.30. Identified next bottleneck: French and misspelled queries still failing, avg rank still ~60. |
| Hour 4 | Added fuzzy spell correction (rapidfuzz) and FR/KIN→EN translation dictionaries. NDCG rose to ~0.40. Added hybrid word+char TF-IDF vectorizer. Discovered catalog had duplicate titles — deduplication brought NDCG to ~0.80, with significant improvement in avg rank and top-5 coverage. |
| Hour 5 | Built `Recommender.py` with CLI (`--q` argument), local-boost logic, fairness cap, and fallback curation. Debugged sklearn version mismatch (pickle saved on 1.8.0, loaded on 1.6.1) — rolled back to 1.6.1 and re-saved pickle. Final NDCG stabilised at ~0.80. |
| Hour 6 | Wrote `dispatcher.md` — offline artisan SMS workflow, unit economics, Kinyarwanda SMS version, 3-month pilot plan. Wrote `eval.ipynb` with full metric progression. Wrote `README.md`. |

---

## Metric Progression (approximate)

| Stage | NDCG@5 | Avg Rank | % in Top-5 |
|---|---|---|---|
| Baseline TF-IDF (char only) | ~0.00 | ~36 | 0% |
| Fixed data generator | ~0.30 | ~60 | ~35% |
| + Fuzzy correction + FR/KIN translation | ~0.40 | ~10 | ~45% |
| + Hybrid word+char vectorizer | ~0.38 | ~9 | ~44% |
| + Catalog deduplication | **~0.80** | **~1–2** | **~95–100%** |

> Note: exact scores vary slightly with random seed and catalog regeneration.
> Final reported NDCG@5 is approximately 0.80.

---

## LLM Tools Used

| Tool | Why I used it |
|---|---|
| Claude (Anthropic) | Debugging eval loop, suggesting hybrid TF-IDF architecture, drafting dispatcher.md structure, fixing version conflicts |

---

## Three Sample Prompts I Actually Sent

**Prompt 1:**
> "I am getting NDCG@5 = 0.0000, avg rank 36.6. Here is my eval loop code. What is wrong?"

*Why I used it:* I had stared at the code for 30 minutes and could not see why all scores were zero. Claude identified the SKU type mismatch and the token overlap problem immediately.

**Prompt 2:**
> "My catalog titles are 'Premium Kigali Leather' but queries are 'leather boots'. There is zero token overlap. How do I fix this without switching to sentence embeddings?"

*Why I used it:* The brief says TF-IDF is acceptable and CPU-only is required. I needed a way to bridge the vocabulary gap without adding heavy dependencies. Claude suggested enriching product descriptions with search terms and using char n-gram TF-IDF for typo robustness.

**Prompt 3:**
> "NDCG is now ~0.80. Give me the updated Recommender.py with CLI, local-boost for niche districts, fairness cap, and fallback curation."

*Why I used it:* I had the logic working in the notebook and needed to port it cleanly into a class with a CLI entry point matching the brief's required format.

---

## Prompt I Discarded and Why

**Discarded prompt:**
> "Use sentence-transformers all-MiniLM-L6-v2 to build the embedding index instead of TF-IDF."

*Why I discarded it:* The brief specifies CPU-only and query-time < 250ms. Sentence embeddings on CPU for a 400-product catalog are feasible, but the brief also says "deep ML is not required — clarity and correctness are." More importantly, the brief specifically names TF-IDF as the expected approach for Tier 1. I kept the hybrid char+word TF-IDF which already achieves NDCG@5 ≈ 0.80.

---

## Hardest Decision

The hardest decision was whether to deduplicate the catalog or fix the generator.

When I discovered that deduplication (reducing duplicate rows down to unique products) was the reason NDCG jumped from ~0.38 to ~0.80, I had two options:

1. **Deduplicate at runtime** in `Recommender.py` — quick fix, but the catalog file stays broken
2. **Fix the generator** so it never produces duplicates — correct fix, but means rewriting the generator and regenerating all files

I chose to fix the generator. A recommender that silently deduplicates its own catalog at runtime is hiding a data quality bug, not solving it. The brief asks for a reproducible pipeline — if the generator produces bad data, the pipeline is not reproducible. Fixing the source was the right engineering decision even though it took longer.

---

## Declared LLM Assistance Summary

All LLM use was for debugging, code porting, and documentation drafting. Every architectural decision (TF-IDF over embeddings, hybrid vectorizer, fuzzy correction, dedup fix) was made by me after understanding the problem. I ran every eval myself, interpreted the numbers, and directed the fixes. I am prepared to defend every line of code in the Live Defense session.
