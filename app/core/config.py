from pathlib import Path


class Settings:
    def __init__(self) -> None:
        self.root_dir = Path(__file__).resolve().parents[2]
        self.app_dir = self.root_dir / "app"
        self.templates_dir = self.root_dir / "templates"
        self.static_dir = self.root_dir / "static"
        self.uploads_dir = self.root_dir / "uploads"
        self.jobs_dir = self.root_dir / "jobs"
        self.logs_dir = self.root_dir / "logs"
        self.database_dir = self.root_dir / "database"
        self.database_file = self.database_dir / "ocr.sqlite"
        self.host = "0.0.0.0"
        self.port = 8000
        self.ocr_provider = "ollama"
        self.ollama_base_url = "http://localhost:11434/v1"
        self.ollama_model = "qwen2.5vl:7b"
        self.ollama_timeout_seconds = 180
        self.ollama_max_output_tokens = 4096
        self.ollama_temperature = 0.0
        self.allowed_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
        self.max_upload_size = 5 * 1024 * 1024 * 1024

        for folder in (
            self.uploads_dir,
            self.jobs_dir,
            self.logs_dir,
            self.database_dir,
            self.static_dir,
            self.templates_dir,
        ):
            folder.mkdir(parents=True, exist_ok=True)


settings = Settings()
