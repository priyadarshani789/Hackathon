import os
from dotenv import load_dotenv

load_dotenv()  # loads from .env file

# Embeddings Configuration
AZURE_EMBEDDING_API_KEY = os.getenv("AZURE_OPENAI_EMBEDDING_API_KEY")
AZURE_EMBEDDING_ENDPOINT = os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT")
AZURE_EMBEDDING_MODEL = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
AZURE_EMBEDDING_API_VERSION = os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION", "2024-02-01")

# Chat Configuration
AZURE_CHAT_API_KEY = os.getenv("AZURE_OPENAI_CHAT_API_KEY")
AZURE_CHAT_ENDPOINT = os.getenv("AZURE_OPENAI_CHAT_ENDPOINT")
AZURE_CHAT_MODEL = os.getenv("AZURE_OPENAI_CHAT_MODEL", "gpt-4")
AZURE_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
AZURE_CHAT_API_VERSION = os.getenv("AZURE_OPENAI_CHAT_API_VERSION", "2024-02-01")

# Legacy OpenAI API Key (for backward compatibility)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Database Configuration
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "healthtech_kb")

# Server Configuration
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Validation function to check if required environment variables are set
def validate_config():
    """Validates that all required configuration variables are set."""
    required_vars = [
        ("AZURE_EMBEDDING_API_KEY", AZURE_EMBEDDING_API_KEY),
        ("AZURE_EMBEDDING_ENDPOINT", AZURE_EMBEDDING_ENDPOINT),
        ("AZURE_EMBEDDING_DEPLOYMENT", AZURE_EMBEDDING_DEPLOYMENT),
        ("AZURE_CHAT_API_KEY", AZURE_CHAT_API_KEY),
        ("AZURE_CHAT_ENDPOINT", AZURE_CHAT_ENDPOINT),
        ("AZURE_CHAT_DEPLOYMENT", AZURE_CHAT_DEPLOYMENT),
    ]
    
    missing_vars = []
    for var_name, var_value in required_vars:
        if not var_value:
            missing_vars.append(var_name)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True