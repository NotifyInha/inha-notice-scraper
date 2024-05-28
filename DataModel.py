from datetime import datetime
from typing import Any
import pytz
from pydantic import BaseModel # type: ignore
from bson import ObjectId

local_timezone = pytz.timezone('Asia/Seoul')

class NoticeLight(BaseModel):
    title:str
    url:str
    category:str
    source:str
    published_date:str
    id:str
    _id:Any

    def __init__(self, title, url, category, source, published_date, _id = None, id=None):
        if id is None:
            id = str(_id)
        else:
            _id = ObjectId(id)
        super().__init__(title=title, url=url, category=category, source=source, published_date=published_date, _id=_id, id=id) 
class Notice(BaseModel):
    title:str
    url:str
    category:str
    source:str
    published_date:str
    scraped_date:str
    id:str
    _id:Any
    content:str
    image:list
    attached:list
    is_sent_notification:bool

    def __init__(self, title, content, images, attached, url, category, source, published_date, scraped_date = None, is_sent_notification = False, _id = None):
        if scraped_date is None:
            scraped_date = datetime.now().astimezone(local_timezone).isoformat()
        if images is None:
            images = []
        if attached is None:
            attached = []
        super().__init__(title=title, content=content, image=images, attached=attached, url=url, category=category, source=source, published_date=published_date, scraped_date=scraped_date, is_sent_notification=is_sent_notification, _id=_id, id=str(_id))

    def to_dict(self):
        return {
            "title": self.title,
            "content": self.content,
            "images": self.image,
            "attached": self.attached,
            "url": self.url,
            "category": self.category,
            "source": self.source,
            "published_date": self.published_date,
            "scraped_date": self.scraped_date,
            "is_sent_notification": self.is_sent_notification
        }
    def to_dict_with_fields(self, *args):
        return {arg: self.__dict__[arg] for arg in args if arg in self.__dict__}
    @classmethod
    def from_dict(cls, data: dict):
        if "_id" in data:#_id가 있으면 id로 저장
            id = data["_id"]
        else:
            id = None
        title = data["title"]
        content = data["content"]
        image = data["images"]
        attached = data["attached"]
        url = data["url"]
        category = data["category"]
        source = data["source"]
        published_date = data["published_date"]
        scraped_date = data["scraped_date"]
        is_sent_notification = data["is_sent_notification"]
        return cls(title, content, image, attached, url, category, source, published_date, 
                   scraped_date = scraped_date, is_sent_notification = is_sent_notification, _id = id)


    def __str__(self):
        return f"title: {self.title}, content: {self.content}, image: {self.image}, attached: {self.attached}, url: {self.url}, category: {self.category}, source: {self.source}, published_date: {self.published_date}, scraped_date: {self.scraped_date}, is_sent_notification: {self.is_sent_notification}"
    


class Page(BaseModel):
    total_count:int
    page:int
    page_size:int
    total_page:int
    notices:list[Notice]

if __name__ == "__main__":
    notice = Notice("title", "content", [],[],"url", "category", "source", "published_date")
    print(notice.to_dict())
    print(notice)