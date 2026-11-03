"""Image Studio engine: listing -> plan (Claude + codex rules) -> images (OpenAI) -> Drive.

Every rule, brief template and brand kit is read from the codex repo on GitHub at run time,
so editing a file in codex changes what the next job does. Credentials come only from
environment variables (Replit Secrets) and never reach the browser.
"""
import base64
import importlib.util
import io
import json
import os
import re
import threading
import time
import traceback
import uuid
import zipfile
from pathlib import Path

import requests
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent  # the codex repo
WORK = Path(os.environ.get("STUDIO_WORK_DIR", Path(__file__).resolve().parent / "work"))
WORK.mkdir(parents=True, exist_ok=True)

RULES_REPO = os.environ.get("RULES_REPO", "solrosenberg-beep/codex")
RULES_BRANCH = os.environ.get("RULES_BRANCH", "main")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5-5")
IMAGE_MODEL = os.environ.get("IMAGE_MODEL", "gpt-image-2")
DRY_RUN = os.environ.get("STUDIO_DRY_RUN") == "1"  # test mode: no API calls, placeholder images

RULE_FILES = {
    "Image rules (masterclass)": ".codex/skills/amazon-listing-image-audit/references/rules.md",
    "Audit skill": ".codex/skills/amazon-listing-image-audit/SKILL.md",
    "Rebuild skill": ".codex/skills/amazon-listing-image-rebuild/SKILL.md",
    "Brief template and prompt pattern": ".codex/skills/amazon-listing-image-rebuild/references/brief_template.md",
}
DRIVE_SCRIPT = ROOT / ".codex/skills/amazon-listing-image-rebuild/scripts/upload_to_drive.py"
ASIN_RE = re.compile(r"\b(B0[A-Z0-9]{8})\b", re.I)
DP_RE = re.compile(r"/(?:dp|gp/product)/([A-Z0-9]{10})", re.I)

_lock = threading.Lock()
JOBS: dict = {}


# ---------------------------------------------------------------- rules from GitHub
_cache: dict = {}


def _cached(key, ttl, fn):
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < ttl:
        return hit[1]
    val = fn()
    _cache[key] = (time.time(), val)
    return val


def read_repo_file(path: str) -> str:
    """Latest version from GitHub (cached 5 min); falls back to the local checkout."""
    def load():
        try:
            r = requests.get(f"https://raw.githubusercontent.com/{RULES_REPO}/{RULES_BRANCH}/{path}", timeout=10)
            if r.status_code == 200:
                return r.text
        except requests.RequestException:
            pass
        local = ROOT / path
        return local.read_text(encoding="utf-8") if local.exists() else ""
    return _cached("f:" + path, 300, load)


def rules_version() -> str:
    def load():
        try:
            r = requests.get(f"https://api.github.com/repos/{RULES_REPO}/commits/{RULES_BRANCH}", timeout=10)
            if r.status_code == 200:
                return r.json()["sha"][:7]
        except requests.RequestException:
            pass
        return "local copy"
    return _cached("sha", 300, load)


def brands() -> list:
    return sorted(p.parent.name for p in (ROOT / "brand-kits").glob("*/BRAND.md"))


def brand_kit(brand: str) -> str:
    return read_repo_file(f"brand-kits/{brand}/BRAND.md")


def logo_file(brand: str):
    assets = sorted((ROOT / "brand-kits" / brand / "assets").glob("*.png"))
    for key in ("logo", "wordmark"):
        for p in assets:
            if key in p.name and "stamp" not in p.name:
                return p
    return None


def match_brand(text: str):
    t = (text or "").lower().replace(" ", "")
    for b in brands():
        if b in t:
            return b
    return None


# ---------------------------------------------------------------- jobs
def new_job(user: str) -> dict:
    job = {
        "id": uuid.uuid4().hex[:10], "created": time.time(), "user": user or "Unknown",
        "asin": None, "sku": None, "brand": None, "mode": "rebuild", "note": "",
        "status": "Starting", "busy": False, "messages": [], "slots": [], "listing": {},
        "plan": None, "uploads": [], "rules_sha": None, "drive_url": None, "pending": None,
    }
    with _lock:
        JOBS[job["id"]] = job
    save(job)
    return job


