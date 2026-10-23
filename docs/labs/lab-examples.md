# Lab examples (For future references)

I’ll look up current public RAG datasets and evaluation benchmarks so the suggestions match what people actually use for data-prep and eval labs.

A good RAG lab library is not “as many datasets as possible.” It is a small set of **public corpora that force different prep work**, plus **gold questions that let you evaluate retrieval and generation separately**. Aim for 5–7 labs, each with a short write-up of pipeline, chunking choices, metrics, and failure cases.

Below is a portfolio-shaped set, then extras if you want more coverage.

## How to pick datasets (so the library actually shows skill)

Choose corpora that differ on at least three axes:

| Axis | Why it matters for a portfolio |
|---|---|
| Document type | Wikipedia markup vs PDF vs HTML vs tables vs multi-turn chat |
| Reasoning type | Factoid, multi-hop, numerical, unanswerable, temporal |
| Eval labels | Gold passages, evidence spans, difficulty scores, or only gold answers |
| Messiness | Clean text is easy; PDFs, tables, and noisy HTML show real prep skill |
| Domain | General, finance, science, news, enterprise — not all Wikipedia |

Keep each lab **small and reproducible**: 50–200 docs and 100–300 questions is enough if you document sampling, licenses, and seed.

---

## Recommended core library (6 labs)

These six cover almost every RAG skill people look for, without overlapping too much.

### 1. Wikipedia + HotpotQA — baseline multi-hop
**Why:** Everyone understands Wikipedia RAG. HotpotQA adds supporting-fact labels, so you can score **retrieval independently of generation**.

