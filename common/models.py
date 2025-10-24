from typing import List

from pydantic import BaseModel


class EmbeddingsContext(BaseModel):
    text: str
    chunk_index: int
    filename: str
    score: float


class LLMResponse(BaseModel):
    text: str
    context: List[EmbeddingsContext]


class UploadedChunk(BaseModel):
    id: str
    filename: str
    chunk_index: int
    file_id: str


class ChunkInfo(BaseModel):
    chunk_index: int
    text: str
