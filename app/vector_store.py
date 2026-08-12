import faiss
import json
import os
import numpy as np
from typing import List, Dict, Any, Tuple

class VectorStore:
    def __init__(self, index_path: str = "faiss_index"):
        self.index_path = index_path
        self.metadata_path = f"{index_path}_meta.json"
        self.index = None
        self.metadata = []
        
    def build(self, embeddings: List[List[float]], metadata: List[Dict[str, Any]]):
        if not embeddings:
            return
            
        dim = len(embeddings[0])
        self.index = faiss.IndexFlatL2(dim)
        vectors = np.array(embeddings).astype('float32')
        self.index.add(vectors)
        self.metadata = metadata
        
    def save(self):
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f)
                
    def load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
        else:
            raise FileNotFoundError("Index or metadata file not found. Please run ingest.py first.")
            
    def search(self, query_embedding: List[float], k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        if self.index is None:
            self.load()
            
        q_vec = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(q_vec, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata):
                results.append((self.metadata[idx], float(distances[0][i])))
                
        return results