- **Prep skills:** wiki markup / section parsing, heading-aware chunking, entity metadata, alias handling
- **Eval skills:** Recall@k on supporting passages, multi-hop failures, answer EM/F1 vs faithfulness
- **Get it:** [HotpotQA](https://hotpotqa.github.io/) (also on Hugging Face); Wikipedia dumps or [Structured Wikipedia](https://rag-repo.org/datasets/)
- **Lab design:** subsample 200–500 articles that cover a HotpotQA question slice; compare naive fixed-size chunks vs section chunks vs parent-child chunks

HotpotQA is better than SQuAD here: SQuAD is single-span and too easy to look impressive.

### 2. Qasper — scientific papers, evidence spans, “unanswerable”
**Why:** Real RAG is papers, not encyclopedia articles. Qasper questions are over NLP papers, with evidence and an explicit unanswerable class.

- **Prep skills:** PDF/XML layout, abstracts vs body, citations, figure/table captions, section hierarchy
- **Eval skills:** evidence-span retrieval, abstention, long-doc chunking tradeoffs
- **Get it:** [allenai/qasper](https://huggingface.co/datasets/allenai/qasper)
- **Lab design:** parse PDFs yourself *and* compare against the provided text; this is a strong “I don’t just `load_dataset()`” demo

Close cousin if you want more PDF/multimodal work: [Open RAG Bench](https://github.com/vectara/open-rag-bench) (1,000 arXiv PDFs, text + tables + images, ~3k QA pairs).

### 3. FinanceBench or FinQA — long PDFs, tables, numbers
**Why:** This is the classic “enterprise RAG is hard” lab. Tables, units, page-level evidence, and arithmetic.

| Dataset | Best for | License / access |
|---|---|---|
| [FinanceBench](https://github.com/patronus-ai/financebench) | Real 10-K/10-Q PDFs, page-level evidence, 150 open QA pairs | CC BY-NC 4.0; full set is gated |
| [FinQA](https://github.com/czyssrs/FinQA) | Numerical reasoning over reports | fully public |
| [TAT-QA](https://github.com/NExTplusplus/TAT-QA) | Hybrid text + table QA | fully public |

- **Prep skills:** PDF parsing, table extraction (Camelot/unstructured/Docling), page metadata, unit normalization, header/footer stripping
- **Eval skills:** exact numeric match, evidence-page hit rate, hallucination on figures
- **Lab design:** one pipeline on raw PDFs, one on extracted tables as structured rows; show that text-only chunking loses table QA

FinanceBench is the most “portfolio impressive.” FinQA/TAT-QA are cleaner if you need a fully open, citable set.

### 4. MultiHop-RAG — cross-document news + metadata
**Why:** Built specifically for RAG, not retrofitted from old QA. Evidence is spread across 2–4 news docs, and queries use metadata (date, source).

- **Prep skills:** news HTML/article cleaning, timestamp/source metadata, dedup, recency filters
- **Eval skills:** multi-doc retrieval, metadata-aware retrieval, claim-level faithfulness
- **Get it:** [yixuantt/MultiHopRAG](https://huggingface.co/datasets/yixuantt/MultiHopRAG)
- **Size:** 2,556 queries — easy to run end-to-end

This is one of the best “I understand RAG as a system, not just embeddings” datasets.

### 5. CRAG (Meta) — messy web HTML, question diversity, dynamism
**Why:** Closest public set to production web RAG. Full HTML pages, KG/mock APIs, false-premise questions, and static vs fast-changing facts.

- **Prep skills:** HTML boilerplate removal, multi-page ranking, noisy snippets, KG vs web fusion
- **Eval skills:** 8 question types (simple, comparison, aggregation, multi-hop, false premise, …), hallucination vs abstention, temporal drift
- **Get it:** [facebookresearch/CRAG](https://github.com/facebookresearch/CRAG/) or [Quivr/CRAG](https://huggingface.co/datasets/Quivr/CRAG)
- **Size:** ~2.7k–4.4k QA pairs; subsample HTML (pages are heavy)

Use this lab to show **refusal on false-premise questions** and **freshness**, not just accuracy.

### 6. MTRAG — multi-turn, enterprise-ish, unanswerable
**Why:** Single-shot QA is only half of RAG. MTRAG is human multi-turn conversations over 4 corpora (ClapNQ, Cloud, FiQA, Govt), with retrieval *and* generation tasks.

- **Prep skills:** conversation state, query rewriting, follow-up resolution, domain corpora with mixed quality
- **Eval skills:** turn-level retrieval, answer groundedness, underspecified / unanswerable questions
- **Get it:** [IBM/mt-rag-benchmark](https://github.com/IBM/mt-rag-benchmark)
- **Follow-on:** MTRAG-UN (unanswerable, underspecified, non-standalone) if you want a 2026-flavored lab

This is the lab that separates “I chunked Wikipedia” from “I can evaluate a conversational RAG system.”

---

## Strong add-ons (pick 1–2, not all)

Use these if you want a seventh lab with a clear extra skill:

| Dataset | Extra skill it proves |
|---|---|
| **BEIR** subsets ([FiQA](https://sites.google.com/view/fiqa/), SciFact, NFCorpus, TREC-COVID) | Retrieval-only eval: nDCG@10, Recall@k, zero-shot domain shift |
| **Natural Questions / MS MARCO** | Large-scale passage retrieval; good for embedding model bake-offs |
| **LiveRAG** ([paper](http://arxiv.org/abs/2511.14531), FineWeb-10BT) | Modern 2025 RAG challenge set with difficulty/discriminability scores |
| **PubMedQA / PMC-OA** | Biomedical abstracts vs full text; domain vocab, citation structure |
| **CUAD** | Legal contracts; clause retrieval, long docs, high cost of error |
| **NarrativeQA** | Book/script-length context; summarization-style answers |
| **FreshQA** | Time-sensitive questions; stale-index failures |
| **RAGBench** | TRACe-style RAG evaluation if you want a paper-aligned metric suite |

For **code/docs RAG** (often missing from portfolios): ingest a public docs site you are allowed to use (e.g. a project’s GitHub `docs/` + issues) and build questions yourself. There is no single gold-standard public “docs RAG” set as clean as HotpotQA, so a small self-built eval set here actually looks more skilled than another Wikipedia clone.

---

## What to run on each dataset (so labs look like skill, not notebooks)

Keep the protocol the same across the library so people can compare:

1. **Prep variants**
   - fixed 512-token chunks vs semantic/section chunks vs parent-child
   - with/without metadata (title, date, section, page, table-id)
   - with/without table/HTML cleaning
2. **Retrieval variants**
   - BM25 vs dense vs hybrid
   - reranker on/off
3. **Generation variants**
   - extractive vs abstractive prompt
   - “answer only from context / say I don’t know”
4. **Metrics, split by stage**
   - Retrieval: Recall@k, nDCG@k, MRR (when gold passages exist)
   - Generation: EM/F1 or numeric exact match; faithfulness / citation hit rate; abstention on unanswerable
   - End-to-end: LLM-as-judge *calibrated against gold*, not instead of it

Datasets that give you **gold evidence** (HotpotQA, Qasper, FinanceBench, MultiHop-RAG) are more valuable than datasets that only give a final answer. They let you prove whether the failure was retrieval or generation.

---

## Practical constraints

- **License:** FinanceBench open sample is **CC BY-NC**. CRAG, HotpotQA, Qasper, FinQA, MultiHop-RAG, MTRAG, BEIR are the usual research-friendly choices. Always put license + citation in each lab README.
- **Size:** Do not ingest full Wikipedia, FineWeb, or PMC. Subsample with a documented seed and publish the ID list.
- **Cost:** 100–300 questions per lab is enough for a public repo. Save full-corpus runs for one flagship (MultiHop-RAG or a BEIR subset).
- **Repro:** pin parser version (unstructured/Docling), embedding model, chunk params, and the exact question IDs.

---

## A tight “library of lab runs” you could actually ship

If you want a concrete 6-lab sequence:

1. **HotpotQA / Wikipedia** — chunking + multi-hop retrieval
2. **Qasper** — PDF/paper structure + evidence spans
3. **FinanceBench or FinQA** — tables, numbers, long PDFs
4. **MultiHop-RAG** — cross-doc news + metadata
5. **CRAG subsample** — HTML noise, false premise, dynamism
6. **MTRAG** — multi-turn and unanswerable

That set demonstrates data prep *and* evaluation without looking like you only reran Wikipedia RAG six times.

If you want, I can turn this into a repo skeleton: one folder per lab, shared eval protocol, and a suggested subsample size / metric table for each dataset.