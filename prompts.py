from utils import to_gpt_messages, call_prompt

def prompt_generate_metadata(chunk_content):
    system = """
You are a helpful assistant that generates metadata for a given text chunk.
""".strip()

    user = f"""
Generate metadata for the following text chunk:
{chunk_content}
""".strip()
    
    return call_prompt(to_gpt_messages([system, user]))

def prompt_get_response(messages):
    system = """
    You are a helpful assistant that generates a response for a given text chunk.
    """

    user = f"""
    {messages}
    """

    return call_prompt(to_gpt_messages([system, user]))


def prompt_summarize_chunk_bullet_points(current_chunk, previous_chunks):
    system = """
You are a helpful assistant tasked with summarizing a chunk of text from a larger document.
Your goal is to produce a list of concise, standalone bullet points based on the current chunk.

- Keep the language simple and informative.
- Each bullet point should capture one distinct idea.
- Retain important named entities like people, organizations, and places.
- Avoid redundancy with previous chunks.
- Do not paraphrase proper nouns; preserve them exactly.
- If the chunk contains dialogue or quotes, summarize the key message.
""".strip()

    user = f"""
Current Chunk:
{current_chunk}

Previous Chunk:
{previous_chunks}

Please return ONLY bullet points summarizing the current chunk.
    """.strip()

    return call_prompt(to_gpt_messages([system, user]))

def prompt_generate_rag_response(context, query, previous_messages=[], last_k=3):
    if previous_messages:
        previous_messages = "\n".join([f"{'USER:' if message['isUser'] else 'AI'}: {message['text']}" for message in previous_messages[-last_k:]])
    else:
        previous_messages = "None"

    system = """
You are an intelligent assistant that provides grounded answers based only on the provided context.
Your job is to answer the user's query as accurately as possible using the context and conversation history.

Guidelines:
- Use only the provided context to form your response.
- If the context does not contain enough information, respond with: "I couldn't find that information in the provided context."
- Be concise but complete in your answer.
- You may refer to names, places, or concepts exactly as written in the context.
- Do not make assumptions or hallucinate beyond the context.
- Quote the source of the information in your response whenever possible.

Use the previous conversation to resolve references, but do not fabricate facts not present in the current context.
    """.strip()

    user = f"""
Context:
{context}

Conversation History:
{previous_messages}

Question:
{query}

Answer:
    """.strip()

    return call_prompt(to_gpt_messages([system, user]))
