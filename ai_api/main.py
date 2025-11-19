from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os, aiofiles, tempfile
from pathlib import Path

def _load_env():
    p = Path(".env")
    if p.exists():
        for line in p.read_text().splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if "=" in s:
                k, v = s.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

_load_env()

from ai_api.ai_analyzer import analyze_reports
from ai_api.email_service import send_email

app = FastAPI()

# -------------------------
# Static files (HTML/CSS/JS) serve karna
# -------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join("static", "index.html"))

# -------------------------
# AI Analyze Endpoint
# -------------------------
@app.post("/analyze")
async def analyze(
    branch: str = Form(None),
    commit: str = Form(None),
    recipients: str = Form(None),
    files: list[UploadFile] = File(None),
    files2: list[UploadFile] = File(None),
):
    saved_paths = []

    all_uploads = []
    for group in (files or []), (files2 or []):
        for f in group:
            fd, path = tempfile.mkstemp(suffix=f.filename)
            os.close(fd)
            async with aiofiles.open(path, "wb") as out:
                await out.write(await f.read())
            saved_paths.append(path)

    ai_output = await analyze_reports(saved_paths, branch, commit)

    dest = (
        recipients.split(",") if recipients else [e.strip() for e in (os.getenv("DEST_EMAIL", "")).split(",") if e.strip()]
    )
    send_email("AI Performance Report", ai_output, dest, attachments=saved_paths)

    return JSONResponse({"status": "ok", "ai": ai_output})

# -------------------------
# Run locally
# -------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ai_api.main:app", host="127.0.0.1", port=8000, reload=True)
