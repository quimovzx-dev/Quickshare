from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from datetime import datetime
import shutil
import mimetypes

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="QuickShare")

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")

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

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

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
