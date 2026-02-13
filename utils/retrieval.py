import re
from typing import List, Tuple


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    """
    Splits long text into overlapping chunks for simple retrieval.
    """
    text = re.sub(r"\s+", " ", text).strip()
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i : i + chunk_size])
        i += (chunk_size - overlap)
    return chunks


def _normalize(q: str) -> List[str]:
    q = re.sub(r"[^a-z0-9 ]+", " ", q.lower())
    tokens = [t for t in q.split() if len(t) > 2]
    return tokens


def _score(query: str, chunk: str) -> int:
    tokens = _normalize(query)
    c = chunk.lower()
    return sum(1 for t in tokens if t in c)


def top_k(query: str, chunks: List[str], k: int = 4) -> List[Tuple[int, str]]:
    """
    Returns top-k chunks as (score, chunk_text).
    """
    scored = []
    for ch in chunks:
        s = _score(query, ch)
        if s > 0:
            scored.append((s, ch))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:k]
