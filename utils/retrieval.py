from __future__ import annotations
import re
from typing import List, Tuple

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()

def chunk_text(text: str, chunk_size: int = 700, overlap: int = 120) -> List[str]:
    text = re.sub(r"\s+", " ", text).strip()
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i+chunk_size])
        i += (chunk_size - overlap)
    return chunks

def score_chunk(query: str, chunk: str) -> int:
    q = normalize(query)
    c = normalize(chunk)
    tokens = [t for t in re.split(r"[^a-z0-9]+", q) if len(t) > 2]
    return sum(1 for t in tokens if t in c)

def retrieve_top_snippets(query: str, corpus_chunks: List[Tuple[str, str]], k: int = 5) -> List[Tuple[str, str, int]]:
    """
    corpus_chunks: list of (source_name, chunk_text)
    returns: (source_name, chunk_text, score)
    """
    scored = []
    for src, ch in corpus_chunks:
        s = score_chunk(query, ch)
        if s > 0:
            scored.append((src, ch, s))
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored[:k]
