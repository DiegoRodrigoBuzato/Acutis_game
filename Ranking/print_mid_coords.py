from PIL import Image
import os

filepath = r"c:\Users\Mkt\Desktop\Ranking\static\retro_carlo\frames\run_1.png"
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

print("Pixels do personagem em colunas do meio-esquerdo (10, 15, 20):")
for x in [10, 15, 20]:
    for y in range(20, height):
        pixel = rgba_img.getpixel((x, y))
        if pixel[3] >= 50 and (abs(pixel[0] - bg_color[0]) > 25 or abs(pixel[1] - bg_color[1]) > 25 or abs(pixel[2] - bg_color[2]) > 25):
            print(f"  Pixel at ({x}, {y}): Color={pixel}")
            break # Apenas o primeiro para não encher a tela
