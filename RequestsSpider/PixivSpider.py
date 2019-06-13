import requests
import re
from RequestsSpider.setting import *
import os
import time
import random
import requests.adapters
import threading

_RANK_JSON_URL = RANK_JSON_REQUEST
requests.adapters.DEFAULT_RETRIES = 3


class PixivSpider:
    __pidBaseUrl = PID_BASE_URL
    __ajaxRequest = AJAX_BASE_REQUEST

    def __init__(self):
        self.loginUrl = LOGIN_URL
        self.baseUrl = BASE_URL
        self.firstPageUrl = FIRST_PAGE
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.session.keep_alive = False
        # self.session.verify = False
        self.savePath = None
        self.failDict = {}      # fail request dictionary

    def __getPostKey(self):
        pattern = re.compile('<input type="hidden".*?value="(.*?)">')
        with self.session.get(self.baseUrl) as loginHtml:
            result = re.search(pattern, loginHtml.text)
        return result.group(1)

    def login(self):
        print('Logging in...')
        postKey = self.__getPostKey()
        loginData = {
            'pixiv_id': PIXIV_ID,
            'password': PASSWORD,
            'post_key': postKey,
            'return_to': RETURN_TO
        }
        response = self.session.post(self.loginUrl, data=loginData)
        response.close()
        print('Login completed.')

    def mkdirRankDate(self):
        with self.session.get(self.firstPageUrl) as result:
            pattern = re.compile('<ul class="sibling-items".*?<a.*?>(.*?日)</a>')
            text = result.text
        date = re.search(pattern, text).group(1)
        self.savePath = os.path.join(SAVE_PATH, date)
        if not os.path.exists(self.savePath):
            os.mkdir(self.savePath)

    def getRankPidListByJSON(self, page=1, endPage=None):
        if endPage and endPage > page:
            pageRange = range(page, endPage+1)
        else:
            pageRange = (page,)
        for p in pageRange:
            with self.session.get(_RANK_JSON_URL % p) as result:
                objects = result.json()['contents']
            yield [obj['illust_id'] for obj in objects]

    # getting image original url according to pixiv json regular
    def getOriginalUrlDict(self, pidList):
        urlDict = {}
        for pid in pidList:
            url = f'{self.__pidBaseUrl}{pid}'
            response = self.session.get(self.__ajaxRequest % pid, headers={'Referer': url})
            urlJSON = response.json()['body']
            originalUrlList = [url['urls']['original'] for url in urlJSON]
            urlDict[url] = originalUrlList
        return urlDict

    def download(self, urlDict, curPage):
        print(f'开始下载排行榜第{curPage}页')
        index = 0
        for Referer, urlList in urlDict.items():
            index += 1
            for url in urlList:
                imgName = url.split('/')[-1]
                try:
                    with self.session.get(url, headers={'Referer': Referer}, timeout=20) as imgResponse:
                        self.saveImg(imgResponse, imgName, curPage, index)
                except Exception:
                    if not self.failDict.get(Referer):
                        self.failDict[Referer] = [{url: [BAD_REQUEST_RETRIES, imgName, curPage, index]}]
                    else:
                        self.failDict[Referer].append({url: [BAD_REQUEST_RETRIES, imgName, curPage, index]})
                    print(f'获取{imgName}失败！第{curPage}页 第{index}')
                time.sleep(random.randint(1, 3))

    def saveImg(self, imgResponse, imgName, curPage, index):
        imgPath = os.path.join(self.savePath, imgName)
        if imgResponse.status_code//100 == 2 and not os.path.exists(imgPath):
            imgData = imgResponse.content
            with open(imgPath, 'wb') as f:
                f.write(imgData)
                print(f'保存 {imgName} 成功！第{curPage}页 第{index}')
        else:
            print(imgName, imgResponse.status_code, f'第{curPage}页 第{index}')

    # deal request failed list
    def badDownloadDeal(self, failDict):
        while failDict:
            for Referer, urlList in failDict.items():
                for urlDict in urlList:
                    (url, infoList), = urlDict.items()
                    try:
                        with self.session.get(url, headers={'Referer': Referer}, timeout=20) as imgResponse:
                            self.saveImg(imgResponse, infoList[1], infoList[2], infoList[3])
                            if imgResponse.status_code//100 == 2:
                                failDict.pop(Referer)
                    except Exception:
                        infoList[0] -= 1
                        print(f'获取{infoList[1]}失败！第{infoList[2]}页 第{infoList[3]} 剩余重试次数{infoList[0]}')
                        if urlDict[url][0] <= 0:
                            urlList.remove(urlDict)
                if not urlList:
                    failDict.pop(Referer)

    def crawl(self, page, endPage):
        self.login()
        self.mkdirRankDate()
        curPage = page
        threads = []
        for pidList in self.getRankPidListByJSON(page, endPage):
            urlDict = self.getOriginalUrlDict(pidList)
            t = threading.Thread(target=self.download, args=(urlDict, curPage))
            threads.append(t)
            curPage += 1
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.badDownloadDeal(self.failDict)


if __name__ == '__main__':
    pixiv = PixivSpider()
    page = int(input('请输入起始页，一页50张插画\n'))
    endPage = int(input('请输入终止页\n'))
    pixiv.crawl(page, endPage)
