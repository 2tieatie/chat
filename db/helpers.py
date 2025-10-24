import uuid

from common.dataclasses import Chunk
from common.models import UploadedChunk, ChunkInfo
from config import logger
from qdrant_client.http.models import SearchParams
import uuid
from utils.embeddings import embed_texts
from typing import Dict, List, Optional
from qdrant_client.http import models as rest
from config import Config
from db.db import qdrant


async def ensure_collection(
    collection_name: str,
    vector_size: int,
    distance: rest.Distance = rest.Distance.COSINE,
) -> None:
    exists = await qdrant.collection_exists(collection_name)
    if exists:
        logger.debug("Qdrant collection '%s' exists", collection_name)
        return

    logger.info("Creating Qdrant collection '%s'", collection_name)
    await qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=rest.VectorParams(size=vector_size, distance=distance),
        on_disk_payload=True,
    )


async def upsert_points_batch(
    collection_name: str,
    points: List[rest.PointStruct],
):
    await qdrant.upsert(
        collection_name=collection_name,
        points=points,
        wait=True,
    )


async def search_vectors(
    collection_name: str,
    vector: List[float],
    limit: int = 5,
    with_payload: bool = True,
):
    return await qdrant.query_points(
        collection_name=collection_name,
        query=vector,
        limit=limit,
        with_payload=with_payload,
        with_vectors=False,
        search_params=SearchParams(exact=False),
    )


async def upsert_chunks(
    chunks: List[Chunk], collection_name: str = Config.qdrant_collection
) -> List[UploadedChunk]:
    if not chunks:
        return []

    texts = [c.text for c in chunks]
    vectors = await embed_texts(texts)

    uploaded: List[UploadedChunk] = []
    points_batch: List[rest.PointStruct] = []
    meta_batch: List[UploadedChunk] = []

    file_id = str(uuid.uuid4())

    for chunk, vec in zip(chunks, vectors):
        pid = str(uuid.uuid4())
        payload = {
            "chunk_index": chunk.chunk_index,
            "filename": chunk.filename,
            "text": chunk.text,
            "file_id": file_id,
        }

        points_batch.append(rest.PointStruct(id=pid, vector=vec, payload=payload))
        meta_batch.append(
            UploadedChunk(
                id=pid,
                filename=chunk.filename,
                chunk_index=chunk.chunk_index,
                file_id=file_id,
            )
        )

        if len(points_batch) >= Config.batch_size:
            try:
                await upsert_points_batch(
                    collection_name=collection_name, points=points_batch
                )
                logger.info("Upserted batch of %d points", len(points_batch))
                uploaded.extend(meta_batch)
            except Exception as e:
                logger.exception(
                    "Failed to upsert batch (%d points): %s", len(points_batch), e
                )
            finally:
                points_batch.clear()
                meta_batch.clear()

    if points_batch:
        try:
            await upsert_points_batch(
                collection_name=collection_name, points=points_batch
            )
            logger.info("Upserted final batch of %d points", len(points_batch))
            uploaded.extend(meta_batch)
        except Exception as e:
            logger.exception(
                "Failed to upsert final batch (%d points): %s", len(points_batch), e
            )

    return uploaded


async def filename_exists(
    filename: str, collection_name: str = Config.qdrant_collection
) -> bool:
    search_result = await qdrant.scroll(
        collection_name=collection_name,
        scroll_filter=rest.Filter(
            must=[
                rest.FieldCondition(
                    key="filename",
                    match=rest.MatchValue(value=filename),
                )
            ]
        ),
        limit=1,
        with_payload=False,
    )

    points, _ = search_result
    return len(points) > 0


async def list_files_grouped(
    collection_name: str = Config.qdrant_collection,
) -> List[dict]:
    files: Dict[str, dict] = {}
    next_offset: Optional[str] = None

    while True:
        points, next_offset = await qdrant.scroll(
            collection_name=collection_name,
            with_payload=True,
            limit=1000,
            offset=next_offset,
        )
        for p in points:
            payload = (p.payload or {}).copy()
            file_id = payload.get("file_id")
            filename = payload.get("filename")
            if not file_id or filename is None:
                continue

            payload.pop("filename", None)
            payload.pop("file_id", None)

            if file_id not in files:
                files[file_id] = {
                    "file_id": file_id,
                    "filename": filename,
                    "chunks": [],
                }

            files[file_id]["chunks"].append(
                ChunkInfo(text=payload["text"], chunk_index=payload["chunk_index"])
            )

        if not next_offset:
            break

    for v in files.values():
        v["chunks"].sort(key=lambda c: getattr(c, "chunk_index", 0))
    return list(files.values())


async def delete_file_by_id(
    file_id: str, collection_name: str = Config.qdrant_collection
) -> None:
    await qdrant.delete(
        collection_name=collection_name,
        points_selector=rest.Filter(
            must=[
                rest.FieldCondition(key="file_id", match=rest.MatchValue(value=file_id))
            ]
        ),
        wait=True,
    )
