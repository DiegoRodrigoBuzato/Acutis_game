from PIL import Image
import os

filepath = r"c:\Users\Mkt\Desktop\Ranking\static\retro_carlo\frames\run_1.png"
img = Image.open(filepath)
width, height = img.size
rgba_img = img.convert("RGBA")

# Contar todas as cores únicas na imagem
color_counts = {}
for y in range(height):
    for x in range(width):
        pixel = rgba_img.getpixel((x, y))
        color_counts[pixel] = color_counts.get(pixel, 0) + 1

# Imprimir as 15 cores mais comuns
sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
print("As 15 cores mais comuns na imagem:")
for color, count in sorted_colors[:15]:
    print(f"  Color: {color}, Count: {count} ({count/(width*height)*100:.2f}%)")
