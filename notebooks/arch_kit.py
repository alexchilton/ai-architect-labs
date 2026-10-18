"""Tiny shared harness for the AI Architect tutorial notebooks.

Local only: nothing leaves http://127.0.0.1:11434 (Ollama). No key, no cloud.
Just the pieces the RAG/agent notebooks need — embeddings, a chat call, and the
classic retrieval primitives (BM25, reciprocal-rank fusion) — implemented in the
standard library so a reader can see exactly what each one does.
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
    return _post("/api/embeddings", {"model": model, "prompt": text})["embedding"]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0


def chat(prompt: str, system: str = "", model: str = CHAT_MODEL,
         temperature: float = 0.0, num_predict: int = 400) -> str:
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": prompt}]
    r = _post("/api/chat", {"model": model, "messages": msgs, "stream": False,
                            "options": {"temperature": temperature, "num_predict": num_predict}})
    return r.get("message", {}).get("content", "")


# --- classic lexical retrieval, so hybrid search is visible, not a black box ----

_TOK = re.compile(r"[a-z0-9]+")
def tokenize(text: str) -> list[str]:
    return _TOK.findall(text.lower())


class BM25:
    """Minimal BM25 over an in-memory corpus. Catches exact terms (IDs, codes)
    that dense vectors miss — the reason hybrid retrieval exists."""
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


def rrf(*rankings: list[int], k: int = 60) -> list[int]:
    """Reciprocal-rank fusion: combine several ranked id-lists into one.
    Each list is doc ids best-first. Returns fused ids best-first."""
    score: dict[int, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            score[doc_id] = score.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return [d for d, _ in sorted(score.items(), key=lambda kv: kv[1], reverse=True)]


def order(scores: list[float]) -> list[int]:
    """Doc ids sorted by score, best first."""
    return [i for i, _ in sorted(enumerate(scores), key=lambda kv: kv[1], reverse=True)]
