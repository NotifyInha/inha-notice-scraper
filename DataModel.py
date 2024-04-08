from datetime import datetime
import pytz

class Notice:
    local_timezone = pytz.timezone('Asia/Seoul')
    def __init__(self, title, content, image, attached, url, category, source, published_date, scraped_date = None, is_sent_notification = False, id = None):
        self.title = title
        self.content = content
        self.image = image
        self.attached = attached
        self.url = url
        self.category = category
        self.source = source
        self.published_date = published_date
        if scraped_date is None:
            self.scraped_date = datetime.now().astimezone(Notice.local_timezone).isoformat()
        else:
            self.scraped_date = scraped_date
        self.is_sent_notification = is_sent_notification
        self.id = id

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
                   scraped_date = scraped_date, is_sent_notification = is_sent_notification, id = id)


    def __str__(self):
        return f"title: {self.title}, content: {self.content}, image: {self.image}, attached: {self.attached}, url: {self.url}, category: {self.category}, source: {self.source}, published_date: {self.published_date}, scraped_date: {self.scraped_date}, is_sent_notification: {self.is_sent_notification}"
    

if __name__ == "__main__":
    notice = Notice("title", "content", [],[],"url", "category", "source", "published_date")
    print(notice.to_dict())
    print(notice)