from fastapi import FastAPI, HTTPException
from app.models import QueryRequest, QueryResponse, DebugQueryResponse
from app.engine import RAGEngine
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="eVitals Documentation RAG API")

# Initialize engine lazily
engine = None

def get_engine():
    global engine
    if engine is None:
        try:
            engine = RAGEngine()
        except Exception as e:
            print(f"Error initializing engine: {e}")
    return engine

@app.on_event("startup")
async def startup_event():
    get_engine()

@app.get("/api/v1/status")
async def status():
    eng = get_engine()
    if eng and getattr(eng, 'is_ready', False):
        return {"status": "ok", "knowledge_base": "ready"}
    return {"status": "ok", "knowledge_base": "not_initialized"}

@app.post("/api/v1/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    eng = get_engine()
    if not eng or not getattr(eng, 'is_ready', False):
        raise HTTPException(status_code=503, detail="Knowledge base not initialized. Please run ingest.py.")
    
    try:
        result = eng.query(request.query)
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/query/debug", response_model=DebugQueryResponse)
async def debug_query_endpoint(request: QueryRequest):
    eng = get_engine()
    if not eng or not getattr(eng, 'is_ready', False):
        raise HTTPException(status_code=503, detail="Knowledge base not initialized.")
    
    try:
        result = eng.query(request.query)
        return DebugQueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            retrieved_chunks=result["debug_chunks"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
