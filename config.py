import os
import dotenv

dotenv.load_dotenv()

DEFAULT_PROJECT_ID = os.getenv("DEFAULT_PROJECT_ID", 1)

postgres_db = os.getenv("postgres_db")
postgres_userName = os.getenv("postgres_userName")
postgres_password = os.getenv("postgres_password")
postgres_url = os.getenv("postgres_url")
postgres_port = os.getenv("postgres_port")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

USE_MOCK_SEARCH = os.getenv("USE_MOCK_SEARCH", "true").lower() == "true"