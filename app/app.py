from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.init import api_router
from config import Config
from db.db import qdrant
from db.helpers import ensure_collection
from qdrant_client.http import models as rest


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_collection(
        collection_name=Config.qdrant_collection, vector_size=Config.vector_size
    )
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://ui-chat-five.vercel.app", "https://ui-chat-five.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
