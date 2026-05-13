from dotenv import load_dotenv
load_dotenv()

import os
import hashlib
import json
import shutil

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator
from agent.rag_agent import answer
from ingestion.loader import load_document
from ingestion.chunker import chunk_documents
from ingestion.vector_store import store_vector
from ingestion.extractor import extract_triplets
from ingestion.graph_store import store_graph
from config.settings import DATA_FOLDER, METADATA_FILE

app = FastAPI(
    title="RAG Vector Graph API",
    description="Hybrid RAG system combining vector search, knowledge graph, and web search",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str
    use_web_search: bool = False

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("query must not be empty")
        if len(v) > 2000:
            raise ValueError("query too long (max 2000 chars)")
        return v


class ChatResponse(BaseModel):
    query: str
    response: str
    used_web_search: bool = False


ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}


def _load_metadata() -> list:
    if not os.path.exists(METADATA_FILE):
        return []
    with open(METADATA_FILE, "r") as f:
        return json.load(f)


def _save_metadata(data: list):
    os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)
    with open(METADATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _file_hash(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}"
        )

    os.makedirs(DATA_FOLDER, exist_ok=True)
    save_path = os.path.join(DATA_FOLDER, file.filename)

    try:
        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    file_hash = _file_hash(save_path)
    processed = _load_metadata()
    if file_hash in processed:
        return {
            "filename": file.filename,
            "status": "skipped",
            "message": "Document already ingested.",
            "chunks_stored": 0,
            "graph_relationships": 0,
        }

    try:
        docs = load_document(save_path)
        chunks = chunk_documents(docs)

        vec_ok = store_vector(chunks)
        if not vec_ok:
            raise HTTPException(status_code=500, detail="Failed to store document in vector DB.")

        graph_count = 0
        for chunk in chunks:
            triplets = extract_triplets(chunk.page_content)
            graph_count += store_graph(triplets)

        processed.append(file_hash)
        _save_metadata(processed)

        return {
            "filename": file.filename,
            "status": "success",
            "message": "Document ingested successfully.",
            "chunks_stored": len(chunks),
            "graph_relationships": graph_count,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        result = answer(req.query, use_web_search=req.use_web_search)
        return ChatResponse(query=req.query, response=result, used_web_search=req.use_web_search)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Serve frontend — must be LAST (catches remaining routes)
_FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
if os.path.isdir(_FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=_FRONTEND_DIR, html=True), name="frontend")
