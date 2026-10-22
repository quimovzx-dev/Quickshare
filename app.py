from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
import secrets
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from datetime import datetime
import shutil
import mimetypes

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Configure these locally before exposing the app on your network.
USER = os.environ.get("QUICKSHARE_USER", "quim")
PASSWORD = os.environ.get("QUICKSHARE_PASSWORD", "")
MAX_UPLOAD_BYTES = 100 * 1024 * 1024
security = HTTPBasic()
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    valid_user = secrets.compare_digest(credentials.username.encode(), USER.encode())
    valid_password = secrets.compare_digest(credentials.password.encode(), PASSWORD.encode())
    if not PASSWORD or not (valid_user and valid_password):
        raise HTTPException(status_code=401, detail="Configure QUICKSHARE_PASSWORD and sign in.", headers={"WWW-Authenticate": "Basic"})
app = FastAPI(title="QuickShare", dependencies=[Depends(authenticate)])

@app.get("/static/{asset}")
def static_asset(asset: str):
    if asset not in {"app.js", "style.css"}:
        raise HTTPException(status_code=404)
    return FileResponse(BASE_DIR / asset)

@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse(BASE_DIR / "index.html")

@app.get("/api/files")
def list_files():
    items = []
    for path in sorted(UPLOAD_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if path.is_file():
            stat = path.stat()
            items.append({
                "name": path.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
    return items

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    safe_name = Path(file.filename or "unnamed_file").name
    if not safe_name:
        raise HTTPException(status_code=400, detail="Invalid filename")

    destination = UPLOAD_DIR / safe_name

    # Avoid overwriting existing files.
    if destination.exists():
        stem, suffix = destination.stem, destination.suffix
        counter = 1
        while destination.exists():
            destination = UPLOAD_DIR / f"{stem}_{counter}{suffix}"
            counter += 1

    # Exclusive creation prevents a concurrent upload from overwriting a file.
    try:
        with destination.open("xb") as buffer:
            size = 0
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail="File exceeds 100 MiB limit")
                buffer.write(chunk)
    except FileExistsError:
        raise HTTPException(status_code=409, detail="Filename already exists. Retry upload.")
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()

    return {"message": "Uploaded successfully", "name": destination.name}

@app.get("/api/download/{filename}")
def download_file(filename: str):
    safe_name = Path(filename).name
    path = UPLOAD_DIR / safe_name
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path,
        filename=path.name,
        media_type=mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    )

@app.delete("/api/files/{filename}")
def delete_file(filename: str):
    safe_name = Path(filename).name
    path = UPLOAD_DIR / safe_name
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    path.unlink()
    return {"message": "Deleted successfully"}
