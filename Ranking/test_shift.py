from PIL import Image
import os

filepath = r"c:\Users\Mkt\Desktop\Ranking\static\retro_carlo\frames\run_1.png"
if os.path.exists(filepath):
    img = Image.open(filepath)
    width, height = img.size
    rgba_img = img.convert("RGBA")
    
    # Criar uma nova imagem deslocada
    shifted_img = Image.new("RGBA", (width, height))
    shift_amount = 45 # Metade de 90
    
    for y in range(height):
        for x in range(width):
            # Deslocamento com wrap-around (circular)
            src_x = (x + shift_amount) % width
            pixel = rgba_img.getpixel((src_x, y))
            shifted_img.putpixel((x, y), pixel)
            
    # Salvar a imagem temporária para análise ASCII
    bg_color = shifted_img.getpixel((0, 0))
    output = []
    for y in range(0, height, 4):
        row = ""
        for x in range(0, width, 2):
            r, g, b, a = shifted_img.getpixel((x, y))
            if a < 50:
                row += " "
            elif abs(r - bg_color[0]) < 20 and abs(g - bg_color[1]) < 20 and abs(b - bg_color[2]) < 20:
                row += "."
            else:
                row += "#"
        output.append(row)
        
    print("ASCII do run_1.png deslocado por 45 pixels:")
    print("\n".join(output))
else:
    print("Arquivo não encontrado")
