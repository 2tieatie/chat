from typing import List

from langchain_openai import OpenAIEmbeddings

from config import Config
from config import EMBEDDING_MODEL

__client = OpenAIEmbeddings(model=EMBEDDING_MODEL)


async def embed_texts(texts: List[str]) -> List[List[float]]:
    vectors: List[List[float]] = []

    for i in range(0, len(texts), Config.batch_size):
        batch = texts[i : i + Config.batch_size]
        batch_vecs = await __client.aembed_documents(batch)
        vectors.extend(batch_vecs)

    return vectors
