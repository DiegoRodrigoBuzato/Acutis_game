from PIL import Image
import os

filepath = r"c:\Users\Mkt\Desktop\Ranking\static\retro_carlo\frames\run_1.png"
if os.path.exists(filepath):
    img = Image.open(filepath)
    width, height = img.size
    print(f"Dimensões reais de run_1.png: {width}x{height}")
    
    # Amostrar pixels para gerar um mapa de caracteres da imagem
    # Vamos converter a imagem para RGBA
    rgba_img = img.convert("RGBA")
    
    # Vamos achar o pixel superior esquerdo
    bg_color = rgba_img.getpixel((0, 0))
    print(f"Cor do pixel (0,0): {bg_color}")
    
    # Imprimir mapa
    for y in range(0, height, 6):
        row_str = ""
        for x in range(0, width, 3):
            r, g, b, a = rgba_img.getpixel((x, y))
            if a < 50:
                row_str += " "
            elif abs(r - bg_color[0]) < 25 and abs(g - bg_color[1]) < 25 and abs(b - bg_color[2]) < 25:
                row_str += "." # Fundo
            else:
                row_str += "#" # Personagem ou texto
        print(row_str)
else:
    print("Arquivo não encontrado")
