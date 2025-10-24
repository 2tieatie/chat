import logging
import os

from dotenv import load_dotenv

load_dotenv()

with open("system_prompt.txt", "r") as f:
    SYSTEM_PROMPT = f.read()

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    "yourapikeyhere",
)
QDRANT_URL = os.getenv("QDRANT_URL", "https://test-task-qdrant.fly.dev:443")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "docs")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4.1-nano")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))
VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", "1536"))
TOP_K = int(os.getenv("TOP_K", "5"))
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "2048"))

API_PREFIX = "/api"

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("async-qdrant-langchain")


class Config:
    openai_api_key: str = OPENAI_API_KEY
    qdrant_url: str = QDRANT_URL
    qdrant_collection: str = QDRANT_COLLECTION
    embedding_model: str = EMBEDDING_MODEL
    llm_model: str = LLM_MODEL
    batch_size: int = BATCH_SIZE
    vector_size: int = VECTOR_SIZE
    top_k: int = TOP_K
    system_prompt: str = SYSTEM_PROMPT
    api_prefix: str = API_PREFIX
    max_message_length: int = MAX_MESSAGE_LENGTH
