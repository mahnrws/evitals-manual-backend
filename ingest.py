import os
from app.document_processor import process_document
from app.embeddings import embedder
from app.vector_store import VectorStore

def main():
    doc_path = "data/eVitals_RAG_Knowledge_Base.docx"
    index_path = "faiss_index"
    
    if not os.path.exists(doc_path):
        print(f"Error: {doc_path} not found.")
        print("Please place the manual in the data directory and try again.")
        return
        
    print(f"Processing document: {doc_path}")
    chunks = process_document(doc_path)
    
    if not chunks:
        print("No chunks extracted from the document.")
        return
        
    print(f"Extracted {len(chunks)} chunks.")
    
    # Prepare data for vector store
    texts = [c.text for c in chunks]
    metadatas = [c.metadata for c in chunks]
    
    # Store text in metadata so we can retrieve it
    for i in range(len(metadatas)):
        metadatas[i]["text"] = texts[i]
        
    print("Generating embeddings (this may take a moment)...")
    embeddings = embedder.embed_batch(texts)
    
    print("Building and saving vector store...")
    store = VectorStore(index_path)
    store.build(embeddings, metadatas)
    store.save()
    
    print(f"Success! Knowledge base saved to {index_path} and {index_path}_meta.json.")

if __name__ == "__main__":
    main()
