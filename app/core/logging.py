import logging
from logging.handlers import RotatingFileHandler

from app.core.config import settings


def configure_logging() -> None:
    log_file = settings.logs_dir / "app.log"
    handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handler.setFormatter(formatter)

    root = logging.getLogger()
    if not root.handlers:
        root.setLevel(logging.INFO)
        root.addHandler(handler)

