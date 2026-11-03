"""Image Studio web server. Run: python image-studio/app.py  (port from $PORT, default 8080)."""
import hmac
import os
import threading
from functools import wraps
from pathlib import Path

from flask import Flask, Response, abort, jsonify, request, send_file, send_from_directory

import studio

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 60 * 1024 * 1024
HERE = Path(__file__).resolve().parent
PASSWORD = os.environ.get("APP_PASSWORD", "")


def guarded(fn):
    """Optional team password (Replit Secret APP_PASSWORD). Any username works."""
    @wraps(fn)
    def inner(*a, **kw):
        if PASSWORD:
            auth = request.authorization
            if not auth or not hmac.compare_digest(auth.password or "", PASSWORD):
                return Response("Password required", 401, {"WWW-Authenticate": 'Basic realm="Image Studio"'})
        return fn(*a, **kw)
    return inner


def get_job(jid):
    job = studio.JOBS.get(jid)
    if not job:
        abort(404)
    return job


@app.get("/")
@guarded
def index():
    return send_from_directory(HERE / "static", "index.html")


@app.get("/api/health")
@guarded
def health():
    return jsonify(studio.health())


@app.get("/api/jobs")
@guarded
def jobs():
    rows = sorted(studio.JOBS.values(), key=lambda j: -j["created"])
    return jsonify([{k: j.get(k) for k in ("id", "created", "user", "asin", "sku", "brand", "mode", "status", "drive_url")}
                    for j in rows if j.get("asin")])


@app.get("/api/job/<jid>")
@guarded
def job(jid):
    j = get_job(jid)
    return jsonify({k: v for k, v in j.items() if k not in ("listing", "plan")})


@app.post("/api/send")
@guarded
def send():
    text = (request.form.get("text") or "").strip()
    jid = request.form.get("job_id") or ""
    user = (request.form.get("user") or "").strip()[:60]
    selected = int(request.form.get("selected") or 1)
    if not text:
        return jsonify(error="Type a message first."), 400
    job = studio.JOBS.get(jid)
    starts_new = not job or (studio.ASIN_RE.search(text) or studio.DP_RE.search(text)) and job.get("asin") \
        and not job.get("pending")
    if starts_new:
        job = studio.new_job(user)
    if job["busy"]:
        return jsonify(error="Still working on the last request. Wait for it to finish."), 409
    uploads = []
    up = studio.jdir(job) / "uploads"
    for f in request.files.getlist("files"):
        if f and f.mimetype.startswith("image/"):
            up.mkdir(exist_ok=True)
            p = up / f"{len(list(up.iterdir())) + 1:02d}.jpg"
            try:
                studio.Image.open(f.stream).convert("RGB").save(p, quality=92)
                uploads.append(str(p))
            except Exception:
                pass
    job["messages"].append({"role": "user", "type": "text", "text": text,
                            "files": len(uploads)})
    job["busy"] = True
    studio.save(job)
    threading.Thread(target=studio.handle_message, args=(job, text, uploads, selected), daemon=True).start()
    return jsonify(job_id=job["id"])


@app.post("/api/job/<jid>/slot/<int:n>/<action>")
@guarded
def slot_action(jid, n, action):
    job = get_job(jid)
    if not 1 <= n <= len(job["slots"]):
        abort(404)
    s = job["slots"][n - 1]
    if action == "approve":
        s["approved"] = not s.get("approved")
        studio.save(job)
    elif action == "regenerate":
        if job["busy"]:
            return jsonify(error="Still working. Wait for the current step to finish."), 409
        job["busy"] = True

        def run():
            try:
                studio.run_slot(job, s)
            finally:
                job["busy"] = False
                studio.save(job)
        threading.Thread(target=run, daemon=True).start()
    else:
        abort(404)
    return jsonify(ok=True)


@app.get("/api/job/<jid>/zip")
@guarded
def zip_download(jid):
    job = get_job(jid)
    data = studio.zip_bytes(job)
    return Response(data, mimetype="application/zip",
                    headers={"Content-Disposition": f'attachment; filename="{job["sku"]}-CODEX.zip"'})


@app.get("/work/<jid>/<path:name>")
@guarded
def work_file(jid, name):
    get_job(jid)
    base = (studio.WORK / jid).resolve()
    p = (base / name).resolve()
    if base not in p.parents or not p.is_file():
        abort(404)
    return send_file(p)


if __name__ == "__main__":
    studio.load_all()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), threaded=True)
