import re
from typing import Dict, List, Tuple, Set

def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    text = re.sub(r"\s+", " ", text).strip()
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i+chunk_size])
        i += (chunk_size - overlap)
    return chunks

def _tokens(s: str) -> List[str]:
    s = re.sub(r"[^a-z0-9 ]+", " ", s.lower())
    return [t for t in s.split() if len(t) > 2]

def build_inverted_index(chunks: List[str], max_unique_tokens_per_chunk: int = 250) -> Dict[str, Set[int]]:
    """
    token -> set(chunk_idx)
    Caps tokens per chunk to control memory usage on Streamlit Cloud.
    """
    index: Dict[str, Set[int]] = {}
    for i, ch in enumerate(chunks):
        toks = list(dict.fromkeys(_tokens(ch)))  # de-dupe, preserve order
        toks = toks[:max_unique_tokens_per_chunk]
        for tok in toks:
            index.setdefault(tok, set()).add(i)
    return index

def top_k(query: str, chunks: List[str], index: Dict[str, Set[int]], k: int = 4) -> List[Tuple[int, str]]:
    q_toks = _tokens(query)
    if not q_toks:
        return []

    candidate_ids: Set[int] = set()
    for t in q_toks:
        ids = index.get(t)
        if ids:
            candidate_ids |= ids

    if not candidate_ids:
        return []

    scored = []
    for i in candidate_ids:
        ch_low = chunks[i].lower()
        score = sum(1 for t in q_toks if t in ch_low)
        if score > 0:
            scored.append((score, chunks[i]))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:k]