def jdir(job) -> Path:
    d = WORK / job["id"]
    d.mkdir(parents=True, exist_ok=True)
    return d


def save(job):
    with _lock:
        (jdir(job) / "job.json").write_text(json.dumps(job, indent=1))


def load_all():
    for f in WORK.glob("*/job.json"):
        try:
            j = json.loads(f.read_text())
            j["busy"] = False
            JOBS[j["id"]] = j
        except (OSError, ValueError):
            pass


def say(job, text, role="assistant"):
    job["messages"].append({"role": role, "type": "text", "text": text})
    save(job)


def steps_msg(job):
    m = {"role": "assistant", "type": "steps", "items": []}
    job["messages"].append(m)
    return m


def step(job, m, label):
    m["items"].append({"label": label, "state": "run"})
    save(job)
    return len(m["items"]) - 1


def done(job, m, i, ok=True, label=None):
    m["items"][i]["state"] = "done" if ok else "fail"
    if label:
        m["items"][i]["label"] = label
    save(job)


# ---------------------------------------------------------------- Amazon listing
class ListingError(Exception):
    pass


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def fetch_listing(asin: str) -> dict:
    key = os.environ.get("KEEPA_API_KEY")
    if key:
        try:
            return _keepa(asin, key)
        except Exception:  # fall back to the page itself
            pass
    return _amazon_page(asin)


def _keepa(asin, key):
    r = requests.get("https://api.keepa.com/product", params={"key": key, "domain": 1, "asin": asin}, timeout=30)
    r.raise_for_status()
    p = (r.json().get("products") or [None])[0]
    if not p:
        raise ListingError("Keepa has no data for this ASIN.")
    names = [n for n in (p.get("imagesCSV") or "").split(",") if n]
    return {
        "title": p.get("title") or "", "brand": p.get("brand") or "", "model": p.get("model") or "",
        "bullets": p.get("features") or [], "specs": {}, "description": p.get("description") or "",
        "images": [f"https://m.media-amazon.com/images/I/{n}" for n in names], "source": "Keepa",
    }


def _amazon_page(asin):
    from bs4 import BeautifulSoup

    try:
        r = requests.get(f"https://www.amazon.com/dp/{asin}", headers=HEADERS, timeout=30)
    except requests.RequestException as e:
        raise ListingError(f"Couldn't reach Amazon ({e.__class__.__name__}).")
    html = r.text
    if r.status_code == 404:
        raise ListingError("Amazon says this ASIN doesn't exist. Check the ASIN.")
    if r.status_code != 200 or "captcha" in html.lower()[:20000] or "api-services-support@amazon.com" in html:
        raise ListingError("Amazon blocked the request (robot check).")
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.select_one("#productTitle") or soup.new_tag("x")).get_text(" ", strip=True)
    brand = (soup.select_one("#bylineInfo") or soup.new_tag("x")).get_text(" ", strip=True)
    brand = re.sub(r"^(Visit the |Brand:\s*)|\s*Store$", "", brand)
    bullets = [li.get_text(" ", strip=True) for li in soup.select("#feature-bullets li span.a-list-item")]
    specs = {}
    for tr in soup.select("table[id^=productDetails] tr, #productOverview_feature_div tr, table.a-keyvalue tr"):
        th, td = tr.find(["th", "td"]), tr.find_all("td")
        if th and td:
            k, v = th.get_text(" ", strip=True), td[-1].get_text(" ", strip=True)
            if k and v and k != v:
                specs[k] = v[:300]
    for li in soup.select("#detailBullets_feature_div li"):
        t = li.get_text(" ", strip=True).replace("‏", "").replace("‎", "")
        if ":" in t:
            k, v = t.split(":", 1)
            specs[k.strip()] = v.strip()[:300]
    images = []
    m = re.search(r"'colorImages':\s*\{\s*'initial':\s*(\[.*?\])\s*\}", html, re.S)
    if m:
        try:
            for it in json.loads(m.group(1)):
                u = it.get("hiRes") or it.get("large")
                if u:
                    images.append(u)
        except ValueError:
            pass
    if not images:
        for u in re.findall(r'"hiRes":"(https://m\.media-amazon\.com/images/I/[^"]+)"', html):
            if u not in images:
                images.append(u)
    if not title and not images:
        raise ListingError("Amazon returned a page without product details.")
    model = next((v for k, v in specs.items() if "model" in k.lower()), "")
    return {"title": title, "brand": brand, "model": model, "bullets": bullets, "specs": specs,
            "description": "", "images": images, "source": "Amazon page"}


