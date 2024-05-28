from abc import ABC, abstractmethod

from DataModel import Notice
class DatabaseWrapper(ABC):
    @abstractmethod
    def ping(self) -> bool:
        pass

    @abstractmethod
    def upload(self,data :Notice):
        pass