from typing import List, Optional

from langchain_core.messages import AnyMessage
from pydantic import BaseModel

from common.models import ChunkInfo


class Chat(BaseModel):
    user_id: Optional[str] = None
    messages: List[AnyMessage]


class QueryPayload(BaseModel):
    user_id: str
    message: str


class HealthResponse(BaseModel):
    status: str


class FileGroup(BaseModel):
    file_id: str
    filename: str
    chunks: List[ChunkInfo]
