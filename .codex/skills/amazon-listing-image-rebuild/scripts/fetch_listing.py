#!/usr/bin/env python3
"""Pull an Amazon listing (title, bullets, spec table, variations, images in order) into work/<ASIN>/.

Usage:
    python fetch_listing.py B0XXXXXXXX
    python fetch_listing.py B0XXXXXXXX --out work

Writes:
    work/<ASIN>/listing.md          title, brand, price, bullets, spec table, variations, image URLs in order
    work/<ASIN>/listing.json        the same as data
    work/<ASIN>/current/01.jpg ...  every listing image, numbered in the order Amazon shows them

Sources, tried in order:
    1. Keepa API, if KEEPA_API_KEY is set (most reliable; gives images, bullets, description, model number).
    2. amazon.com product page over plain HTTPS with a browser user agent.

Needs outbound internet to amazon.com (and api.keepa.com if used). In web Codex, turn on
"Agent internet access" for the environment or this script cannot reach Amazon.
Only the standard library is used, so nothing has to be installed.
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def http_get(url, timeout=30):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def clean(t):
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t).strip()


# ---------- Keepa ----------
def from_keepa(asin, key):
    url = f"https://api.keepa.com/product?key={key}&domain=1&asin={asin}&stats=0&history=0"
    data = json.loads(http_get(url))
    prods = data.get("products") or []
    if not prods:
        raise RuntimeError("Keepa returned no product")
    p = prods[0]
    imgs = [f"https://m.media-amazon.com/images/I/{i.strip()}" for i in (p.get("imagesCSV") or "").split(",") if i.strip()]
    specs = {}
    if p.get("model"):
        specs["Item model number"] = p["model"]
    for k in ("packageWeight", "packageLength", "packageWidth", "packageHeight", "itemWeight", "itemLength", "itemWidth", "itemHeight", "color", "size", "material", "numberOfItems"):
        if p.get(k) not in (None, -1, "", 0):
            specs[k] = p[k]
    return {
        "source": "keepa",
        "asin": asin,
        "title": p.get("title", ""),
        "brand": p.get("brand", ""),
        "model": p.get("model", ""),
        "bullets": p.get("features") or [],
        "description": clean(p.get("description") or ""),
        "specs": specs,
        "variations": [v.get("asin") for v in (p.get("variations") or []) if v.get("asin")],
        "images": imgs,
    }


# ---------- amazon.com HTML ----------
def from_amazon(asin):
    raw = http_get(f"https://www.amazon.com/dp/{asin}?th=1&psc=1").decode("utf-8", "ignore")
    if "api-services-support@amazon.com" in raw or "Enter the characters you see below" in raw:
        raise RuntimeError("Amazon returned a robot check page")

    title = clean(re.search(r'id="productTitle"[^>]*>(.*?)</span>', raw, re.S).group(1)) if re.search(r'id="productTitle"', raw) else ""
    brand_m = re.search(r'id="bylineInfo"[^>]*>(.*?)</a>', raw, re.S)
    brand = clean(brand_m.group(1)).replace("Visit the ", "").replace(" Store", "").replace("Brand: ", "") if brand_m else ""

    bullets = []
    fb = re.search(r'id="feature-bullets".*?<ul[^>]*>(.*?)</ul>', raw, re.S)
    if fb:
        bullets = [clean(b) for b in re.findall(r"<li[^>]*>(.*?)</li>", fb.group(1), re.S)]
        bullets = [b for b in bullets if b and "Make sure this fits" not in b]

    specs = {}
    for tbl_id in ("productDetails_techSpec_section_1", "productDetails_detailBullets_sections1", "productDetails_techSpec_section_2"):
        t = re.search(rf'id="{tbl_id}".*?</table>', raw, re.S)
        if t:
            for k, v in re.findall(r"<th[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>", t.group(0), re.S):
                specs[clean(k)] = clean(v)
    for k, v in re.findall(r'<span class="a-text-bold">\s*(.*?)\s*(?:&lrm;)?:?\s*</span>\s*<span>(.*?)</span>', raw, re.S):
        k2 = clean(k).rstrip(":"); v2 = clean(v)
        if k2 and v2 and k2 not in specs and len(k2) < 60:
            specs[k2] = v2
    ov = re.search(r'id="productOverview_feature_div".*?</table>', raw, re.S)
    if ov:
        for k, v in re.findall(r'<td[^>]*class="[^"]*a-span3[^"]*"[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>', ov.group(0), re.S):
            specs.setdefault(clean(k), clean(v))

    imgs = []
    m = re.search(r"'colorImages':\s*\{\s*'initial':\s*(\[.*?\])\s*\}", raw, re.S)
    if m:
        try:
            for entry in json.loads(m.group(1)):
                u = entry.get("hiRes") or entry.get("large")
                if u:
                    imgs.append(u)
        except json.JSONDecodeError:
            pass
    if not imgs:
        for u in re.findall(r'"hiRes":"(https://[^"]+)"', raw):
            if u not in imgs:
                imgs.append(u)
    if not imgs:
        for u in re.findall(r'"large":"(https://m\.media-amazon\.com/images/I/[^"]+)"', raw):
            if u not in imgs:
                imgs.append(u)

    variations = []
    vm = re.search(r'"dimensionValuesDisplayData"\s*:\s*(\{.*?\})', raw, re.S)
    if vm:
        try:
            variations = list(json.loads(vm.group(1)).keys())
        except json.JSONDecodeError:
            pass

    price_m = re.search(r'class="a-offscreen">(\$[\d,.]+)</span>', raw)
    rating_m = re.search(r'id="acrPopover"[^>]*title="([^"]+)"', raw)
    count_m = re.search(r'id="acrCustomerReviewText"[^>]*>([^<]+)<', raw)

    return {
        "source": "amazon.com",
        "asin": asin,
        "title": title,
        "brand": brand,
        "model": specs.get("Item model number", ""),
        "price": price_m.group(1) if price_m else "",
        "rating": clean(rating_m.group(1)) if rating_m else "",
        "review_count": clean(count_m.group(1)) if count_m else "",
        "bullets": bullets,
        "description": "",
        "specs": specs,
        "variations": variations,
        "images": imgs,
    }


def write_outputs(d, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "listing.json").write_text(json.dumps(d, indent=2))
    lines = [f"# {d['asin']}  ({d['source']})", "",
             f"Title: {d['title']}", f"Brand: {d['brand']}", f"Model / SKU: {d.get('model','')}",
             f"Price: {d.get('price','')}  Rating: {d.get('rating','')}  Reviews: {d.get('review_count','')}", "",
             "## Bullets"]
    lines += [f"- {b}" for b in d["bullets"]] or ["- (none found)"]
    lines += ["", "## Specs"]
    lines += [f"- {k}: {v}" for k, v in d["specs"].items()] or ["- (none found)"]
    if d.get("description"):
        lines += ["", "## Description", d["description"]]
    lines += ["", "## Variations (child ASINs)"]
    lines += [f"- {v}" for v in d["variations"]] or ["- (none)"]
    lines += ["", "## Images in listing order"]
    lines += [f"{i+1:02d}. {u}" for i, u in enumerate(d["images"])] or ["(none found)"]
    (out_dir / "listing.md").write_text("\n".join(lines) + "\n")

    cur = out_dir / "current"
    cur.mkdir(exist_ok=True)
    saved = 0
    for i, u in enumerate(d["images"], 1):
        ext = ".png" if u.lower().endswith(".png") else ".jpg"
        try:
            (cur / f"{i:02d}{ext}").write_bytes(http_get(u))
            saved += 1
        except Exception as e:  # noqa: BLE001
            print(f"  image {i:02d} failed: {e}")
    return saved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("asin")
    ap.add_argument("--out", default="work")
    a = ap.parse_args()
    asin = a.asin.strip().upper()
    out_dir = Path(a.out) / asin

    errors = []
    data = None
    key = os.environ.get("KEEPA_API_KEY")
    if key:
        try:
            data = from_keepa(asin, key)
        except Exception as e:  # noqa: BLE001
            errors.append(f"keepa: {e}")
    if data is None:
        try:
            data = from_amazon(asin)
        except Exception as e:  # noqa: BLE001
            errors.append(f"amazon.com: {e}")

    if data is None or not data.get("images"):
        print("Could not fetch the listing.")
        for e in errors:
            print("  " + e)
        print("\nMost likely cause in web Codex: the environment has no internet access. "
              "Turn on Agent internet access (allow amazon.com, m.media-amazon.com, api.keepa.com) "
              "and start a new task. Or ask the user to attach the images, bullets and spec table.")
        sys.exit(2)

    n = write_outputs(data, out_dir)
    print(f"Source: {data['source']}")
    print(f"Title: {data['title']}")
    print(f"Brand: {data['brand']}   Model: {data.get('model','')}")
    print(f"Bullets: {len(data['bullets'])}   Specs: {len(data['specs'])}   Images: {len(data['images'])} ({n} saved)")
    print(f"Wrote {out_dir}/listing.md and {out_dir}/current/")


if __name__ == "__main__":
    main()
