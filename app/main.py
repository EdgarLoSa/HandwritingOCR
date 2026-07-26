from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.database.init_db import init_db
from app.queue.manager import job_queue
from app.queue.worker import worker_loop

configure_logging()
init_db()
job_queue.start_worker(worker_loop)

app = FastAPI(title="HandwritingOCR")

app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")
app.include_router(api_router)
