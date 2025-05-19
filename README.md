# RAG-based Chat Application

This is a Flask-based application that implements a Retrieval-Augmented Generation (RAG) system for answering questions based on imported documents.

## Prerequisites

- Python 3.x
- PostgreSQL database
- OpenAI API key
- example directory contains some transcripts from a podcast which are already inserted with "Project 1".

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following variables:
```
OPENAI_API_KEY=your_openai_api_key
USE_MOCK_SEARCH=true  # setting true will utilize openai function calling
```
See .env.example to check what env variables are to be exposed

4. The application uses a PostgreSQL database. The database configuration is already set up in `config.py` with the following default values:
- Database: relyque-db
- Host: ap-southeast-2.sql.xata.sh
- Port: 5432

## Usage

### Starting the Server

To start the Flask server:
```bash
python app.py runserver
```

The server will start in debug mode and be accessible at `http://localhost:5000`.

### Importing Data
You can specify `DEFAULT_PROJECT_ID` to specify in which project to dump this file.

To import a text file for processing (right now we only support text file):
```bash
python app.py import_data <path_to_text_file>
```

For example:
```bash
python app.py import_data example/transcript.txt
```

The import process will:
1. Split the text into chunks
2. Generate embeddings for each chunk
3. Store the chunks and embeddings in the database
4. Generate metadata for each chunk

### API Endpoints

1. **Get Chat Reply**
   - Endpoint: `/get_chat_reply/<project_id>`
   - Method: POST
   - Body: `{"query": "your question here"}`
   - Returns: Response with answer and supporting evidence

2. **List Projects**
   - Endpoint: `/list_projects`
   - Method: GET
   - Returns: List of available projects

3. **Ping**
   - Endpoint: `/ping`
   - Method: GET
   - Returns: Simple health check response

