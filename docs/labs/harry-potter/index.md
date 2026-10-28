# Harry Potter RAG Lab

A demonstration of RAG pipeline using Harry Potter as the context.

- [Lab 1: Basic RAG](./lab1-basic_rag.ipynb)

```mermaid
flowchart TD
    subgraph build["Build the index — once per config"]
        A["harrypotter.pdf"] --> B["Ingest — PyMuPDF + TOC<br/>slice Book 1, 17 chapters"]
        B --> C["Chunk — 512 tokens, 15% overlap<br/>249 chunks to harrypotter-chunks.jsonl"]
        C --> D["Validate<br/>shape, unit norms, metadata keys"]
        D --> E["Embed — Titan Text v2<br/>1024-d, normalised, disk-cached"]
        E --> F[("Chroma hp1-c512-ov15<br/>cosine, embedding stays on Bedrock")]
        C --> G["BM25 index<br/>same 249 chunks"]
    end
    subgraph ask["Answer a question"]
        Q[Question] --> R{Retrieve top-5}
        R -->|dense| S["5 chunk records"]
        R -->|sparse| S
        S --> T["Build prompt<br/>labelled excerpts + grounding rules"]
        T --> U["Generate — Bedrock Converse<br/>temperature 0"]
        U --> V["Answer + citations<br/>+ the retrieved chunks"]
        V --> W["Evaluate by eye<br/>retrieval hit vs answer quality"]
    end
    F -.-> R
    G -.-> R
    W --> X["Finding — the winner flips with the wording"]
```


- [Lab 2: Evaluation Prep](./lab2-evaluation-prep.ipynb)
- [Lab 3: Evaluation](./lab3-rag-evaluation.ipynb)


*Disclaimer: The source book is copyrighted and is not included in this repository. This lab is for personal, non-commercial study only — only original code, questions, and metrics are published.*