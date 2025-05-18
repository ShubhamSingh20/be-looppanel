from flask import Flask, request, jsonify
from worker import worker
import sys
import traceback
import time
from config import DEFAULT_PROJECT_ID
from rag import rag_get_response
from flask_cors import CORS
import tiktoken

app = Flask(__name__)

CORS(app, origins="*")

@app.route('/get_chat_reply/<project_id>', methods=['POST'])
def get_chat_reply(project_id):
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "Missing query in request body"}), 400

        query = data["query"]
        
        rag_result = rag_get_response(int(project_id), query, data.get("messageHistory", []))
        
        return jsonify({
            "message": "Success",
            "project_id": project_id,
            "query": query,
            "response": rag_result["response"],
            "proof": rag_result["proof"]
        }), 200
        
    except Exception as e:

        return jsonify({"error": str(e)}), 500

@app.route('/list_projects', methods=['GET'])
def list_projects():
    try:
        projects = [
            {"id": "1", "name": "Project 1"},
            {"id": "2", "name": "Project 2"},
            {"id": "3", "name": "Project 3"}
        ]
        
        return jsonify({
            "message": "Success",
            "projects": projects
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "pong"}), 200

if __name__ == '__main__':
    command = sys.argv[1] if len(sys.argv) > 1 else None        
    if command == 'runserver':
        tiktoken.get_encoding('o200k_base')
        app.run(debug=True)
    elif command == 'import_data':
        if len(sys.argv) < 3:
            print("To import data, use: python app.py import_data <text_file_path>")
            sys.exit(1)
        text_file_path = sys.argv[2]
        worker(text_file_path, DEFAULT_PROJECT_ID)
    else:
        print("To start the server, use: python app.py runserver")
        print("To import data, use: python app.py import_data <text_file_path>")

