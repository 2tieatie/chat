from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    chunk_index: int
    filename: str
