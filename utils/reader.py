import io
from typing import Tuple

import PyPDF2


def read_pdf_bytes(file_bytes: bytes) -> str:
    texts = []
    with io.BytesIO(file_bytes) as buffer:
        reader = PyPDF2.PdfReader(buffer)
        for page in reader.pages:
            texts.append(page.extract_text() or "")
    return "\n".join(texts)


def read_text_bytes(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")


def read_file_bytes(file_bytes: bytes, filename: str) -> str:
    filename = filename.lower()

    if filename.endswith(".pdf"):
        return read_pdf_bytes(file_bytes)

    if filename.endswith((".txt", ".md")):
        return read_text_bytes(file_bytes)

    raise ValueError(f"Unsupported file type for {filename}")
