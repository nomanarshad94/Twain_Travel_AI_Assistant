import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Book paths
BOOK_RAW_PATH = DATA_DIR / "innocents_abroad_raw.txt"
BOOK_CLEAN_PATH = DATA_DIR / "innocents_abroad_clean.txt"
BOOK_PROCESSED_PATH = DATA_DIR / "innocents_abroad_chunks.json"

# Project Gutenberg URL for "The Innocents Abroad"
INNOCENTS_ABROAD_URL = "https://www.gutenberg.org/cache/epub/3176/pg3176.txt"

# LangChain Text Splitter Configuration
LANGCHAIN_CHUNK_SIZE = 1000
LANGCHAIN_CHUNK_OVERLAP = 200
LANGCHAIN_SEPARATOR = "\n\n"

# PostgreSQL Database Configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'travel_advisor_db')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_VERSION = os.getenv('OPENAI_API_VERSION')
GPT_DEPLOYMENT_NAME = os.getenv('GPT_DEPLOYMENT_NAME')
AZURE_OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE'))

# OpenWeatherMap Configuration
OPENWEATHER_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Embedding Configuration (Azure OpenAI Embeddings)
EMBEDDING_MODEL_NAME = os.getenv('EMBEDDING_MODEL_NAME')
FAISS_INDEX_PATH = DATA_DIR / "faiss_index"

# Agent Configuration
AGENT_RECURSION_LIMIT = int(os.getenv('AGENT_RECURSION_LIMIT', '10'))
AGENT_MAX_RETRIES = int(os.getenv('AGENT_MAX_RETRIES', '3'))

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"
