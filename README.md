# 🎓 SSIT Campus Regulations Assistant

A Retrieval-Augmented Generation (RAG) assistant built for college hackathons to help students, faculty, and administrators quickly query campus regulations, course policies, grading criteria, and exam guidelines.

Powered by **Google Gemma 4** (via Google AI Studio), **Sentence Transformers** (`all-MiniLM-L6-v2`), a **FastAPI** backend, and a modern **React.js** frontend.

---

## 🌟 Key Features & Requirements Handled

| Requirement | Implementation Detail |
| :--- | :--- |
| **Document & Page Metadata** | Each extracted text chunk explicitly records `document` (e.g. `SSIT CS 101 Regulations & Syllabus.pdf`) and 1-based original `page` number (`Page 2`). |
| **API Key Security** | The `GOOGLE_API_KEY` is kept strictly on the backend in `.env` and never exposed or sent to the React frontend. |
| **Gemma 4 Grounded Generation** | Prompts use strict citation instructions requiring document names and page numbers in citations: `(Document Name, Page X)`. Supported models: `gemma-4-26b-a4b-it` (fast, MoE) and `gemma-4-31b-it`. |
| **Demonstration Mode Fallback** | If no `GOOGLE_API_KEY` is provided, the system does not crash; it runs full semantic retrieval using `all-MiniLM-L6-v2` and presents the most relevant passages and citations with clear guidance. |
| **PDF Ingestion & Chunking** | Word-based chunking (150 words with 30-word overlap) using `pypdf`, dynamically indexed into an in-memory normalized vector store. |
| **Modern React Interface** | Glassmorphic dark theme, interactive suggestion chips, live status badges, drag-and-drop PDF dropzone, and expandable citation cards with match percentages. |

---

## 📁 Project Structure

```text
SSIT REGULATIONS ASSIST/
├── backend/
│   ├── .env.example              # Environment variables template
│   ├── requirements.txt          # Python dependencies
│   └── app/
│       ├── __init__.py           # Package marker
│       ├── config.py             # Settings, prompts, model selection, env loader
│       ├── schemas.py            # Pydantic models (QueryRequest, QueryResponse, ChunkMetadata)
│       ├── ingestion.py          # PDF extraction (pypdf) & word chunker preserving doc & page
│       ├── retriever.py          # SentenceTransformer embeddings & in-memory numpy cosine search
│       ├── generator.py          # Gemma LLM client, citation prompts, friendly error handler, demo mode
│       └── main.py               # FastAPI application with REST endpoints & static file serving
├── frontend/
│   ├── index.html                # HTML5 entry with Google Fonts (Plus Jakarta Sans)
│   ├── package.json              # React 18 + Vite dependencies
│   ├── vite.config.js            # Vite build configuration with /api proxy to :8000
│   └── src/
│       ├── main.jsx              # React DOM mounting
│       ├── App.jsx               # Main state management, notifications, query workflow
│       ├── index.css             # Glassmorphic dark-mode CSS design system
│       ├── api.js                # Frontend REST client
│       └── components/
│           ├── Navbar.jsx        # Status pills, demo mode badge, model spec, chunks counter
│           ├── ChatArea.jsx      # Message timeline, welcome hero, input bar, thinking animation
│           ├── MessageItem.jsx   # Message bubbles, copy answer action, citations container
│           ├── SourceCard.jsx    # Document name, page badge, similarity score, snippet preview
│           ├── DocumentManager.jsx # PDF dropzone, indexed regulations list, tech specs
│           └── SuggestedQuestions.jsx # Quick clickable regulation questions
├── test_backend.py               # Standalone verification script for RAG pipeline
├── run_backend.sh                # Start FastAPI backend server
├── run_frontend.sh               # Start Vite dev server
├── start_all.sh                  # Single-command runner for both backend and frontend
└── README.md
```

---

## 🚀 Quick Start Guide

### Option A: Start Everything (Single Command)

```bash
./start_all.sh
```
This launches the FastAPI backend on `http://localhost:8000` and the React frontend on `http://localhost:5173`.

---

### Option B: Step-by-Step Setup

#### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure Google AI Studio API Key (Optional for live Gemma generation)
cp .env.example .env
```

Edit `backend/.env`:
```env
GOOGLE_API_KEY=your_google_ai_studio_api_key_here
GEMMA_MODEL=gemma-4-26b-a4b-it
```
*(If left blank, the assistant automatically operates in **Demonstration Mode**, returning exact semantic retrieval matches without failing).*

#### 2. Run Verification Test

Run the backend verification script to test chunking, metadata preservation, vector retrieval, and question answering:

```bash
python3 ../test_backend.py
```

#### 3. Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Interactive Swagger API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Endpoint: [http://localhost:8000/api/health](http://localhost:8000/api/health)

#### 4. Frontend Setup

In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
Open your browser to [http://localhost:5173](http://localhost:5173).

---

## 📡 REST API Documentation

### 1. Health & Status
- **Endpoint:** `GET /api/health`
- **Response:**
  ```json
  {
    "status": "healthy",
    "demo_mode": false,
    "gemma_model": "gemma-4-26b-a4b-it",
    "embed_model": "sentence-transformers/all-MiniLM-L6-v2",
    "total_chunks": 14,
    "indexed_documents": ["SSIT CS 101 Regulations & Syllabus"]
  }
  ```

### 2. Query Regulations
- **Endpoint:** `POST /api/query`
- **Request Body:**
  ```json
  {
    "question": "What happens if I submit a lab late?",
    "top_k": 3
  }
  ```
- **Response:**
  ```json
  {
    "question": "What happens if I submit a lab late?",
    "answer": "Late assignments lose 10% penalty per day up to a maximum of 3 days, after which they receive zero credit. Every student receives two grace days per semester that can be used on lab assignments without penalty (SSIT CS 101 Regulations & Syllabus, Page 2).",
    "sources": [
      {
        "document": "SSIT CS 101 Regulations & Syllabus",
        "page": 2,
        "text": "Grading Breakdown and Assessment Policies... Late Submission Policy: Late assignments lose 10% penalty per day...",
        "score": 0.812
      }
    ],
    "demo_mode": false
  }
  ```

### 3. Upload Regulation PDF
- **Endpoint:** `POST /api/documents/upload`
- **Content-Type:** `multipart/form-data`
- **Field:** `file` (PDF file)

### 4. Restore Sample Data
- **Endpoint:** `POST /api/documents/sample`

### 5. Clear Knowledge Base
- **Endpoint:** `POST /api/documents/clear`

---

## 🧪 Testing with cURL

Ask a regulation question directly via terminal:
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the minimum attendance required for final exams?"}'
```