def download_images(job, urls) -> list:
    out = []
    cur = jdir(job) / "current"
    cur.mkdir(exist_ok=True)
    for i, u in enumerate(urls[:9], 1):
        try:
            r = requests.get(u, headers=HEADERS, timeout=30)
            r.raise_for_status()
            img = Image.open(io.BytesIO(r.content)).convert("RGB")
            p = cur / f"{i:02d}.jpg"
            img.save(p, quality=92)
            out.append(str(p))
        except Exception:
            continue
    return out


# ---------------------------------------------------------------- Claude
def _claude():
    import anthropic
    return anthropic.Anthropic()


def _b64(path, max_side=1568):
    img = Image.open(path).convert("RGB")
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=88)
    return base64.b64encode(buf.getvalue()).decode()


def claude_json(system: str, content: list, schema: dict, effort="high") -> dict:
    """One Claude call that must return JSON matching `schema`."""
    client = _claude()
    with client.beta.messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=32000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        thinking={"type": "adaptive"},
        output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
        system=system,
        messages=[{"role": "user", "content": content}],
    ) as stream:
        msg = stream.get_final_message()
    if msg.stop_reason == "refusal":
        raise RuntimeError("Claude declined this request.")
    if msg.stop_reason == "max_tokens":
        raise RuntimeError("Claude's answer was cut off. Try again.")
    text = next(b.text for b in msg.content if b.type == "text")
    return json.loads(text)


PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "sku": {"type": "string"},
        "summary": {"type": "string"},
        "problems": {"type": "array", "items": {"type": "string"}},
        "left_off": {"type": "array", "items": {"type": "string"}},
        "slots": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "n": {"type": "integer"},
                "message": {"type": "string"},
                "fix": {"type": "string"},
                "prompt": {"type": "string"},
                "logo_position": {"type": "string", "enum": ["top-left", "top-right", "bottom-left", "bottom-right", "none"]},
            },
            "required": ["n", "message", "fix", "prompt", "logo_position"],
            "additionalProperties": False,
        }},
    },
    "required": ["sku", "summary", "problems", "left_off", "slots"],
    "additionalProperties": False,
}


def rules_system(brand: str) -> str:
    parts = ["You are the Sound Around Amazon listing image designer. Apply the team's rules below exactly. "
             "They come from the codex repo and are the only source of truth. Plain language, no em dashes."]
    for name, path in RULE_FILES.items():
        parts.append(f"\n\n===== {name} ({path}) =====\n{read_repo_file(path)}")
    parts.append(f"\n\n===== Brand kit: brand-kits/{brand}/BRAND.md =====\n{brand_kit(brand)}")
    return "".join(parts)


