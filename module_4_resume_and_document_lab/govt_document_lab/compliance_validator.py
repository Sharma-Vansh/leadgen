"""
Government Portal Compliance Validator
Verifies candidate documents (photographs, signatures, certificates) against
exact technical constraints published by official recruitment boards (SSC, UPSC, IBPS, RRB, PSCs).
"""
import io
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image

# Official Recruitment Board Specifications Registry
GOVT_PORTAL_RULES: Dict[str, Dict[str, Any]] = {
    "SSC": {
        "board_name": "Staff Selection Commission",
        "photo": {
            "format": ["JPEG", "JPG"],
            "min_kb": 20.0,
            "max_kb": 50.0,
            "width_cm": 3.5,
            "height_cm": 4.5,
            "notes": "Clear light or white background; no glasses or caps."
        },
        "signature": {
            "format": ["JPEG", "JPG"],
            "min_kb": 10.0,
            "max_kb": 20.0,
            "width_cm": 6.0,
            "height_cm": 2.0,
            "notes": "Black or dark blue ink on white paper; illegible miniature signatures rejected."
        },
        "marksheet": {
            "format": ["PDF"],
            "min_kb": 50.0,
            "max_kb": 300.0,
            "notes": "Official scanned marksheet or degree certificate."
        }
    },
    "UPSC": {
        "board_name": "Union Public Service Commission",
        "photo": {
            "format": ["JPEG", "JPG"],
            "min_kb": 20.0,
            "max_kb": 300.0,
            "min_width_px": 350,
            "min_height_px": 350,
            "notes": "Frontal face capture occupying 3/4th of area."
        },
        "signature": {
            "format": ["JPEG", "JPG"],
            "min_kb": 20.0,
            "max_kb": 300.0,
            "min_width_px": 350,
            "min_height_px": 350,
            "notes": "Signature box properly cropped without surrounding artifacts."
        }
    },
    "IBPS": {
        "board_name": "Institute of Banking Personnel Selection",
        "photo": {
            "format": ["JPEG", "JPG"],
            "min_kb": 20.0,
            "max_kb": 50.0,
            "width_px": 200,
            "height_px": 230,
            "notes": "Passport photo taken against light-coloured, preferably white background."
        },
        "signature": {
            "format": ["JPEG", "JPG"],
            "min_kb": 10.0,
            "max_kb": 20.0,
            "width_px": 140,
            "height_px": 60,
            "notes": "Signatures in capital letters are strictly NOT accepted."
        },
        "thumb_impression": {
            "format": ["JPEG", "JPG"],
            "min_kb": 20.0,
            "max_kb": 50.0,
            "width_px": 240,
            "height_px": 240,
            "notes": "Left thumb impression on white paper with black or blue ink."
        }
    },
    "RRB": {
        "board_name": "Railway Recruitment Boards",
        "photo": {
            "format": ["JPEG", "JPG"],
            "min_kb": 20.0,
            "max_kb": 50.0,
            "width_cm": 3.5,
            "height_cm": 4.5,
            "notes": "Recent color photograph on white background."
        },
        "signature": {
            "format": ["JPEG", "JPG"],
            "min_kb": 10.0,
            "max_kb": 20.0,
            "width_px": 140,
            "height_px": 60,
            "notes": "Running handwriting signature."
        }
    }
}


class ComplianceValidator:
    """Pre-flight validator checking documents against target portal constraints."""

    @classmethod
    def validate_file(
        cls,
        file_bytes: bytes,
        portal_code: str,
        document_type: str
    ) -> Dict[str, Any]:
        """
        Validates file size, format, and dimensions against portal rules.
        """
        portal_code = portal_code.upper()
        document_type = document_type.lower()

        ruleset = GOVT_PORTAL_RULES.get(portal_code, GOVT_PORTAL_RULES["SSC"])
        doc_rules = ruleset.get(document_type)

        if not doc_rules:
            # Fallback to standard SSC photo/signature rules
            doc_rules = GOVT_PORTAL_RULES["SSC"].get(document_type, GOVT_PORTAL_RULES["SSC"]["photo"])

        size_bytes = len(file_bytes)
        size_kb = round(size_bytes / 1024.0, 2)
        min_kb = doc_rules.get("min_kb", 10.0)
        max_kb = doc_rules.get("max_kb", 50.0)

        issues: List[str] = []

        # 1. Size Check
        if size_kb < min_kb:
            issues.append(f"File size too small: {size_kb} KB. Must be at least {min_kb} KB.")
        elif size_kb > max_kb:
            issues.append(f"File size exceeds limit: {size_kb} KB. Maximum allowed is {max_kb} KB.")

        # 2. Format & Image Dimensions Check
        width = None
        height = None
        detected_format = None

        if document_type in ("photo", "signature", "thumb_impression"):
            try:
                img = Image.open(io.BytesIO(file_bytes))
                detected_format = img.format
                width, height = img.size

                allowed_formats = [f.upper() for f in doc_rules.get("format", ["JPEG", "JPG"])]
                if detected_format and detected_format.upper() not in allowed_formats and not (detected_format.upper() == "JPEG" and "JPG" in allowed_formats):
                    issues.append(f"Invalid image format: '{detected_format}'. Allowed: {allowed_formats}.")

            except Exception as e:
                issues.append(f"Corrupted image payload: Unable to parse image file ({e}).")
        elif document_type == "marksheet":
            if not file_bytes.startswith(b"%PDF"):
                issues.append("Invalid marksheet document: File must be a valid PDF format.")
            detected_format = "PDF"

        is_compliant = len(issues) == 0

        return {
            "portal": portal_code,
            "board_name": ruleset.get("board_name"),
            "document_type": document_type,
            "size_kb": size_kb,
            "width_px": width,
            "height_px": height,
            "detected_format": detected_format,
            "is_compliant": is_compliant,
            "issues": issues,
            "portal_rules": doc_rules
        }
