import json, re, hashlib, os, urllib.request
from pathlib import Path
import numpy as np
import boto3
from botocore.config import Config
from rank_bm25 import BM25Okapi
from dotenv import load_dotenv
from tqdm.auto import tqdm

LABS = Path("/Users/tc/Documents/Github/monitus_code/labs"); DATA = LABS / "data"
load_dotenv(LABS / ".env")
region = os.getenv("AWS_REGION")

# --- Titan (cached) ---
TITAN = "amazon.titan-embed-text-v2:0"; TDIM, TNORM = 1024, True
tkey = lambda t: hashlib.sha256(f"{TITAN}|{TDIM}|{TNORM}|{t}".encode()).hexdigest()
CACHE = {}
for line in (DATA / "embeddings_cache.jsonl").read_text(encoding="utf-8").splitlines():
    if line.strip():
        r = json.loads(line); CACHE[r["key"]] = r["vector"]

# --- Qwen3 via Ollama ---
QWEN = "qwen3-embedding:4b"
INSTRUCT = "Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery: "

def ollama_embed(texts, batch=16):
    out = []
    for i in range(0, len(texts), batch):
        req = urllib.request.Request(
            "http://localhost:11434/api/embed",
            data=json.dumps({"model": QWEN, "input": texts[i:i + batch]}).encode(),
            headers={"Content-Type": "application/json"})
        out += json.loads(urllib.request.urlopen(req, timeout=600).read())["embeddings"]
    v = np.array(out, dtype=np.float32)
    return v / np.linalg.norm(v, axis=1, keepdims=True)

# --- data ---
CHUNKS = [json.loads(l) for l in (DATA / "harrypotter-chunks.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
BY = {c["chunk_id"]: c for c in CHUNKS}
tokenize = lambda t: re.findall(r"[a-z0-9]+", t.lower())
bm25 = BM25Okapi([tokenize(c["text"]) for c in CHUNKS])
rows = [json.loads(l) for l in (LABS / "eval" / "qa_candidates.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
usable = [r for r in rows if r.get("locatable")]

texts = [c["text"] for c in CHUNKS]
print("embedding corpus with Titan (cache) and Qwen3 (Ollama)...")
XT = np.array([CACHE[tkey(t)] for t in texts], dtype=np.float32)
XT /= np.linalg.norm(XT, axis=1, keepdims=True)
XQ = ollama_embed(texts)

QT = np.array([CACHE[tkey(r["question"])] for r in usable], dtype=np.float32)
QT /= np.linalg.norm(QT, axis=1, keepdims=True)
QQ = ollama_embed([INSTRUCT + r["question"] for r in usable])

# --- rerank ---
rerank_client = boto3.client("bedrock-agent-runtime", region_name=region)
RERANK = "amazon.rerank-v1:0"
RC = DATA / "rerank_cache.jsonl"
RCACHE = {}
if RC.exists():
    for line in RC.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line); RCACHE[r["key"]] = r["ranking"]

def rerank(question, ids, top_n=5):
    key = hashlib.sha256(f"{RERANK}|{question}|{top_n}|{'|'.join(ids)}".encode()).hexdigest()
    if key in RCACHE:
        return [r["chunk_id"] for r in RCACHE[key]]
    resp = rerank_client.rerank(
        queries=[{"type": "TEXT", "textQuery": {"text": question}}],
        sources=[{"type": "INLINE", "inlineDocumentSource": {"type": "TEXT", "textDocument": {"text": BY[c]["text"]}}} for c in ids],
        rerankingConfiguration={"type": "BEDROCK_RERANKING_MODEL", "bedrockRerankingConfiguration": {
            "modelConfiguration": {"modelArn": f"arn:aws:bedrock:{region}::foundation-model/{RERANK}"},
            "numberOfResults": top_n}})
    ranking = [{"chunk_id": ids[r["index"]], "score": r["relevanceScore"]} for r in resp["results"]]
    RCACHE[key] = ranking
    with open(RC, "a", encoding="utf-8") as f:
        f.write(json.dumps({"key": key, "ranking": ranking}) + "\n")
    return [r["chunk_id"] for r in ranking]

def rrf(rankings, k, rrf_k=60):
    fused = {}
    for ranking in rankings:
        for rank, cid in enumerate(ranking, 1):
            fused[cid] = fused.get(cid, 0.0) + 1 / (rrf_k + rank)
    return [c for c, _ in sorted(fused.items(), key=lambda kv: kv[1], reverse=True)[:k]]

def sc(ret, rel):
    rel = set(rel); ret = list(ret); hit = rel & set(ret)
    return (1.0 if hit else 0.0, len(hit)/len(rel), next((1/r for r, c in enumerate(ret, 1) if c in rel), 0.0))

def run(X, Q, label):
    dense5 = hyb5 = rr5 = 0.0; rec_h = rec_rr = 0.0; mrr = 0.0; cand = 0
    for i, r in enumerate(tqdm(usable, desc=label)):
        rel = r["evidence_chunk_ids"]
        dense = [CHUNKS[j]["chunk_id"] for j in np.argsort(-(X @ Q[i]))[:50]]
        sparse = [CHUNKS[j]["chunk_id"] for j in np.argsort(bm25.get_scores(tokenize(r["question"])))[::-1][:50]]
        cand += bool(set(dense) & set(rel))
        h5 = sc(dense[:5], rel); d5 = rrf([dense[:5], sparse[:5]], 5)
        hb = sc(d5, rel)
        top = rerank(r["question"], rrf([dense, sparse], 50))
        rr = sc(top, rel)
        dense5 += h5[0]; hyb5 += hb[0]; rr5 += rr[0]; rec_h += hb[1]; rec_rr += rr[1]; mrr += rr[2]
    n = len(usable)
    print(f"{label:<10} dense@5 {dense5/n:.3f} | hybrid@5 hit {hyb5/n:.3f} rec {rec_h/n:.3f} | "
          f"+rerank hit {rr5/n:.3f} rec {rec_rr/n:.3f} mrr {mrr/n:.3f} | candHit@50 {cand}/{n}")

run(XT, QT, "Titan")
run(XQ, QQ, "Qwen3-4B")
