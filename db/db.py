from qdrant_client import AsyncQdrantClient

from config import Config

qdrant = AsyncQdrantClient(url=Config.qdrant_url, prefer_grpc=False)
