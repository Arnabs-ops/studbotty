import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:1b")
    ANKI_CONNECT_URL = os.getenv("ANKI_CONNECT_URL", "http://localhost:8765")
    OFFLINE_MODE = os.getenv("OFFLINE_MODE", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    PERSISTENCE_FILE = os.getenv("PERSISTENCE_FILE", "studbotty_data.json")

config = Config()
