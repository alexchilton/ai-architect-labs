"""Tiny shared harness for the AI Architect tutorial notebooks.

Local only: nothing leaves http://127.0.0.1:11434 (Ollama). No key, no cloud.
The retrieval primitives (a small analyzer + BM25 + reciprocal-rank fusion) are
stdlib so a reader sees exactly what each does. This is a teaching harness, not a
production index — the docstrings say where it is deliberately simpler than Lucene.
"""
from __future__ import annotations
import json, math, re, urllib.request
from collections import Counter

OLLAMA = "http://127.0.0.1:11434"
EMBED_MODEL = "bge-m3"
CHAT_MODEL = "qwen2.5:7b"


def _post(path: str, payload: dict, timeout: float = 120) -> dict:
    req = urllib.request.Request(OLLAMA + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def embed(text: str, model: str = EMBED_MODEL) -> list[float]:
    # Ollama's /api/embeddings (prompt=) still works; /api/embed (input=) is the newer path.
    return _post("/api/embeddings", {"model": model, "prompt": text})["embedding"]


def cosine(a: list[float], b: list[float]) -> float:
    # Raise on length mismatch rather than silently truncating — a mixed-embedder bug
    # (the exact thing the architecture skill warns about) must fail loudly here.
    if len(a) != len(b):
        raise ValueError(f"vector length mismatch {len(a)} vs {len(b)} — same embedder on both sides?")
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0


def chat(prompt: str, system: str = "", model: str = CHAT_MODEL,
         temperature: float = 0.0, num_predict: int = 400, num_ctx: int | None = None) -> str:
    # num_ctx MUST be set for long-context work: Ollama's default window (often 2k-4k) silently
    # truncates a long prompt, which would turn a context experiment into a truncation artifact.
    opts = {"temperature": temperature, "num_predict": num_predict}
    if num_ctx is not None:
        opts["num_ctx"] = num_ctx
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": prompt}]
    r = _post("/api/chat", {"model": model, "messages": msgs, "stream": False, "options": opts})
    return r.get("message", {}).get("content", "")


# --- a small analyzer, so BM25 behaves like a real lexical index, not a strawman ----

# A real engine (Lucene/Elastic/Qdrant) runs an analyzer: lowercase, drop stopwords,
# and stem. Without one, "to" matches everything and "expenses" != "expense" — which
# makes a toy BM25 look worse than it is. This is a light analyzer (stopwords + plural
# stripping); a production system uses a full stemmer (Porter/Snowflake).
STOPWORDS = {
    "a","an","the","of","to","for","in","on","at","by","and","or","is","are","be","was",
    "were","with","as","it","its","this","that","these","those","from","per","i","you",
    "can","my","me","do","how","what","which","up","within",
}
_TOK = re.compile(r"[a-z0-9]+")
def _stem(w: str) -> str:
    return w[:-1] if len(w) > 3 and w.endswith("s") else w   # crude plural strip only
def tokenize(text: str) -> list[str]:
    return [_stem(w) for w in _TOK.findall(text.lower()) if w not in STOPWORDS]


class BM25:
    """Minimal BM25 over an in-memory corpus, with the light analyzer above. Catches
    exact terms (IDs, codes) that dense vectors can miss. NOTE: repeated query terms
    double-count (as in `rank_bm25`); fine for a teaching corpus."""
    def __init__(self, docs: list[str], k1: float = 1.5, b: float = 0.75):
        self.docs = docs
        self.tok = [tokenize(d) for d in docs]
        self.len = [len(t) for t in self.tok]
        self.avg = sum(self.len) / len(self.len) if self.len else 0.0
        self.df: Counter = Counter()
        for t in self.tok:
            for w in set(t):
                self.df[w] += 1
        self.N = len(docs)
        self.k1, self.b = k1, b

    def _idf(self, term: str) -> float:
        n = self.df.get(term, 0)
        return math.log(1 + (self.N - n + 0.5) / (n + 0.5))

    def scores(self, query: str) -> list[float]:
        q = tokenize(query)
        out = []
        for i, toks in enumerate(self.tok):
            tf = Counter(toks)
            s = 0.0
            for term in q:
                if term not in tf:
                    continue
                idf = self._idf(term)
                num = tf[term] * (self.k1 + 1)
                den = tf[term] + self.k1 * (1 - self.b + self.b * self.len[i] / (self.avg or 1))
                s += idf * num / den
            out.append(s)
        return out

    def ranking(self, query: str) -> list[int]:
        """Doc ids that actually matched a query term (score > 0), best first.
        Excludes zero-score docs so RRF never credits a doc that matched nothing."""
        sc = self.scores(query)
        return [i for i in order(sc) if sc[i] > 0]


def rrf(*rankings: list[int], k: int = 60) -> list[int]:
    """Reciprocal-rank fusion: combine several ranked id-lists (best-first) into one.
    Lists may be partial — a doc absent from a list simply gets no contribution from it."""
    score: dict[int, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            score[doc_id] = score.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return [d for d, _ in sorted(score.items(), key=lambda kv: kv[1], reverse=True)]


def order(scores: list[float]) -> list[int]:
    """Doc ids sorted by score, best first (stable: ties keep index order)."""
    return [i for i, _ in sorted(enumerate(scores), key=lambda kv: kv[1], reverse=True)]
