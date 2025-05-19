import time
import tiktoken
from openai import OpenAI
from config import OPENAI_API_KEY

def get_embedding(text: str, model="text-embedding-ada-002"):
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.embeddings.create(
        model=model,
        input=text
    )
    return response.data[0].embedding

def get_openai_client():
    return OpenAI(api_key=OPENAI_API_KEY)

def read_file(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read()

def to_gpt_messages(arr: list[str]):
    messages = []
    for i, element in enumerate(arr):
        if i == 0:
            messages.append({"role": "system", "content": element})
        elif i%2 == 0 and i > 0:
            messages.append({"role": "assistant", "content": element})
        else:
            messages.append({"role": "user", "content": element})

    return messages

def get_total_tokens_from_messages(messages, model="gpt-4o"):
    if all(isinstance(message, str) for message in messages):
        messages = to_gpt_messages(messages)

    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    if model not in {
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-4-0314",
            "gpt-4",
            "gpt-4-32k-0314",
            "gpt-4-turbo-preview",
            "gpt-35-turbo",
            "gpt-4-0613",
            "gpt-4o",
            "azure-gpt-4o",
            "gpt-4o-mini",
            "gpt-4-32k-0613",
            "claude-3-haiku-20240307",
            "claude-3-sonnet-20240229",
            "claude-3-opus-20240229"
            }:

            # log warning
            print(f"Warning: Model {model} not found. Assuming 'tokens_per_message' = 3 and 'tokens_per_name' = 1")

    tokens_per_message = 3
    tokens_per_name = 1

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>

    return num_tokens

def split_text_by_tokens(text: str, max_chunk_size=1200, separator='. '):
    chunks = []
    current_chunk = ''
    text = text.strip()
    sentences = text.split(separator)
    last_index = len(sentences) - 1

    # filter out empty sentences
    sentences = [sentence for sentence in sentences if sentence.strip()]

    for i, sentence in enumerate(sentences):
        if i != last_index:
            sentence += separator  # Adding back the full stop removed by split() but not for the last sentence.
        
        updated_chunk = current_chunk + sentence

        if get_total_tokens_from_messages([updated_chunk]) <= max_chunk_size:
            current_chunk = updated_chunk
        else:
            chunks.append(current_chunk)
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def call_prompt(messages, model="gpt-4o"):
    start_time = time.time()
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    end_time = time.time()

    # format time_diff to 2 decimal places
    time_diff = round(end_time - start_time, 2)

    # print(f"[{model}] {time_diff} seconds")
    return response.choices[0].message.content


def cosine_similarity(a, b):
    return sum(a * b for a, b in zip(a, b)) / (sum(a * a for a in a) ** 0.5 * sum(b * b for b in b) ** 0.5)