"""
Government Document Lab Schemas
Pydantic v2 models for document processing, photo/signature resizing, and compliance reports.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class DocumentProcessResponse(BaseModel):
    document_type: str
    size_kb: float
    width: int
    height: int
    format: str
    is_compliant: bool
    min_allowed_kb: float
    max_allowed_kb: float
    base64_data: Optional[str] = None
    message: str

    model_config = ConfigDict(from_attributes=True)


class ComplianceCheckResponse(BaseModel):
    portal: str
    board_name: Optional[str] = None
    document_type: str
    size_kb: float
    width_px: Optional[int] = None
    height_px: Optional[int] = None
    detected_format: Optional[str] = None
    is_compliant: bool
    issues: List[str]
    portal_rules: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)
