from db import PostgreSQL
from utils import read_file, split_text_by_tokens, get_embedding, get_total_tokens_from_messages
import os
import traceback
from tqdm import tqdm
import json
import time
from prompts import prompt_summarize_chunk_bullet_points

def generate_metadata(chunk_content):
    return {
        "chunk_size": get_total_tokens_from_messages([chunk_content])
    }

def worker(file_path, project_id):
    db = PostgreSQL()
    text = read_file(file_path)
    filename = os.path.basename(file_path)

    document_id = db.insert("insert into lp_document (name, type, project_id) values (%s, %s, %s) returning id", (filename, "text", project_id))

    chunks = split_text_by_tokens(text, max_chunk_size=1500)

    chunk_data = []

    previous_chunks = ""
    for index, chunk in tqdm(enumerate(chunks), total=len(chunks)):
        metadata = generate_metadata(chunk)
        bullet_point_summary = prompt_summarize_chunk_bullet_points(chunk, previous_chunks)

        metadata["bullet_points"] = bullet_point_summary

        bullet_point_embedding = get_embedding(bullet_point_summary)

        values = (
            document_id,
            index,
            chunk,
            json.dumps(bullet_point_embedding),
            json.dumps(metadata)
        )

        previous_chunks = str(chunk)
        
        chunk_data.append(values)
    
    insert_sql = """
        INSERT INTO lp_chunks (document_id, chunk_index, content, embedding, metadata)
        VALUES %s
    """

    try:
        db.bulk_insert(insert_sql, chunk_data)
    except Exception as e:
        print(f"Error inserting chunks: {e}")
        traceback.print_exc()
    del db
