"""
Configuration and runtime environment manager for SSIT Campus Regulations Assistant.
Supports dynamic environment loading, safe fallback parsing, and strict formula/grounding rules.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

# ==========================================
# Module-level defaults (explicitly declared)
# ==========================================
GOOGLE_API_KEY: str = ""
DEMO_MODE: bool = True
GEMMA_MODEL: str = "gemma-4-26b-a4b-it"
TEMPERATURE: float = 0.2
CHUNK_SIZE: int = 150
CHUNK_OVERLAP: int = 30
TOP_K: int = 3
EMBED_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

# Strict grounded answering rules with clear mathematical formatting instructions
ANSWER_RULES: str = """You are the official Campus Regulations Assistant for SSIT. Answer the question using ONLY the provided context passages.

1. Grounding & Accuracy:
- Answer using ONLY the provided context. If the context does not contain enough information to answer the question, state: "I don't have enough information in the provided campus documents to answer this." Do not extrapolate, guess, or fabricate policies.
- Do not invent formulas, rules, or grading criteria. Retrieve the official rules from the source text and strictly preserve all conditions, criteria, and exceptions.
- Always cite your sources at the end of each policy statement using the exact document title and page number format: (Document Name, Page X).

2. Formula & Mathematics Formatting:
- Present mathematical or grading formulas (such as CGPA, SGPA, attendance percentage, or class conversion) in clear, readable natural language using plain text first.
  Format standard formulas cleanly, for example:
  CGPA = Sum of (Course Credits × Grade Points) / Sum of Course Credits (for all eligible courses until that semester)
- Clearly distinguish the numerator and denominator, and explain which courses/grades are included or excluded according to the official text (e.g., courses with 'F' and transitional grades).
- If LaTeX notation is used, it must be syntactically valid, complete, and properly structured using fractions (\\frac{numerator}{denominator}) and standard operators. NEVER output incomplete, unclosed, or malformed math expressions without operators.

3. Tone & Structure:
- Structure your answer with clear Markdown headings, bullet points, and clean paragraphs.
- Maintain an objective, authoritative, and helpful tone suitable for college students and faculty."""

_file_mtimes: Dict[str, float] = {}


def _parse_float(val: Optional[str], default: float) -> float:
    """Safely converts an environment string to float, falling back to default."""
    if val is None:
        return default
    val_str = str(val).strip()
    if not val_str:
        return default
    try:
        return float(val_str)
    except (ValueError, TypeError):
        return default


def _parse_int(val: Optional[str], default: int) -> int:
    """Safely converts an environment string to int, falling back to default."""
    if val is None:
        return default
    val_str = str(val).strip()
    if not val_str:
        return default
    try:
        return int(val_str)
    except (ValueError, TypeError):
        return default


def _clean_value(val: str) -> str:
    """Strips quotes and inline comments from an environment string."""
    cleaned = val.strip()
    # Strip quotes if enclosed
    if (cleaned.startswith('"') and cleaned.endswith('"')) or (
        cleaned.startswith("'") and cleaned.endswith("'")
    ):
        cleaned = cleaned[1:-1].strip()
    return cleaned


def reload_env() -> str:
    """
    Safely reloads environment variables from both workspace root .env and backend/.env
    whenever either file modification timestamp changes.
    """
    global GOOGLE_API_KEY, DEMO_MODE, GEMMA_MODEL, TEMPERATURE, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K, EMBED_MODEL_NAME, _file_mtimes

    current_file = Path(__file__).resolve()
    backend_env = current_file.parent.parent / ".env"
    root_env = current_file.parent.parent.parent / ".env"

    env_paths = [root_env, backend_env]

    for p in env_paths:
        try:
            if p.exists() and p.is_file():
                current_mtime = p.stat().st_mtime
                prev_mtime = _file_mtimes.get(str(p), 0.0)
                if current_mtime > prev_mtime:
                    try:
                        from dotenv import load_dotenv
                        load_dotenv(dotenv_path=p, override=True)
                    except ImportError:
                        with open(p, "r", encoding="utf-8") as f:
                            for line in f:
                                line = line.strip()
                                if line and not line.startswith("#") and "=" in line:
                                    k, v = line.split("=", 1)
                                    # Strip inline comment if any
                                    if " #" in v:
                                        v = v.split(" #", 1)[0]
                                    os.environ[k.strip()] = _clean_value(v)
                    _file_mtimes[str(p)] = current_mtime
        except Exception as e:
            print(f"[config] Warning loading {p.name}: {e}")

    # Extract API key and sanitize
    raw_key = os.environ.get("GOOGLE_API_KEY", "")
    GOOGLE_API_KEY = _clean_value(raw_key)
    DEMO_MODE = not bool(GOOGLE_API_KEY)

    raw_model = os.environ.get("GEMMA_MODEL", "gemma-4-26b-a4b-it")
    GEMMA_MODEL = _clean_value(raw_model) or "gemma-4-26b-a4b-it"

    TEMPERATURE = _parse_float(os.environ.get("TEMPERATURE"), 0.2)
    CHUNK_SIZE = _parse_int(os.environ.get("CHUNK_SIZE"), 150)
    CHUNK_OVERLAP = _parse_int(os.environ.get("CHUNK_OVERLAP"), 30)
    TOP_K = _parse_int(os.environ.get("TOP_K"), 3)

    raw_embed = os.environ.get("EMBED_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    EMBED_MODEL_NAME = _clean_value(raw_embed) or "sentence-transformers/all-MiniLM-L6-v2"

    return GOOGLE_API_KEY


def get_api_key() -> str:
    """Returns the active Google AI Studio API key."""
    reload_env()
    return GOOGLE_API_KEY


def is_demo_mode() -> bool:
    """Returns True if the assistant is running without an LLM key."""
    reload_env()
    return DEMO_MODE


def get_gemma_model() -> str:
    """Returns the configured Gemma model name."""
    reload_env()
    return GEMMA_MODEL


# Initial load at module import
reload_env()

__all__ = [
    "GOOGLE_API_KEY",
    "DEMO_MODE",
    "GEMMA_MODEL",
    "TEMPERATURE",
    "CHUNK_SIZE",
    "CHUNK_OVERLAP",
    "TOP_K",
    "EMBED_MODEL_NAME",
    "ANSWER_RULES",
    "reload_env",
    "get_api_key",
    "is_demo_mode",
    "get_gemma_model",
]
