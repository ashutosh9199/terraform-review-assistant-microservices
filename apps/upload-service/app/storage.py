import shutil
import zipfile
from pathlib import Path
from uuid import uuid4

from app.config import config

ALLOWED_EXTENSIONS = {".tf", ".tfvars", ".zip"}
PARSEABLE_EXTENSIONS = {".tf", ".tfvars"}


class UploadError(Exception):
    """Raised for invalid uploads. Carries an HTTP status code for the API layer."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class UploadStore:
    def __init__(self) -> None:
        self.base = config.storage_path
        self.base.mkdir(parents=True, exist_ok=True)

    def _expanded_dir(self, review_id: int) -> Path:
        return self.base / str(review_id) / "expanded"

    def reset_expanded(self, review_id: int) -> Path:
        expanded = self._expanded_dir(review_id)
        if expanded.exists():
            shutil.rmtree(expanded)
        expanded.mkdir(parents=True, exist_ok=True)
        return expanded

    def store(self, review_id: int, files: list[tuple[str, bytes]]) -> list[str]:
        """Validate and expand uploaded files into the review's expanded directory.

        `files` is a list of (filename, content) tuples. ZIP archives are
        safely extracted; individual .tf/.tfvars files are written directly.
        Returns the list of stored relative paths.
        """
        if not files:
            raise UploadError(400, "At least one file is required.")

        for filename, content in files:
            extension = Path(filename).suffix.lower()
            if extension not in ALLOWED_EXTENSIONS:
                raise UploadError(400, "Only .tf, .tfvars, and .zip uploads are supported.")
            if len(content) > config.max_upload_bytes:
                raise UploadError(413, "Upload exceeds configured size limit.")

        expanded = self.reset_expanded(review_id)
        used_names: set[str] = set()
        for filename, content in files:
            extension = Path(filename).suffix.lower()
            if extension == ".zip":
                self._extract_zip(content, expanded)
            else:
                target = expanded / self._unique_name(Path(filename).name, used_names)
                target.write_bytes(content)

        return self.list_relative_paths(review_id)

    def _extract_zip(self, content: bytes, destination: Path) -> None:
        archive_path = destination.parent / f"upload-{uuid4().hex}.zip"
        archive_path.write_bytes(content)
        try:
            with zipfile.ZipFile(archive_path) as archive:
                for member in archive.infolist():
                    member_path = destination / member.filename
                    resolved = member_path.resolve()
                    if not str(resolved).startswith(str(destination.resolve())):
                        raise UploadError(400, "Unsafe ZIP path detected.")
                    if member.file_size > config.max_upload_bytes:
                        raise UploadError(413, "ZIP member exceeds size limit.")
                archive.extractall(destination)
        finally:
            archive_path.unlink(missing_ok=True)

    def list_relative_paths(self, review_id: int) -> list[str]:
        expanded = self._expanded_dir(review_id)
        if not expanded.exists():
            return []
        paths = sorted(
            p for p in expanded.rglob("*")
            if p.is_file() and p.suffix.lower() in PARSEABLE_EXTENSIONS
        )
        return [str(p.relative_to(expanded).as_posix()) for p in paths]

    def read_files(self, review_id: int) -> list[dict[str, str]]:
        expanded = self._expanded_dir(review_id)
        if not expanded.exists():
            return []
        result: list[dict[str, str]] = []
        for relative in self.list_relative_paths(review_id):
            content = (expanded / relative).read_text(encoding="utf-8", errors="replace")
            result.append({"path": relative, "content": content})
        return result

    def _unique_name(self, filename: str, used_names: set[str]) -> str:
        stem = Path(filename).stem or "terraform"
        suffix = Path(filename).suffix or ".tf"
        candidate = f"{stem}{suffix}"
        counter = 1
        while candidate in used_names:
            candidate = f"{stem}-{counter}{suffix}"
            counter += 1
        used_names.add(candidate)
        return candidate
