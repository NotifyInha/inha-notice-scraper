from abc import ABC, abstractmethod

from DataModel import Notice
class DatabaseWrapper(ABC):
    @abstractmethod
    async def ping(self) -> bool:
        pass

    @abstractmethod
    async def upload(self,data :Notice):
        pass