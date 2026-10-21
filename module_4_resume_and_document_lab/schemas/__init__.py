"""
Schemas Package for Module 4
"""
from module_4_resume_and_document_lab.schemas.resume import (
    TailorResumeRequest,
    TailoredResumeResponse,
    ATSScoreReport
)
from module_4_resume_and_document_lab.schemas.documents import (
    DocumentProcessResponse,
    ComplianceCheckResponse
)

__all__ = [
    "TailorResumeRequest",
    "TailoredResumeResponse",
    "ATSScoreReport",
    "DocumentProcessResponse",
    "ComplianceCheckResponse"
]
