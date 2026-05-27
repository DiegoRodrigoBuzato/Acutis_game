from PIL import Image
import os

# Directories (adjust if needed)
FRAMES_DIR = r"c:\Users\Mkt\Desktop\Ranking\static\retro_carlo\frames"
OUTPUT_DIR = r"c:\Users\Mkt\Desktop\Ranking\static\retro_carlo\processed"
os.makedirs(OUTPUT_DIR, exist_ok=True)

FINAL_SIZE = 128  # canvas size
PADDING = 8      # added on each side before centering

def most_common_color(img: Image) -> tuple:
    """Return the most frequent RGB colour among opaque pixels.
    This works even when there is label text at the top because we count all
    non‑transparent pixels.
    """
    width, height = img.size
    color_counts = {}
    for y in range(height):
        for x in range(width):
            r, g, b, a = img.getpixel((x, y))
            if a < 50:
                continue
            key = (r, g, b)
            color_counts[key] = color_counts.get(key, 0) + 1
    # fallback to a dark colour if nothing found
    return max(color_counts, key=color_counts.get) if color_counts else (0, 0, 0)

def find_bbox(img: Image, bg_rgb: tuple) -> tuple:
    """Return (x_min, y_min, x_max, y_max) that encloses all non‑background pixels.
    Background is defined by colour similarity with a tolerance of 42 (the same
    threshold used previously).
    """
    width, height = img.size

    x_min, y_min = width, height
    x_max, y_max = -1, -1
    has_pixels = False
    for y in range(height):
        for x in range(width):
            r, g, b, a = img.getpixel((x, y))
            if a < 50:
                continue

            # Skip background pixels (within tolerance of most common color)
            if (abs(r - bg_rgb[0]) <= 42 and abs(g - bg_rgb[1]) <= 42 and abs(b - bg_rgb[2]) <= 42):
                continue
            has_pixels = True
            if x < x_min:
                x_min = x
            if x > x_max:
                x_max = x
            if y < y_min:
                y_min = y
            if y > y_max:
                y_max = y
    if not has_pixels:
        return None
    return x_min, y_min, x_max, y_max

def process_image(filepath: str, out_path: str):
    img = Image.open(filepath).convert("RGBA")
    bg_rgb = most_common_color(img)
    bbox = find_bbox(img, bg_rgb)
    if bbox is None:
        print(f"[WARN] No character detected in {os.path.basename(filepath)}")
        return
    x_min, y_min, x_max, y_max = bbox
    # Crop character
    cropped = img.crop((x_min, y_min, x_max + 1, y_max + 1))

    # Remove background pixels (make them transparent)
    cropped = cropped.copy()  # ensure writable
    pixels = cropped.load()
    cw, ch = cropped.size
    for py in range(ch):
        for px in range(cw):
            r, g, b, a = pixels[px, py]
            if a < 50:
                continue
            if (abs(r - bg_rgb[0]) <= 42 and abs(g - bg_rgb[1]) <= 42 and abs(b - bg_rgb[2]) <= 42):
                pixels[px, py] = (0, 0, 0, 0)

    char_w, char_h = cropped.size

    # Determine scaling factor so the larger side fits FINAL_SIZE - 2*PADDING
    max_allowed = FINAL_SIZE - 2 * PADDING
    scale = min(max_allowed / char_w, max_allowed / char_h)
    # Resize when scale differs from 1 (both up‑scaling and down‑scaling)
    if scale != 1.0:
        new_w = int(char_w * scale)
        new_h = int(char_h * scale)
        cropped = cropped.resize((new_w, new_h), Image.LANCZOS)
        char_w, char_h = new_w, new_h

    # Create final canvas with transparent background
    final_img = Image.new("RGBA", (FINAL_SIZE, FINAL_SIZE), (0, 0, 0, 0))
    # Position: centre horizontally, align bottom (character feet on canvas bottom)
    dest_x = (FINAL_SIZE - char_w) // 2
    dest_y = FINAL_SIZE - char_h
    final_img.paste(cropped, (dest_x, dest_y), cropped)
    final_img.save(out_path)
    print(f"Processed {os.path.basename(filepath)}: orig={char_w}x{char_h}, scale={scale:.3f}, pos=({dest_x},{dest_y})")

def process_all():
    for filename in sorted(os.listdir(FRAMES_DIR)):
        if not filename.lower().endswith('.png'):
            continue
        in_path = os.path.join(FRAMES_DIR, filename)
        out_path = os.path.join(OUTPUT_DIR, filename)
        process_image(in_path, out_path)

if __name__ == "__main__":
    process_all()