def make_plan(job) -> dict:
    L = job["listing"]
    n = len(job["slots"])
    if DRY_RUN:
        return {"sku": job["sku"] or "TEST", "summary": "Test mode plan.", "problems": ["Test problem one.", "Test problem two."],
                "left_off": [], "slots": [{"n": i + 1, "message": f"TEST MESSAGE {i + 1}", "fix": "Test fix.",
                                           "prompt": "test", "logo_position": "none" if i == 0 else "bottom-right"} for i in range(n)]}
    content = []
    for s in job["slots"]:
        content.append({"type": "text", "text": f"Current image {s['n']:02d}:"})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": _b64(s["current"])}})
    for i, u in enumerate(job["uploads"][:3], 1):
        content.append({"type": "text", "text": f"Extra product photo from the user {i}:"})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": _b64(u)}})
    facts = {k: L.get(k) for k in ("title", "brand", "model", "bullets", "specs", "description")}
    content.append({"type": "text", "text": (
        f"ASIN {job['asin']}. Brand kit: {job['brand']}. Known SKU: {job['sku'] or 'unknown'}.\n"
        f"Listing data (the only allowed source of numbers and claims):\n{json.dumps(facts, indent=1)[:30000]}\n\n"
        f"The user's request (this is the priority): {job['note'] or 'rebuild the images'}\n\n"
        f"Write the plan for this listing's {n} images, slot for slot in the same order (n = 1..{n}). Do not reorder.\n"
        "- sku: the Sound Around model number (from 'Item model number', model, or title). If unknown, use the ASIN.\n"
        "- summary: 2 to 3 sentences, bottom line first.\n"
        "- problems: the top 3 to 5 problems with the current images, one short sentence each.\n"
        "- left_off: any number or claim you left off the images because the listing conflicts or does not confirm it, and why.\n"
        "- For each slot: message (5 words or fewer), fix (what is wrong now and what the new image does), and prompt: a complete "
        "image-model prompt that follows the brief template's prompt pattern, with exact headline and sub text, brand hex colors, "
        "realistic scene, and a clear corner for the logo. The attached current photos are passed to the image model as the "
        "product reference, so describe the product as 'the product from the reference photo'.\n"
        "- logo_position: where the logo is pasted afterwards ('none' for the hero unless the brand kit says otherwise).\n"
        "Every number on an image must appear in the listing data above."
    )})
    return claude_json(rules_system(job["brand"]), content, PLAN_SCHEMA, effort="high")


EDIT_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["regenerate", "approve", "unapprove", "save_drive", "download", "chat"]},
        "slots": {"type": "array", "items": {"type": "integer"}},
        "new_prompts": {"type": "array", "items": {
            "type": "object",
            "properties": {"n": {"type": "integer"}, "prompt": {"type": "string"}},
            "required": ["n", "prompt"], "additionalProperties": False}},
        "reply": {"type": "string"},
    },
    "required": ["action", "slots", "new_prompts", "reply"],
    "additionalProperties": False,
}


def interpret(job, text, selected) -> dict:
    slots = [{"n": s["n"], "message": s.get("message"), "status": s["status"], "approved": s.get("approved"),
              "prompt": s.get("prompt")} for s in job["slots"]]
    content = [{"type": "text", "text": (
        f"The user is reviewing generated listing images for {job['sku']} ({job['brand']}). "
        f"The image they are looking at is slot {selected}.\n"
        f"Slots: {json.dumps(slots, indent=1)}\n\nUser message: {text}\n\n"
        "Decide the action. For 'regenerate', list the slots and write a full new prompt for each that keeps everything "
        "that was right and applies the change. Keep all numbers from the old prompt unless the user corrects them. "
        "'reply' is one or two plain sentences to show the user."
    )}]
    return claude_json(rules_system(job["brand"]), content, EDIT_SCHEMA, effort="medium")


# ---------------------------------------------------------------- images
def _openai():
    from openai import OpenAI
    return OpenAI()


def generate_image(job, slot) -> str:
    out = jdir(job) / "new"
    out.mkdir(exist_ok=True)
    slot["v"] = slot.get("v", 0) + 1
    path = out / f"{job['sku']}-{slot['n']:02d}.png"
    if DRY_RUN:
        img = Image.new("RGB", (1024, 1024), (230, 240, 240))
        ImageDraw.Draw(img).text((40, 40), f"TEST {slot['n']:02d} v{slot['v']}\n{slot.get('message', '')}", fill=(0, 0, 0))
    else:
        refs = [slot["current"]]
        if job["slots"] and job["slots"][0]["current"] not in refs:
            refs.append(job["slots"][0]["current"])
        refs += job["uploads"][:2]
        prompt = (
            "Use the attached photos only as the reference for the exact product: same shape, color, parts, and any logo printed "
            "on the product itself. Do not redesign the product. Do not draw any brand logo in the image; a logo is added later.\n\n"
            + slot["prompt"]
            + (f"\nKeep the {slot['logo_position'].replace('-', ' ')} corner clear for the logo." if slot.get("logo_position", "none") != "none" else "")
        )
        client = _openai()
        files = [open(p, "rb") for p in refs]
        try:
            r = client.images.edit(model=IMAGE_MODEL, image=files, prompt=prompt, size="1024x1024", quality="high")
        finally:
            for f in files:
                f.close()
        img = Image.open(io.BytesIO(base64.b64decode(r.data[0].b64_json))).convert("RGB")
    img = img.resize((2000, 2000), Image.LANCZOS)
    pos = slot.get("logo_position", "none")
    logo = logo_file(job["brand"])
    if pos != "none" and logo:
        lg = Image.open(logo).convert("RGBA")
        w = int(2000 * 0.22)
        lg = lg.resize((w, int(lg.height * w / lg.width)), Image.LANCZOS)
        m = 80
        x = m if "left" in pos else 2000 - w - m
        y = m if "top" in pos else 2000 - lg.height - m
        img.paste(lg, (x, y), lg)
    img.save(path)
    slot["file"] = f"new/{path.name}"
    return str(path)


