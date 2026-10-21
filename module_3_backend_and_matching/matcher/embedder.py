"""
Semantic Vector Embedder & Similarity Engine
Produces 384-dimensional dense embeddings for student profiles and job descriptions.
Supports sentence-transformers (all-MiniLM-L6-v2) with a zero-dependency deterministic
feature hashing fallback for offline resilience.
"""
import hashlib
import logging
import math
from typing import List, Optional

logger = logging.getLogger("SemanticEmbedder")

# Attempt loading sentence_transformers
try:
    from sentence_transformers import SentenceTransformer
    _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    SENTENCE_TRANSFORMER_ACTIVE = True
    logger.info("[Embedder] SentenceTransformer (all-MiniLM-L6-v2) loaded successfully.")
except Exception:
    _MODEL = None
    SENTENCE_TRANSFORMER_ACTIVE = False
    logger.info("[Embedder] Using zero-dependency deterministic dense projection (384-dim).")


def generate_embedding(text: str, dim: int = 384) -> List[float]:
    """
    Generates a 384-dimensional unit-normalized embedding vector for input text.
    Uses sentence-transformers if available, otherwise deterministic hashing projection.
    """
    if not text or not text.strip():
        return [0.0] * dim

    clean_text = text.strip()

    if SENTENCE_TRANSFORMER_ACTIVE and _MODEL is not None:
        try:
            vec = _MODEL.encode(clean_text, normalize_embeddings=True)
            return vec.tolist()
        except Exception as e:
            logger.warning(f"[Embedder] SentenceTransformer inference failed: {e}. Falling back.")

    # Resilient Deterministic Feature Projection
    vector = [0.0] * dim
    words = clean_text.lower().split()
    for word in words:
        # Murmur/MD5 feature hash
        h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
        index = h % dim
        sign = 1.0 if ((h >> 8) & 1) else -1.0
        weight = 1.0 + (len(word) / 10.0)
        vector[index] += sign * weight

    # L2 Unit Normalization
    norm = math.sqrt(sum(v * v for v in vector))
    if norm > 1e-9:
        vector = [round(v / norm, 6) for v in vector]
    else:
        vector[0] = 1.0

    return vector


def cosine_similarity(vec1: Optional[List[float]], vec2: Optional[List[float]]) -> float:
    """
    Computes cosine similarity between two unit-normalized vectors.
    Returns float in range [0.0, 1.0].
    """
    if not vec1 or not vec2:
        return 0.0
    if len(vec1) != len(vec2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    # Clip numerical precision artifacts
    sim = max(0.0, min(1.0, dot_product))
    return round(sim, 4)
