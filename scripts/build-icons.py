#!/usr/bin/env python3
"""Build matching SVG, PNG and ICO LTS icons using only Python's standard library."""
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parent.parent
BG = (5, 13, 20)
BLUE = (22, 140, 255)
WHITE = (255, 255, 255)
# Vector rectangles on a 64-unit canvas. Glyphs do not depend on installed fonts.
shapes = [(0, 0, 64, 64, BG), (8, 49, 48, 5, BLUE)]
glyphs = ('100100100100111', '111010010010010', '111100111001111')
for index, glyph in enumerate(glyphs):
    for cell, filled in enumerate(glyph):
        if filled == '1':
            shapes.append((10 + index * 16 + cell % 3 * 4, 20 + cell // 3 * 4, 4, 4, WHITE))

def png(size):
    rows = bytearray()
    for y in range(size):
        rows.append(0)
        for x in range(size):
            color = BG
            px, py = (x + .5) * 64 / size, (y + .5) * 64 / size
            for left, top, width, height, fill in shapes:
                if left <= px < left + width and top <= py < top + height:
                    color = fill
            rows.extend(color)
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(rows, 9)) + chunk(b'IEND', b'')

svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">\n'
for x, y, width, height, color in shapes:
    svg += f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="#{bytes(color).hex()}"/>\n'
(ROOT / 'favicon.svg').write_text(svg + '</svg>\n')
for size, name in [(16, 'favicon-16x16.png'), (32, 'favicon-32x32.png'), (180, 'apple-touch-icon.png'), (192, 'web-app-manifest-192x192.png'), (512, 'web-app-manifest-512x512.png')]:
    (ROOT / name).write_bytes(png(size))
# Multi-resolution ICO with embedded PNG images.
sizes = (16, 32, 48)
images = [png(size) for size in sizes]
header = struct.pack('<HHH', 0, 1, len(images))
entries = bytearray()
offset = 6 + 16 * len(images)
for size, data in zip(sizes, images):
    entries.extend(struct.pack('<BBBBHHII', size, size, 0, 0, 1, 32, len(data), offset))
    offset += len(data)
(ROOT / 'favicon.ico').write_bytes(header + entries + b''.join(images))
print('Built SVG, ICO, 16/32 px favicons and 180/192/512 px app icons.')
