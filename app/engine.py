import os
from groq import Groq
from app.embeddings import embedder
from app.vector_store import VectorStore
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class RAGEngine:
    def __init__(self, index_path: str = "faiss_index"):
        self.vector_store = VectorStore(index_path)
        try:
            self.vector_store.load()
            self.is_ready = True
        except FileNotFoundError:
            self.is_ready = False
            
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print("Warning: GROQ_API_KEY not found in environment")
        self.groq_client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.is_ready:
            raise RuntimeError("Knowledge base not initialized. Run ingest.py.")
            
        query_emb = embedder.embed_text(query)
        results = self.vector_store.search(query_emb, k=top_k)
        
        # format results for easier use
        formatted_results = []
        for meta, score in results:
            item = meta.copy()
            item["score"] = score
            formatted_results.append(item)
            
        return formatted_results

    def generate_answer(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        context_str = "\n\n---\n\n".join([
            f"Module: {c.get('module', '')}\nTask: {c.get('task', '')}\nSubtask: {c.get('subtask', '')}\nContent:\n{c.get('text', '')}" 
            for c in context_chunks
        ])
        
        prompt = f"""You are an experienced product trainer for the eVitals RPM platform. Explain workflows and processes directly and clearly based on the provided documentation.

Core Guidelines:
1. Be direct and concise. Do NOT use introductory filler phrases (e.g., "To answer your question...", "Let's break down..."). Start answering immediately.
2. Stop when the question is answered. Do not provide unnecessary extra information outside the scope of the user's query.
3. Understand the intent: If the user asks for steps (e.g., "how do I..."), provide numbered steps. If they ask a conceptual or permission question, give a direct explanation.
4. Multi-role handling: If the user asks a general "how to" question without specifying a role, briefly cover every role that has permission.
5. Describe UI flow in natural language using available layout cues and screenshot references.
6. Include brief source citations (e.g., [Module: X, Task: Y]) at the end.

=== GROUNDING AND REFUSAL RULES (STRICT) ===
You are answering questions ONLY from the retrieved eVitals knowledge base chunks provided to you in context. These rules override any instinct to be "helpful" by filling gaps.

1. HARD BOUNDARY ON SOURCE MATERIAL
You may only state a fact if it appears in the retrieved chunks. You may NOT use general knowledge about RPM/CCM platforms, healthcare software, insurance industry norms, or "typical" product behavior to fill in an answer, even if it seems like a reasonable guess.

2. MANDATORY REFUSAL PHRASE
If the retrieved chunks do not contain the answer, respond with EXACTLY this sentence and nothing else added to it:
"The requested information is not available."
Do not soften it, explain around it, or pair it with a guess.

3. NO "HELPFUL ELABORATION" ON UNGROUNDED TOPICS
If a question is about something the knowledge base explicitly states is out of scope or never mentions, do not describe what such a feature "likely" does. A short refusal is always correct; a detailed guess is always wrong.

4. DO NOT INFER CLINICAL OR BUSINESS MEANING BEYOND WHAT'S STATED
If the source describes a UI behavior (e.g., "out-of-range readings render in red") but does not define the clinical or business meaning behind it, do not explain what the color means medically. State only what the source states.

5. PARTIAL GROUNDING IS NOT FULL GROUNDING
If a question has multiple parts and only some parts are answerable, answer only the grounded parts explicitly, and apply the mandatory refusal phrase (Rule 2) to the ungrounded part(s).

Context:
{context_str}

User Question: {query}
Answer:"""

        response = self.groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an experienced product trainer. Use the provided context to synthesize complete, role-aware procedural instructions."},
                {"role": "user", "content": prompt}
            ],
            model=self.model,
            temperature=0.0
        )
        
        return response.choices[0].message.content

    def query(self, query: str) -> Dict[str, Any]:
        chunks = self.retrieve(query, top_k=5)
        answer = self.generate_answer(query, chunks)
        
        # extract sources for API response (without text to keep it clean)
        sources = [
            {
                "module": c.get("module"),
                "task": c.get("task"),
                "subtask": c.get("subtask")
            }
            for c in chunks
        ]
        
        return {
            "answer": answer,
            "sources": sources,
            "debug_chunks": chunks  # will be filtered out by endpoint if not debug
        }
