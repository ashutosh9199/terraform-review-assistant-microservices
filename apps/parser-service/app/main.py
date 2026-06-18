import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.parser import TerraformParserService

app = FastAPI(
    title="Terraform Parser Service",
    version="0.1.0",
    description="Parses Terraform HCL into a structured inventory and dependency graph.",
)

parser = TerraformParserService()


class SourceFile(BaseModel):
    path: str
    content: str


class ParseRequest(BaseModel):
    files: list[SourceFile]


@app.get("/healthz", tags=["system"])
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "parser-service"}


@app.post("/parse", tags=["parser"])
def parse(request: ParseRequest) -> dict[str, object]:
    if not request.files:
        raise HTTPException(status_code=400, detail="No Terraform files supplied.")
    with tempfile.TemporaryDirectory(prefix="tf-parse-") as tmp:
        root = Path(tmp)
        for source in request.files:
            relative = Path(source.path)
            if relative.is_absolute() or ".." in relative.parts:
                raise HTTPException(status_code=400, detail=f"Unsafe file path: {source.path}")
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source.content, encoding="utf-8")
        inventory, graph = parser.parse_project(root)
    return {"inventory": inventory, "dependency_graph": graph}
