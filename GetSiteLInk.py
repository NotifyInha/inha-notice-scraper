import requests
import sys
from bs4 import BeautifulSoup as bs

# div._fnctWrap._articleTable > form:nth-child(1)

#표만 나와있는 사이트 주소 구하기
def getNoticeLinkFromUserNoticeSite(url):
    res = requests.get(url)
    bs_content = bs(res.text, "html.parser")
    link = bs_content.select_one("div._fnctWrap._articleTable > form:nth-child(1)")
    route = link["action"]
    return '/'.join(url.split('/')[:3])+route

def getMainPageLink(url):
    title = url.split('/')[2].split('.')[0]
    return '/'.join([url , title , "index.do"])

def getNoticeDirectFromMainPage(url):
    url = getMainPageLink(url)
    res = requests.get(url)
    bs_content = bs(res.text, "html.parser")
    links = bs_content.select(".recentBbsMore")
    boardlinks = []
    for link in links:
        boardlinks.append((link["title"],link["href"]))
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
    return ('/'.join(url.split('/')[:3])+boardlinks[matchindex][1]).split('?')[0]


def getMainPages():
    url = "https://www.inha.ac.kr/kr/988/subview.do"
    res = requests.get(url)
    bs_content = bs(res.text, "html.parser")
    dangadae_html = bs_content.select("div._obj._objHtml")
    dangadae = []
    for item in dangadae_html:
        getNoticeDirectFromMainPage(item.select_one("a")["href"])
if __name__ == "__main__":
    