def run_slot(job, slot, tries=2):
    slot["status"] = "generating"
    slot["error"] = None
    save(job)
    for attempt in range(tries):
        try:
            generate_image(job, slot)
            slot["status"] = "ready"
            slot["approved"] = False
            save(job)
            return True
        except Exception as e:
            slot["error"] = friendly(e)
            if attempt + 1 < tries:
                time.sleep(3)
    slot["status"] = "failed"
    save(job)
    return False


def friendly(e: Exception) -> str:
    name = e.__class__.__name__
    msg = str(e)
    if "api_key" in msg.lower() or name == "AuthenticationError":
        return "The image or AI key is missing or wrong. Check OPENAI_API_KEY and ANTHROPIC_API_KEY in Replit Secrets."
    if name == "RateLimitError":
        return "The image service is busy or out of credit. Wait a minute, or check the OpenAI account balance."
    if "safety" in msg.lower() or "moderation" in msg.lower():
        return "The image service refused this prompt. Try rewording the change."
    if name in ("APITimeoutError", "APIConnectionError", "Timeout"):
        return "The image service timed out. Try again."
    return f"{name}: {msg[:200]}"


# ---------------------------------------------------------------- conversation
def handle_message(job, text, uploads, selected=1):
    job["busy"] = True
    save(job)
    try:
        if job.get("pending") == "brand":
            b = match_brand(text)
            if not b:
                say(job, "I still need the brand. Reply with one of: " + ", ".join(brands()) + ".")
                return
            job["brand"], job["pending"] = b, None
            return build(job)
        if not job["asin"]:
            return start(job, text, uploads)
        return follow_up(job, text, selected)
    except Exception as e:
        traceback.print_exc()
        say(job, f"Something went wrong: {friendly(e)} Your work so far is saved; send the message again to retry.")
        job["status"] = "Error"
    finally:
        job["busy"] = False
        save(job)


