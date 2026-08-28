#!/usr/bin/env python3
"""
Builds the social share image (og.jpg, 1200x630).

Mirrors the look of index.html: the same pink-to-red elliptical ramp, the same
Y2K starburst, sparkles, and Pirata One set in white with a dark halo. Values
here are kept deliberately in step with the CSS — if the page's palette or ray
geometry changes, change it here too and re-run:

    python3 tools/make-og.py
"""
import math, os, urllib.request
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1200, 630
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONTS = os.environ.get("OG_FONT_DIR", os.path.join(HERE, "fonts"))
FONT_URL = ("https://github.com/google/fonts/raw/main/ofl/pirataone/"
            "PirataOne-Regular.ttf")


def font_path():
    """Fetch Pirata One on first run rather than committing the binary."""
    os.makedirs(FONTS, exist_ok=True)
    path = os.path.join(FONTS, "PirataOne-Regular.ttf")
    if not os.path.exists(path):
        print("fetching Pirata One...")
        urllib.request.urlretrieve(FONT_URL, path)
    return path

LINES = ["Slayyyter didn’t", "complete the Census"]

# radial-gradient(112% 80% at 50% 22%, ...) from the page
STOPS = [
    (0.00, (0xFF, 0x9A, 0xE0)), (0.17, (0xFF, 0x4F, 0xB2)),
    (0.33, (0xFF, 0x1E, 0x86)), (0.49, (0xFF, 0x0B, 0x52)),
    (0.65, (0xEA, 0x0B, 0x2E)), (0.79, (0xC1, 0x08, 0x26)),
    (0.92, (0x7A, 0x03, 0x22)), (1.00, (0x4E, 0x01, 0x19)),
]


def ramp():
    cx, cy = 0.50 * W, 0.22 * H
    rx, ry = 1.12 * W, 0.80 * H
    ys, xs = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2).clip(0, 1)
    pos = np.array([s[0] for s in STOPS])
    out = np.zeros((H, W, 3))
    for ch in range(3):
        out[..., ch] = np.interp(d, pos, [s[1][ch] for s in STOPS])
    return Image.fromarray(out.astype(np.uint8), "RGB")


def rays(img):
    """repeating-conic-gradient: 5deg of white at .115, then a 6deg gap."""
    cx, cy = 0.50 * W, 0.22 * H
    layer = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    R = 3000
    for start in range(0, 360, 11):
        a0, a1 = math.radians(start), math.radians(start + 5)
        d.polygon(
            [(cx * 2, cy * 2),
             (cx * 2 + R * math.cos(a0), cy * 2 + R * math.sin(a0)),
             (cx * 2 + R * math.cos(a1), cy * 2 + R * math.sin(a1))],
            fill=(255, 255, 255, 29),
        )
    return Image.alpha_composite(img.convert("RGBA"), layer.resize((W, H), Image.LANCZOS))


def bezier(p0, p1, p2, p3, n=24):
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        yield (u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
               u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1])


def star_points(size):
    """The same four-point sparkle the page draws in SVG."""
    segs = [((50,0),(54,38),(62,46),(100,50)), ((100,50),(62,54),(54,62),(50,100)),
            ((50,100),(46,62),(38,54),(0,50)), ((0,50),(38,46),(46,38),(50,0))]
    pts = []
    for s in segs:
        pts.extend(bezier(*s))
    return [(x * size / 100, y * size / 100) for x, y in pts]


def sparkles(img):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x, y, s, a in [(96,110,44,210),(1090,86,32,180),(150,520,30,150),
                       (1120,470,40,190),(300,86,22,150),(940,556,26,150)]:
        pts = [(px + x, py + y) for px, py in star_points(s)]
        d.polygon(pts, fill=(255, 255, 255, a))
    return Image.alpha_composite(img, layer)


def vignette(img):
    cx, cy = 0.50 * W, 0.46 * H
    rx, ry = 0.72 * W, 0.62 * H
    ys, xs = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2).clip(0, 1)
    alpha = ((1 - d) * 0.30).clip(0, 1)
    layer = np.zeros((H, W, 4))
    layer[..., 0], layer[..., 1], layer[..., 2] = 74, 0, 28
    layer[..., 3] = alpha * 255
    return Image.alpha_composite(img, Image.fromarray(layer.astype(np.uint8), "RGBA"))


def fit_font(path, lines, max_w, max_h):
    """Largest size where every line clears max_w and the block clears max_h."""
    size = 10
    while size < 260:
        f = ImageFont.truetype(path, size + 2)
        widths = [f.getbbox(l)[2] - f.getbbox(l)[0] for l in lines]
        block = int((size + 2) * 1.04) * len(lines)
        if max(widths) > max_w or block > max_h:
            break
        size += 2
    return ImageFont.truetype(path, size)


def draw_text(img):
    font = fit_font(font_path(), LINES, W - 270, 360)
    line_h = int(font.size * 1.04)
    total = line_h * len(LINES)
    top = (H - total) // 2 - int(font.size * 0.10)

    def stamp(layer, fill, dx=0, dy=0):
        d = ImageDraw.Draw(layer)
        for i, line in enumerate(LINES):
            bb = font.getbbox(line)
            x = (W - (bb[2] - bb[0])) // 2 - bb[0] + dx
            d.text((x, top + i * line_h - bb[1] + dy), line, font=font, fill=fill)

    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    stamp(halo, (74, 0, 28, 190))
    img = Image.alpha_composite(img, halo.filter(ImageFilter.GaussianBlur(20)))

    drop = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    stamp(drop, (92, 1, 37, 150), dy=7)
    img = Image.alpha_composite(img, drop.filter(ImageFilter.GaussianBlur(2)))

    top_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    stamp(top_layer, (255, 255, 255, 255))
    return Image.alpha_composite(img, top_layer), font.size


def grain(img):
    rng = np.random.default_rng(11)
    noise = rng.normal(0, 3.2, (H, W, 1))
    arr = np.asarray(img.convert("RGB")).astype(np.float64) + noise
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGB")


img = ramp()
img = rays(img)
img = sparkles(img)
img = vignette(img)
img, pt = draw_text(img)
img = grain(img)

out = os.path.join(ROOT, "og.jpg")
img.save(out, "JPEG", quality=92, optimize=True, progressive=True)
print(f"wrote {out}  {img.size[0]}x{img.size[1]}  type {pt}px  {os.path.getsize(out)/1024:.0f} KB")
