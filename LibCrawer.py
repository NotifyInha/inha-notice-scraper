import numpy as np
import pytz
import MongodbWrapper as mw
from DataModel import Notice
from datetime import datetime
import feedparser
from bs4 import BeautifulSoup as bs
from html2text import html2text


def guessCategory(title : str, content : str):
    for i in category_list:
        if i in title + " " +content:
            return i
    return "기타"


def getList(url):
    local_timezone = pytz.timezone('Asia/Seoul')
    feed = feedparser.parse(url)
    for i in feed['entries']:
        title = i['title']
        published_date = i['updated']
        published_date = datetime.fromisoformat(published_date).astimezone(local_timezone).isoformat()
        content = html2text(i['content'][0].value)
        url = i['link']
        source = "정석학술도서관"
        category = guessCategory(title, content)
        notice = Notice(title, content, [], [], url, category, source, published_date)
        


def Run():
    global db
    global local_timezone
    global source_set
    global category_list
    
    db = mw.MongodbWrapper()
    category_list = np.loadtxt("categoryList.csv", dtype=str)
    url = "https://lib.inha.ac.kr/rss/blog.php?g=897555"
    getList(url)
    
if __name__ == "__main__":
    Run()
    
