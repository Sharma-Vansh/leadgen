"""
Unit Tests for Stage 3: Two-Tier Deduplicator
Tests HashDeduplicator and VectorDeduplicator fallback.
"""
import pytest
from module_2_database_and_ingestion.ingestion.stage3_deduplicator import (
    HashDeduplicator,
    VectorDeduplicator
)


def test_deterministic_sha256_hash():
    h1 = HashDeduplicator.compute_hash(
        company="Swiggy",
        title="Senior Python Engineer",
        city="Bangalore"
    )
    h2 = HashDeduplicator.compute_hash(
        company="  SWIGGY  ",
        title="senior python engineer ",
        city="bangalore"
    )
    assert len(h1) == 64  # SHA-256 produces 64 hex characters
    assert h1 == h2, "Whitespace and case variations must generate identical hash"


def test_distinct_jobs_produce_distinct_hashes():
    h1 = HashDeduplicator.compute_hash(
        company="Swiggy",
        title="Backend Engineer",
        city="Bangalore"
    )
    h2 = HashDeduplicator.compute_hash(
        company="Zomato",
        title="Backend Engineer",
        city="Bangalore"
    )
    assert h1 != h2, "Different companies must generate different hashes"


def test_vector_deduplicator_graceful_degradation():
    # Calling generate_embedding should return either a 384-element float list or None without throwing an unhandled exception
    vec = VectorDeduplicator.generate_embedding("Senior Software Engineer React TypeScript")
    if vec is not None:
        assert isinstance(vec, list)
        assert len(vec) == 384
    else:
        assert vec is None  # Offline mode without model
