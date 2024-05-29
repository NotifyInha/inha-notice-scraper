import asyncio
from venv import logger
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

# 메인 공지사항 json 주소
# https://lib.inha.ac.kr/pyxis-api/1/bulletin-boards/1/bulletins?nameOption=&isSeq=false&onlyWriter=false&max=10&offset=0
# 각 게시글 json 주소
# https://lib.inha.ac.kr/pyxis-api/1/bulletins/1/{id}?nameOption=undefined
# 실제 게시글 주소
# https://lib.inha.ac.kr/guide/bulletins/notice/{id}?max=10&offset=0


LOG_PATH = "./LibCrawler.log"
RICH_FORMAT = "[%(filename)s:%(lineno)s] >> %(message)s"
FILE_HANDLER_FORMAT = "[%(asctime)s]\\t%(levelname)s\\t[%(filename)s:%(funcName)s:%(lineno)s]\\t>> %(message)s"

IGNORE_DAYS = 3
local_timezone = pytz.timezone('Asia/Seoul')

# 메인 게시판에 접속 실패 시 발생하는 예외
class MainBoardConnectionError(Exception):
    def __init__(self):
        super().__init__('메인 게시판에 접속 실패했습니다.')

# 게시글에 접속 실패 시 발생하는 예외
class BoardConnectionError(Exception):
    def __init__(self, title):
        super().__init__('게시글 ' + title + '에 접속 실패했습니다.')


def ConvertDate(date):
    # 문자열을 datetime 객체로 변환
    date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    # 타임존 정보 설정 (예: 대한민국 표준시)
    korea_tz = pytz.timezone("Asia/Seoul")

    # datetime 객체에 타임존 정보 추가
    localized_date = korea_tz.localize(date_obj)

    # ISO 8601 형식으로 변환
    iso_date_string = localized_date.isoformat()
    return iso_date_string

def GetContentandImage(id):
    res = requests.get(f"https://lib.inha.ac.kr/pyxis-api/1/bulletins/1/{id}?nameOption=undefined")
    data = res.json()
    if data["success"] == False:
        print("Failed to get data")
        raise BoardConnectionError(id)
    data = data["data"]
    html_content = data["content"]
    bs_content = bs(html_content, "html.parser")
    images_html = bs_content.find_all("img")
    images = []
    for img in images_html:
        src = img["src"]
        images.append(src)
    content = bs_content.text
    return content, images

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

async def Run():
    global db

    factory = DBFactory.BackendFactory()
    db = factory.get_database()
    if not await db.ping():
        logger.error("server connection failed try connect directly")
        factory = DBFactory.MongoDBFactory()
        db = factory.get_database()
        if not await db.ping():
            logger.error("db connection failed")
            return
        
    res = requests.get("https://lib.inha.ac.kr/pyxis-api/1/bulletin-boards/1/bulletins?nameOption=&isSeq=false&onlyWriter=false&max=10&offset=0")
    #make res to json
    data = res.json()
    if data["success"] == False:
        print("Failed to get data")
        raise MainBoardConnectionError()
    data = data["data"]
    today = datetime.today().astimezone(local_timezone)
    for item in data['list']:    
        id = item['id']
        title = item['title']
        created_at = ConvertDate(item['lastUpdated'])
        diff = today - datetime.fromisoformat(created_at)
        if diff.days > IGNORE_DAYS:#일주일 전의 데이터는 무시
            continue
        category = item['bulletinCategory']['name']
        content, images = GetContentandImage(id)
        source = "정석학술정보관"
        url = f"https://lib.inha.ac.kr/guide/bulletins/notice/{id}"
        notice = Notice(title, content, images, [], url, category, source, created_at)
        asyncio.create_task(process_notice(notice))
        
        await asyncio.sleep(1)  # 1초 간격으로 요청 보내기

if __name__ == "__main__":
    logger = Logger.set_logger(LOG_PATH, RICH_FORMAT, FILE_HANDLER_FORMAT)
    sys.excepthook = Logger.handle_exception
    try:
        asyncio.run(Run())
    except MainBoardConnectionError:
        logger.error("메인 게시판에 접속 실패했습니다.")
        sys.exit(1)