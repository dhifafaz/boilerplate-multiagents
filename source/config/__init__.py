from pydantic.v1 import BaseSettings
from dotenv import load_dotenv
from typing import Optional 
import os, sys
path_this = os.path.dirname(os.path.abspath(__file__))
path_project = os.path.dirname(os.path.join(path_this, '..'))
path_root = os.path.dirname(os.path.join(path_this, '../..'))
sys.path.append(path_root)
sys.path.append(path_project)
sys.path.append(path_this)

class AppConfig(BaseSettings):
    QDRANT_URI: str
    QDRANT_PORT: int
    QDRANT_API_KEY: str
    QDRANT_COLLECTION_NAME: str

    CLUSTERING_BASE_URL: str
    CLUSTERING_RELEVANCE: int
    CLUSTERING_MODEL_NAME: str
    CLUSTERING_METRIC: str
    CLUSTERING_N_CLUSTERS: int
    
    LLM_BASE_URL: str
    LLM_MODEL_NAME: str
    LLM_API_KEY: str
    LLM_PROVIDER: str

    AGENT_STAGE: str
    AGENT_NAME: str

    EMBEDDINGS_BASE_URL: str
    EMBEDDINGS_MODEL_NAME: str
    
    LLM_TEMPERATURE: float
    LLM_MAX_TOKENS: int
    LLM_TIMEOUT: int

    OPENAI_API_KEY: str
    OPENAI_MODEL_NAME: str
    OPENAI_API_BASE_URL: str
    
    # Optional database settings
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: Optional[int] = None

    MONGO_DB_USERNAME: Optional[str] = None
    MONGO_DB_PASSWORD: Optional[str] = None
    MONGO_DB_HOSTS: Optional[str] = None
    MONGO_DB_NAME: Optional[str] = None

    class Config:
        env_file = os.path.join(path_root, ".env")

    load_dotenv(".env", override=True)

settings = AppConfig()