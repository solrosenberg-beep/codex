#!/usr/bin/env python3
"""Brand color gate for generated listing images.

Usage:
    python brand_check.py <brand> <image> [<image> ...]
    python brand_check.py serenelife work/B0HJ3R1ZQD/new/*.png

Reads the HEX codes from brand-kits/<brand>/BRAND.md, then looks at every
colorful (saturated) pixel in each image. Product photos are mostly neutral
(black, gray, white, wood), so the colorful pixels are the panels, headlines,
callouts and accents the designer added. Those must be brand colors.

PASS  = at least 80% of colorful pixels are close to a brand color.
FAIL  = an off-brand accent color (e.g. red on a SereneLife image).

Prints the top off-brand colors so the fix is obvious. Exit code 1 on any FAIL.
Needs Pillow only. If Pillow is missing, says so and exits 2 (do not pip install).
"""
import re
import sys
import colorsys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Pillow missing: brand_check skipped. Flag it in qa.md. Do not pip install inside the task.")
    sys.exit(2)

REPO = Path(__file__).resolve().parents[4]
PASS_SHARE = 0.80
SAT_MIN = 0.35      # below this a pixel counts as neutral (photo, shadows, white)
VAL_MIN = 0.20      # very dark pixels are neutral too
MATCH_DIST = 60     # RGB distance that counts as "this brand color"


def palette(brand):
    slug = brand.lower().replace(" ", "").replace("-", "")
    if slug.startswith("pyle"):  # Pyle Pro, Pyle Vintage use the Pyle kit
        slug = "pyle"
    kit = REPO / "brand-kits" / slug / "BRAND.md"
    if not kit.exists():
        kits = sorted(p.name for p in (REPO / "brand-kits").iterdir() if p.is_dir())
        print(f"No brand kit for '{brand}'. Available: {', '.join(kits)}. STOP: do not generate off-brand images.")
        sys.exit(1)
    text = kit.read_text(encoding="utf-8")
    colors_section = text.split("## Colors", 1)[1].split("\n## ", 1)[0] if "## Colors" in text else text
    hexes = sorted(set(h.upper() for h in re.findall(r"#([0-9A-Fa-f]{6})\b", colors_section)))
    return kit, [tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) for h in hexes], hexes


def is_colorful(rgb):
    h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
    return s >= SAT_MIN and v >= VAL_MIN


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def check(path, pal):
    img = Image.open(path).convert("RGB")
    img.thumbnail((300, 300))
    raw = img.tobytes()
    pixels = [tuple(raw[i:i + 3]) for i in range(0, len(raw), 3)]
    colorful = [p for p in pixels if is_colorful(p)]
    if not colorful:
        return True, 1.0, []
    off = {}
    on = 0
    for p in colorful:
        if min(dist(p, c) for c in pal) <= MATCH_DIST:
            on += 1
        else:
            key = tuple((x // 32) * 32 + 16 for x in p)
            off[key] = off.get(key, 0) + 1
    share = on / len(colorful)
    colorful_share_of_image = len(colorful) / (img.width * img.height)
    # Tiny amounts of color (a product LED, a plant) do not decide the verdict.
    ok = share >= PASS_SHARE or colorful_share_of_image < 0.02
    top = sorted(off.items(), key=lambda kv: -kv[1])[:3]
    return ok, share, [("#%02X%02X%02X" % k, round(100 * n / len(colorful))) for k, n in top]


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    brand, files = sys.argv[1], sys.argv[2:]
    kit, pal, hexes = palette(brand)
    print(f"Brand: {brand}  Kit: {kit.relative_to(REPO)}  Palette: {' '.join('#' + h for h in hexes)}")
    failed = 0
    for f in files:
        ok, share, top = check(f, pal)
        verdict = "PASS" if ok else "FAIL"
        extra = "" if ok else "  off-brand: " + ", ".join(f"{h} ({p}%)" for h, p in top)
        print(f"{verdict}  {Path(f).name}  on-brand {round(share * 100)}%{extra}")
        failed += not ok
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
