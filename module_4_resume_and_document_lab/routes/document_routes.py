"""
Government Document Lab API Routes
Endpoints for signature cleaning & compression (10-20 KB), passport photo resizing (20-50 KB),
and official recruitment portal compliance verification.
"""
import base64
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from module_4_resume_and_document_lab.govt_document_lab.signature_resizer import SignatureResizer
from module_4_resume_and_document_lab.govt_document_lab.photo_processor import PhotoProcessor
from module_4_resume_and_document_lab.govt_document_lab.compliance_validator import ComplianceValidator
from module_4_resume_and_document_lab.schemas.documents import (
    DocumentProcessResponse,
    ComplianceCheckResponse
)

router = APIRouter(prefix="/documents", tags=["Government Document Lab"])


@router.post("/process-signature", response_model=DocumentProcessResponse)
async def process_signature(
    file: UploadFile = File(...),
    min_kb: float = Form(10.0),
    max_kb: float = Form(20.0)
):
    """
    Cleans background paper noise, thresholds contrast, normalizes dimensions to 6x2 cm,
    and compresses file size strictly between 10 KB and 20 KB for SSC/UPSC submissions.
    """
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file uploaded")

    try:
        res = SignatureResizer.process_signature(contents, min_kb=min_kb, max_kb=max_kb)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Image processing error: {e}")

    b64 = base64.b64encode(res["image_bytes"]).decode("utf-8")
    status_msg = "Successfully processed and verified within 10KB-20KB limit." if res["is_compliant"] else "Processed with warning: check portal range."

    return DocumentProcessResponse(
        document_type="signature",
        size_kb=res["size_kb"],
        width=res["width"],
        height=res["height"],
        format=res["format"],
        is_compliant=res["is_compliant"],
        min_allowed_kb=res["min_allowed_kb"],
        max_allowed_kb=res["max_allowed_kb"],
        base64_data=f"data:image/jpeg;base64,{b64}",
        message=status_msg
    )


@router.post("/process-photo", response_model=DocumentProcessResponse)
async def process_photo(
    file: UploadFile = File(...),
    min_kb: float = Form(20.0),
    max_kb: float = Form(50.0)
):
    """
    Auto-centers, crops to 3.5cm x 4.5cm, and compresses candidate photos strictly
    between 20 KB and 50 KB for official recruitment forms.
    """
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file uploaded")

    try:
        res = PhotoProcessor.process_photo(contents, min_kb=min_kb, max_kb=max_kb)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Photo processing error: {e}")

    b64 = base64.b64encode(res["image_bytes"]).decode("utf-8")
    status_msg = "Successfully processed and verified within 20KB-50KB limit." if res["is_compliant"] else "Processed with warning."

    return DocumentProcessResponse(
        document_type="photo",
        size_kb=res["size_kb"],
        width=res["width"],
        height=res["height"],
        format=res["format"],
        is_compliant=res["is_compliant"],
        min_allowed_kb=res["min_allowed_kb"],
        max_allowed_kb=res["max_allowed_kb"],
        base64_data=f"data:image/jpeg;base64,{b64}",
        message=status_msg
    )


@router.post("/verify-compliance", response_model=ComplianceCheckResponse)
async def verify_document_compliance(
    file: UploadFile = File(...),
    portal_code: str = Form("SSC", description="SSC, UPSC, IBPS, RRB"),
    document_type: str = Form("photo", description="photo, signature, marksheet")
):
    """
    Pre-flight audit tool validating documents against target recruitment board constraints.
    """
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file uploaded")

    res = ComplianceValidator.validate_file(
        file_bytes=contents,
        portal_code=portal_code,
        document_type=document_type
    )

    return ComplianceCheckResponse(
        portal=res["portal"],
        board_name=res["board_name"],
        document_type=res["document_type"],
        size_kb=res["size_kb"],
        width_px=res["width_px"],
        height_px=res["height_px"],
        detected_format=res["detected_format"],
        is_compliant=res["is_compliant"],
        issues=res["issues"],
        portal_rules=res["portal_rules"]
    )
