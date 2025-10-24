import re
from typing import List

from common.dataclasses import Chunk


def text_to_chunks(
    text: str, filename: str, chunk_size_chars: int = 2000, overlap: int = 200
) -> List[Chunk]:
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return []

    chunks: List[Chunk] = []
    start = 0
    idx = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size_chars, length)
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(Chunk(text=chunk_text, chunk_index=idx, filename=filename))
            idx += 1

        if end >= length:
            break

        next_start = start + (chunk_size_chars - overlap)
        if next_start <= start:
            next_start = start + chunk_size_chars

        start = next_start

    return chunks
