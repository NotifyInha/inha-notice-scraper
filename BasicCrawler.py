import asyncio
import pytz
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import utils.DatabaseFactory as DBFactory
from DataModel import Notice, NoticeCreate
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
IGNORE_DAYS = 5

def guessCategory(title : str, content : str):
    for i in category_list:
        if i in title + " " +content:
            return i
    return "기타"

def getData(data : pd.Series):
    res = requests.get(data["links"])
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
    if attached_item != []:
        for item in attached_item:
            attached.append({"text": item.text.strip(), "link": getHost(data["links"]) + item.find("a")["href"]})
    

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
    notice = NoticeCreate(title=title, content=content, images=images, attached=attached, url=url, category=category, source=source, published_date=published_date, is_sent_notification=False)
    return notice

def getHost(url : str):
    return '/'.join(url.split("/")[:3])

def preprocessDate(url : str):
    return url.strip().rstrip(".")

async def process_notice(notice):
    try:
        target = await db.upload(notice)
        if target == True:
            logger.info(f"{notice.source}의 공지 {notice.title}을 추가합니다.")
        elif target == False:
            logger.info(f"{notice.source}의 공지 {notice.title}은 이미 최신 데이터입니다.")
        else:
            logger.info(f"{notice.source}의 공지 {notice.title}을 업데이트합니다.")
    except Exception as e:
        logger.error(f"공지 처리 중 오류 발생: {e}")


async def getList(url : str, source : str):
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
        if diff.days > IGNORE_DAYS:#일주일 전의 데이터는 무시
            continue
        #자세한 데이터를 가져와서
        row["source"] = source
        data = getData(row)
        asyncio.create_task(process_notice(data))

        await asyncio.sleep(1)

async def Run():
    global db
    global local_timezone
    global source_set
    global category_list

    if len(sys.argv) == 3:
        if sys.argv[1] == "nodb":
            logger.info("No db Flag is set")
            db = DBFactory.LocalFactory().get_database(sys.argv[2])
    else:
        factory = DBFactory.BackendFactory()
        db = factory.get_database()
        if not await db.ping():
            logger.error("server connection failed try connect directly")
            factory = DBFactory.MongoDBFactory()
            db = factory.get_database()
            if not await db.ping():
                logger.error("db connection failed")
                return
        
    logger.info("db connected")
    category_list = np.loadtxt("categoryList.csv", dtype=str, encoding="utf-8")
    local_timezone = pytz.timezone('Asia/Seoul')


    url_list = pd.read_csv("urlList.csv", dtype=str)
    for idx, data in url_list.iterrows():
        try:
            await getList(data['url'], data['source'])
        except Exception as e:
            logger.error(f"Fetch Error: {data['source']}", exc_info=sys.exc_info())
        await asyncio.sleep(1)
    if len(sys.argv) == 3:
        if sys.argv[1] == "nodb":
            db.save()

if __name__ == "__main__":
    logger = Logger.set_logger(LOG_PATH, RICH_FORMAT, FILE_HANDLER_FORMAT)
    sys.excepthook = Logger.handle_exception

    asyncio.run(Run())
