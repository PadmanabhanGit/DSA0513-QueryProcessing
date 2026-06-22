import os
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(__file__)
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

# Database configuration - update these or set as environment variables or in .env
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "password"),
    "database": os.environ.get("DB_NAME", "ai_query_optimizer"),
    "port": int(os.environ.get("DB_PORT", 3306)),
}

MODEL_PATH = os.path.join(PROJECT_ROOT, "query_model.pkl")
DATASET_PATH = os.path.join(PROJECT_ROOT, "dataset", "query_dataset.csv")
