import os
import struct

frames_dir = r"c:\Users\Mkt\Desktop\Ranking\static\retro_carlo\frames"

def get_png_size(filepath):
    with open(filepath, 'rb') as f:
        data = f.read(24)
        if len(data) >= 24 and data[:8] == b'\x89PNG\r\n\x1a\n' and data[12:16] == b'IHDR':
            width, height = struct.unpack('>II', data[16:24])
            return width, height
    return None

if os.path.exists(frames_dir):
    print("Dimensões dos frames do Carlo:")
    for filename in sorted(os.listdir(frames_dir)):
        if filename.endswith(".png"):
            filepath = os.path.join(frames_dir, filename)
            size = get_png_size(filepath)
            print(f"  {filename}: {size[0]}x{size[1]}" if size else f"  {filename}: Erro ao ler")
else:
    print(f"Diretório não encontrado: {frames_dir}")
