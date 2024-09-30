from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from DataModel import Notice
if os.path.exists('Config.py'):
    from Config import server_address
else:
    server_address = os.environ['server_address']
from utils.DatabaseWrapper import DatabaseWrapper

#TODO : Mongodb controller를 Motor로 변경
#Mongodb에 직접 접속하여 데이터를 추가하거나 업데이트하는 클래스
class MongodbWrapper(DatabaseWrapper):
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

    def ping(self) -> bool:
        try:
            self.client.admin.command('ping')
            return True
        except:
            return False
        
    def upload(self,data :Notice):
        target = self.need_update(data)
        if target is None:#새로운 데이터
            self.insert(data)
            return True
        elif target == False:# 이미 최신 데이터
            return False    
        else:#업데이트 필요
            data.id = target.id
            self.update(data)
            return data
        

    def insert(self, data :Notice):
        # Get the database
        db = self.client["inha_notice"]
        # Get the collection
        collection = db["notice"]
        # Insert the data
        if not self._check_duplicate(data):
            collection.insert_one(data.model_dump())
        
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

    async def update(self, data :Notice):
        if data.id is None:
            raise ValueError("The data must have an id to update")
        db = self.client["inha_notice"]
        collection = db["notice"]

        result = collection.update_one({"_id": data.id}, {"$set": data.model_dump()})
        return result.modified_count > 0
        
    def _check_duplicate(self, data :Notice):
        db = self.client["inha_notice"]
        collection = db["notice"]
        return collection.find_one({"url": data.url}) is not None

if __name__ == "__main__":
    pass
    
