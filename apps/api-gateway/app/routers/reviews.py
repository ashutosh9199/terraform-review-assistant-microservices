import base64
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, get_db
from app.dependencies import get_current_user
from app.models.domain import Finding, Project, Report, ReviewJob, User
from app.schemas import ReviewRead
from app.services import clients
from app.services.audit import write_audit
from app.services.clients import ServiceError
from app.services.orchestrator import ReviewOrchestrator

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


async def run_review_background(review_id: int) -> None:
    db = SessionLocal()
    try:
        await ReviewOrchestrator(db).run(review_id)
    finally:
        db.close()


@router.post("/upload", response_model=ReviewRead)
async def upload_review(
    background_tasks: BackgroundTasks,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    project_id: int,
    files: list[UploadFile] | None = File(default=None),
    file: UploadFile | None = File(default=None),
) -> ReviewRead:
    project = db.get(Project, project_id)
    if not project or project.created_by != user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    uploads = files or ([file] if file else [])
    if not uploads:
        raise HTTPException(status_code=400, detail="At least one file is required.")
    payload: list[tuple[str, bytes, str]] = []
    for upload in uploads:
        content = await upload.read()
        payload.append((upload.filename or "upload.tf", content, upload.content_type or "application/octet-stream"))
    display_name = uploads[0].filename or "terraform-upload"
    if len(uploads) > 1:
        display_name = f"{len(uploads)} Terraform files"
    job = ReviewJob(
        project_id=project.id,
        original_filename=display_name,
        storage_path="pending",
        created_by=user.id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    try:
        await clients.store_upload(job.id, payload)
    except ServiceError as exc:
        db.delete(job)
        db.commit()
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    job.storage_path = f"upload-service://{job.id}"
    db.commit()
    write_audit(
        db,
        "review.uploaded",
        actor_user_id=user.id,
        target=str(job.id),
        metadata={"file": job.original_filename, "file_count": len(uploads)},
    )
    background_tasks.add_task(run_review_background, job.id)
    return _read_review(db, job.id)


@router.get("/{review_id}", response_model=ReviewRead)
def get_review(
    review_id: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ReviewRead:
    return _read_review(db, review_id, user.id)


@router.get("/{review_id}/report.json")
def get_json_report(
    review_id: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    _authorize_review(db, review_id, user.id)
    report = db.scalar(select(Report).where(Report.review_job_id == review_id, Report.format == "json"))
    if not report:
        raise HTTPException(status_code=404, detail="Report not ready")
    return Response(report.content, media_type="application/json")


@router.get("/{review_id}/report.html", response_class=HTMLResponse)
def get_html_report(
    review_id: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> str:
    _authorize_review(db, review_id, user.id)
    report = db.scalar(select(Report).where(Report.review_job_id == review_id, Report.format == "html"))
    if not report:
        raise HTTPException(status_code=404, detail="Report not ready")
    return report.content


@router.get("/{review_id}/report.pdf")
def get_pdf_report(
    review_id: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    _authorize_review(db, review_id, user.id)
    report = db.scalar(select(Report).where(Report.review_job_id == review_id, Report.format == "pdf"))
    if not report:
        raise HTTPException(status_code=404, detail="Report not ready")
    return Response(
        base64.b64decode(report.content),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="terraform-review-{review_id}.pdf"'},
    )


def _authorize_review(db: Session, review_id: int, user_id: int) -> ReviewJob:
    job = db.get(ReviewJob, review_id)
    if not job:
        raise HTTPException(status_code=404, detail="Review not found")
    project = db.get(Project, job.project_id)
    if not project or project.created_by != user_id:
        raise HTTPException(status_code=404, detail="Review not found")
    return job


def _read_review(db: Session, review_id: int, user_id: int | None = None) -> ReviewRead:
    job = db.get(ReviewJob, review_id)
    if not job:
        raise HTTPException(status_code=404, detail="Review not found")
    if user_id is not None:
        _authorize_review(db, review_id, user_id)
    findings = list(db.scalars(select(Finding).where(Finding.review_job_id == review_id)))
    return ReviewRead(
        id=job.id,
        project_id=job.project_id,
        status=job.status,
        original_filename=job.original_filename,
        created_at=job.created_at,
        completed_at=job.completed_at,
        error_message=job.error_message,
        inventory=job.inventory,
        dependency_graph=job.dependency_graph,
        scorecard=job.scorecard,
        findings=findings,
    )
