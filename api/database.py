import os
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId

class Database:
    def __init__(self, debug=False):
        # Load environment variables
        load_dotenv()
        
        # Get MongoDB connection string from environment or use default
        self.uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.client = None
        self.db = None
        self.debug = debug
        
        # Automatically connect when initializing
        self.connect()
        
    def connect(self):
        """
        Connect to MongoDB database
        """
        try:
            if self.debug:
                print(f"Connecting to MongoDB at: {self.uri}")
            
            self.client = MongoClient(self.uri)
            self.db = self.client.ai_evaluator
            
            if self.debug:
                print(f"Successfully connected to MongoDB")
                print(f"Available databases: {self.client.list_database_names()}")
            return True
        except Exception as e:
            if self.debug:
                print(f"Failed to connect to MongoDB: {str(e)}")
            raise e
            
    def close(self):
        """
        Close the database connection
        """
        if self.client:
            self.client.close()
            if self.debug:
                print("MongoDB connection closed")
    
    def insert_one(self, collection_name, document):
        """
        Insert a single document into a collection
        """
        if self.db is None:
            raise Exception("Database not connected. Call connect() first.")
        return self.db[collection_name].insert_one(document)
        
    def insert_many(self, collection_name, documents):
        """
        Insert multiple documents into a collection
        """
        if self.db is None:
            raise Exception("Database not connected. Call connect() first.")
        return self.db[collection_name].insert_many(documents)
    
    def find_one(self, collection_name, query, projection=None):
        """
        Find a single document matching the query
        """
        if self.db is None:
            raise Exception("Database not connected. Call connect() first.")
        return self.db[collection_name].find_one(query, projection)
    
    def find(self, collection_name, query, projection=None, sort=None, limit=0):
        """
        Find all documents matching the query
        """
        if self.db is None:
            raise Exception("Database not connected. Call connect() first.")
        cursor = self.db[collection_name].find(query, projection)
        
        if sort:
            cursor = cursor.sort(sort)
        
        if limit > 0:
            cursor = cursor.limit(limit)
            
        return list(cursor)
    
    def update_one(self, collection_name, query, update, upsert=False):
        """
        Update a single document matching the query
        """
        if self.db is None:
            raise Exception("Database not connected. Call connect() first.")
        return self.db[collection_name].update_one(query, update, upsert=upsert)
    
    def update_many(self, collection_name, query, update, upsert=False):
        """
        Update multiple documents matching the query
        """
        if self.db is None:
            raise Exception("Database not connected. Call connect() first.")
        return self.db[collection_name].update_many(query, update, upsert=upsert)
    
    def delete_one(self, collection_name, query):
        """
        Delete a single document matching the query
        """
        if self.db is None:
            raise Exception("Database not connected. Call connect() first.")
        return self.db[collection_name].delete_one(query)
    
    def delete_many(self, collection_name, query):
        """
        Delete multiple documents matching the query
        """
        if self.db is None:
            raise Exception("Database not connected. Call connect() first.")
        return self.db[collection_name].delete_many(query)