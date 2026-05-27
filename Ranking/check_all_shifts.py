from PIL import Image
import os

frames_dir = r"c:\Users\Mkt\Desktop\Ranking\static\retro_carlo\frames"

for filename in sorted(os.listdir(frames_dir)):
    if filename.endswith(".png"):
        filepath = os.path.join(frames_dir, filename)
        img = Image.open(filepath)
        width, height = img.size
        rgba_img = img.convert("RGBA")
        
        # Encontrar os limites x_min, x_max, y_min, y_max dos pixels do personagem
        # (ignorando a cor de fundo, que é getpixel((0,0)))
        bg_color = rgba_img.getpixel((0, 0))
        
        x_min, x_max = width, 0
        y_min, y_max = height, 0
        
        for y in range(height):
            for x in range(width):
                r, g, b, a = rgba_img.getpixel((x, y))
                if a >= 50:
                    # Se não for a cor de fundo
                    if abs(r - bg_color[0]) > 20 or abs(g - bg_color[1]) > 20 or abs(b - bg_color[2]) > 20:
                        if x < x_min: x_min = x
                        if x > x_max: x_max = x
                        if y < y_min: y_min = y
                        if y > y_max: y_max = y
                        
        print(f"{filename}: size={width}x{height}, character bounds: X=[{x_min}..{x_max}], Y=[{y_min}..{y_max}]")
