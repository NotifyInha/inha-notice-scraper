import pytz
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import utils.DatabaseFactory as DBFactory
from DataModel import Notice
from datetime import datetime
import numpy as np
import time 
from io import StringIO
import sys
import utils.Logger as Logger

LOG_PATH = "./BasicCrawler.log"
RICH_FORMAT = "[%(filename)s:%(lineno)s] >> %(message)s"
FILE_HANDLER_FORMAT = "[%(asctime)s]\\t%(levelname)s\\t[%(filename)s:%(funcName)s:%(lineno)s]\\t>> %(message)s"

MANUAL = False

def guessCategory(title : str, content : str):
    for i in category_list:
        if i in title + " " +content:
            return i
    return "기타"

def getData(data : pd.Series):
    res = requests.get("https://" + data["links"])
    soup = bs(res.text, "html.parser")
    text = soup.select_one("div.artclView")
    images_item = soup.select("div.artclView img")
    attached_item = soup.select("dd.artclInsert li")
    modified = soup.select_one(".artclViewHead dl:nth-child(2) dd")
    
    if modified is not None:
        data["작성일"] = modified.text

    content = text.text#기본 데이터 가져오기
    content = content.replace("\xa0", u" ")

    images = []
    if images_item != None:
        for img in images_item:
            images.append(img["src"])

    attached = []
    if attached_item != None:
        for item in attached_item:
            attached.append({"text": item.text.strip(), "link": getHost("https://" + data["links"]) + item.find("a")["href"]})
    

    source = data["source"]
    
    title = data["제목"]
    title = title.replace("\xa0", u" ")
    url = data["links"]
    if data["제목"].strip()[0] == "[":#카테고리 유추
        category = data["제목"].split("]")[0][1:]
    else:
        category = guessCategory(title, content)
    published_date = datetime.strptime(preprocessDate(data["작성일"]), "%Y.%m.%d").astimezone(local_timezone).isoformat()
    logger.info(f"Get Data: {title} {published_date}")
    notice = Notice(title, content, images, attached, url, category, source, published_date)
    return notice

def getHost(url : str):
    return url.split("/")[2]

def preprocessDate(url : str):
    return url.strip().rstrip(".")

def getList(url : str, source : str):
    res = requests.get(url)
    soup = bs(res.text, "html.parser")
    table_html = soup.select_one("table.artclTable")
    table = pd.read_html(StringIO(str(table_html)))
    links = []
    for tr in table_html.findAll("tr"):
        trs = tr.findAll("td")
        for each in trs:
            try:
                link = each.find('a')['href']
                links.append(getHost(url) + link)
            except:
                pass
    table = table[0]
    table["links"] = links
    today = datetime.today().astimezone(local_timezone)
    for idx, row in table.iterrows():
        diff = today - datetime.strptime(preprocessDate(row["작성일"]), "%Y.%m.%d").astimezone(local_timezone)
        if diff.days > 7:#일주일 전의 데이터는 무시
            continue
        #자세한 데이터를 가져와서
        row["source"] = source
        data = getData(row)
        target = db.upload(data)
        if target == True:#새로운 데이터
            logger.info(f"{data.source}의 공지 {data.title}을 추가합니다.")
        elif target == False:# 이미 최신 데이터
            logger.info(f"{data.source}의 공지 {data.title}은 이미 최신 데이터입니다.")  
        else:#업데이트 필요
            logger.info(f"{data.source}의 공지 {data.title}을 업데이트합니다.")

        # time.sleep(0.5)


def Run():
    global db
    global local_timezone
    global source_set
    global category_list
    
    factory = DBFactory.BackendFactory()
    db = factory.get_database()
    if not db.ping():
        logger.error("server connection failed try connect directly")
        factory = DBFactory.MongoDBFactory()
        db = factory.get_database()
        if not db.ping():
            logger.error("db connection failed")
            return
        
    logger.info("db connected")
    category_list = np.loadtxt("categoryList.csv", dtype=str, encoding="utf-8")
    local_timezone = pytz.timezone('Asia/Seoul')

    if len(sys.argv) == 3:
        getList(sys.argv[1], sys.argv[2])
        
    else: 
        url_list = pd.read_csv("urlList.csv", dtype=str)
        for idx, data in url_list.iterrows():
            try:
                getList(data['url'], data['source'])
            except Exception as e:
                logger.error(f"Fetch Error: {data['source']}", exc_info=sys.exc_info())
            time.sleep(1)

if __name__ == "__main__":
    logger = Logger.set_logger(LOG_PATH, RICH_FORMAT, FILE_HANDLER_FORMAT)
    sys.excepthook = Logger.handle_exception

    Run()
