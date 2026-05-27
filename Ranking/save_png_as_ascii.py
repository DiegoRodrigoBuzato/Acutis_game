from PIL import Image
import os

frames_dir = r"c:\Users\Mkt\Desktop\Ranking\static\retro_carlo\frames"

def save_ascii(filename):
    filepath = os.path.join(frames_dir, filename)
    img = Image.open(filepath)
    width, height = img.size
    rgba_img = img.convert("RGBA")
    
    # Amostrar a cada 2 pixels na largura e 4 na altura para melhor resolução
    output = []
    bg_color = rgba_img.getpixel((0, 0))
    for y in range(0, height, 4):
        row = ""
        for x in range(0, width, 2):
            r, g, b, a = rgba_img.getpixel((x, y))
            if a < 50:
                row += " "
            elif abs(r - bg_color[0]) < 20 and abs(g - bg_color[1]) < 20 and abs(b - bg_color[2]) < 20:
                row += "."
            else:
                row += "#"
        output.append(row)
    
    with open(f"ascii_{filename.replace('.png', '.txt')}", "w") as f:
        f.write("\n".join(output))
    print(f"Salvo ascii_{filename.replace('.png', '.txt')}")

save_ascii("idle_1.png")
save_ascii("walk_1.png")
save_ascii("run_1.png")
