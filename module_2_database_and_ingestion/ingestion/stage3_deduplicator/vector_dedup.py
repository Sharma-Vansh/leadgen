"""
Stage 3 Deduplicator: Level 2 Semantic Vector Engine
Detects reworded job postings for the same employer using pgvector cosine similarity.
Gracefully degrades when the embedding model or vector extension is unavailable.
"""
from typing import Optional, Tuple, List
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from module_2_database_and_ingestion.config import settings

logger = logging.getLogger("VectorDeduplicator")

# Global model cache for sentence-transformers
_embedder = None
_model_failed = False


def get_embedder():
    """Lazily loads sentence-transformers model with graceful fallback."""
    global _embedder, _model_failed
    if _model_failed:
        return None

    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedder = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            logger.info(f"[VectorDedup] Loaded local embedding model: {settings.EMBEDDING_MODEL_NAME}")
        except Exception as e:
            logger.warning(f"[VectorDedup] SentenceTransformer unavailable ({e}). Semantic vector deduplication disabled.")
            _model_failed = True
            return None

    return _embedder


class VectorDeduplicator:
    """Computes embeddings and performs semantic cosine similarity checks."""

    @classmethod
    def generate_embedding(cls, text_content: str) -> Optional[List[float]]:
        """Generates 384-dimensional dense vector embedding or returns None if offline."""
        embedder = get_embedder()
        if embedder is None:
            return None

        try:
            vector = embedder.encode(text_content, normalize_embeddings=True)
            return vector.tolist()
        except Exception as e:
            logger.warning(f"[VectorDedup] Failed to encode text: {e}")
            return None

    @classmethod
    async def find_semantic_duplicate(
        cls,
        session: AsyncSession,
        company_id: Optional[str],
        embedding: Optional[List[float]],
        threshold: Optional[float] = None
    ) -> Tuple[bool, Optional[str], float]:
        """
        Queries database for jobs from the same company with cosine similarity above threshold.
        Returns: (is_duplicate: bool, matched_job_id: Optional[str], similarity_score: float)
        """
        if not company_id or not embedding:
            return False, None, 0.0

        cutoff = threshold or settings.SIMILARITY_THRESHOLD

        try:
            # Query candidate jobs from the same company with pgvector <=> cosine distance operator
            # cosine_similarity = 1 - cosine_distance
            query = text("""
                SELECT id, (1 - (embedding <=> :vec::vector)) AS similarity
                FROM jobs
                WHERE company_id = :comp_id
                  AND embedding IS NOT NULL
                  AND status != 'expired'
                ORDER BY embedding <=> :vec::vector
                LIMIT 1;
            """)

            result = await session.execute(
                query,
                {"comp_id": company_id, "vec": str(embedding)}
            )
            row = result.first()

            if row:
                job_id, similarity = row[0], float(row[1])
                if similarity >= cutoff:
                    logger.info(f"[VectorDedup] Semantic duplicate detected: Job {job_id} (similarity: {similarity:.4f} >= {cutoff})")
                    return True, str(job_id), similarity

        except Exception as e:
            # Table might not have pgvector enabled or dialect is SQLite
            logger.debug(f"[VectorDedup] Vector query skipped or unsupported ({e})")

        return False, None, 0.0
