from typing import List, Optional
from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    """Metadata and snippet for an individual document chunk."""
    document: str = Field(..., description="Source document filename or title")
    page: int = Field(..., description="Original 1-based page number")
    text: str = Field(..., description="Text content of the chunk")
    score: Optional[float] = Field(None, description="Cosine similarity score (0.0 to 1.0)")


class LatencyMetrics(BaseModel):
    """Latency breakdown in milliseconds."""
    retrieval_ms: float = Field(..., description="Time taken to retrieve and score chunks")
    total_ms: float = Field(..., description="Total end-to-end processing time")
    first_token_ms: Optional[float] = Field(None, description="Time to first generated token")


class QueryRequest(BaseModel):
    """Request payload for querying regulations."""
    question: str = Field(..., min_length=2, description="The user's query about campus regulations")
    top_k: Optional[int] = Field(None, ge=1, le=10, description="Number of chunks to retrieve")


class QueryResponse(BaseModel):
    """Response payload containing generated answer and cited passages."""
    question: str
    answer: str
    sources: List[ChunkMetadata]
    demo_mode: bool
    latency_ms: Optional[LatencyMetrics] = None


class FeedbackRequest(BaseModel):
    """User feedback payload submitted after an answer."""
    question: str = Field(..., description="The query that was answered")
    answer: str = Field(..., description="The answer text that received feedback")
    rating: str = Field(..., description="'helpful' or 'unhelpful'")
    tags: Optional[List[str]] = Field(default_factory=list, description="Categorical feedback tags")
    comment: Optional[str] = Field(None, description="Optional user commentary or suggestions")
    sources: Optional[List[ChunkMetadata]] = Field(default=None, description="Cited sources for the answer")


class FeedbackResponse(BaseModel):
    """Feedback submission acknowledgement."""
    status: str
    message: str
    feedback_id: str


class DocumentIngestResponse(BaseModel):
    """Response payload following document ingestion."""
    message: str
    document: str
    pages_count: int
    chunks_count: int
    total_chunks: int


class HealthResponse(BaseModel):
    """System health and status inspection."""
    status: str
    demo_mode: bool
    gemma_model: str
    embed_model: str
    total_chunks: int
    indexed_documents: List[str]


class ClearResponse(BaseModel):
    """Response payload when clearing the knowledge base."""
    message: str
    total_chunks: int
