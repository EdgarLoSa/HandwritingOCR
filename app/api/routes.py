from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import SessionLocal
from app.models.job import Job
from app.queue.manager import JobTask, job_queue

router = APIRouter()
templates = Jinja2Templates(directory=str(settings.templates_dir))


def _job_dir(job_id: str) -> Path:
    folder = settings.jobs_dir / job_id
    folder.mkdir(parents=True, exist_ok=True)
    for name in ("input", "output", "processed", "logs"):
        (folder / name).mkdir(exist_ok=True)
    return folder


def _create_job_record(db: Session, job_id: str, filename: str, total_files: int) -> Job:
    job = Job(
        uuid=job_id,
        filename=filename,
        status="queued",
        progress=0,
        total=total_files,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def _serialize_job(job: Job | dict[str, str]) -> dict[str, str | int]:
    if isinstance(job, dict):
        return {
            "uuid": job["uuid"],
            "filename": job["filename"],
            "status": job.get("status", "queued"),
            "progress": job.get("progress", 0),
            "total": job.get("total", 1),
        }
    return {
        "uuid": job.uuid,
        "filename": job.filename,
        "status": job.status,
        "progress": job.progress,
        "total": job.total,
    }


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    db = SessionLocal()
    jobs = db.query(Job).order_by(Job.created_at.desc()).limit(10).all()
    db.close()
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "jobs": jobs,
            "settings": settings,
        },
    )


@router.post("/upload")
async def upload_files(
    request: Request,
    files: list[UploadFile] = File(...),
    title: str = Form(default=""),
):
    if not files:
        raise HTTPException(status_code=400, detail="Please upload at least one image.")

    db = SessionLocal()
    created_jobs: list[dict[str, str]] = []

    try:
        for upload in files:
            extension = Path(upload.filename or "").suffix.lower()
            if extension not in settings.allowed_extensions:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {upload.filename}")

            job_id = str(uuid4())
            job_folder = _job_dir(job_id)
            input_path = job_folder / "input" / f"source{extension}"
            content = await upload.read()
            input_path.write_bytes(content)
            _create_job_record(db, job_id, upload.filename or "upload", len(files))
            job_queue.submit(JobTask(job_uuid=job_id, filename=upload.filename or "upload", input_path=input_path))
            created_jobs.append(
                {
                    "uuid": job_id,
                    "filename": upload.filename or "upload",
                    "status": "queued",
                    "progress": 0,
                    "total": len(files),
                    "title": title.strip(),
                }
            )
    except HTTPException:
        db.rollback()
        raise
    except OSError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not store uploaded file.") from exc
    finally:
        db.close()

    return templates.TemplateResponse(
        request,
        "progress.html",
        {
            "jobs": [_serialize_job(job) for job in created_jobs],
            "message": "Files uploaded successfully.",
        },
    )


@router.get("/jobs/{job_uuid}", response_class=HTMLResponse)
def job_status(request: Request, job_uuid: str):
    db = SessionLocal()
    job = db.query(Job).filter(Job.uuid == job_uuid).first()
    db.close()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    return templates.TemplateResponse(
        request,
        "progress.html",
        {
            "jobs": [_serialize_job(job)],
            "message": "Job details loaded.",
        },
    )


@router.get("/api/jobs/{job_uuid}")
def job_status_json(job_uuid: str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.uuid == job_uuid).first()
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found.")
        return _serialize_job(job)
    finally:
        db.close()
