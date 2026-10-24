#!/usr/bin/env python3
"""
Test script for the SSIT Campus Regulations Assistant backend RAG pipeline.
Validates chunking, metadata preservation, vector retrieval, and answer generation.
Automatically detects and uses the backend virtual environment if available.
"""

import os
import sys

# 1. Environment and Virtualenv Auto-Switching
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Potential virtual environment locations (prefer backend/venv where dependencies are installed)
_VENV_CANDIDATES = [
    os.path.join(_CURRENT_DIR, "backend", "venv", "bin", "python3"),
    os.path.join(_CURRENT_DIR, "venv", "bin", "python3"),
    os.path.join(_CURRENT_DIR, "..", "backend", "venv", "bin", "python3"),
]

_TARGET_VENV = None
for candidate in _VENV_CANDIDATES:
    if os.path.exists(candidate):
        _TARGET_VENV = candidate
        break

# Switch to virtualenv by checking sys.prefix (do NOT use realpath as macOS venvs symlink to system python)
if _TARGET_VENV and not os.environ.get("_SSIT_VENV_SWITCHED"):
    target_prefix = os.path.dirname(os.path.dirname(_TARGET_VENV))
    if os.path.abspath(sys.prefix) != os.path.abspath(target_prefix):
        os.environ["_SSIT_VENV_SWITCHED"] = "1"
        try:
            os.execv(_TARGET_VENV, [_TARGET_VENV] + sys.argv)
        except Exception as e:
            print(f"[Notice] Could not execv into {_TARGET_VENV}: {e}. Continuing with current interpreter.")

# 2. Add backend and root directory to python path
_BACKEND_DIR = os.path.join(_CURRENT_DIR, "backend") if not _CURRENT_DIR.endswith("backend") else _CURRENT_DIR
_ROOT_DIR = os.path.dirname(_BACKEND_DIR)

for path_entry in [_BACKEND_DIR, _ROOT_DIR, _CURRENT_DIR]:
    if path_entry not in sys.path:
        sys.path.insert(0, path_entry)

# 3. Safe imports with dual package path support
try:
    from backend.app.config import (
        DEMO_MODE,
        GEMMA_MODEL,
        EMBED_MODEL_NAME,
        is_demo_mode,
        get_gemma_model,
        reload_env,
    )
    from backend.app.ingestion import SAMPLE_PAGES, split_into_chunks
    from backend.app.retriever import VectorStore
    from backend.app.generator import answer_question
except ImportError:
    from app.config import (
        DEMO_MODE,
        GEMMA_MODEL,
        EMBED_MODEL_NAME,
        is_demo_mode,
        get_gemma_model,
        reload_env,
    )
    from app.ingestion import SAMPLE_PAGES, split_into_chunks
    from app.retriever import VectorStore
    from app.generator import answer_question


def run_tests():
    # Force reload of environment
    reload_env()

    print("=" * 65)
    print("SSIT CAMPUS REGULATIONS ASSISTANT - BACKEND VERIFICATION")
    print("=" * 65)
    print(f"Configured Gemma Model: {get_gemma_model()}")
    print(f"Embedding Model:        {EMBED_MODEL_NAME}")
    print(f"Demonstration Mode:     {is_demo_mode()}")
    print(f"Python Interpreter:     {sys.executable}")
    print(f"Python Prefix:          {sys.prefix}")
    print("-" * 65)

    # 1. Test Ingestion and Metadata Preservation
    doc_title = "SSIT CS 101 Regulations & Syllabus"
    chunks = split_into_chunks(SAMPLE_PAGES, document_name=doc_title)
    print(f"[TEST 1] Ingestion: Generated {len(chunks)} chunks from {len(SAMPLE_PAGES)} pages.")
    assert len(chunks) > 0, "No chunks were generated!"

    first_chunk = chunks[0]
    assert "document" in first_chunk, "Missing 'document' in chunk metadata!"
    assert "page" in first_chunk, "Missing 'page' in chunk metadata!"
    assert first_chunk["document"] == doc_title, f"Document name mismatch: {first_chunk['document']}"
    assert first_chunk["page"] == 1, f"Expected page 1, got: {first_chunk['page']}"
    print(f"   -> Verified metadata preservation: Doc='{first_chunk['document']}', Page={first_chunk['page']}")

    # 2. Test Vector Indexing and Semantic Retrieval
    store = VectorStore()
    added = store.add_chunks(chunks)
    print(f"\n[TEST 2] Vector Store: Successfully indexed {added} chunks.")

    test_query = "What happens if I submit a lab late?"
    results = store.retrieve(test_query, top_k=3)
    print(f"   -> Query: '{test_query}'")
    print(f"   -> Retrieved {len(results)} chunks:")
    for idx, r in enumerate(results, start=1):
        print(f"      {idx}. [{r['document']} - Page {r['page']}] (similarity: {r['score']:.3f})")
        print(f"         Snippet: {r['text'][:85]}...")

    assert len(results) > 0, "Retrieval returned 0 chunks!"
    assert results[0]["page"] == 2, "Expected grading & late submission policy from Page 2 as top match!"

    # 3. Test Answer Generation
    print("\n[TEST 3] Answer Generation:")
    answer_text, is_demo = answer_question(test_query, results)
    print(f"   -> Is Demo Mode: {is_demo}")
    print(f"   -> Response:\n{answer_text}")

    print("\n" + "=" * 65)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
