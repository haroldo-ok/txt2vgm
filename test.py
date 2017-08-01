'''
Created on 31 de jul de 2017

@author: Haroldo
'''
from sphinx.ext.autosummary import process_autosummary_toc
from _functools import reduce

"""
import vgmparse

file_data = open('Alex Kidd in Miracle World - 01 - Title Screen.vgm', 'rb').read()
vgm_data = vgmparse.Parser(file_data)

print (vgm_data)
"""

import re, struct

RX_LINE = re.compile(r'^(.*?):\s*(.*)$')
RX_DATA = re.compile(r'^([\dA-F]{2})\s([\dA-F]{2})?\s([\dA-F]{2})?\s+([^:]+):?\s*(.*)$')

headers = {}
data = []
processing_headers = True

with open('Alex Kidd in Miracle World - 01 - Title Screen.txt', 'rt') as f:
    for line in (line.rstrip('\n') for line in f):
        pair = RX_LINE.match(line)
        if pair:
            key = pair.group(1)
            value = pair.group(2)
            if processing_headers:
                if key == 'VGMData':
                    processing_headers = False
                else:
                    headers[key] = value
            else:
                parts = RX_DATA.match(value)
                raw = [int(b, 16) for b in (parts.group(n) for n in (1, 2, 3)) if b]
                data.append({
                    'command': raw[0],
                    'param': reduce(lambda a, x: a * 255 + x, reversed(raw[1:]), 0),
                    'raw': raw,
                    'type': parts.group(4),
                    'detail': parts.group(5)
                })
        
print(headers)
print(data)

def pack32(n):
    return struct.pack('<I', n)

def pack8(n):
    return struct.pack('B', n)

with open('test.vgm', 'wb') as f:
    # Write header
    f.write(b'Vgm ')
    f.write(pack32(0)) # 0x04: Eof offset (32 bits)
    f.write(pack32(0x101)) # 0x08: Version number (32 bits)
    f.write(pack32(3579545)) # 0x0c: SN76489 clock (32 bits)
    f.write(pack32(0)) # 0x10: YM2413 clock (32 bits)
    f.write(pack32(0)) # 0x14: GD3 offset (32 bits)
    f.write(pack32(0)) # 0x18: Total # samples (32 bits)
    f.write(pack32(0)) # 0x1c: Loop offset (32 bits)
    f.write(pack32(0)) # 0x20: Loop # samples (32 bits)
    f.write(pack32(60)) # 0x24: Rate (32 bits)
    f.write(b'\0' * (0x40 - f.tell())) # Padding up to 0x40
        
    # Write data
    for d in data:
        f.write(bytes(d['raw']))
