from fastapi import FastAPI, File, HTTPException, UploadFile

from app.storage import UploadError, UploadStore

app = FastAPI(
    title="Upload Service",
    version="0.1.0",
    description="Validates, stores, and expands uploaded Terraform projects.",
)

store = UploadStore()


@app.get("/healthz", tags=["system"])
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "upload-service"}


@app.post("/uploads/{review_id}", tags=["uploads"])
async def store_upload(
    review_id: int,
    files: list[UploadFile] = File(...),
) -> dict[str, object]:
    payload: list[tuple[str, bytes]] = []
    for upload in files:
        content = await upload.read()
        payload.append((upload.filename or "upload.tf", content))
    try:
        stored = store.store(review_id, payload)
    except UploadError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    return {"review_id": review_id, "file_count": len(stored), "files": stored}


@app.get("/uploads/{review_id}/files", tags=["uploads"])
def get_files(review_id: int) -> dict[str, object]:
    files = store.read_files(review_id)
    if not files:
        raise HTTPException(status_code=404, detail="No stored Terraform files for this review.")
    return {"review_id": review_id, "files": files}
