import os
import struct
import zlib

def read_png_pixels(filepath):
    # Decodificador PNG super básico nativo em Python
    with open(filepath, 'rb') as f:
        signature = f.read(8)
        if signature != b'\x89PNG\r\n\x1a\n':
            return None
        
        chunks = []
        while True:
            length_data = f.read(4)
            if not length_data:
                break
            length = struct.unpack('>I', length_data)[0]
            chunk_type = f.read(4)
            chunk_data = f.read(length)
            crc = f.read(4)
            chunks.append((chunk_type, chunk_data))
            if chunk_type == b'IEND':
                break
                
        ihdr = [c for c in chunks if c[0] == b'IHDR'][0][1]
        width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack('>IIBBBBB', ihdr)
        
        idat_data = b''.join([c[1] for c in chunks if c[0] == b'IDAT'])
        decompressed = zlib.decompress(idat_data)
        
        # Modo RGBA (color_type == 6)
        if color_type == 6 and bit_depth == 8:
            pixels = []
            stride = width * 4 + 1
            for y in range(height):
                row = decompressed[y * stride : (y + 1) * stride]
                filter_type = row[0]
                # Para simplificar, ignoramos os filtros de reconstrução se pudermos apenas ver opacidade aproximada
                # Caso contrário, vamos reconstruir a linha
                # Mas para analisar a opacidade básica, podemos apenas contar pixels não nulos ou não-transparentes
                pixels.append(row[1:])
            return width, height, pixels
    return None

filepath = r"c:\Users\Mkt\Desktop\Ranking\static\retro_carlo\frames\run_1.png"
result = read_png_pixels(filepath)
if result:
    width, height, rows = result
    print(f"run_1.png: {width}x{height}")
    # Vamos imprimir um mapa de caracteres da opacidade dos pixels
    # Amostrando a cada 4 pixels na largura e 8 na altura
    for y in range(0, height, 6):
        row_str = ""
        for x in range(0, width, 3):
            # Acelerar: checar se os pixels nessa área têm canal alpha > 10
            # Cada pixel tem 4 bytes (R, G, B, A)
            idx = x * 4
            if idx + 3 < len(rows[y]):
                a = rows[y][idx + 3]
                r = rows[y][idx]
                g = rows[y][idx+1]
                b = rows[y][idx+2]
                
                # Se for a cor de fundo (por exemplo, azul escuro ou preto)
                # Vamos ver se é transparente ou se é da cor do personagem
                # O personagem tem pele cor de carne, roupa vermelha, calça azul
                # O fundo é azul escuro.
                # Vamos marcar com '#' se for o personagem, '.' se for fundo, e ' ' se for transparente
                if a == 0:
                    row_str += " "
                elif r < 20 and g < 30 and b < 50: # Fundo azul escuro aproximado
                    row_str += "."
                else:
                    row_str += "#"
            else:
                row_str += " "
        print(row_str)
else:
    print("Falha ao ler o PNG")
