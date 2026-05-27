from PIL import Image
import os

frames_dir = r"c:\Users\Mkt\Desktop\Ranking\static\retro_carlo\frames"

def process_frame(filename):
    filepath = os.path.join(frames_dir, filename)
    img = Image.open(filepath)
    width, height = img.size
    rgba_img = img.convert("RGBA")
    
    color_counts = {}
    for y in range(height):
        for x in range(width):
            pixel = rgba_img.getpixel((x, y))
            if pixel[3] > 50:
                color_key = pixel[:3]
                color_counts[color_key] = color_counts.get(color_key, 0) + 1
    
    bg_color = max(color_counts, key=color_counts.get)
    
    # 1. Definir a linha separadora para cortar o texto do topo (y entre 20 e 60)
    y_separator = 40
    for y in range(20, 60):
        is_empty = True
        for x in range(width):
            pixel = rgba_img.getpixel((x, y))
            # Usando tolerância de 42
            if pixel[3] >= 50 and (abs(pixel[0] - bg_color[0]) > 42 or abs(pixel[1] - bg_color[1]) > 42 or abs(pixel[2] - bg_color[2]) > 42):
                is_empty = False
                break
        if is_empty:
            y_separator = y
            break
            
    # 2. Encontrar o melhor deslocamento horizontal para juntar o personagem e minimizar a largura
    best_s = 0
    min_bbox_width = width
    best_x_min = 0
    best_x_max = width
    
    for s in range(width):
        x_min, x_max = width, 0
        has_pixels = False
        for y in range(y_separator, height):
            for x in range(width):
                pixel = rgba_img.getpixel((x, y))
                if pixel[3] >= 50 and (abs(pixel[0] - bg_color[0]) > 42 or abs(pixel[1] - bg_color[1]) > 42 or abs(pixel[2] - bg_color[2]) > 42):
                    new_x = (x + s) % width
                    if new_x < x_min: x_min = new_x
                    if new_x > x_max: x_max = new_x
                    has_pixels = True
        if has_pixels:
            bbox_width = x_max - x_min
            if bbox_width < min_bbox_width:
                min_bbox_width = bbox_width
                best_s = s
                best_x_min = x_min
                best_x_max = x_max
                
    # 3. Criar imagem deslocada e sem fundo
    shifted_img = Image.new("RGBA", (width, height))
    for y in range(height):
        for x in range(width):
            src_x = (x + best_s) % width
            pixel = rgba_img.getpixel((src_x, y))
            if pixel[3] < 50 or (abs(pixel[0] - bg_color[0]) <= 42 and abs(pixel[1] - bg_color[1]) <= 42 and abs(pixel[2] - bg_color[2]) <= 42):
                shifted_img.putpixel((x, y), (0, 0, 0, 0))
            else:
                shifted_img.putpixel((x, y), pixel)
                
    char_width = best_x_max - best_x_min + 1
    char_height = height - y_separator
    
    print(f"{filename} processado (tolerância 42):")
    print(f"  Linha divisória Y: {y_separator}")
    print(f"  Shift X: {best_s}")
    print(f"  Tamanho do personagem: {char_width}x{char_height}")
    print(f"  Limites X: [{best_x_min}..{best_x_max}]")

process_frame("run_1.png")
process_frame("walk_1.png")
process_frame("idle_1.png")
