"""
Government Passport Photo Processor
Crops, aligns, and compresses candidate photos to 3.5cm x 4.5cm and strictly
between 20.0 KB and 50.0 KB adhering to SSC, IBPS, and UPSC portal constraints.
"""
import io
from typing import Any, Dict, Tuple
from PIL import Image, ImageOps


class PhotoProcessor:
    """Processes candidate passport photographs for government recruitment portals."""

    TARGET_WIDTH = 350     # 3.5 cm
    TARGET_HEIGHT = 450    # 4.5 cm
    MIN_SIZE_BYTES = 20 * 1024      # 20 KB
    MAX_SIZE_BYTES = 50 * 1024      # 50 KB

    @classmethod
    def process_photo(
        cls,
        image_bytes: bytes,
        min_kb: float = 20.0,
        max_kb: float = 50.0
    ) -> Dict[str, Any]:
        """
        Crops to 7:9 ratio, centers, and compresses strictly between min_kb and max_kb.
        """
        min_bytes = int(min_kb * 1024)
        max_bytes = int(max_kb * 1024)

        img = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB (in case of RGBA, palette, or CMYK)
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Auto-orient if EXIF orientation tag exists
        img = ImageOps.exif_transpose(img) or img

        # Center-crop to 7:9 aspect ratio (3.5cm : 4.5cm)
        target_ratio = cls.TARGET_WIDTH / cls.TARGET_HEIGHT
        img_width, img_height = img.size
        current_ratio = img_width / img_height

        if current_ratio > target_ratio:
            # Image is wider than 7:9 -> crop sides
            new_width = int(img_height * target_ratio)
            left = (img_width - new_width) // 2
            box = (left, 0, left + new_width, img_height)
            cropped = img.crop(box)
        else:
            # Image is taller than 7:9 -> crop top/bottom with slight bias towards top (face)
            new_height = int(img_width / target_ratio)
            top = max(0, int((img_height - new_height) * 0.35))
            box = (0, top, img_width, top + new_height)
            cropped = img.crop(box)

        # Resize to standard dimensions
        final_img = cropped.resize((cls.TARGET_WIDTH, cls.TARGET_HEIGHT), Image.Resampling.LANCZOS)

        # Quality tuning to fit strictly between min_bytes and max_bytes
        best_output = None
        best_size = 0

        for quality in range(95, 20, -5):
            buf = io.BytesIO()
            final_img.save(buf, format="JPEG", quality=quality, optimize=True)
            size = buf.tell()

            if min_bytes <= size <= max_bytes:
                best_output = buf.getvalue()
                best_size = size
                break
            elif size < min_bytes:
                # Add safe JPEG padding comment if compression resulted in < 20KB
                padding = b" " * (min_bytes - size + 200)
                buf_pad = io.BytesIO()
                final_img.save(buf_pad, format="JPEG", quality=max(quality, 85), comment=padding)
                pad_size = buf_pad.tell()
                if min_bytes <= pad_size <= max_bytes:
                    best_output = buf_pad.getvalue()
                    best_size = pad_size
                    break
            elif size > max_bytes:
                continue

        if best_output is None:
            buf = io.BytesIO()
            final_img.save(buf, format="JPEG", quality=60, optimize=True)
            if buf.tell() < min_bytes:
                pad = b" " * (min_bytes - buf.tell() + 200)
                buf_pad = io.BytesIO()
                final_img.save(buf_pad, format="JPEG", quality=75, comment=pad)
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
            "aspect_ratio": "7:9 (3.5cm x 4.5cm)",
            "format": "JPEG",
            "is_compliant": is_compliant,
            "min_allowed_kb": min_kb,
            "max_allowed_kb": max_kb
        }
