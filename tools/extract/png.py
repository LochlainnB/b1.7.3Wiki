"""Minimal 8-bit RGBA PNG decode/encode. Standard library only.

Beta 1.7.3's sheets are all non-interlaced 8-bit RGBA, which keeps this small.
"""
import struct
import zlib


class Image:
    __slots__ = ('w', 'h', 'px')

    def __init__(self, w, h, px=None):
        self.w = w
        self.h = h
        self.px = px if px is not None else bytearray(w * h * 4)

    def crop(self, x0, y0, w, h):
        out = Image(w, h)
        for y in range(h):
            src = ((y0 + y) * self.w + x0) * 4
            dst = y * w * 4
            out.px[dst:dst + w * 4] = self.px[src:src + w * 4]
        return out

    def scale(self, factor):
        """Nearest-neighbour upscale, so pixel art stays pixel art."""
        w, h = self.w * factor, self.h * factor
        out = Image(w, h)
        for y in range(h):
            src_row = (y // factor) * self.w * 4
            dst_row = y * w * 4
            for x in range(w):
                s = src_row + (x // factor) * 4
                d = dst_row + x * 4
                out.px[d:d + 4] = self.px[s:s + 4]
        return out

    def is_blank(self):
        return not any(self.px[3::4])


def decode(data):
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('not a PNG')
    pos = 8
    idat = bytearray()
    w = h = bitdepth = colortype = None
    palette = None
    trns = None
    while pos < len(data):
        length, ctype = struct.unpack_from('>I4s', data, pos)
        body = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if ctype == b'IHDR':
            w, h, bitdepth, colortype, comp, filt, interlace = struct.unpack('>IIBBBBB', body)
            if interlace:
                raise ValueError('interlaced PNG not supported')
            if bitdepth != 8:
                raise ValueError('only 8-bit PNGs supported')
        elif ctype == b'PLTE':
            palette = body
        elif ctype == b'tRNS':
            trns = body
        elif ctype == b'IDAT':
            idat += body
        elif ctype == b'IEND':
            break

    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[colortype]
    raw = zlib.decompress(bytes(idat))
    stride = w * channels
    out = bytearray(h * stride)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        ft = raw[p]; p += 1
        line = bytearray(raw[p:p + stride]); p += stride
        if ft == 1:
            for i in range(channels, stride):
                line[i] = (line[i] + line[i - channels]) & 0xFF
        elif ft == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif ft == 3:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif ft == 4:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                b = prev[i]
                c = prev[i - channels] if i >= channels else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        elif ft != 0:
            raise ValueError('bad filter %d' % ft)
        out[y * stride:(y + 1) * stride] = line
        prev = line

    # normalise everything to RGBA
    img = Image(w, h)
    for i in range(w * h):
        if colortype == 6:
            img.px[i * 4:i * 4 + 4] = out[i * 4:i * 4 + 4]
        elif colortype == 2:
            img.px[i * 4:i * 4 + 3] = out[i * 3:i * 3 + 3]
            img.px[i * 4 + 3] = 255
        elif colortype == 0:
            g = out[i]
            img.px[i * 4:i * 4 + 4] = bytes((g, g, g, 255))
        elif colortype == 4:
            g, a = out[i * 2], out[i * 2 + 1]
            img.px[i * 4:i * 4 + 4] = bytes((g, g, g, a))
        elif colortype == 3:
            idx = out[i]
            img.px[i * 4:i * 4 + 3] = palette[idx * 3:idx * 3 + 3]
            img.px[i * 4 + 3] = trns[idx] if trns and idx < len(trns) else 255
    return img


def encode(img):
    raw = bytearray()
    stride = img.w * 4
    for y in range(img.h):
        raw.append(0)                              # filter type 0 (None)
        raw += img.px[y * stride:(y + 1) * stride]

    def chunk(ctype, body):
        return (struct.pack('>I', len(body)) + ctype + body
                + struct.pack('>I', zlib.crc32(ctype + body) & 0xFFFFFFFF))

    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', img.w, img.h, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + chunk(b'IEND', b''))
