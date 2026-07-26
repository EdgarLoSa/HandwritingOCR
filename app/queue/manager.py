from __future__ import annotations

import queue
import threading
from dataclasses import dataclass
from pathlib import Path

from app.core.config import settings


@dataclass(frozen=True)
class JobTask:
    job_uuid: str
    filename: str
    input_path: Path


class JobQueue:
    def __init__(self) -> None:
        self._queue: queue.Queue[JobTask] = queue.Queue()
        self._started = False
        self._lock = threading.Lock()

    def start_worker(self, worker_fn) -> None:
        with self._lock:
            if self._started:
                return
            thread = threading.Thread(target=worker_fn, daemon=True, name="ocr-worker")
            thread.start()
            self._started = True

    def submit(self, task: JobTask) -> None:
        self._queue.put(task)

    def get(self, timeout: float | None = None) -> JobTask:
        return self._queue.get(timeout=timeout)

    def task_done(self) -> None:
        self._queue.task_done()


job_queue = JobQueue()

