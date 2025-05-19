from utils import to_gpt_messages, call_prompt, get_openai_client
from mock_search import mock_search
import json

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


openai_functions = [
    {
        "type": "function",
        "function": {
            "name": "search_workspace",
            "description": "Search the workspace for documents relevant to the user's question",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query to run in the workspace"
                    }
                },
            }
        }
    }
]

def prompt_generate_rag_response_with_function_call(context, query, previous_messages=[], last_k=3):
    messages = []

    system = """
You are an intelligent assistant that provides grounded answers based only on the provided context.
Your job is to answer the user's query as accurately as possible using the context and conversation history.

Guidelines:
- Use only the provided context to form your response.
- Be concise but complete in your answer.
- You may refer to names, places, or concepts exactly as written in the context.
- Do not make assumptions or hallucinate beyond the context.
- Quote the source of the information in your response whenever possible.
- Use prior conversation history only to resolve references or follow-up intent - not to infer new facts.
- If you have sufficient context to answer the query directly, do so without calling any functions.


If the query requires locating or verifying a specific fact, event, date, or user action—where precision and recall are critical—you must call the search_workspace function.
i.e: "What is the date of the event?" or "What action did the user take?", "Who said this quote?" or "List out the names of xyz"
This ensures that your response is based on the most accurate and comprehensive match, especially when the existing context may be incomplete or ambiguous.

Use the search function whenever exactness matters more than speed. Otherwise, rely solely on the provided context to generate the answer.
    """.strip()

    messages.append({"role": "system", "content": system })

    # Add previous chat history
    if previous_messages:
        previous_messages = "\n".join([f"{'USER:' if message['isUser'] else 'AI'}: {message['text']}" for message in previous_messages[-last_k:]])
    else:
        previous_messages = "None"

    user_message = f"""
Context:
{context}

Conversation History:
{previous_messages}

Question:
{query}

Answer:
    """.strip()

    messages.append({"role": "user", "content": user_message})

    openai_client = get_openai_client()
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=openai_functions,
        tool_choice="auto"
    )

    response_content = response.choices[0].message.content

    if response.choices[0].message.tool_calls:
        func_name = response.choices[0].message.tool_calls[0].function.name
        arguments = json.loads(response.choices[0].message.tool_calls[0].function.arguments)

        if func_name == "search_workspace":
            context = mock_search(arguments["query"])

            messages.append({
                "role": "function",
                "name": func_name,
                "content": context
            })

            final_response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )

            return final_response.choices[0].message.content
    
    return response_content
