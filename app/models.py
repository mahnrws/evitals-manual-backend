from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class QueryRequest(BaseModel):
    query: str

class SourceMetadata(BaseModel):
    module: Optional[str] = None
    task: Optional[str] = None
    subtask: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceMetadata]

class DebugQueryResponse(QueryResponse):
    retrieved_chunks: List[Dict[str, Any]]