def start(job, text, uploads):
    m = DP_RE.search(text) or ASIN_RE.search(text)
    if not m:
        say(job, "Paste an ASIN (like B0HJ3R1ZQD) or an Amazon link, and say what you need. Add **audit** if you only want a review.")
        return
    job["asin"] = m.group(1).upper()
    job["note"] = text
    job["mode"] = "audit" if re.search(r"\baudit\b|\breview only\b", text, re.I) and not re.search(r"rebuild|redo|new images", text, re.I) else "rebuild"
    job["uploads"] = uploads
    sm = re.search(r"\bsku[:\s]+([A-Z0-9.\-]{3,})", text, re.I)
    if sm:
        job["sku"] = sm.group(1).upper()
    st = steps_msg(job)
    job["_steps"] = len(job["messages"]) - 1
    i = step(job, st, f"Opening amazon.com/dp/{job['asin']}")
    try:
        if DRY_RUN:
            L = {"title": "Test product", "brand": match_brand(text) or "SereneLife", "model": "TEST1", "bullets": [], "specs": {}, "description": "", "images": [], "source": "test"}
        else:
            L = fetch_listing(job["asin"])
        job["listing"] = L
        done(job, st, i, label=f"Read the listing ({L['source']}): {L['title'][:80]}")
    except ListingError as e:
        done(job, st, i, ok=False, label=f"Couldn't read the Amazon page: {e}")
        if not uploads:
            job["status"] = "Needs images"
            say(job, "I couldn't get the listing from Amazon. Click **+**, attach the current listing images in order (1, 2, 3...), "
                     "and send the ASIN again. Add the brand and SKU in the message too, e.g. *B0HJ3R1ZQD SereneLife SKU SLTRD15 rebuild*.")
            job["asin"] = None
            return
        job["listing"] = {"title": "", "brand": "", "model": "", "bullets": [], "specs": {}, "description": "", "images": [], "source": "your uploads"}
    i = step(job, st, "Collecting the current images in listing order")
    paths = [] if DRY_RUN else download_images(job, job["listing"]["images"])
    if DRY_RUN and not uploads:
        p = jdir(job) / "current"
        p.mkdir(exist_ok=True)
        for k in range(1, 4):
            Image.new("RGB", (600, 600), (250, 250, 250)).save(p / f"{k:02d}.jpg")
            paths.append(str(p / f"{k:02d}.jpg"))
    if not paths and uploads:
        paths, job["uploads"] = uploads, []
    if not paths:
        done(job, st, i, ok=False, label="No images found on the listing")
        say(job, "I couldn't download any images. Attach them with **+** and send the ASIN again.")
        job["asin"] = None
        return
    job["slots"] = [{"n": k + 1, "current": p, "status": "queued", "approved": False, "v": 0} for k, p in enumerate(paths)]
    done(job, st, i, label=f"Found {len(paths)} images")
    job["sku"] = job["sku"] or (job["listing"].get("model") or "").upper().replace(" ", "") or None
    job["brand"] = match_brand(text) or match_brand(job["listing"].get("brand")) or match_brand(job["listing"].get("title"))
    if not job["brand"]:
        job["pending"] = "brand"
        job["status"] = "Needs brand"
        say(job, "Which brand kit should I use? Reply with one of: " + ", ".join(brands()) + ".")
        return
    build(job)


def build(job):
    st = job["messages"][job.get("_steps", -1)] if job.get("_steps") is not None else steps_msg(job)
    i = step(job, st, f"Loading the {job['brand']} brand kit and image rules from codex")
    job["rules_sha"] = rules_version()
    done(job, st, i, label=f"Loaded the {job['brand']} brand kit and image rules (codex @ {job['rules_sha']})")
    i = step(job, st, "Writing a brief for every image")
    job["status"] = "Planning"
    plan = make_plan(job)
    job["plan"] = plan
    job["sku"] = (job["sku"] or plan.get("sku") or job["asin"]).upper()
    for s in job["slots"]:
        p = next((x for x in plan["slots"] if x["n"] == s["n"]), None)
        if p:
            s.update(message=p["message"], fix=p["fix"], prompt=p["prompt"], logo_position=p["logo_position"])
    done(job, st, i, label=f"Wrote {len(job['slots'])} briefs · SKU {job['sku']}")
    lines = [f"**{plan['summary']}**", "", "**Top problems:**"] + [f"- {p}" for p in plan["problems"]]
    if plan["left_off"]:
        lines += ["", "**Left off the images (not confirmed on the listing):**"] + [f"- {x}" for x in plan["left_off"]]
    say(job, "\n".join(lines))
    if job["mode"] == "audit":
        say(job, "\n".join(["**Fix brief per image, in listing order:**"] + [f"{s['n']}. **{s.get('message', '')}** {s.get('fix', '')}" for s in job["slots"]]
                           + ["", "Say **rebuild** to turn these into images."]))
        job["status"] = "Audit done"
        return
    generate_all(job)


def generate_all(job):
    job["status"] = "Generating"
    job["messages"].append({"role": "assistant", "type": "gallery"})
    save(job)
    for s in job["slots"]:
        s["status"] = "queued"
    for s in job["slots"]:
        run_slot(job, s)
    failed = [s["n"] for s in job["slots"] if s["status"] == "failed"]
    if failed:
        err = next(s["error"] for s in job["slots"] if s["status"] == "failed")
        say(job, f"Done, except image {', '.join(map(str, failed))}: {err} Click it and press **Regenerate**.")
    else:
        say(job, f"Done. All {len(job['slots'])} images are ready, in listing order. Approve the ones you like, type changes "
                 "(for example *make the hero text bigger*), then say **save to drive**.")
    job["status"] = "In review"


