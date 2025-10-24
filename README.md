# RAG Chat Server — Setup Guide

This repo contains a FastAPI backend with Qdrant as the vector database.

- Python: **3.12**
- Vector DB: **Qdrant**
- Run modes: local (venv) or **Docker Compose** (API + Qdrant)

---

## 📌 .env configuration example

Create `.env` from this template:

```ini
# === API ===
APP_HOST=0.0.0.0
APP_PORT=8000

# Comma-separated list
CORS_ORIGINS=http://localhost:5173

# === Qdrant ===
# For local host run:
# QDRANT_URL=http://localhost:6333
# For docker-compose networking:
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION=docs
VECTOR_SIZE=1536
BATCH_SIZE=64

# === Embeddings / LLM ===
OPENAI_API_KEY=replace_me
```

---

## 🐳 docker-compose.yml (API + Qdrant stack)

```yaml
version: "3.9"

services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:6333/collections"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: api
    env_file:
      - .env
    ports:
      - "8000:8000"
    depends_on:
      qdrant:
        condition: service_healthy
    command: uvicorn app.app:app --host 0.0.0.0 --port 8000

volumes:
  qdrant_storage:
```

---

## ✅ Quick Start

### Clone the project
```bash
git clone <your-repo-url>.git
cd <your-project>
```

Copy `.env`:
```bash
cp .env.example .env
```

---

## 🧪 Local setup (Unix/macOS & Linux)

### Install Python 3.12
```bash
python3.12 --version
```

### Create & activate virtual environment
```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Run server
```bash
uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🧩 Local setup (Windows)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload
```

If PowerShell blocks activation:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🚀 Run Everything in Docker (recommended)

```bash
docker compose up --build
```

UI:
- Swagger UI → http://localhost:8000/docs
- Qdrant REST → http://localhost:6333

Logs:
```bash
docker compose logs -f api
docker compose logs -f qdrant
```

---

## 🔍 Smoke test script

```python
import asyncio, httpx
from qdrant_client import AsyncQdrantClient

async def smoke():
    transport = httpx.AsyncHTTPTransport(http2=False, retries=2)
    client = AsyncQdrantClient(url="http://localhost:6333", prefer_grpc=False, timeout=60, transport=transport)
    print(await client.get_collections())

asyncio.run(smoke())
```

---

## 🎯 Notes

- Set correct `VECTOR_SIZE` to match your embeddings model.
- When using Docker Compose, ensure:
  ```
  QDRANT_URL=http://qdrant:6333
  ```
- Qdrant collection auto‑initialized on app startup.

---

