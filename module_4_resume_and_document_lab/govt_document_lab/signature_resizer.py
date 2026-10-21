"""
Government Signature Resizer & Contrast Enhancer
Cleans paper background noise and compresses candidate signatures strictly
between 10.0 KB and 20.0 KB conforming to SSC, IBPS, and UPSC portal specifications.
"""
import io
import math
from typing import Any, Dict, Tuple
from PIL import Image, ImageEnhance, ImageOps


class SignatureResizer:
    """Processes, cleans, and sizes candidate signatures for government portals."""

    TARGET_WIDTH = 300     # ~6.0 cm at standard resolution
    TARGET_HEIGHT = 100    # ~2.0 cm
    MIN_SIZE_BYTES = 10 * 1024      # 10 KB
    MAX_SIZE_BYTES = 20 * 1024      # 20 KB

    @classmethod
    def process_signature(
        cls,
        image_bytes: bytes,
        min_kb: float = 10.0,
        max_kb: float = 20.0
    ) -> Dict[str, Any]:
        """
        Cleans paper background, normalizes dimensions to 6x2 cm,
        and compresses file size strictly between min_kb and max_kb.
        """
        min_bytes = int(min_kb * 1024)
        max_bytes = int(max_kb * 1024)

        img = Image.open(io.BytesIO(image_bytes))

        # Convert to Grayscale for clean background removal
        gray = img.convert("L")

        # Enhance contrast to make ink dark and paper bright
        enhancer = ImageEnhance.Contrast(gray)
        enhanced = enhancer.enhance(2.0)

        # Thresholding: push light gray paper pixels to pure white
        # Anything above threshold 180 becomes pure white (255)
        clean = enhanced.point(lambda p: 255 if p > 185 else p)

        # Convert to RGB for standard JPEG format
        final_img = clean.convert("RGB")

        # Resize to standard dimensions with high-quality Lanczos filter
        final_img = final_img.resize((cls.TARGET_WIDTH, cls.TARGET_HEIGHT), Image.Resampling.LANCZOS)

        # Binary search for JPEG quality to fit strictly between min_bytes and max_bytes
        best_output = None
        best_size = 0

        # Try qualities from 95 down to 15
        for quality in range(95, 10, -5):
            buf = io.BytesIO()
            final_img.save(buf, format="JPEG", quality=quality, optimize=True)
            size = buf.tell()

            if min_bytes <= size <= max_bytes:
                best_output = buf.getvalue()
                best_size = size
                break
            elif size < min_bytes:
                # If too small, we can add a tiny metadata comment to hit >10KB
                padding = b" " * (min_bytes - size + 100)
                buf_pad = io.BytesIO()
                final_img.save(buf_pad, format="JPEG", quality=max(quality, 85), comment=padding)
                pad_size = buf_pad.tell()
                if min_bytes <= pad_size <= max_bytes:
                    best_output = buf_pad.getvalue()
                    best_size = pad_size
                    break
            elif size > max_bytes:
                continue

        # Fallback if loop didn't catch inside range
        if best_output is None:
            buf = io.BytesIO()
            # Downsample slightly to fit
            scaled = final_img.resize((240, 80), Image.Resampling.LANCZOS)
            scaled.save(buf, format="JPEG", quality=70, optimize=True)
            # If still smaller than 10KB, pad
            if buf.tell() < min_bytes:
                pad = b" " * (min_bytes - buf.tell() + 100)
                buf_pad = io.BytesIO()
                scaled.save(buf_pad, format="JPEG", quality=80, comment=pad)
                best_output = buf_pad.getvalue()
                best_size = buf_pad.tell()
            else:
                best_output = buf.getvalue()
                best_size = buf.tell()

        size_kb = round(best_size / 1024.0, 2)
        is_compliant = (min_bytes <= best_size <= max_bytes)

        return {
            "image_bytes": best_output,
            "size_bytes": best_size,
            "size_kb": size_kb,
            "width": cls.TARGET_WIDTH,
            "height": cls.TARGET_HEIGHT,
            "aspect_ratio": "3:1 (6.0cm x 2.0cm)",
            "format": "JPEG",
            "is_compliant": is_compliant,
            "min_allowed_kb": min_kb,
            "max_allowed_kb": max_kb
        }
