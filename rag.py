from db import PostgreSQL
from utils import get_embedding, cosine_similarity
from prompts import prompt_generate_rag_response

def rag_get_response(project_id: int, query: str, previous_messages: list = None, top_k: int = 2, similarity_threshold: float = 0.9):
    db = PostgreSQL()

    chunks = db.select_many("""
        SELECT lc.*, ld.name as file_name 
        FROM lp_chunks lc
        JOIN lp_document ld ON lc.document_id = ld.id
        WHERE ld.project_id = %s
    """, (project_id,))

    if len(chunks) == 0:
        return {
            "response": "No documents found for this project",
            "proof": []
        }

    query_embedding = get_embedding(query)
    
    similarities = []
    for chunk in chunks:
        chunk_embedding = chunk["embedding"]
        similarity = cosine_similarity(query_embedding, chunk_embedding)
        similarities.append((chunk, similarity))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    top_chunks = [(chunk, score) for chunk, score in similarities if score >= similarity_threshold]

    if not top_chunks:
        top_chunks = similarities[:top_k]

    # construct prompt with context
    context = ""
    for chunk, score in top_chunks:
        context += f"Chunk: {chunk['content']}\n"
        context += f"Document Name: {chunk['file_name']}\n"
        context += "==========\n\n"

    response = prompt_generate_rag_response(context, query, previous_messages)
    
    result = {
        "response": response,
        "proof": [
            {
                "chunk_id": chunk["id"],
                "file_name": chunk["file_name"],
                "similarity_score": score
            }
            for chunk, score in similarities[:top_k]
        ]
    }
    
    return result
