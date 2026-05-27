from PIL import Image
import os

frames_dir = r"c:\Users\Mkt\Desktop\Ranking\static\retro_carlo\frames"

def analyze_file(filename):
    filepath = os.path.join(frames_dir, filename)
    img = Image.open(filepath)
    width, height = img.size
    rgba_img = img.convert("RGBA")
    bg_color = rgba_img.getpixel((0, 0))
    
    print(f"\n=== {filename} ({width}x{height}) ===")
    
    # Vamos gerar uma versão compacta (15x15) do mapa de pixels
    for y in range(0, height, height // 15):
        row_str = ""
        for x in range(0, width, width // 20):
            r, g, b, a = rgba_img.getpixel((x, y))
            if a < 50:
                row_str += " "
            elif abs(r - bg_color[0]) < 20 and abs(g - bg_color[1]) < 20 and abs(b - bg_color[2]) < 20:
                row_str += "."
            else:
                row_str += "#"
        print(row_str)

analyze_file("idle_1.png")
analyze_file("walk_1.png")
analyze_file("jump_1.png")
