APP_NAME="mini-RAG"
APP_VERSION="0.1"
OPENAI_API_KEY=""

FILE_ALLOWED_TYPES = ["text/plain", "application/pdf"]
FILE_MAX_SIZE = 10
FILE_DEFAULT_CHNUK_SIZE = 512000 #500 KB

########################### DATABASE #############################

POSTGRES_USERNAME="postgres"
POSTGRES_PASSWORD="postgres_password"
POSTGRES_HOST="pgvector"
POSTGRES_PORT=5432
POSTGRES_MAIN_DATABASE="minirag"

# MONGODB_URL = ""
# MONGODB_DATABASE = ""

########################## LLM Config ###########################

GENERATION_BACKEND = "COHERE"
EMBEDDING_BACKEND = "COHERE"

OPENAI_API_KEY = "---------"
OPENAI_API_URL = "---------" 
COHERE_API_KEY = "---------"

GENERATION_MODEL_ID_LITERAL = ["command-a-03-2025", "gemma3:4b-it-fp16", "gpt-3.5-turbo-0125"]
GENERATION_MODEL_ID = "command-a-03-2025" 
EMBEDDING_MODEL_ID = "embed-multilingual-v3.0"
EMBEDDING_MODEL_SIZE = 1024

INPUT_DEFAULT_MAX_CHARACTERS = 1024
GENERATION_DEFAULT_MAX_TOKENS = 200
GENERATION_DEFAULT_TEMPERATURE = 0.1

########################## VectorDB Config ###########################

VECTOR_DB_BACKEND_LITERAL = ["PGVECTOR", "QDRANT"]
VECTOR_DB_BACKEND = "PGVECTOR"
VECTOR_DB_PATH = "qdrant_db"
VECTOR_DB_DISTANCE_METHOD = "cosine"
VECTOR_DB_PGVEC_INDEX_THRESHOLD = 70

########################## Template Config ###########################

PRIMARY_LANG = "en"
DEFAULT_LANG = "en"