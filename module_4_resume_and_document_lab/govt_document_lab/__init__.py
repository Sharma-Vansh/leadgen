"""
Government Document Lab Package
Exports signature resizer, photo processor, and portal compliance validator.
"""
from module_4_resume_and_document_lab.govt_document_lab.signature_resizer import SignatureResizer
from module_4_resume_and_document_lab.govt_document_lab.photo_processor import PhotoProcessor
from module_4_resume_and_document_lab.govt_document_lab.compliance_validator import (
    ComplianceValidator,
    GOVT_PORTAL_RULES
)

__all__ = [
    "SignatureResizer",
    "PhotoProcessor",
    "ComplianceValidator",
    "GOVT_PORTAL_RULES"
]
