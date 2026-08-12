# eVitals Documentation RAG Backend

This is a production-ready RAG backend for the eVitals RPM User Manual. It provides endpoints to query the knowledge base and retrieve answers with source citations (Module -> Task -> Subtask). 

## Technologies Used
- **Python 3.9+**
- **FastAPI** (Backend API)
- **FAISS** (Local Vector Database)
- **Sentence Transformers** (`all-MiniLM-L6-v2` for embeddings)
- **Groq** (`llama-3.1-8b-instant` for LLM)

## Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   Copy `.env.example` to `.env` and add your Groq API key:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set `GROQ_API_KEY=your_api_key_here`.

3. **Data Placement:**
   Ensure the `eVitals_User_Guide_v25_HTA.docx` is placed inside the `data/` directory.

4. **Ingest the Document:**
   Run the ingestion script to parse the document, chunk it, create embeddings, and build the FAISS index.
   ```bash
   python ingest.py
   ```
   *Note: Re-run this script anytime the manual is updated.*

## Running the Backend API

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. You can view the interactive Swagger documentation at `http://localhost:8000/docs`.

### API Endpoints
- `GET /api/v1/status`: Check if the knowledge base is ready.
- `POST /api/v1/query`: Ask a question. Returns the answer and sources.
- `POST /api/v1/query/debug`: Same as above, but includes raw retrieved chunks and similarity scores for debugging.

## Testing with Streamlit (Development Only)

A temporary Streamlit application is included to test the API easily. 

Ensure the FastAPI server is running, then in a new terminal run:
```bash
streamlit run test_app.py
```
This will open a chat interface in your browser to test the system. You can delete `test_app.py` before deploying to production.
