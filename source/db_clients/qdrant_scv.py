import os, sys
from configparser import ConfigParser
from loguru import logger

from qdrant_client import QdrantClient, AsyncQdrantClient
from source.config import settings

class AsyncQdrantService:

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = AsyncQdrantClient(
                url=settings.QDRANT_URI,
                port=settings.QDRANT_PORT,
                api_key=settings.QDRANT_API_KEY,
                https=False,
                timeout=100
            )
        return cls.instance

class QdrantService:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = QdrantClient(
                url=settings.QDRANT_URI,
                port=settings.QDRANT_PORT,
                api_key=settings.QDRANT_API_KEY,
                https=False,
                timeout=100
            )
        return cls.instance