def follow_up(job, text, selected):
    t = text.lower().strip()
    if job["mode"] == "audit" and re.search(r"\brebuild\b|\bmake (the )?images\b|\bgo\b", t):
        job["mode"] = "rebuild"
        return generate_all(job)
    if re.search(r"\bsave\b.*\bdrive\b|\bdrive\b", t):
        return save_to_drive(job)
    if re.fullmatch(r"approve all\.?", t):
        for s in job["slots"]:
            if s["status"] == "ready":
                s["approved"] = True
        say(job, "Approved every ready image.")
        return
    if not job["slots"] or not any(s.get("file") for s in job["slots"]):
        say(job, "There are no images yet. Send an ASIN to start.")
        return
    if DRY_RUN:
        d = {"action": "regenerate", "slots": [selected], "new_prompts": [], "reply": f"Regenerating image {selected}."}
    else:
        d = interpret(job, text, selected)
    say(job, d["reply"])
    act = d["action"]
    nums = [n for n in d["slots"] if 1 <= n <= len(job["slots"])] or [selected]
    if act == "regenerate":
        for np in d["new_prompts"]:
            if 1 <= np["n"] <= len(job["slots"]):
                job["slots"][np["n"] - 1]["prompt"] = np["prompt"]
        for n in nums:
            job["slots"][n - 1]["note"] = text
            run_slot(job, job["slots"][n - 1])
        say(job, f"Updated image {', '.join(map(str, nums))}.")
    elif act in ("approve", "unapprove"):
        for n in nums:
            job["slots"][n - 1]["approved"] = act == "approve"
    elif act == "save_drive":
        save_to_drive(job)
    elif act == "download":
        say(job, f"[Download {job['sku']}-CODEX.zip](/api/job/{job['id']}/zip)")


def chosen_files(job):
    approved = [s for s in job["slots"] if s.get("approved") and s.get("file")]
    return approved or [s for s in job["slots"] if s.get("file") and s["status"] == "ready"], bool(approved)


def save_to_drive(job):
    slots, only_approved = chosen_files(job)
    if not slots:
        say(job, "There are no finished images to save yet.")
        return
    folder = f"{job['sku']}-CODEX"
    say(job, f"Saving {len(slots)} {'approved' if only_approved else ''} images to Google Drive › **{folder}**…".replace("  ", " "))
    try:
        spec = importlib.util.spec_from_file_location("upload_to_drive", DRIVE_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        try:
            svc = mod.get_service()
        except SystemExit:
            say(job, "Couldn't save to Google Drive: the Drive key isn't set up. Add **GDRIVE_SERVICE_ACCOUNT_JSON** in Replit Secrets "
                     "(see the codex README, 'One-time setup for Drive upload'). Your images are still here; you can download them.")
            job["status"] = "Drive save failed"
            return
        folder_id, _ = mod.find_or_create_folder(svc, folder, mod.SHARED_DRIVE_ID)
        for s in slots:
            mod.upload_file(svc, jdir(job) / s["file"], folder_id)
        job["drive_url"] = f"https://drive.google.com/drive/folders/{folder_id}"
        job["status"] = "Saved to Drive"
        say(job, f"Saved {len(slots)} images to [{folder}]({job['drive_url']}).")
    except Exception as e:
        traceback.print_exc()
        job["status"] = "Drive save failed"
        say(job, f"Couldn't save to Google Drive: {friendly(e)} If it says 'not found' or 'permission', share the image drive "
                 "with the service account email as Content manager. Your images are still here.")


def zip_bytes(job) -> bytes:
    slots, _ = chosen_files(job)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for s in slots:
            z.write(jdir(job) / s["file"], f"{job['sku']}-CODEX/{Path(s['file']).name}")
    return buf.getvalue()


def health() -> dict:
    return {
        "anthropic_key": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "openai_key": bool(os.environ.get("OPENAI_API_KEY")),
        "drive": bool(os.environ.get("GDRIVE_SERVICE_ACCOUNT_JSON") or os.environ.get("GDRIVE_SERVICE_ACCOUNT_FILE")),
        "keepa": bool(os.environ.get("KEEPA_API_KEY")),
        "rules": rules_version(),
        "dry_run": DRY_RUN,
    }
