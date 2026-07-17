from pathlib import Path

ROOT = Path(__file__).parent

UPLOAD_FOLDER = ROOT / "uploads"
JOB_FOLDER = ROOT / "jobs"
DATABASE_FOLDER = ROOT / "database"
LOG_FOLDER = ROOT / "logs"

DATABASE_FILE = DATABASE_FOLDER / "ocr.sqlite"

HOST = "0.0.0.0"
PORT = 8000

MAX_UPLOAD_SIZE = 1024 * 1024 * 1024 * 5   # 5 GB

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tiff",
    ".webp"
}

UPLOAD_FOLDER.mkdir(exist_ok=True)
JOB_FOLDER.mkdir(exist_ok=True)
DATABASE_FOLDER.mkdir(exist_ok=True)
LOG_FOLDER.mkdir(exist_ok=True)