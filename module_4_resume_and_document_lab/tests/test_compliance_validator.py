"""
Unit Tests for Government Portal Compliance Validator
Tests pre-flight verification against SSC, UPSC, and IBPS official technical limits.
"""
from module_4_resume_and_document_lab.govt_document_lab.compliance_validator import ComplianceValidator
from module_4_resume_and_document_lab.tests.test_photo_processor import create_sample_portrait_photo
from module_4_resume_and_document_lab.govt_document_lab.photo_processor import PhotoProcessor
from module_4_resume_and_document_lab.govt_document_lab.signature_resizer import SignatureResizer
from module_4_resume_and_document_lab.tests.test_signature_resizer import create_sample_signature_image


def test_processed_photo_passes_ssc_compliance():
    raw_photo = create_sample_portrait_photo()
    processed = PhotoProcessor.process_photo(raw_photo, min_kb=20.0, max_kb=50.0)

    val_res = ComplianceValidator.validate_file(
        file_bytes=processed["image_bytes"],
        portal_code="SSC",
        document_type="photo"
    )

    assert val_res["is_compliant"] is True
    assert len(val_res["issues"]) == 0
    assert 20.0 <= val_res["size_kb"] <= 50.0


def test_undersized_photo_fails_ssc_compliance():
    # Only 5 KB photo
    tiny_fake_bytes = b" " * (5 * 1024)

    val_res = ComplianceValidator.validate_file(
        file_bytes=tiny_fake_bytes,
        portal_code="SSC",
        document_type="photo"
    )

    assert val_res["is_compliant"] is False
    assert any("too small" in issue for issue in val_res["issues"])


def test_processed_signature_passes_ssc_compliance():
    raw_sig = create_sample_signature_image()
    processed = SignatureResizer.process_signature(raw_sig, min_kb=10.0, max_kb=20.0)

    val_res = ComplianceValidator.validate_file(
        file_bytes=processed["image_bytes"],
        portal_code="SSC",
        document_type="signature"
    )

    assert val_res["is_compliant"] is True
    assert len(val_res["issues"]) == 0
    assert 10.0 <= val_res["size_kb"] <= 20.0


def test_marksheet_pdf_validation():
    fake_pdf = b"%PDF-1.4\n" + b"A" * (120 * 1024)  # 120 KB valid PDF header

    val_res = ComplianceValidator.validate_file(
        file_bytes=fake_pdf,
        portal_code="SSC",
        document_type="marksheet"
    )

    assert val_res["is_compliant"] is True
    assert val_res["detected_format"] == "PDF"
