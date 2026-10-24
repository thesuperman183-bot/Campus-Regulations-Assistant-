import os
import time
import json
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse

from app.config import (
    GEMMA_MODEL,
    EMBED_MODEL_NAME,
    TOP_K,
    DEMO_MODE,
)
from app.schemas import (
    QueryRequest,
    QueryResponse,
    ChunkMetadata,
    DocumentIngestResponse,
    HealthResponse,
    ClearResponse,
    LatencyMetrics,
    FeedbackRequest,
    FeedbackResponse,
)
from app.ingestion import read_pdf, split_into_chunks, SAMPLE_PAGES
from app.retriever import knowledge_base
from app.generator import answer_question, answer_question_stream, get_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes the knowledge base with the starter sample regulations on startup."""
    if knowledge_base.total_chunks() == 0:
        sample_doc_name = "SSIT CS 101 Regulations & Syllabus"
        sample_chunks = split_into_chunks(SAMPLE_PAGES, document_name=sample_doc_name)
        knowledge_base.add_chunks(sample_chunks)
        print(f"[Startup] Preloaded {len(sample_chunks)} chunks from '{sample_doc_name}'.")
    yield


app = FastAPI(
    title="SSIT Campus Regulations Assistant API",
    description="RAG backend powered by Gemma 4 and Sentence Transformers for campus regulations.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health_check():
    """Returns backend status, configured model, and knowledge base stats."""
    _, is_demo = get_client()
    active_model = os.environ.get("GEMMA_MODEL", GEMMA_MODEL).strip() or "gemma-4-26b-a4b-it"
    return HealthResponse(
        status="healthy",
        demo_mode=is_demo,
        gemma_model=active_model,
        embed_model=EMBED_MODEL_NAME,
        total_chunks=knowledge_base.total_chunks(),
        indexed_documents=knowledge_base.list_documents(),
    )


@app.post("/api/query", response_model=QueryResponse)
def query_campus_regulations(req: QueryRequest):
    """
    Retrieves the most relevant passages for the user's question,
    generates a grounded answer citing document names and page numbers.
    Includes measured latency metrics.
    """
    t_start = time.perf_counter()
    k = req.top_k or TOP_K
    retrieved = knowledge_base.retrieve(req.question, top_k=k)
    t_retrieval = time.perf_counter()
    retrieval_ms = (t_retrieval - t_start) * 1000

    answer_text, is_demo = answer_question(req.question, retrieved)
    t_end = time.perf_counter()
    total_ms = (t_end - t_start) * 1000

    sources = [
        ChunkMetadata(
            document=c.get("document", "Unknown Document"),
            page=c.get("page", 1),
            text=c.get("text", ""),
            score=c.get("score"),
        )
        for c in retrieved
    ]

    return QueryResponse(
        question=req.question,
        answer=answer_text,
        sources=sources,
        demo_mode=is_demo,
        latency_ms=LatencyMetrics(
            retrieval_ms=round(retrieval_ms, 2),
            total_ms=round(total_ms, 2),
        ),
    )


@app.post("/api/query/stream")
def query_campus_regulations_stream(req: QueryRequest):
    """
    Server-Sent Events (SSE) streaming endpoint for live answer generation.
    Sends retrieved sources immediately, then streams tokens as Gemma generates them,
    drastically reducing perceived response latency.
    """
    t_start = time.perf_counter()
    k = req.top_k or TOP_K
    retrieved = knowledge_base.retrieve(req.question, top_k=k)
    t_retrieval = time.perf_counter()
    retrieval_ms = round((t_retrieval - t_start) * 1000, 2)

    sources = [
        {
            "document": c.get("document", "Unknown Document"),
            "page": c.get("page", 1),
            "text": c.get("text", ""),
            "score": c.get("score"),
        }
        for c in retrieved
    ]

    stream_gen, is_demo = answer_question_stream(req.question, retrieved)

    def event_generator():
        # Event 1: Immediately send retrieved sources & retrieval latency
        sources_event = {
            "type": "sources",
            "sources": sources,
            "demo_mode": is_demo,
            "latency_ms": {"retrieval_ms": retrieval_ms},
        }
        yield f"data: {json.dumps(sources_event)}\n\n"

        first_token = True
        first_token_ms = None

        # Event 2...N: Stream tokens as Gemma generates them
        try:
            for token in stream_gen:
                if first_token:
                    first_token_ms = round((time.perf_counter() - t_start) * 1000, 2)
                    first_token = False
                token_event = {"type": "token", "token": token}
                yield f"data: {json.dumps(token_event)}\n\n"
        except Exception as e:
            error_event = {"type": "error", "error": str(e)}
            yield f"data: {json.dumps(error_event)}\n\n"

        # Final Event: Completion and total latency metrics
        t_end = time.perf_counter()
        total_ms = round((t_end - t_start) * 1000, 2)
        done_event = {
            "type": "done",
            "latency_ms": {
                "retrieval_ms": retrieval_ms,
                "first_token_ms": first_token_ms or total_ms,
                "total_ms": total_ms,
            },
        }
        yield f"data: {json.dumps(done_event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/documents/upload", response_model=DocumentIngestResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Ingests an uploaded PDF file, extracts page text, creates chunks preserving
    document name and original page numbers, and indexes them in vector storage.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are currently supported.")

    content = await file.read()
    try:
        pages = read_pdf(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {e}")

    if not pages or all(len(p.strip()) == 0 for p in pages):
        raise HTTPException(
            status_code=400,
            detail="No readable text extracted. Scanned image-only PDFs require OCR before ingestion."
        )

    chunks = split_into_chunks(pages, document_name=file.filename)
    if not chunks:
        raise HTTPException(status_code=400, detail="Document could not be partitioned into valid chunks.")

    knowledge_base.add_chunks(chunks)

    return DocumentIngestResponse(
        message=f"Successfully ingested and indexed '{file.filename}'.",
        document=file.filename,
        pages_count=len(pages),
        chunks_count=len(chunks),
        total_chunks=knowledge_base.total_chunks(),
    )


@app.post("/api/documents/sample", response_model=DocumentIngestResponse)
def load_sample_document():
    """Loads (or reloads) the built-in starter syllabus into the knowledge base."""
    doc_name = "SSIT CS 101 Regulations & Syllabus"
    chunks = split_into_chunks(SAMPLE_PAGES, document_name=doc_name)
    knowledge_base.add_chunks(chunks)
    return DocumentIngestResponse(
        message=f"Loaded built-in {doc_name}.",
        document=doc_name,
        pages_count=len(SAMPLE_PAGES),
        chunks_count=len(chunks),
        total_chunks=knowledge_base.total_chunks(),
    )


@app.post("/api/documents/clear", response_model=ClearResponse)
def clear_knowledge_base():
    """Clears all indexed chunks and documents from memory."""
    knowledge_base.clear()
    return ClearResponse(
        message="Knowledge base successfully cleared.",
        total_chunks=0,
    )


# ==========================================
# Feedback System Endpoints
# ==========================================
feedback_records = []
feedback_file_path = Path(__file__).resolve().parent.parent / "feedback.jsonl"


@app.post("/api/feedback", response_model=FeedbackResponse)
def submit_feedback(req: FeedbackRequest):
    """
    Records student/user feedback on an answer.
    Saves to an append-only JSONL log and maintains in-memory stats.
    """
    feedback_id = f"fb_{int(time.time() * 1000)}"
    entry = {
        "id": feedback_id,
        "timestamp": time.time(),
        "question": req.question,
        "answer": req.answer,
        "rating": req.rating,  # "helpful" | "unhelpful"
        "tags": req.tags or [],
        "comment": req.comment or "",
        "sources": [s.model_dump() for s in req.sources] if req.sources else [],
    }

    feedback_records.append(entry)

    # Persist to disk
    try:
        with open(feedback_file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[Feedback] Warning saving to disk: {e}")

    return FeedbackResponse(
        status="success",
        message="Thank you! Your feedback has been recorded.",
        feedback_id=feedback_id,
    )


@app.get("/api/feedback/stats")
def get_feedback_stats():
    """Returns feedback breakdown (helpful count, unhelpful count, tag distribution)."""
    helpful = sum(1 for f in feedback_records if f["rating"] == "helpful")
    unhelpful = sum(1 for f in feedback_records if f["rating"] == "unhelpful")
    tag_counts = {}
    for f in feedback_records:
        for t in f.get("tags", []):
            tag_counts[t] = tag_counts.get(t, 0) + 1

    return {
        "total": len(feedback_records),
        "helpful": helpful,
        "unhelpful": unhelpful,
        "tags": tag_counts,
        "recent": feedback_records[-10:],
    }


# Serve frontend static assets if built
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")
