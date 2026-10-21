"""
Schemas Package
Exports auth, profile, and job feed schemas.
"""
from module_3_backend_and_matching.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse
)
from module_3_backend_and_matching.schemas.profile import (
    StudentProfileUpdate,
    StudentProfileResponse,
    ProfileCompletenessResponse
)
from module_3_backend_and_matching.schemas.job_feed import (
    SkillGapReport,
    MatchedJobCard,
    MatchedFeedResponse
)

__all__ = [
    "UserRegisterRequest",
    "UserLoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "UserResponse",
    "StudentProfileUpdate",
    "StudentProfileResponse",
    "ProfileCompletenessResponse",
    "SkillGapReport",
    "MatchedJobCard",
    "MatchedFeedResponse"
]
