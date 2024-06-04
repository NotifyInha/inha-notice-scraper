import asyncio
from datetime import datetime
from typing import Optional
import pytz
from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

db_tz = pytz.timezone('UTC')
local_timezone = pytz.timezone('Asia/Seoul')
PyObjectId = Annotated[str, BeforeValidator(str)]

def getNow():
    return datetime.now().astimezone(local_timezone)

def validate_date(value: str) -> datetime:
    if type(value) == str:
        value = datetime.fromisoformat(value)
    value = db_tz.localize(value)
    value.astimezone(local_timezone)
    return value.isoformat()

class NoticeGet(BaseModel):
    title:Optional[str] = None
    url:Optional[str] = None
    category:Optional[str] = None
    source:Optional[str] = None
    published_date:Optional[datetime] = None
    id:PyObjectId = Field(alias="_id", default=None)

class NoticeUpdate(BaseModel):
    title:Optional[str] = None
    url:Optional[str] = None
    category:Optional[str] = None
    source:Optional[str] = None
    published_date:Optional[datetime] = None
    content:Optional[str] = None
    image:Optional[list] = None
    attached:Optional[list] = None
    is_sent_notification:Optional[bool] = False
    

class NoticeCreate(BaseModel):
    title:str
    url:str
    category:str
    source:str
    published_date:datetime
    content:Optional[str] = ""
    images:Optional[list] = []
    attached:Optional[list] = []
    is_sent_notification:Optional[bool] = False


class Notice(BaseModel):
    title:str
    url:str
    category:str
    source:str
    published_date:datetime
    scraped_date: datetime = Field(default_factory=getNow)
    id: PyObjectId = Field(alias="_id", default=None)
    content:str
    images:list
    attached:list
    is_sent_notification:bool

    def __str__(self):
        return f"title: {self.title}, content: {self.content}, image: {self.image}, attached: {self.attached}, url: {self.url}, category: {self.category}, source: {self.source}, published_date: {self.published_date}, scraped_date: {self.scraped_date}, is_sent_notification: {self.is_sent_notification}"

if __name__ == "__main__":
    notice = Notice("title", "content", [],[],"url", "category", "source", "published_date")
    print(notice.model_dump())
    print(notice)