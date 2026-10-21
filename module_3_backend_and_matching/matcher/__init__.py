"""
Matcher Package
Exports embedding generator, rule filter, skill gap analyzer, and match orchestrator.
"""
from module_3_backend_and_matching.matcher.embedder import (
    generate_embedding,
    cosine_similarity
)
from module_3_backend_and_matching.matcher.rule_filter import (
    RuleFilter,
    calculate_age
)
from module_3_backend_and_matching.matcher.skill_gap_analyzer import (
    SkillGapAnalyzer,
    normalize_skill
)
from module_3_backend_and_matching.matcher.semantic_scorer import (
    SemanticScorer
)
from module_3_backend_and_matching.matcher.match_orchestrator import (
    MatchOrchestrator
)

__all__ = [
    "generate_embedding",
    "cosine_similarity",
    "RuleFilter",
    "calculate_age",
    "SkillGapAnalyzer",
    "normalize_skill",
    "SemanticScorer",
    "MatchOrchestrator"
]
