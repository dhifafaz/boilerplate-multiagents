import os
import sys
import json
import pymongo
from configparser import ConfigParser
from pymongo import MongoClient
from bson.objectid import ObjectId
from hashlib import md5

from loguru import logger

from source.config import settings

class StellarConfigDB:
    _instance = None
    _is_initialized = False
    
    def __new__(cls):
        """Implement singleton pattern"""
        if cls._instance is None:
            cls._instance = super(StellarConfigDB, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize connection only once"""
        if not StellarConfigDB._is_initialized:
            # MongoDB connection parameters
            
            self.username = settings.MONGO_DB_USERNAME
            self.password = settings.MONGO_DB_PASSWORD
            self.hosts = settings.MONGO_DB_HOSTS
            self.database_name = settings.MONGO_DB_NAME
            
            # Create MongoDB connection
            self.client = None
            self.db = None
            self.connect()
            
            StellarConfigDB._is_initialized = True
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            connection_string = f"mongodb://{self.username}:{self.password}@{self.hosts}/{self.database_name}"
            self.client = MongoClient(connection_string)
            
            # Test the connection by running a simple command
            self.client.admin.command('ping')
            
            self.db = self.client[self.database_name]
            logger.debug("Connected to MongoDB successfully")
        except Exception as e:
            logger.debug(f"Error connecting to MongoDB: {str(e)}")
            self.client = None
            self.db = None
    
    def disconnect(self):
        """Close connection to MongoDB"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            StellarConfigDB._is_initialized = False
            logger.debug("Disconnected from MongoDB")
    
    # Collection Management
    
    def get_all_collections(self):
        """
        Retrieve all collections in the database
        
        Returns:
            list: List of all collection names
        """
        try:
            collections = self.db.list_collection_names()
            return collections
        except Exception as e:
            logger.debug(f"Error retrieving collections: {str(e)}")
            return []
    
    def get_all_from_collection(self, collection_name):
        """
        Retrieve all documents from a specific collection
        
        Args:
            collection_name (str): Name of the collection
        
        Returns:
            list: List of all documents in the collection
        """
        try:
            collection = self.db[collection_name]
            documents = list(collection.find())
            return documents
        except Exception as e:
            logger.debug(f"Error retrieving documents from collection '{collection_name}': {str(e)}")
            return []
    
    def get_by_id(self, collection_name, doc_id):
        """
        Retrieve a document by ID from a specific collection
        
        Args:
            collection_name (str): Name of the collection
            doc_id (str): ID of the document to retrieve
        
        Returns:
            dict: Retrieved document or None if not found
        """
        try:
            collection = self.db[collection_name]
            
            # Handle ObjectId or string ID
            if isinstance(doc_id, str) and ObjectId.is_valid(doc_id):
                document = collection.find_one({"_id": ObjectId(doc_id)})
            else:
                document = collection.find_one({"_id": doc_id})
            
            return document
        except Exception as e:
            logger.debug(f"Error retrieving document from collection '{collection_name}': {str(e)}")
            return None
    
    def create_by_id(self, collection_name, doc_id, data):
        """
        Create a new document with a specified ID in a collection
        
        Args:
            collection_name (str): Name of the collection
            doc_id (str): Unique identifier for the document
            data (dict): Document data to insert
        
        Returns:
            str: ID of the inserted document
        """
        try:
            collection = self.db[collection_name]
            
            # Add _id field if it's a valid ID
            if doc_id:
                data['_id'] = doc_id
            
            result = collection.insert_one(data)
            return result.inserted_id
        except pymongo.errors.DuplicateKeyError:
            logger.debug(f"Error: Document with ID '{doc_id}' already exists in collection '{collection_name}'")
            return None
        except Exception as e:
            logger.debug(f"Error creating document in collection '{collection_name}': {str(e)}")
            return None
    
    def update_by_id(self, collection_name, doc_id, update_data):
        """
        Update a document by ID in a specific collection
        
        Args:
            collection_name (str): Name of the collection
            doc_id (str): ID of the document to update
            update_data (dict): New data to update the document with
        
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            collection = self.db[collection_name]
            
            # Handle ObjectId or string ID
            if isinstance(doc_id, str) and ObjectId.is_valid(doc_id):
                result = collection.update_one(
                    {"_id": ObjectId(doc_id)},
                    {"$set": update_data}
                )
            else:
                result = collection.update_one(
                    {"_id": doc_id},
                    {"$set": update_data}
                )
            
            return result.modified_count > 0
        except Exception as e:
            logger.debug(f"Error updating document in collection '{collection_name}': {str(e)}")
            return False
    
    def delete_by_id(self, collection_name, doc_id):
        """
        Delete a document by ID from a specific collection
        
        Args:
            collection_name (str): Name of the collection
            doc_id (str): ID of the document to delete
        
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            collection = self.db[collection_name]
            
            # Handle ObjectId or string ID
            if isinstance(doc_id, str) and ObjectId.is_valid(doc_id):
                result = collection.delete_one({"_id": ObjectId(doc_id)})
            else:
                result = collection.delete_one({"_id": doc_id})
            
            return result.deleted_count > 0
        except Exception as e:
            logger.debug(f"Error deleting document from collection '{collection_name}': {str(e)}")
            return False

# Example usage:
if __name__ == "__main__":
    # First instance creates the connection
    db1 = StellarConfigDB()
    
    # Second instance reuses the same connection
    db2 = StellarConfigDB()
    
    # Both variables point to the same instance
    logger.debug(f"Same instance: {db1 is db2}")  # Should print: Same instance: True