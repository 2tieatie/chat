from fastapi import APIRouter, UploadFile, File, HTTPException, status, Path
from pydantic import BaseModel
from typing import List

from app.api.models import FileGroup
from common.models import UploadedChunk
from db.helpers import (
    upsert_chunks,
    filename_exists,
    list_files_grouped,
    delete_file_by_id,
)
from utils.reader import read_file_bytes
from utils.utils import text_to_chunks

router = APIRouter(prefix="/files", tags=["files"])


def validate_extension(filename: str) -> None:
    f = filename.lower()
    if not (f.endswith(".pdf") or f.endswith(".txt") or f.endswith(".md")):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {filename}. Allowed: pdf, txt, md",
        )


@router.post("/upload", response_model=List[UploadedChunk])
async def upload_files(files: List[UploadFile] = File(...)) -> List[UploadedChunk]:
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    result: List[UploadedChunk] = []
    for f in files:
        validate_extension(f.filename)
        if await filename_exists(f.filename):
            raise HTTPException(
                status_code=409,
                detail=f"File with filename '{f.filename}' already exists",
            )
        try:
            raw = await f.read()
            text = read_file_bytes(raw, f.filename)
            chunks = text_to_chunks(text, f.filename)
            uploaded = await upsert_chunks(chunks)
            result.extend(uploaded)
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid file (only pdf, txt, md)."
            )

    return result


@router.get("/", response_model=List[FileGroup])
async def get_files_grouped() -> List[FileGroup]:
    data = await list_files_grouped()
    return [FileGroup(**g) for g in data]


@router.delete("/{file_id}", status_code=204)
async def delete_file(file_id: str = Path(..., min_length=1)) -> None:
    await delete_file_by_id(file_id)
