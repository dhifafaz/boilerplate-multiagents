"""
Unit tests for database services.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from qdrant_client import AsyncQdrantClient, QdrantClient

from source.db_clients.qdrant_scv import AsyncQdrantService, QdrantService
from source.db_clients.redis_svc import RedisService
from source.db_clients.mongo_svc import StellarConfigDB


class TestQdrantServices:
    """Test suite for Qdrant service classes."""
    
    @patch('source.db_clients.qdrant_scv.AsyncQdrantClient')
    def test_async_qdrant_service_singleton(self, mock_client):
        """Test AsyncQdrantService singleton pattern."""
        # Reset singleton
        AsyncQdrantService.instance = None
        
        service1 = AsyncQdrantService()
        service2 = AsyncQdrantService()
        
        assert service1 is service2
        mock_client.assert_called_once()
    
    @patch('source.db_clients.qdrant_scv.QdrantClient')
    def test_qdrant_service_singleton(self, mock_client):
        """Test QdrantService singleton pattern."""
        # Reset singleton
        QdrantService.instance = None
        
        service1 = QdrantService()
        service2 = QdrantService()
        
        assert service1 is service2
        mock_client.assert_called_once()


class TestRedisService:
    """Test suite for RedisService."""
    
    @patch('source.db_clients.redis_svc.redis.Redis')
    def test_redis_service_singleton(self, mock_redis):
        """Test RedisService singleton pattern."""
        # Reset singleton
        RedisService.instance = None
        
        service1 = RedisService()
        service2 = RedisService()
        
        assert service1 is service2
        mock_redis.assert_called_once()


class TestStellarConfigDB:
    """Test suite for MongoDB service."""
    
    @patch('source.db_clients.mongo_svc.MongoClient')
    def test_mongo_singleton(self, mock_client):
        """Test MongoDB singleton pattern."""
        # Reset singleton
        StellarConfigDB._instance = None
        StellarConfigDB._is_initialized = False
        
        mock_db = Mock()
        mock_client.return_value = mock_db
        mock_db.admin.command = Mock(return_value=True)
        
        db1 = StellarConfigDB()
        db2 = StellarConfigDB()
        
        assert db1 is db2
    
    @patch('source.db_clients.mongo_svc.MongoClient')
    def test_get_all_collections(self, mock_client):
        """Test retrieving all collections."""
        # Reset singleton
        StellarConfigDB._instance = None
        StellarConfigDB._is_initialized = False
        
        mock_db_instance = Mock()
        mock_client.return_value = mock_db_instance
        mock_db_instance.admin.command = Mock(return_value=True)
        
        mock_database = Mock()
        mock_database.list_collection_names = Mock(return_value=["collection1", "collection2"])
        mock_db_instance.__getitem__ = Mock(return_value=mock_database)
        
        db = StellarConfigDB()
        db.db = mock_database
        
        collections = db.get_all_collections()
        
        assert len(collections) == 2
        assert "collection1" in collections
    
    @patch('source.db_clients.mongo_svc.MongoClient')
    def test_get_by_id(self, mock_client):
        """Test retrieving document by ID."""
        # Reset singleton
        StellarConfigDB._instance = None
        StellarConfigDB._is_initialized = False
        
        mock_db_instance = Mock()
        mock_client.return_value = mock_db_instance
        mock_db_instance.admin.command = Mock(return_value=True)
        
        mock_collection = Mock()
        mock_collection.find_one = Mock(return_value={"_id": "test-id", "data": "test"})
        
        mock_database = Mock()
        mock_database.__getitem__ = Mock(return_value=mock_collection)
        mock_db_instance.__getitem__ = Mock(return_value=mock_database)
        
        db = StellarConfigDB()
        db.db = mock_database
        
        doc = db.get_by_id("test_collection", "test-id")
        
        assert doc is not None
        assert doc["_id"] == "test-id"
    
    @patch('source.db_clients.mongo_svc.MongoClient')
    def test_create_by_id(self, mock_client):
        """Test creating document with ID."""
        # Reset singleton
        StellarConfigDB._instance = None
        StellarConfigDB._is_initialized = False
        
        mock_db_instance = Mock()
        mock_client.return_value = mock_db_instance
        mock_db_instance.admin.command = Mock(return_value=True)
        
        mock_result = Mock()
        mock_result.inserted_id = "test-id"
        
        mock_collection = Mock()
        mock_collection.insert_one = Mock(return_value=mock_result)
        
        mock_database = Mock()
        mock_database.__getitem__ = Mock(return_value=mock_collection)
        mock_db_instance.__getitem__ = Mock(return_value=mock_database)
        
        db = StellarConfigDB()
        db.db = mock_database
        
        inserted_id = db.create_by_id("test_collection", "test-id", {"data": "test"})
        
        assert inserted_id == "test-id"
    
    @patch('source.db_clients.mongo_svc.MongoClient')
    def test_update_by_id(self, mock_client):
        """Test updating document by ID."""
        # Reset singleton
        StellarConfigDB._instance = None
        StellarConfigDB._is_initialized = False
        
        mock_db_instance = Mock()
        mock_client.return_value = mock_db_instance
        mock_db_instance.admin.command = Mock(return_value=True)
        
        mock_result = Mock()
        mock_result.modified_count = 1
        
        mock_collection = Mock()
        mock_collection.update_one = Mock(return_value=mock_result)
        
        mock_database = Mock()
        mock_database.__getitem__ = Mock(return_value=mock_collection)
        mock_db_instance.__getitem__ = Mock(return_value=mock_database)
        
        db = StellarConfigDB()
        db.db = mock_database
        
        result = db.update_by_id("test_collection", "test-id", {"data": "updated"})
        
        assert result is True
    
    @patch('source.db_clients.mongo_svc.MongoClient')
    def test_delete_by_id(self, mock_client):
        """Test deleting document by ID."""
        # Reset singleton
        StellarConfigDB._instance = None
        StellarConfigDB._is_initialized = False
        
        mock_db_instance = Mock()
        mock_client.return_value = mock_db_instance
        mock_db_instance.admin.command = Mock(return_value=True)
        
        mock_result = Mock()
        mock_result.deleted_count = 1
        
        mock_collection = Mock()
        mock_collection.delete_one = Mock(return_value=mock_result)
        
        mock_database = Mock()
        mock_database.__getitem__ = Mock(return_value=mock_collection)
        mock_db_instance.__getitem__ = Mock(return_value=mock_database)
        
        db = StellarConfigDB()
        db.db = mock_database
        
        result = db.delete_by_id("test_collection", "test-id")
        
        assert result is True
