from PIL import Image, ImageDraw
import os

def create_icon(size, filename):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Outer rounded square with border
    margin = max(1, size // 16)
    corner = max(2, size // 4)
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin], 
        radius=corner, 
        fill=(11, 17, 32, 255), 
        outline=(56, 189, 248, 255), 
        width=max(1, size // 16)
    )
    
    # Inner glowing circular core
    mid = size // 2
    r = size // 3
    draw.ellipse([mid - r, mid - r, mid + r, mid + r], fill=(56, 189, 248, 230))
    
    # Inner contrast symbol
    h_w = max(1, r // 2)
    h_h = max(1, r // 3)
    draw.rectangle([mid - h_w, mid - h_h, mid + h_w, mid + h_h], fill=(11, 17, 32, 255))
    
    out_dir = os.path.join(os.path.dirname(__file__), 'icons')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename)
    img.save(out_path, format='PNG')
    print(f"Generated {out_path} ({size}x{size})")

if __name__ == '__main__':
    create_icon(16, 'icon16.png')
    create_icon(48, 'icon48.png')
    create_icon(128, 'icon128.png')
