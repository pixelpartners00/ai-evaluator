import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

class Database:
    """
    Handles connections to MongoDB and database operations.
    """
    def __init__(self, debug=False):
        """
        Initialize the database connection.
        
        Args:
            debug (bool): Whether to print debug information
        """
        # Load environment variables
        load_dotenv()
        
        self.debug = debug
        self.uri = os.getenv("MONGODB_URI")
        self.db_name = os.getenv("MONGODB_DB_NAME", "ai_evaluator")
        self.client = None
        self.db = None
        
        if not self.uri:
            raise ValueError("MONGODB_URI is not set in the .env file")
        
        # Replace <db_password> placeholder with actual password
        db_password = os.getenv("MONGODB_PASSWORD")
        if db_password:
            self.uri = self.uri.replace("<db_password>", db_password)
    
    def connect(self):
        """
        Connect to the MongoDB database.
        
        Returns:
            pymongo.database.Database: MongoDB database object
        
        Raises:
            ConnectionError: If connection to MongoDB fails
        """
        try:
            if self.debug:
                print(f"Connecting to MongoDB with URI: {self.uri[:20]}...")
            
            # Create a MongoDB client
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            
            # Check if the connection is successful
            self.client.admin.command('ping')
            
            # Get the database
            self.db = self.client[self.db_name]
            
            if self.debug:
                print(f"Connected to MongoDB database: {self.db_name}")
            
            return self.db
        
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            error_msg = f"Failed to connect to MongoDB: {str(e)}"
            if self.debug:
                print(error_msg)
            raise ConnectionError(error_msg)
    
    def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            if self.debug:
                print("MongoDB connection closed")
    
    def get_collection(self, collection_name):
        """
        Get a MongoDB collection.
        
        Args:
            collection_name (str): Name of the collection
            
        Returns:
            pymongo.collection.Collection: MongoDB collection
        """
        if self.db is None:
            self.connect()
        
        return self.db[collection_name]
    
    def insert_one(self, collection_name, document):
        """
        Insert a single document into a collection.
        
        Args:
            collection_name (str): Name of the collection
            document (dict): Document to insert
            
        Returns:
            pymongo.results.InsertOneResult: Result of the insert operation
        """
        collection = self.get_collection(collection_name)
        return collection.insert_one(document)
    
    def find_one(self, collection_name, query):
        """
        Find a single document in a collection.
        
        Args:
            collection_name (str): Name of the collection
            query (dict): Query to find the document
            
        Returns:
            dict: Found document or None
        """
        collection = self.get_collection(collection_name)
        return collection.find_one(query)
    
    def find(self, collection_name, query=None, projection=None):
        """
        Find documents in a collection.
        
        Args:
            collection_name (str): Name of the collection
            query (dict, optional): Query to find documents
            projection (dict, optional): Fields to include/exclude
            
        Returns:
            pymongo.cursor.Cursor: Cursor to the documents
        """
        collection = self.get_collection(collection_name)
        return collection.find(query or {}, projection)
    
    def update_one(self, collection_name, query, update):
        """
        Update a single document in a collection.
        
        Args:
            collection_name (str): Name of the collection
            query (dict): Query to find the document
            update (dict): Update operations
            
        Returns:
            pymongo.results.UpdateResult: Result of the update operation
        """
        collection = self.get_collection(collection_name)
        return collection.update_one(query, update)
    
    def delete_one(self, collection_name, query):
        """
        Delete a single document from a collection.
        
        Args:
            collection_name (str): Name of the collection
            query (dict): Query to find the document
            
        Returns:
            pymongo.results.DeleteResult: Result of the delete operation
        """
        collection = self.get_collection(collection_name)
        return collection.delete_one(query)
