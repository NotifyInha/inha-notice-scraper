from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from DataModel import Notice
import certifi
from Config import connection_string #db 정보

class MongodbWrapper:
    def __init__(self):
        # Read the connection string from a file
        
        uri = connection_string

        # Create a new client and connect to the server
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

    def insert(self, data :Notice):
        # Get the database
        db = self.client["inha_notice"]
        # Get the collection
        collection = db["notice"]
        # Insert the data
        if not self._check_duplicate(data):
            collection.insert_one(data.to_dict())
        
    def need_update(self, data :Notice):
        db = self.client["inha_notice"]
        collection = db["notice"]
        e = collection.find_one({"url": data.url}) 
        if e is not None:
            item = Notice.from_dict(e)
            if item.published_date != data.published_date:
                return item
            return False
        return None
                
    def search_by_url(self, url :str):
        db = self.client["inha_notice"]
        collection = db["notice"]
        e = collection.find_one({"url": url})
        if e is not None:
            item = Notice.from_dict(e)
            return item
        return None

    def update(self, data :Notice):
        if data.id is None:
            raise ValueError("The data must have an id to update")
        db = self.client["inha_notice"]
        collection = db["notice"]

        result = collection.update_one({"_id": data.id}, {"$set": data.to_dict()})
        return result.modified_count > 0

    def get_all(self):
        db = self.client["inha_notice"]
        collection = db["notice"]
        return collection.find()
        
    def _check_duplicate(self, data :Notice):
        db = self.client["inha_notice"]
        collection = db["notice"]
        return collection.find_one({"url": data.url}) is not None

if __name__ == "__main__":
    mw = MongodbWrapper()
    test = Notice.from_dict(mw.get_all()[0])
    test.published_date = "2024-03-01T00:00:00+09:00"
    test.title = "test"
    test.content = "test"
    mw.update(test)
    
