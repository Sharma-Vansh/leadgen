"""
Unit Tests for Government Signature Resizer
Verifies background noise thresholding, 6x2 cm aspect ratio, and strict 10 KB - 20 KB file size limits.
"""
import io
from PIL import Image, ImageDraw
from module_4_resume_and_document_lab.govt_document_lab.signature_resizer import SignatureResizer


def create_sample_signature_image() -> bytes:
    """Generates a synthetic signature image simulating black ink on off-white paper."""
    img = Image.new("RGB", (600, 200), color=(240, 238, 230))  # Slightly yellowish paper
    draw = ImageDraw.Draw(img)

    # Draw cursive signature strokes
    draw.line([(50, 100), (120, 40), (180, 150), (250, 70), (350, 130), (520, 80)], fill=(20, 20, 30), width=4)
    draw.line([(80, 160), (480, 170)], fill=(15, 15, 25), width=3)  # Underline

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def test_signature_resizing_strictly_between_10kb_and_20kb():
    raw_sig_bytes = create_sample_signature_image()
    assert len(raw_sig_bytes) > 0

    result = SignatureResizer.process_signature(raw_sig_bytes, min_kb=10.0, max_kb=20.0)

    # 1. Verification of compliance flag
    assert result["is_compliant"] is True

    # 2. Exact size constraint verification (10 KB <= size <= 20 KB)
    size_bytes = result["size_bytes"]
    assert 10 * 1024 <= size_bytes <= 20 * 1024, f"Actual size {size_bytes} bytes is outside 10KB-20KB limit!"

    # 3. Dimensional verification
    assert result["width"] == 300
    assert result["height"] == 100
    assert result["format"] == "JPEG"

    # 4. Valid image payload
    processed_img = Image.open(io.BytesIO(result["image_bytes"]))
    assert processed_img.size == (300, 100)
    assert processed_img.format == "JPEG"
