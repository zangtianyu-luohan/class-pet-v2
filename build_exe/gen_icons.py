import struct, zlib

def create_png(width, height, bg_color=(49,46,129)):
    rows = []
    for y in range(height):
        row = b'\x00'
        for x in range(width):
            cx, cy = width//2, height//2
            dx, dy = x - cx, y - cy
            r = int(width * 0.42)
            if dx*dx + dy*dy < r*r:
                bar_w = width // 8
                bars = [
                    (int(cx - bar_w*1.8), int(cy + r*0.1), int(bar_w*0.8), int(r*0.5)),
                    (int(cx - bar_w*0.6), int(cy - r*0.3), int(bar_w*0.8), int(r*0.7)),
                    (int(cx + bar_w*0.6), int(cy - r*0.05), int(bar_w*0.8), int(r*0.45)),
                    (int(cx + bar_w*1.8), int(cy - r*0.4), int(bar_w*0.8), int(r*0.6)),
                ]
                in_bar = False
                for bx, by, bw, bh in bars:
                    if bx <= x < bx+bw and by <= y < by+bh:
                        in_bar = True
                        break
                if in_bar:
                    row += bytes([255, 255, 255, 255])
                else:
                    row += bytes([bg_color[0], bg_color[1], bg_color[2], 255])
            else:
                row += bytes([0, 0, 0, 0])
        rows.append(row)

    def make_chunk(chunk_type, data):
        chunk = chunk_type + data
        return struct.pack('>I', len(data)) + chunk + struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    raw = b''.join(rows)
    idat = zlib.compress(raw)
    return sig + make_chunk(b'IHDR', ihdr) + make_chunk(b'IDAT', idat) + make_chunk(b'IEND', b'')

base = r'C:\Users\53205\Desktop\资料\罗涵\学习积分管理系统\frontend\public'
for size in [192, 512]:
    png = create_png(size, size)
    with open(f'{base}/icon-{size}.png', 'wb') as f:
        f.write(png)
    print(f'Created icon-{size}.png ({len(png)} bytes)')
