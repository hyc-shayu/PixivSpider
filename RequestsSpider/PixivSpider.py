import requests
import re
from RequestsSpider.setting import *
import os
import time
import random
import requests.adapters

_COOKIE_FILE = os.path.join(os.getcwd(), 'cookie.txt')


class PixivSpider:
    __pidUrl = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='
    __ajaxRequest = 'https://www.pixiv.net/ajax/illust/%s/pages'

    def __init__(self):
        self.loginUrl = LOGIN_URL
        self.baseUrl = BASE_URL
        self.firstPageUrl = FIRST_PAGE
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.session.keep_alive = False
        # self.session.verify = False
        self.savePath = None

    def __getPostKey(self):
        loginHtml = self.session.get(self.baseUrl)
        pattern = re.compile('<input type="hidden".*?value="(.*?)">')
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
        self.session.post(self.loginUrl, data=loginData)
        print('Login completed.')

    def getRankPidList(self):
        result = self.session.get(self.firstPageUrl)
        pattern = re.compile('<ul class="sibling-items".*?<a.*?>(.*?日)</a>')
        text = result.text
        date = re.search(pattern, text).group(1)
        self.savePath = os.path.join(SAVE_PATH, date)
        if not os.path.exists(self.savePath):
            os.mkdir(self.savePath)
        pattern = re.compile('<section.*?data-title=".*?" data-user-name=".*?" data-date=".*?".*?data-id="(.*?)"', re.S)
        pidList = re.findall(pattern, text)
        return pidList

    def getOriginalUrlDict(self, pidList):
        urlDict = {}
        for pid in pidList:
            url = f'{self.__pidUrl}{pid}'
            response = self.session.get(self.__ajaxRequest % pid, headers={'Referer': url})
            urlJSON = response.json()['body']
            originalUrlList = [url['urls']['original'] for url in urlJSON]
            urlDict[url] = originalUrlList
        return urlDict

    def download(self, urlDict):
        requests.adapters.DEFAULT_RETRIES = 3
        for Referer, urlList in urlDict.items():
            for url in urlList:
                imgName = url.split('/')[-1]
                imgPath = os.path.join(self.savePath, imgName)
                imgResponse = self.session.get(url, headers={'Referer': Referer})
                if imgResponse.status_code == 200 and not os.path.exists(imgPath):          # 需要优化
                    imgData = imgResponse.content
                    with open(imgPath, 'wb') as f:
                        f.write(imgData)
                        print(f'保存 {imgName} 成功！')
                else:
                    print(imgName, imgResponse.status_code)
                time.sleep(random.random())

    def crawl(self):
        self.login()
        pidList = self.getRankPidList()
        urlDict = self.getOriginalUrlDict(pidList)
        self.download(urlDict)


if __name__ == '__main__':
    pixiv = PixivSpider()
    pixiv.crawl()
    # pixiv.login()
    # pixiv.getRankPidList()
    # for urlDict in pixiv.getOriginalUrlList(['75087826']):
    #     pixiv.download(urlDict)
