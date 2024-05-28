from abc import ABC, abstractmethod
from utils.BackendWrapper import BackendWrapper
from utils.MongodbWrapper import MongodbWrapper

class DataBaseFactory(ABC):
    @abstractmethod
    def get_database(self):
        pass

class MongoDBFactory(DataBaseFactory):
    def get_database(self):
        return MongodbWrapper()
    
class BackendFactory(DataBaseFactory):
    def get_database(self):
        return BackendWrapper()