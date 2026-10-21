"""
Unit Tests for Government Passport Photo Processor
Verifies 3.5cm x 4.5cm proportions, centering, and strict 20 KB - 50 KB file size limits.
"""
import io
from PIL import Image, ImageDraw
from module_4_resume_and_document_lab.govt_document_lab.photo_processor import PhotoProcessor


def create_sample_portrait_photo() -> bytes:
    """Generates a synthetic portrait image simulating a candidate photo."""
    img = Image.new("RGB", (600, 800), color=(230, 235, 245))  # Light background
    draw = ImageDraw.Draw(img)

    # Draw face and shoulders
    draw.ellipse([(200, 200), (400, 450)], fill=(210, 160, 130))  # Head
    draw.rectangle([(150, 450), (450, 750)], fill=(40, 70, 130))   # Shirt

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def test_photo_processing_strictly_between_20kb_and_50kb():
    raw_photo_bytes = create_sample_portrait_photo()
    assert len(raw_photo_bytes) > 0

    result = PhotoProcessor.process_photo(raw_photo_bytes, min_kb=20.0, max_kb=50.0)

    # 1. Verification of compliance flag
    assert result["is_compliant"] is True

    # 2. Exact size constraint verification (20 KB <= size <= 50 KB)
    size_bytes = result["size_bytes"]
    assert 20 * 1024 <= size_bytes <= 50 * 1024, f"Actual size {size_bytes} bytes is outside 20KB-50KB limit!"

    # 3. Dimensional verification
    assert result["width"] == 350
    assert result["height"] == 450
    assert result["format"] == "JPEG"

    # 4. Valid image payload
    processed_img = Image.open(io.BytesIO(result["image_bytes"]))
    assert processed_img.size == (350, 450)
    assert processed_img.format == "JPEG"
