import time
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd

import sys
import logging
import logging.handlers

from rich.logging import RichHandler

LOG_PATH = "./SiteFetcher.log"
RICH_FORMAT = "[%(filename)s:%(lineno)s] >> %(message)s"
FILE_HANDLER_FORMAT = "[%(asctime)s]\\t%(levelname)s\\t[%(filename)s:%(funcName)s:%(lineno)s]\\t>> %(message)s"

MANUAL = False

def set_logger() -> logging.Logger:
    logging.basicConfig(
        level="NOTSET",
        format=RICH_FORMAT,
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    logger = logging.getLogger("rich")

    file_handler = logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(FILE_HANDLER_FORMAT))
    logger.addHandler(file_handler)

    return logger

def handle_exception(exc_type, exc_value, exc_traceback):
    logger = logging.getLogger("rich")

    logger.error("Unexpected exception",
                 exc_info=(exc_type, exc_value, exc_traceback))

# div._fnctWrap._articleTable > form:nth-child(1)

# 표만 나와있는 사이트 주소 구하기

def getNoticeLinkFromUserNoticeSite(url):
    res = requests.get(url)
    bs_content = bs(res.text, "html.parser")
    link = bs_content.select_one(
        "div._fnctWrap._articleTable > form:nth-child(1)")
    route = link["action"]
    return '/'.join(url.split('/')[:3])+route


def getMainPageLink(url):
    res = requests.get(url)
    a = res.text.find(" var acturl = ")
    b = res.text[a:]
    c = b.split("\"")

    return c[1]


def getNoticeDirectFromMainPage(url):
    url = getMainPageLink(url)
    res = requests.get(url)
    bs_content = bs(res.text, "html.parser")
    links = bs_content.select(".recentBbsMore")
    boardlinks = []
    for link in links:
        boardlinks.append((link["title"], link["href"]))
    matchindex = 0
    matchvalue = -1
    for i in range(len(boardlinks)):
        tval = 0
        if "공지" in boardlinks[i][0]:
            tval += 1
        if "학사" in boardlinks[i][0]:
            tval += 1
        if matchvalue < tval:
            matchvalue = tval
            matchindex = i
    res = ('/'.join(url.split('/')[:3])+boardlinks[matchindex][1]).split('?')[0]
    logger.info(f"fetched {res} from {url}")
    return res


def getMainPages():
    url = "https://www.inha.ac.kr/kr/988/subview.do"
    res = requests.get(url)
    bs_content = bs(res.text, "html.parser")
    dangadae_html = bs_content.select("div._obj._objHtml")
    dangadae = []
    for item in dangadae_html:
        name = item.select_one(".collegeWrap_1_con>h3>a")
        if name is None:
            continue
        name = name.text
        try:
            link = getNoticeDirectFromMainPage(item.select_one(".collegeWrap_1_con>a")["href"])
            dangadae.append((link, name))
            logger.info(f"added {name} {link}")
        except Exception as e:
            if MANUAL:
                print("Error: ", url)
                print(e.with_traceback())
                url = input(f"Enter the direct url of {url}")
                dangadae.append((link, name))
                logger.info(f"added {name} {link}")
            else:
                logger.error(f"Fetch Error: {name}", exc_info=sys.exc_info())
            

        major = item.select(".collegeWrap_1>ul>li")
        time.sleep(0.5)
        for m in major:
            name = m.select_one("a").text
            link_html = m.select_one("a.icon_home")
            if link_html is None:
                continue
            try:
                link = getNoticeDirectFromMainPage(link_html["href"])
                dangadae.append((link, name))
                logger.info(f"added {name} {link}")
            except Exception as e:
                if MANUAL:
                    print("Error: ", link_html["href"])
                    print(e.with_traceback())
                    link = input(f"Enter the direct url of {link_html['href']}")
                else:
                    logger.error(f"Fetch Error: {name}", exc_info=sys.exc_info())
            time.sleep(0.5)
    return dangadae


if __name__ == "__main__":
    # if run like python SiteFetcher.py --manual, it will ask url that Fetcher can't get
    logger = set_logger()
    sys.excepthook = handle_exception
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        MANUAL = True
    res = getMainPages()
    headers = ["url", "source"]
    df = pd.DataFrame(res, columns=headers)
    df.to_csv("inhalinks.csv", index=False)
