from PIL import Image
import os

filepath = r"c:\Users\Mkt\Desktop\Ranking\static\retro_carlo\frames\run_1.png"
img = Image.open(filepath)
width, height = img.size
rgba_img = img.convert("RGBA")

# Contar pixels não-fundo por coluna para y >= 20
color_counts = {}
for y in range(height):
    for x in range(width):
        pixel = rgba_img.getpixel((x, y))
        if pixel[3] > 50:
            color_key = pixel[:3]
            color_counts[color_key] = color_counts.get(color_key, 0) + 1

bg_color = max(color_counts, key=color_counts.get)
print(f"Fundo detectado: {bg_color}")

print("Contagem de pixels do personagem por coluna (x de 0 a 89):")
columns = []
for x in range(width):
    count = 0
    for y in range(20, height):
        pixel = rgba_img.getpixel((x, y))
        if pixel[3] >= 50 and (abs(pixel[0] - bg_color[0]) > 20 or abs(pixel[1] - bg_color[1]) > 20 or abs(pixel[2] - bg_color[2]) > 20):
            count += 1
    columns.append((x, count))

# Imprimir colunas com pixels do personagem
for x, count in columns:
    if count > 0:
        print(f"  Col {x}: {count} pixels")
