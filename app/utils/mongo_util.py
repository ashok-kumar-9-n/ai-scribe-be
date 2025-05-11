import datetime
from pymongo import MongoClient, ReturnDocument
from app.constants.config import MONGODB_URI, DATABASE_NAME
import re


class MongoDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            cls._instance._init_connection(MONGODB_URI)
            cls._instance.default_db = DATABASE_NAME
        return cls._instance

    def _init_connection(self, uri):
        self.client = MongoClient(uri)
        self.dbs = {}

    def get_db(self, db_name=None):
        """
        Get a specific database instance. Use the default database if `db_name` is None.
        """
        db_name = db_name or self.default_db
        if db_name not in self.dbs:
            self.dbs[db_name] = self.client[db_name]
        return self.dbs[db_name]

    def get_collection(self, collection_name, db_name=None):
        """
        Get a specific collection from the specified database.
        If `db_name` is None, use the default database.
        """
        return self.get_db(db_name)[collection_name]

    def insert_one(self, collection_name, data, db_name=None):
        return self.get_collection(collection_name, db_name).insert_one(data).inserted_id

    def find_one(self, collection_name, query, projection=None, db_name=None):
        return self.get_collection(collection_name, db_name).find_one(query, projection)

    def find(self, collection_name, query, projection=None, db_name=None):
        return list(self.get_collection(collection_name, db_name).find(query, projection))

    def update_one(
        self, collection_name, query, update_data, upsert=False, array_filters=None, db_name=None
    ):
        collection = self.get_collection(collection_name, db_name)
        return collection.update_one(
            query, update_data, upsert=upsert, array_filters=array_filters
        )
    
    def find_one_and_update(
        self, collection_name, query, update_data, upsert=False, array_filters=None, db_name=None, return_before=True
    ):
        collection = self.get_collection(collection_name, db_name)
        
        return collection.find_one_and_update(
            query, update_data, upsert=upsert, array_filters=array_filters, return_document=ReturnDocument.BEFORE if return_before else ReturnDocument.AFTER
        )
    
    def update_many(self, collection_name, query, update_data, db_name=None, array_filters=None):
        collection = self.get_collection(collection_name, db_name)
        if array_filters:
            return collection.update_many(query, update_data, array_filters=array_filters)
        else:
            return collection.update_many(query, update_data)

    def delete_one(self, collection_name, query, db_name=None):
        return self.get_collection(collection_name, db_name).delete_one(query)

    def aggregate(self, collection_name, pipeline, db_name=None):
        collection = self.get_collection(collection_name, db_name)
        return list(collection.aggregate(pipeline))

    def add_timestamps_on_insert(self, data):
        data["created_on"] = datetime.datetime.now()
        data["updated_on"] = datetime.datetime.now()
        return data

    def update_timestamp_on_update(self, data):
        data['$set'] = data.get('$set', {})
        data["$set"]["updated_on"] = datetime.datetime.now()
        return data
    
    def insert_many(self, collection_name, data, db_name=None):
        return self.get_collection(collection_name, db_name).insert_many(data)
    

mongo_util = MongoDB()
