import os
from DataModel import Notice, NoticeCreate, NoticeGet
from utils.DatabaseWrapper import DatabaseWrapper
import pandas as pd

class LocalOutputWrapper(DatabaseWrapper):
    def __init__(self, address: str):
        self.address = address
        self.data = []

    async def ping(self) -> bool:
        return True

    async def upload(self, data: Notice):
        items: NoticeGet = await self.check_data(data)
        if items is False:
            self.data.append(NoticeGet(**data.model_dump()).model_dump())
            return True
        else:
            # 업데이트 작업 수행
            for i, item in enumerate(self.data):
                if item["url"] == data.url:
                    self.data[i] = NoticeGet(**data.model_dump()).model_dump()
                    break
            return data

    async def check_data(self, data: Notice) -> bool:
        for item in self.data:
            if item["url"] == data.url:
                return NoticeGet(**item)
        return False

    def save_to_csv(self):
        if not self.data:
            return
        
        df = pd.DataFrame(self.data)
        file_path = self.get_file_path(".csv")
        df.to_csv(file_path, index=False)

    def save_to_txt(self):
        if not self.data:
            return
        
        file_path = self.get_file_path(".txt")
        with open(file_path, "w", encoding="utf-8") as file:
            for item in self.data:
                file.write(f"Title: {item['title']}\n")
                file.write(f"URL: {item['url']}\n")
                file.write(f"Category: {item['category']}\n")
                file.write(f"Source: {item['source']}\n")
                file.write(f"Published Date: {item['published_date']}\n")
                file.write("=" * 50 + "\n")

    def save(self):
        filename = os.path.basename(self.address)
        name, ext = os.path.splitext(filename)

        if ext == ".csv":
            self.save_to_csv()
        else:
            self.save_to_txt()


    def get_file_path(self, extension):
        directory = os.path.dirname(self.address)
        filename = os.path.basename(self.address)
        name, _ = os.path.splitext(filename)
        file_path = os.path.join(directory, f"{name}{extension}")
        return file_path