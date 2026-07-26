from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from app.core.config import settings
from app.database.session import SessionLocal
from app.export.writer import write_docx_export, write_text_export
from app.ocr.ollama_engine import transcribe_with_ollama
from app.models.job import Job
from app.ocr.tesseract_engine import choose_best_result
from app.preprocessing.pipeline import build_variants
from app.queue.manager import job_queue

logger = logging.getLogger(__name__)


def _update_job(job_uuid: str, **fields) -> None:
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.uuid == job_uuid).first()
        if job is None:
            return
        for key, value in fields.items():
            setattr(job, key, value)
        db.commit()
    finally:
        db.close()


def _process_job(job_uuid: str, filename: str, input_path: Path) -> None:
    _update_job(job_uuid, status="processing", progress=5)
    job_dir = input_path.parent.parent
    output_dir = job_dir / "output"
    processed_dir = job_dir / "processed"

    with tempfile.TemporaryDirectory(prefix=f"ocr-{job_uuid}-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        best_text = ""
        best_conf = -1.0
        best_label = "original"
        engine_used = settings.ocr_provider

        if settings.ocr_provider == "ollama":
            try:
                _update_job(job_uuid, progress=20)
                best_text = transcribe_with_ollama(input_path)
                best_label = "ollama"
                best_conf = 100.0 if best_text else 0.0
                if not best_text:
                    raise RuntimeError("Ollama returned an empty transcription.")
            except Exception:
                logger.exception("Ollama OCR failed for job %s, falling back to Tesseract", job_uuid)
                engine_used = "tesseract-fallback"

        if not best_text:
            variants = build_variants(input_path, temp_dir / "variants")
            _update_job(job_uuid, progress=20)

            for index, variant in enumerate(variants, start=1):
                candidate = choose_best_result(variant.path, temp_dir / f"tess_{variant.label}", variant.label)
                if candidate.confidence > best_conf and candidate.text.strip():
                    best_text = candidate.text.strip()
                    best_conf = candidate.confidence
                    best_label = candidate.label
                progress = 20 + int((index / max(len(variants), 1)) * 60)
                _update_job(job_uuid, progress=progress)

            if not best_text:
                raise RuntimeError("Tesseract produced no text.")

        _update_job(job_uuid, progress=80)
        text_path = write_text_export(output_dir, filename, best_text)
        docx_path = write_docx_export(output_dir, filename, best_text)
        processed_marker = processed_dir / "complete.txt"
        processed_marker.write_text(
            f"Engine: {engine_used}\nBest variant: {best_label}\nConfidence: {best_conf:.2f}\nText file: {text_path.name}\nDocx file: {docx_path.name}\n",
            encoding="utf-8",
        )

    _update_job(job_uuid, status="completed", progress=100)


def worker_loop() -> None:
    logger.info("OCR worker started")
    while True:
        task = job_queue.get()
        try:
            _process_job(task.job_uuid, task.filename, task.input_path)
        except Exception:
            logger.exception("Failed to process job %s", task.job_uuid)
            _update_job(task.job_uuid, status="failed", progress=0)
        finally:
            job_queue.task_done()
